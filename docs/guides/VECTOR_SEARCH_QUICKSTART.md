# Vector Search Quickstart Guide

This guide shows you how to use the low-latency vector search pipeline to enable sub-120ms query performance for your Vertex AI Search system.

## Overview

The vector search pipeline consists of 5 independent modules that process HTML documents into searchable vector embeddings:

1. **html-chunker** - Split HTML documents into 450-token chunks with 80-token overlap
2. **embedding-generator** - Generate text-embedding-004 vectors (768 dimensions)
3. **vector-index-prep** - Prepare JSONL format for Vertex AI Vector Search
4. **vector-search-index** - Create and manage Vector Search indexes
5. **vector-query-client** - Execute fast ANN (Approximate Nearest Neighbor) queries

**Performance Target**: <120ms p95 query latency

## Prerequisites

### GCP Setup
- Google Cloud Project with billing enabled
- Vertex AI API enabled
- Service account with permissions:
  - `aiplatform.endpoints.predict`
  - `aiplatform.indexes.create`
  - `aiplatform.indexes.update`
  - `aiplatform.indexEndpoints.deploy`

### Environment Setup
```bash
# Set your GCP project
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# Install modules (each module is independent)
cd html-chunker && make setup && cd ..
cd embedding-generator && make setup && cd ..
cd vector-index-prep && make setup && cd ..
cd vector-search-index && make setup && cd ..
cd vector-query-client && make setup && cd ..
```

## Step-by-Step Guide

### Step 1: Chunk Your HTML Documents

Break HTML documents into semantic chunks suitable for embedding.

```python
from html_chunker.chunker import HTMLChunker
from shared_contracts.models import TextChunk

# Initialize chunker
chunker = HTMLChunker(
    chunk_size=450,  # tokens per chunk
    overlap=80,      # token overlap between chunks
)

# Chunk a single document
with open("document.html", "r") as f:
    html_content = f.read()

chunks: list[TextChunk] = chunker.chunk_html(
    html_content=html_content,
    doc_id="doc_123",
    metadata={"source": "wikipedia", "category": "science"},
)

print(f"Created {len(chunks)} chunks")
# Output: Created 15 chunks

# Each chunk has:
# - chunk_id: "doc_123_chunk_0", "doc_123_chunk_1", ...
# - text: The actual text content
# - token_count: Number of tokens
# - metadata: Your custom metadata
```

### Step 2: Generate Vector Embeddings

Convert text chunks into 768-dimensional vectors using text-embedding-004.

```python
from embedding_generator.generator import EmbeddingGenerator
from shared_contracts.models import Vector768

# Initialize generator
generator = EmbeddingGenerator(
    project_id="your-project-id",
    location="us-central1",
    model="text-embedding-004",  # 768 dimensions
)

# Generate embeddings for chunks
vectors: list[Vector768] = generator.generate_embeddings(chunks)

print(f"Generated {len(vectors)} vectors")
# Output: Generated 15 vectors

# Each vector has:
# - chunk_id: Matching the TextChunk ID
# - embedding: list[float] of 768 dimensions
# - model: "text-embedding-004"
# - timestamp: Generation time
```

**Batch Processing**:
```python
# For large datasets, use batch processing
batch_size = 100
all_vectors = []

for i in range(0, len(chunks), batch_size):
    batch = chunks[i:i+batch_size]
    batch_vectors = generator.generate_embeddings(batch)
    all_vectors.extend(batch_vectors)
    print(f"Processed {len(all_vectors)}/{len(chunks)} chunks")
```

### Step 3: Prepare Index Data

Convert vectors to JSONL format required by Vertex AI Vector Search.

```python
from vector_index_prep.prep import IndexPreparation
from pathlib import Path

# Initialize prep tool
prep = IndexPreparation(
    output_dir=Path("/tmp/vector-index-data"),
)

# Prepare JSONL file
output_file = prep.prepare_index_data(
    vectors=vectors,
    chunks=chunks,  # Optional: include metadata
    output_filename="index_data.jsonl",
)

print(f"Created index file: {output_file}")
# Output: Created index file: /tmp/vector-index-data/index_data.jsonl

# File format (one JSON object per line):
# {"id": "doc_123_chunk_0", "embedding": [0.1, 0.2, ...], "restricts": [...], "metadata": {...}}
# {"id": "doc_123_chunk_1", "embedding": [0.3, 0.4, ...], "restricts": [...], "metadata": {...}}
```

