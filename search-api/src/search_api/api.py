"""FastAPI application for search and summarize endpoints.

TDD GREEN Phase - Minimal implementation to make tests pass.
"""

import hashlib
import json
import os
import re
import time
from collections.abc import AsyncIterator
from typing import Any

import vertexai
from cachetools import TTLCache
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from google.cloud import storage
from pydantic import BaseModel, Field
from shared_contracts import SearchMatch
from vector_query_client import VectorQueryClient
from vertexai.generative_models import GenerativeModel

# Initialize FastAPI app
app = FastAPI(title="Search API", version="0.1.0")

# Add CORS middleware to allow requests from demo-website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize cache: 300s TTL, 1000 max entries
search_cache: TTLCache[str, tuple[list[SearchMatch], float]] = TTLCache(
    maxsize=1000, ttl=300
)

# Content lookup dictionary: chunk_id -> content
content_lookup: dict[str, str] = {}

# Initialize VectorQueryClient (lazily to avoid issues during testing)
_vector_client: VectorQueryClient | None = None


def get_vector_client() -> VectorQueryClient:
    """Get or create VectorQueryClient instance."""
    global _vector_client
    if _vector_client is None:
        _vector_client = VectorQueryClient(
            project_id=os.environ.get("GCP_PROJECT_ID", ""),
            location=os.environ.get("GCP_LOCATION", ""),
            index_endpoint_id=os.environ.get("INDEX_ENDPOINT_ID", ""),
            deployed_index_id=os.environ.get("DEPLOYED_INDEX_ID", ""),
        )
    return _vector_client


# Pydantic models for request/response validation
class SummarizeRequest(BaseModel):
    """Request model for /summarize endpoint."""

    query: str = Field(..., min_length=1)
    max_tokens: int | None = Field(default=None, ge=1)
    top_k: int = Field(default=5, ge=1, le=20)


class SearchResponse(BaseModel):
    """Response model for /search endpoint."""

    results: list[SearchMatch]
    latency_ms: float
    cache_hit: bool = False


@app.on_event("startup")
async def load_content_lookup() -> None:
    """Load chunk content from GCS on startup."""
    global content_lookup

    try:
        client = storage.Client()
        bucket = client.bucket("nq-html-docs-20251024")
        blob = bucket.blob("chunks/all-chunks.jsonl")

        # Download and parse chunks
        content = blob.download_as_text()
        for line in content.strip().split("\n"):
            if line:
                chunk = json.loads(line)
                content_lookup[chunk["chunk_id"]] = chunk["content"]

        print(f"Loaded {len(content_lookup)} chunks into content lookup")
    except Exception as e:
        print(f"Warning: Failed to load content lookup: {e}")
        # Continue without content - app will still work but with empty content fields


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "search-api"}


@app.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1), top_k: int = Query(default=10, ge=1)
) -> dict[str, Any]:
    """Execute vector search with caching.

    Args:
        q: Query text
        top_k: Number of results to return

    Returns:
        SearchResponse with results, latency, and cache status
    """
    start_time = time.time()

    # Check if vector search is configured
    index_endpoint_id = os.environ.get("INDEX_ENDPOINT_ID", "")
    deployed_index_id = os.environ.get("DEPLOYED_INDEX_ID", "")

    if not index_endpoint_id or not deployed_index_id:
        # Return empty results with helpful message
        from fastapi import HTTPException

        raise HTTPException(
            status_code=503,
            detail=(
                "Vector search not configured. Please set "
                "INDEX_ENDPOINT_ID and DEPLOYED_INDEX_ID environment variables."
            ),
        )

    # Normalize query for cache consistency (lowercase + strip + collapse whitespace)
    normalized_q = re.sub(r"\s+", " ", q.lower().strip())

    # Generate cache key from normalized query
    cache_key = hashlib.md5(f"{normalized_q}:{top_k}".encode()).hexdigest()

    # Check cache
    if cache_key in search_cache:
        cached_results, _ = search_cache[cache_key]
        latency_ms = (time.time() - start_time) * 1000
        return {
            "results": cached_results,
            "latency_ms": latency_ms,
            "cache_hit": True,
        }

    # Cache miss - query vector search with normalized query
    client = get_vector_client()
    results = client.query(normalized_q, top_k=top_k)

    # Populate content from lookup
    for result in results:
        if result.chunk_id in content_lookup:
            result.content = content_lookup[result.chunk_id]

    # Store in cache
    search_cache[cache_key] = (results, time.time())

    # Calculate total latency
    latency_ms = (time.time() - start_time) * 1000

    return {
        "results": results,
        "latency_ms": latency_ms,
        "cache_hit": False,
    }


def classify_query_complexity(query: str, result_count: int) -> str:
    """Classify query complexity for model selection.

    Args:
        query: The user's query
        result_count: Number of search results found

    Returns:
        "simple" for straightforward queries (gemini-2.5-flash-lite)
        "medium" for moderate queries (gemini-2.5-flash)
        "complex" for detailed analysis (gemini-2.5-pro)
    """
    # Simple heuristic based on query length
    word_count = len(query.split())
    has_simple_indicators = any(
        word in query.lower()
        for word in ["what", "when", "where", "who", "list", "show"]
    )

    # Simple queries: very short factual questions
    if word_count <= 5 and has_simple_indicators:
        return "simple"

    # Medium queries: standard questions with moderate context
    if word_count <= 15:
        return "medium"

    # Complex queries: detailed questions or many results to synthesize
    return "complex"


