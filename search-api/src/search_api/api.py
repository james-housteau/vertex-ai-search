"""FastAPI application for search and summarize endpoints.

TDD GREEN Phase - Minimal implementation to make tests pass.
"""

import hashlib
import os
import time
from typing import Any, AsyncIterator

import google.generativeai as genai
from cachetools import TTLCache
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from shared_contracts import SearchMatch
from vector_query_client import VectorQueryClient

# Initialize FastAPI app
app = FastAPI(title="Search API", version="0.1.0")

# Initialize cache: 300s TTL, 1000 max entries
search_cache: TTLCache[str, tuple[list[SearchMatch], float]] = TTLCache(
    maxsize=1000, ttl=300
)

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

    content: str = Field(..., min_length=1)
    max_tokens: int | None = Field(default=None, ge=1)


class SearchResponse(BaseModel):
    """Response model for /search endpoint."""

    results: list[SearchMatch]
    latency_ms: float
    cache_hit: bool = False


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

    # Generate cache key
    cache_key = hashlib.md5(f"{q}:{top_k}".encode()).hexdigest()

    # Check cache
    if cache_key in search_cache:
        cached_results, _ = search_cache[cache_key]
        latency_ms = (time.time() - start_time) * 1000
        return {
            "results": cached_results,
            "latency_ms": latency_ms,
            "cache_hit": True,
        }

    # Cache miss - query vector search
    client = get_vector_client()
    results = client.query(q, top_k=top_k)

    # Store in cache
    search_cache[cache_key] = (results, time.time())

    # Calculate total latency
    latency_ms = (time.time() - start_time) * 1000

    return {
        "results": results,
        "latency_ms": latency_ms,
        "cache_hit": False,
    }


@app.post("/summarize")
async def summarize(request: SummarizeRequest) -> StreamingResponse:
    """Generate streaming summary using Gemini Flash.

    Args:
        request: SummarizeRequest with content and optional max_tokens

    Returns:
        StreamingResponse with Server-Sent Events
    """

    async def generate_sse() -> AsyncIterator[str]:
        """Generate SSE stream from Gemini."""
        # Initialize Gemini
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Generate summary with streaming
        prompt = f"Summarize the following content concisely:\n\n{request.content}"

        # Configure generation
        generation_config = {}
        if request.max_tokens:
            generation_config["max_output_tokens"] = request.max_tokens

        response = model.generate_content(
            prompt, stream=True, generation_config=generation_config or None
        )

        # Stream tokens as SSE
        for chunk in response:
            if chunk.text:
                yield f"data: {chunk.text}\n\n"

    return StreamingResponse(generate_sse(), media_type="text/event-stream")