**Upload to GCS**:
```python
from google.cloud import storage

# Upload to GCS bucket
client = storage.Client()
bucket = client.bucket("your-bucket-name")
blob = bucket.blob("vector-data/index_data.jsonl")
blob.upload_from_filename(output_file)

print(f"Uploaded to gs://your-bucket-name/vector-data/index_data.jsonl")
```

### Step 4: Create Vector Search Index

Create a Vertex AI Vector Search index from your JSONL data.

```python
from vector_search_index.index_manager import VectorSearchIndexManager

# Initialize index manager
manager = VectorSearchIndexManager(
    project_id="your-project-id",
    location="us-central1",
)

# Create index
index_id = manager.create_index(
    display_name="nq-html-docs-index",
    description="Vector search index for Natural Questions HTML documents",
    dimensions=768,  # text-embedding-004
    shard_size="SHARD_SIZE_SMALL",  # Options: SMALL, MEDIUM, LARGE
    distance_measure="DOT_PRODUCT_DISTANCE",  # Or COSINE, EUCLIDEAN
    algorithm_config={
        "treeAhConfig": {
            "leafNodeEmbeddingCount": 1000,
            "leafNodesToSearchPercent": 7,
        }
    },
    gcs_uri="gs://your-bucket-name/vector-data/index_data.jsonl",
)

print(f"Created index: {index_id}")
# Output: Created index: projects/123/locations/us-central1/indexes/456

# Wait for index to be ready (can take 30-60 minutes)
manager.wait_for_index_ready(index_id, timeout_minutes=90)
```

**Deploy Index to Endpoint**:
```python
# Create endpoint (one-time setup)
endpoint_id = manager.create_endpoint(
    display_name="nq-search-endpoint",
    description="Endpoint for fast vector search queries",
)

# Deploy index to endpoint
deployed_index_id = manager.deploy_index(
    endpoint_id=endpoint_id,
    index_id=index_id,
    deployed_index_id="nq_html_docs_v1",
    min_replica_count=1,
    max_replica_count=2,
)

print(f"Deployed index {deployed_index_id} to endpoint {endpoint_id}")
```

### Step 5: Query Your Index

Execute fast vector similarity searches with <120ms latency.

```python
from vector_query_client.query_client import VectorQueryClient
from shared_contracts.models import SearchMatch

# Initialize query client
client = VectorQueryClient(
    project_id="your-project-id",
    location="us-central1",
    index_endpoint_id=endpoint_id,
    deployed_index_id=deployed_index_id,
)

# Execute a search query
query = "What is machine learning?"
results: list[SearchMatch] = client.search(
    query_text=query,
    top_k=10,
    embedding_model="text-embedding-004",
)

# Display results
for i, match in enumerate(results, 1):
    print(f"{i}. Score: {match.score:.3f}")
    print(f"   Chunk: {match.chunk_id}")
    print(f"   Preview: {match.content[:100]}...")
    print()

# Output:
# 1. Score: 0.876
#    Chunk: doc_123_chunk_5
#    Preview: Machine learning is a subset of artificial intelligence...
#
# 2. Score: 0.834
#    Chunk: doc_456_chunk_2
#    Preview: Supervised learning algorithms learn from labeled data...
```

**Performance Tracking**:
```python
import time

# Measure query latency
start = time.time()
results = client.search(query_text=query, top_k=10)
latency_ms = (time.time() - start) * 1000

print(f"Query latency: {latency_ms:.1f}ms")
# Target: <120ms p95 latency

# Batch queries
queries = [
    "What is machine learning?",
    "How does deep learning work?",
    "What are neural networks?",
]

latencies = []
for q in queries:
    start = time.time()
    results = client.search(query_text=q, top_k=10)
    latency = (time.time() - start) * 1000
    latencies.append(latency)

import statistics
print(f"Average latency: {statistics.mean(latencies):.1f}ms")
print(f"P95 latency: {statistics.quantiles(latencies, n=20)[18]:.1f}ms")
```

## Complete Example

Here's a full end-to-end example:

```python
from pathlib import Path
from html_chunker.chunker import HTMLChunker
from embedding_generator.generator import EmbeddingGenerator
from vector_index_prep.prep import IndexPreparation
from vector_search_index.index_manager import VectorSearchIndexManager
from vector_query_client.query_client import VectorQueryClient

# Configuration
PROJECT_ID = "your-project-id"
LOCATION = "us-central1"
BUCKET_NAME = "your-bucket-name"
HTML_DIR = Path("/path/to/html/files")
OUTPUT_DIR = Path("/tmp/vector-data")

# Step 1: Chunk HTML files
chunker = HTMLChunker(chunk_size=450, overlap=80)
all_chunks = []

for html_file in HTML_DIR.glob("*.html"):
    with open(html_file, "r") as f:
        chunks = chunker.chunk_html(
            html_content=f.read(),
            doc_id=html_file.stem,
            metadata={"source": html_file.name},
        )
        all_chunks.extend(chunks)

print(f"Step 1: Created {len(all_chunks)} chunks from {len(list(HTML_DIR.glob('*.html')))} files")

# Step 2: Generate embeddings
generator = EmbeddingGenerator(
    project_id=PROJECT_ID,
    location=LOCATION,
    model="text-embedding-004",
)

# Process in batches
batch_size = 100
all_vectors = []

for i in range(0, len(all_chunks), batch_size):
    batch = all_chunks[i:i+batch_size]
    vectors = generator.generate_embeddings(batch)
    all_vectors.extend(vectors)
    print(f"  Processed {len(all_vectors)}/{len(all_chunks)} embeddings")

print(f"Step 2: Generated {len(all_vectors)} vectors")

# Step 3: Prepare index data
prep = IndexPreparation(output_dir=OUTPUT_DIR)
output_file = prep.prepare_index_data(
    vectors=all_vectors,
    chunks=all_chunks,
    output_filename="index_data.jsonl",
)

print(f"Step 3: Created index file at {output_file}")

# Upload to GCS
from google.cloud import storage
client = storage.Client()
bucket = client.bucket(BUCKET_NAME)
blob = bucket.blob("vector-data/index_data.jsonl")
blob.upload_from_filename(output_file)
gcs_uri = f"gs://{BUCKET_NAME}/vector-data/index_data.jsonl"

print(f"  Uploaded to {gcs_uri}")

# Step 4: Create and deploy index
manager = VectorSearchIndexManager(
    project_id=PROJECT_ID,
    location=LOCATION,
)

# Create index
index_id = manager.create_index(
    display_name="nq-html-docs-index",
    description="Vector search for Natural Questions",
    dimensions=768,
    shard_size="SHARD_SIZE_SMALL",
    distance_measure="DOT_PRODUCT_DISTANCE",
    algorithm_config={
        "treeAhConfig": {
            "leafNodeEmbeddingCount": 1000,
            "leafNodesToSearchPercent": 7,
        }
    },
    gcs_uri=gcs_uri,
)

print(f"Step 4: Created index {index_id}")
print("  Waiting for index to be ready (this can take 30-60 minutes)...")

manager.wait_for_index_ready(index_id, timeout_minutes=90)

# Create and deploy endpoint
endpoint_id = manager.create_endpoint(
    display_name="nq-search-endpoint",
    description="Fast vector search endpoint",
)

deployed_index_id = manager.deploy_index(
    endpoint_id=endpoint_id,
    index_id=index_id,
    deployed_index_id="nq_html_v1",
    min_replica_count=1,
    max_replica_count=2,
)

print(f"  Deployed to endpoint {endpoint_id}")

# Step 5: Query the index
query_client = VectorQueryClient(
    project_id=PROJECT_ID,
    location=LOCATION,
    index_endpoint_id=endpoint_id,
    deployed_index_id=deployed_index_id,
)

# Test queries
test_queries = [
    "What is machine learning?",
    "How does artificial intelligence work?",
    "What are neural networks?",
]

print(f"\nStep 5: Executing {len(test_queries)} test queries")

for query in test_queries:
    results = query_client.search(query_text=query, top_k=5)
    print(f"\nQuery: {query}")
    print(f"  Found {len(results)} results")
    for i, match in enumerate(results[:3], 1):
        print(f"  {i}. {match.chunk_id} (score: {match.score:.3f})")

print("\n✅ Vector search pipeline complete!")
print(f"   - Total chunks: {len(all_chunks)}")
print(f"   - Total vectors: {len(all_vectors)}")
print(f"   - Index: {index_id}")
print(f"   - Endpoint: {endpoint_id}")
```