@app.post("/summarize")
async def summarize(request: SummarizeRequest) -> StreamingResponse:
    """RAG-powered streaming summary using Vector Search + Gemini.

    Workflow:
    1. Search the Wikipedia corpus using vector search
    2. Retrieve relevant document chunks
    3. Generate summary based on retrieved content
    4. Stream response with Gemini 2.5 models

    Model selection:
    - Simple queries (≤5 words) → gemini-2.5-flash-lite (ultra fast)
    - Medium queries (≤15 words) → gemini-2.5-flash (fast & intelligent)
    - Complex queries (>15 words) → gemini-2.5-pro (most advanced)

    Args:
        request: SummarizeRequest with query, top_k, and optional max_tokens

    Returns:
        StreamingResponse with Server-Sent Events
    """

    async def generate_sse() -> AsyncIterator[str]:
        """Generate RAG SSE stream: Search → Retrieve → Generate."""
        import json

        start_time = time.time()

        # Normalize query for cache consistency
        # (lowercase + strip + collapse whitespace)
        normalized_q = re.sub(r"\s+", " ", request.query.lower().strip())

        # Generate cache key from normalized query
        cache_key = hashlib.md5(f"{normalized_q}:{request.top_k}".encode()).hexdigest()

        # Check cache
        cache_hit = False
        if cache_key in search_cache:
            search_results, _ = search_cache[cache_key]
            cache_hit = True
        else:
            # Step 1: Search the corpus (cache miss)
            client = get_vector_client()
            search_results = client.query(normalized_q, top_k=request.top_k)

            # Populate content from lookup
            for result in search_results:
                if result.chunk_id in content_lookup:
                    result.content = content_lookup[result.chunk_id]

            # Store in cache
            search_cache[cache_key] = (search_results, time.time())

        search_time_ms = (time.time() - start_time) * 1000

        # Step 2: Build context from search results
        if not search_results:
            # No results found - use general knowledge
            context = (
                f"No specific documents found in the knowledge base for: "
                f"{request.query}"
            )
        else:
            # Combine retrieved chunks into context
            context_parts = []
            for i, result in enumerate(search_results, 1):
                chunk_text = (
                    result.content
                    if result.content
                    else f"[Document: {result.chunk_id}]"
                )
                context_parts.append(
                    f"Document {i} (relevance: {result.score:.2f}):\n{chunk_text}"
                )
            context = "\n\n".join(context_parts)

        # Step 3: Select model based on query complexity
        complexity = classify_query_complexity(request.query, len(search_results))
        if complexity == "simple":
            model_name = "gemini-2.5-flash-lite"
        elif complexity == "medium":
            model_name = "gemini-2.5-flash"
        else:
            model_name = "gemini-2.5-pro"

        # Step 4: Initialize Vertex AI
        project_id = os.environ.get("GCP_PROJECT_ID", "")
        location = os.environ.get("GCP_LOCATION", "")
        vertexai.init(project=project_id, location=location)
        model = GenerativeModel(model_name)

        # Step 5: Build RAG prompt
        prompt = (
            f"Based on the following documents from the knowledge base, "
            f"provide a comprehensive answer to the user's question.\n\n"
            f"Question: {request.query}\n\n"
            f"Retrieved Documents:\n{context}\n\n"
            f"Please synthesize the information above and provide a clear, "
            f"accurate answer. If the documents don't contain enough "
            f"information, acknowledge this."
        )

        # Configure generation
        generation_config: dict[str, Any] | None = None
        if request.max_tokens:
            generation_config = {"max_output_tokens": request.max_tokens}

        # Step 6: Generate streaming response
        response = model.generate_content(
            prompt, stream=True, generation_config=generation_config
        )

        # Track streaming metrics
        first_token_time = None
        last_token_time = None
        token_count = 0

        # Stream tokens as SSE
        for chunk in response:
            if chunk.text:
                # Approximate token count using word count * 1.3
                # (rough heuristic: ~1.3 tokens per word for English text)
                words_in_chunk = len(chunk.text.split())
                token_count += max(1, int(words_in_chunk * 1.3))

                # Send metadata on first token
                if first_token_time is None:
                    first_token_time = time.time()
                    time_to_first_token_ms = (first_token_time - start_time) * 1000

                    metadata = json.dumps(
                        {
                            "metadata": {
                                "model": model_name,
                                "search_time_ms": round(search_time_ms, 2),
                                "results_found": len(search_results),
                                "time_to_first_token_ms": round(
                                    time_to_first_token_ms, 2
                                ),
                                "cache_hit": cache_hit,
                            }
                        }
                    )
                    yield f"data: {metadata}\n\n"

                # Track last token time
                last_token_time = time.time()

                # Send text token
                data = json.dumps({"text": chunk.text})
                yield f"data: {data}\n\n"

        # Send final metadata
        total_time_ms = (time.time() - start_time) * 1000
        time_to_last_token_ms = (
            (last_token_time - start_time) * 1000 if last_token_time else 0
        )
        final_metadata = json.dumps(
            {
                "done": True,
                "total_time_ms": round(total_time_ms, 2),
                "time_to_last_token_ms": round(time_to_last_token_ms, 2),
                "token_count": token_count,
            }
        )
        yield f"data: {final_metadata}\n\n"

    return StreamingResponse(generate_sse(), media_type="text/event-stream")
