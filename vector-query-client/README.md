# vector-query-client

Execute vector similarity search queries against Vertex AI Vector Search.

## Overview

This module provides a client for executing vector similarity search queries. It converts text queries to embeddings and executes approximate nearest neighbor (ANN) search, returning ranked results with similarity scores.

## Features

- Text query to vector embedding conversion
- ANN search execution against Vertex AI Vector Search
- Similarity score calculation (0.0 to 1.0)
- Query latency tracking for SLO monitoring
- Configurable result count (top_k)
- Type-safe SearchMatch results

## Installation

```bash
# From module directory
cd vector-query-client/
make setup
```

## Usage

```python
from vector_query_client import VectorQueryClient

# Initialize client
client = VectorQueryClient(
    project_id="my-project",
    location="us-central1",
    index_endpoint_id="projects/123/locations/us-central1/indexEndpoints/456",
    deployed_index_id="deployed_index_789"
)

# Execute query
results = client.query("What is machine learning?", top_k=5)

# Process results
for match in results:
    print(f"Chunk: {match.chunk_id}")
    print(f"Score: {match.score:.3f}")
    print(f"Metadata: {match.metadata}")

# Check query latency
print(f"Query latency: {client.last_query_latency_ms:.2f}ms")
```

## API

### VectorQueryClient

Main class for executing vector queries.

#### Constructor

```python
VectorQueryClient(
    project_id: str,
    location: str,
    index_endpoint_id: str,
    deployed_index_id: str
)
```

#### Methods

##### query(query_text: str, top_k: int = 10) -> list[SearchMatch]

Execute a vector similarity search.

**Parameters:**
- `query_text`: Text query to search for
- `top_k`: Number of results to return (default: 10)

**Returns:**
- List of `SearchMatch` objects sorted by similarity score (highest first)

**Attributes:**
- `last_query_latency_ms`: Latency of last query in milliseconds

## Development

```bash
# Run tests
make test

# Run tests with coverage
make test-cov

# Format code
make format

# Lint code
make lint

# Type check
make typecheck

# All quality checks
make quality

# Build package
make build
```

## Performance

### Latency Target

- **p95 latency target**: <120ms
- Measured per query via `last_query_latency_ms`
- Includes embedding generation + vector search

### Optimization

- Uses batch embedding generation
- Efficient ANN search via Vertex AI
- Minimal post-processing

## Data Models

Uses `SearchMatch` from `shared-contracts`:

```python
SearchMatch(
    chunk_id: str,           # Unique chunk identifier
    score: float,            # Similarity score [0.0, 1.0]
    content: str,            # Matched content (empty if not fetched)
    metadata: dict[str, Any] # Match metadata
)
```

## Dependencies

- `google-cloud-aiplatform`: Vertex AI SDK
- `shared-contracts`: SearchMatch data model
- `pydantic`: Data validation

## Testing

All tests use mocked Vertex AI API calls:

```bash
# Run all tests
make test

# Run specific test
poetry run pytest tests/test_query_client.py::TestVectorQueryClient::test_query_single_result -v

# Coverage report
make test-cov
```

## Architecture

```
Query Text
    ↓
[Embedding Generation]
    ↓
Query Vector (768-dim)
    ↓
[Vertex AI Vector Search]
    ↓
Neighbor IDs + Distances
    ↓
[Distance → Score Conversion]
    ↓
List[SearchMatch]
```

## Score Conversion

Distance to similarity score conversion:

- **Distance = 0**: Perfect match → Score = 1.0
- **Distance increases**: Score decreases toward 0.0
- **Formula**: `score = 1 / (1 + distance)`

## Module Isolation

This module follows Pure Module Isolation:

- Independent build: `make setup && make test && make build`
- No `../` imports
- Self-contained tests
- Under 60 files

## License

Internal use only.