## Performance Characteristics

### Expected Latency
- **Target**: <120ms p95 query latency
- **Typical**: 60-90ms average latency
- **Factors affecting latency**:
  - Index size (number of vectors)
  - Replica count (more replicas = lower latency)
  - Network proximity to Vertex AI region
  - Top-k value (higher = slightly slower)

### Tuning for Performance

**1. Adjust leafNodesToSearchPercent**:
```python
# More accuracy, slightly slower (7-10%)
algorithm_config = {
    "treeAhConfig": {
        "leafNodesToSearchPercent": 10,
    }
}

# Faster, slightly less accurate (3-5%)
algorithm_config = {
    "treeAhConfig": {
        "leafNodesToSearchPercent": 5,
    }
}
```

**2. Scale replicas based on load**:
```python
# Low traffic: 1 replica
min_replica_count = 1
max_replica_count = 1

# High traffic: auto-scale 2-10 replicas
min_replica_count = 2
max_replica_count = 10
```

**3. Choose appropriate shard size**:
```python
# < 1M vectors
shard_size = "SHARD_SIZE_SMALL"

# 1M - 10M vectors
shard_size = "SHARD_SIZE_MEDIUM"

# > 10M vectors
shard_size = "SHARD_SIZE_LARGE"
```

## Monitoring and Troubleshooting

### Check Index Status
```python
from vector_search_index.index_manager import VectorSearchIndexManager

manager = VectorSearchIndexManager(
    project_id="your-project-id",
    location="us-central1",
)

# Get index details
index = manager.get_index(index_id)
print(f"Index state: {index.deployed_indexes[0].state}")
print(f"Create time: {index.create_time}")
print(f"Update time: {index.update_time}")
```

### Measure Query Performance
```python
import time
import statistics

# Collect latency samples
latencies = []
for _ in range(100):
    start = time.time()
    results = query_client.search(query_text="test query", top_k=10)
    latency = (time.time() - start) * 1000
    latencies.append(latency)

print(f"Average latency: {statistics.mean(latencies):.1f}ms")
print(f"P50 latency: {statistics.median(latencies):.1f}ms")
print(f"P95 latency: {statistics.quantiles(latencies, n=20)[18]:.1f}ms")
print(f"P99 latency: {statistics.quantiles(latencies, n=100)[98]:.1f}ms")
```

### Common Issues

**1. High Latency (>200ms)**
- Check replica count - increase min_replica_count
- Verify network proximity to Vertex AI region
- Reduce leafNodesToSearchPercent if accuracy allows
- Consider smaller top_k values

**2. Low Relevance Scores**
- Verify embedding model matches (text-embedding-004)
- Check distance measure (DOT_PRODUCT_DISTANCE for normalized embeddings)
- Ensure chunks are semantically meaningful (not too small/large)

**3. Index Creation Failures**
- Verify JSONL format is correct
- Check GCS bucket permissions
- Ensure dimensions match embedding model (768 for text-embedding-004)
- Verify project has sufficient quota

**4. Deployment Timeout**
- Increase timeout_minutes parameter
- Large indexes can take 60+ minutes to deploy
- Check Vertex AI console for deployment status

## Production API Usage (search-api)

The **search-api** module provides a production-ready FastAPI service that wraps the vector search pipeline with caching and streaming capabilities.

### Features

- **GET /search**: Fast vector similarity search with in-memory caching
- **POST /summarize**: Streaming Gemini Flash summaries via Server-Sent Events (SSE)
- **GET /health**: Health check endpoint for load balancers

### Setup

```bash
cd search-api
make setup
make test
```

### Running Locally

```python
# Start the API server
poetry run uvicorn search_api.api:app --reload --port 8000

# The API will be available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

### Using the Search Endpoint

```bash
# Simple search query
curl "http://localhost:8000/search?q=machine+learning&k=10"

