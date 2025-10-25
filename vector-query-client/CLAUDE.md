# CLAUDE.md

This file provides guidance to Claude Code when working with this module.

## Module Overview

**vector-query-client** executes vector similarity search queries against Vertex AI Vector Search. It converts text queries to embeddings and returns ranked SearchMatch results with latency tracking.

## Purpose

This module exists to:
1. Execute text-to-vector similarity searches
2. Convert query text to embeddings using Vertex AI
3. Query Vertex AI Vector Search index
4. Return ranked results as SearchMatch objects
5. Track query latency for SLO monitoring (target: <120ms p95)

## Development Commands

### Essential Commands
```bash
# Initial setup
make setup

# Run tests
make test                 # All tests with verbose output
make test-quick          # Fast subset for rapid feedback
make test-cov            # Tests with coverage report (80% minimum)

# Code quality
make format              # Format with black and ruff
make lint                # Lint with ruff
make typecheck           # Type check with mypy
make quality             # All quality checks

# Build
make build               # Build wheel packages
make clean               # Clean artifacts
```

### Single Test Execution
```bash
# Run specific test file
poetry run pytest tests/test_query_client.py -v

# Run specific test class
poetry run pytest tests/test_query_client.py::TestVectorQueryClient -v

# Run specific test function
poetry run pytest tests/test_query_client.py::TestVectorQueryClient::test_query_single_result -v

# Run tests matching pattern
poetry run pytest -k "latency" -v
```

## Code Architecture

### Module Structure
```
vector-query-client/
├── src/vector_query_client/
│   ├── __init__.py      # Public API exports
│   └── query_client.py  # Core query client logic
├── tests/
│   └── test_query_client.py # Comprehensive tests with mocked API
├── Makefile             # Standard targets
├── pyproject.toml       # Poetry configuration
├── CLAUDE.md            # This file
└── README.md            # Usage documentation
```

### Core Components

#### VectorQueryClient
Main class for executing vector queries.
- Initializes Vertex AI client
- Generates query embeddings
- Executes ANN search
- Converts distances to similarity scores
- Tracks query latency

## Technology Stack

- **Python Version**: 3.13+
- **Package Manager**: Poetry
- **Vertex AI SDK**: google-cloud-aiplatform
- **Embedding Model**: text-embedding-004 (768 dimensions)
- **Validation**: Pydantic v2 (via shared-contracts)
- **Testing**: pytest with mocked API calls
- **Code Quality**: black (88 chars), ruff, mypy strict

## Important Notes

### Pure Module Isolation
- **No `../` imports** - This module is completely independent
- **Dependencies**: google-cloud-aiplatform, pydantic, shared-contracts
- **Can build independently**: `cd vector-query-client && make setup && make test`
- **Must stay under 60 files** (currently at ~8 files)

### API Integration
- Uses Vertex AI MatchingEngineIndexEndpoint for queries
- Uses TextEmbeddingModel for query embedding generation
- All tests mock API calls - no real requests during testing
- Configurable top_k for result count

### Distance to Score Conversion
- **Input**: Distance from vector search (lower = more similar)
- **Output**: Similarity score [0.0, 1.0] (higher = more similar)
- **Formula**: `score = 1 / (1 + distance)`
- Distance 0 → Score 1.0 (perfect match)
- Higher distance → Lower score

### Latency Tracking
- Measured per query in milliseconds
- Stored in `last_query_latency_ms` attribute
- Includes embedding generation + vector search time
- Target: <120ms p95 for production

## Dependencies

### Upstream
- **shared-contracts** - Uses SearchMatch model

### Downstream
This module provides query functionality to:
- **evaluator** - Uses query results for evaluation
- End-user search interfaces

## Testing Requirements

- 80% minimum coverage (enforced)
- Mock all Vertex AI API calls
- Test single and multiple results
- Test latency tracking
- Test empty results
- Test custom top_k
- Test distance-to-score conversion
- Test initialization parameters

## Code Quality Requirements

- **Coverage**: Minimum 80% (enforced by pytest)
- **Formatting**: Black with 88 character line length
- **Linting**: Ruff with strict settings
- **Type Safety**: mypy strict mode, all functions typed
- **Testing**: pytest framework, HTML coverage reports

## Development Workflow

1. **Always work within this directory**: `cd vector-query-client/`
2. **Run tests frequently**: `make test` or `make test-quick`
3. **Check coverage**: `make test-cov`
4. **Verify quality**: `make quality` before commits
5. **Keep it simple**: Minimal code to satisfy requirements

## Implementation Notes

### Lean TDD Approach
- Write minimal code to pass tests
- No premature abstractions
- Direct implementation over design patterns
- Inline code before extracting functions

### Key Simplifications
- Single class (VectorQueryClient)
- Direct Vertex AI SDK usage
- Simple distance-to-score conversion
- No factory patterns or abstract base classes
- Content and metadata fetched separately (not in this module)

## Quick Reference

```bash
# First time setup
cd vector-query-client/
make setup

# Development cycle
make test-quick    # Fast feedback
make format        # Format code
make quality       # Full quality check

# Before commit
make test-cov      # Verify 80% coverage
make quality       # All checks pass
```

## Configuration Parameters

### project_id (required)
GCP project ID for Vertex AI

### location (required)
GCP location (e.g., "us-central1")

### index_endpoint_id (required)
Vertex AI index endpoint resource name

### deployed_index_id (required)
Deployed index ID within the endpoint

### top_k (optional, per query)
Number of results to return (default: 10)

## Performance Targets

### Latency
- **p95 target**: <120ms
- **Measurement**: `last_query_latency_ms` attribute
- **Components**: Embedding generation + Vector search

### Throughput
- Limited by Vertex AI quotas
- Optimize by batching queries if needed

## Integration Points

### Input
- Text query string
- Optional top_k parameter

### Output
- `List[SearchMatch]` from shared-contracts
- Sorted by similarity score (highest first)
- Empty list if no matches found

### Latency
- `last_query_latency_ms` attribute
- Updated after each query
- Used for SLO monitoring

## Error Handling

- Vertex AI API errors propagate to caller
- Empty results return empty list (not error)
- Invalid parameters caught by type system

## Future Enhancements

Keep it simple - no future enhancements until needed:
- Content fetching (separate module)
- Metadata enrichment (separate module)
- Query caching (if performance requires)
- Batch query support (if throughput requires)
