# CLAUDE.md

This file provides guidance to Claude Code when working with this module.

## Module Overview

**search-api** is a Cloud Run API service providing fast vector search and streaming summaries. It implements Phase 3 of Issue #1 with <120ms p95 vector search latency using in-memory caching.

## Purpose

This module exists to:
1. Provide GET /search endpoint for fast vector search with caching
2. Provide POST /summarize endpoint for streaming Gemini Flash summaries via SSE
3. Achieve <120ms p95 latency for search queries
4. Implement in-memory caching with 300s TTL and 1000 entry limit
5. Return SearchMatch results from shared-contracts

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
poetry run pytest tests/test_search_endpoint.py -v

# Run specific test class
poetry run pytest tests/test_search_endpoint.py::TestSearchEndpoint -v

# Run specific test function
poetry run pytest tests/test_search_endpoint.py::TestSearchEndpoint::test_search_returns_results -v

# Run tests matching pattern
poetry run pytest -k "cache" -v
```

## Code Architecture

### Module Structure
```
search-api/
├── src/search_api/
│   ├── __init__.py      # Public API exports
│   └── api.py           # FastAPI application
├── tests/
│   ├── test_search_endpoint.py     # /search endpoint tests
│   ├── test_summarize_endpoint.py  # /summarize endpoint tests
│   └── test_health_endpoint.py     # /health endpoint tests
├── Makefile             # Standard targets
├── pyproject.toml       # Poetry configuration
├── CLAUDE.md            # This file
└── README.md            # Usage documentation
```

## API Endpoints

### GET /search
Fast vector search with in-memory caching.

**Parameters:**
- `q` (required): Query text
- `top_k` (optional, default=10): Number of results

**Response:**
```json
{
  "results": [
    {
      "chunk_id": "chunk-123",
      "score": 0.95,
      "content": "matched content",
      "metadata": {}
    }
  ],
  "latency_ms": 42.5,
  "cache_hit": true
}
```

**Performance Targets:**
- Cache hits: <10ms
- Cache misses: <120ms p95

### POST /summarize
Streaming Gemini Flash summaries via Server-Sent Events.

**Request Body:**
```json
{
  "content": "text to summarize",
  "max_tokens": 100
}
```

**Response:** SSE stream
```
data: Token1
data: Token2
data: Token3
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "search-api"
}
```

## Technology Stack

- **Python Version**: 3.13+
- **Web Framework**: FastAPI
- **ASGI Server**: Uvicorn
- **Caching**: cachetools.TTLCache
- **Vector Search**: VectorQueryClient (from vector-query-client)
- **Data Models**: SearchMatch (from shared-contracts)
- **Summarization**: google-generativeai (Gemini Flash)
- **Testing**: pytest with mocked dependencies

## Important Notes

### Pure Module Isolation
- **No `../` imports** - This module is completely independent
- **Dependencies**: fastapi, uvicorn, cachetools, google-cloud-aiplatform, google-generativeai
- **Local dependencies**: shared-contracts, vector-query-client
- **Can build independently**: `cd search-api && make setup && make test`
- **Must stay under 60 files** (currently at ~10 files)

### Caching Strategy
- **Implementation**: cachetools.TTLCache
- **TTL**: 300 seconds (5 minutes)
- **Max entries**: 1000
- **Cache key**: hash(query_text + str(top_k))
- **Cache hit target**: <10ms
- **Cache miss target**: <120ms p95

### Streaming Strategy
- **Format**: Server-Sent Events (SSE)
- **Model**: Gemini Flash (fast, cost-effective)
- **Streaming**: Token-by-token via SSE
- **Content-Type**: text/event-stream

## Dependencies

### Upstream
- **shared-contracts** - Uses SearchMatch model
- **vector-query-client** - Uses VectorQueryClient for search

### Downstream
This module provides API endpoints for:
- Client applications
- Load testing
- Integration testing

## Testing Requirements

- 80% minimum coverage (enforced)
- Mock all external dependencies
- Test /search endpoint functionality
- Test /summarize streaming
- Test caching behavior
- Test health check
- Test latency tracking
- Test validation

## Code Quality Requirements

- **Coverage**: Minimum 80% (enforced by pytest)
- **Formatting**: Black with 88 character line length
- **Linting**: Ruff with strict settings
- **Type Safety**: mypy strict mode, all functions typed
- **Testing**: pytest framework, HTML coverage reports

## Development Workflow

1. **Always work within this directory**: `cd search-api/`
2. **Run tests frequently**: `make test` or `make test-quick`
3. **Check coverage**: `make test-cov`
4. **Verify quality**: `make quality` before commits
5. **Keep it simple**: Minimal code to satisfy requirements

## TDD Implementation Notes

### Lean TDD Approach
- Write minimal code to pass tests
- No premature abstractions
- Direct implementation over design patterns
- Inline code before extracting functions

### Current Phase
This module is being implemented using complete TDD methodology:
1. **RED**: Write failing tests first ✓
2. **GREEN**: Minimal implementation to pass tests (in progress)
3. **REFACTOR**: Improve code quality while maintaining tests

## Quick Reference

```bash
# First time setup
cd search-api/
make setup

# Development cycle
make test-quick    # Fast feedback
make format        # Format code
make quality       # Full quality check

# Before commit
make test-cov      # Verify 80% coverage
make quality       # All checks pass
```

## Performance Targets

### Latency
- **Cache hits**: <10ms
- **Cache misses**: <120ms p95
- **Measurement**: Tracked in response
- **Components**: VectorQueryClient query + cache overhead

### Caching
- **TTL**: 300 seconds
- **Max entries**: 1000
- **Eviction**: LRU when at capacity
- **Key**: hash(query_text + str(top_k))

## Error Handling

- FastAPI validation for request parameters
- Pydantic models for request/response validation
- External API errors propagate to client with proper status codes
- Empty results return empty list (not error)

## Cloud Run Deployment

This service is designed for Cloud Run deployment:
- Stateless design (cache is per-instance)
- Health check for readiness probes
- Efficient cold start (<2s)
- Scales to zero when idle