# Response (first call - cache miss):
{
  "results": [
    {
      "chunk_id": "doc_123_chunk_5",
      "text": "Machine learning is a subset of artificial intelligence...",
      "score": 0.92,
      "metadata": {"source": "wikipedia", "category": "AI"}
    },
    ...
  ],
  "latency_ms": 85.3,
  "cached": false,
  "timestamp": "2025-10-25T12:34:56.789Z"
}

# Same query again (cache hit - <10ms):
{
  "results": [...],
  "latency_ms": 2.1,
  "cached": true,
  "timestamp": "2025-10-25T12:35:01.234Z"
}
```

### Using the Summarize Endpoint

```bash
# Stream a summary via Server-Sent Events
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Your long document text here...",
    "max_tokens": 150
  }' \
  -N

# Response (SSE stream):
data: {"text": "Machine", "done": false}
data: {"text": " learning", "done": false}
data: {"text": " is", "done": false}
...
data: {"text": "", "done": true}
```

### Python Client Example

```python
import httpx
from typing import List
from shared_contracts.models import SearchMatch

# Search with caching
def search_api(query: str, top_k: int = 10) -> List[SearchMatch]:
    response = httpx.get(
        "http://localhost:8000/search",
        params={"q": query, "k": top_k},
        timeout=30.0,
    )
    response.raise_for_status()
    data = response.json()

    print(f"Latency: {data['latency_ms']:.1f}ms (cached: {data['cached']})")
    return [SearchMatch(**r) for r in data["results"]]

# Streaming summarization
def summarize_stream(content: str, max_tokens: int = 150):
    with httpx.stream(
        "POST",
        "http://localhost:8000/summarize",
        json={"content": content, "max_tokens": max_tokens},
        timeout=60.0,
    ) as response:
        for line in response.iter_lines():
            if line.startswith("data: "):
                chunk = json.loads(line[6:])
                if not chunk["done"]:
                    print(chunk["text"], end="", flush=True)
        print()  # newline

# Example usage
results = search_api("quantum computing", top_k=5)
for match in results:
    print(f"Score: {match.score:.2f} - {match.text[:100]}...")
```

### Deployment to Cloud Run

```bash
# Build and deploy
cd search-api
gcloud run deploy search-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars GOOGLE_CLOUD_PROJECT=your-project-id

# Get the service URL
gcloud run services describe search-api \
  --region us-central1 \
  --format 'value(status.url)'
```

### Performance Characteristics

- **Cache hits**: <10ms latency (in-memory TTLCache)
- **Cache misses**: <120ms latency (p95 target via vector-query-client)
- **Cache TTL**: 300 seconds (configurable)
- **Cache size**: 1000 entries (configurable)
- **Concurrent requests**: Async FastAPI handles 100+ concurrent requests

### Monitoring

```python
# Health check
response = httpx.get("http://localhost:8000/health")
print(response.json())
# {"status": "healthy", "service": "search-api", "timestamp": "..."}

# Monitor cache effectiveness
# Add to your application metrics:
# - cache_hit_rate = cache_hits / total_requests
# - avg_latency_cache_hit vs avg_latency_cache_miss
```

## Next Steps

1. **Integrate with existing search**: Combine vector search with keyword search for hybrid results
2. **Add re-ranking**: Use cross-encoder models to re-rank top results
3. **Implement filtering**: Use metadata restricts for filtered searches
4. **Monitor production**: Set up Cloud Monitoring alerts for latency/errors
5. **Optimize costs**: Right-size replicas and use cheaper regions for dev/test

## Additional Resources

- [Vertex AI Vector Search Documentation](https://cloud.google.com/vertex-ai/docs/vector-search)
- [Text Embedding Models](https://cloud.google.com/vertex-ai/docs/generative-ai/embeddings/get-text-embeddings)
- [ScaNN Algorithm](https://github.com/google-research/google-research/tree/master/scann)
- [Performance Tuning Guide](https://cloud.google.com/vertex-ai/docs/vector-search/performance-tuning)

---

**Last Updated**: 2025-10-25
**Module Versions**: html-chunker v0.1.0, embedding-generator v0.1.0, vector-index-prep v0.1.0, vector-search-index v0.1.0, vector-query-client v0.1.0, search-api v0.1.0
