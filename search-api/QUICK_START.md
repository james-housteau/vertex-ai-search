# Search API - Quick Start Guide

## 5-Minute Setup

### 1. Navigate to Module
```bash
cd /Users/source-code/vertex-ai-search/worktrees/feature-20/search-api/
```

### 2. Install Dependencies
```bash
make setup
```

### 3. Run Tests
```bash
make test
```

### 4. Check Coverage
```bash
make test-cov
```

### 5. Verify Code Quality
```bash
make quality
```

---

## Development Workflow

### Run Specific Tests
```bash
# Single test file
poetry run pytest tests/test_search_endpoint.py -v

# Single test class
poetry run pytest tests/test_search_endpoint.py::TestSearchEndpoint -v

# Single test function
poetry run pytest tests/test_search_endpoint.py::TestSearchEndpoint::test_search_returns_results -v

# Pattern matching
poetry run pytest -k "cache" -v
```

### Code Quality
```bash
# Format code
make format

# Lint code
make lint

# Type check
make typecheck

# All quality checks
make quality
```

---

## Running Locally

### Set Environment Variables
```bash
export GCP_PROJECT_ID="your-project-id"
export GCP_LOCATION="us-central1"
export INDEX_ENDPOINT_ID="projects/.../indexEndpoints/..."
export DEPLOYED_INDEX_ID="your-deployed-index-id"
export GEMINI_API_KEY="your-gemini-api-key"
```

### Start Server
```bash
# Method 1: Using main.py
poetry run python -m search_api.main

# Method 2: Using uvicorn directly
poetry run uvicorn search_api.api:app --reload --port 8080
```

### Test Endpoints

#### Health Check
```bash
curl http://localhost:8080/health
```

#### Search
```bash
curl "http://localhost:8080/search?q=machine+learning&top_k=5"
```

#### Summarize
```bash
curl -X POST http://localhost:8080/summarize \
  -H "Content-Type: application/json" \
  -d '{"content": "Your long text here", "max_tokens": 100}'
```

---

## Common Tasks

### Add New Dependency
```bash
poetry add package-name

# Development dependency
poetry add --group dev package-name
```

### Update Dependencies
```bash
poetry update
```

### View API Documentation
```bash
# Start server, then visit:
# http://localhost:8080/docs (Swagger UI)
# http://localhost:8080/redoc (ReDoc)
```

### Clean Build Artifacts
```bash
make clean
```

### Build Package
```bash
make build
```

---

## Troubleshooting

### Tests Failing?
```bash
# Run with verbose output
poetry run pytest -vv

# Run with print statements visible
poetry run pytest -s

# Stop on first failure
poetry run pytest -x
```

### Import Errors?
```bash
# Reinstall dependencies
make clean
make setup
```

### Type Errors?
```bash
# Check types
make typecheck

# With detailed output
poetry run mypy src/ --show-error-codes
```

### Coverage Too Low?
```bash
# See which lines aren't covered
make test-cov
open htmlcov/index.html
```

---

## Integration with Other Modules

### Using Shared Contracts
```python
from shared_contracts import SearchMatch

match = SearchMatch(
    chunk_id="chunk-1",
    score=0.95,
    content="content",
    metadata={}
)
```

### Using Vector Query Client
```python
from vector_query_client import VectorQueryClient

client = VectorQueryClient(
    project_id="project",
    location="us-central1",
    index_endpoint_id="endpoint",
    deployed_index_id="index"
)

results = client.query("query text", top_k=10)
```

---

## Performance Monitoring

### Check Cache Hit Rate
```python
from search_api.api import search_cache

print(f"Cache size: {len(search_cache)}")
print(f"Cache info: {search_cache.currsize}/{search_cache.maxsize}")
```

### Monitor Latency
- Cache hits should be <10ms
- Cache misses should be <120ms p95
- Check `latency_ms` field in response

---

## Deployment Checklist

- [ ] All tests pass (`make test`)
- [ ] Coverage ≥80% (`make test-cov`)
- [ ] Code quality checks pass (`make quality`)
- [ ] Environment variables configured
- [ ] Docker image builds successfully
- [ ] Health check responds correctly
- [ ] Search endpoint returns results
- [ ] Summarize endpoint streams properly

---

## Help & Resources

### Module Documentation
- `README.md` - Module overview
- `CLAUDE.md` - Development guidance
- `IMPLEMENTATION_SUMMARY.md` - Implementation details

### Project Documentation
- Root `CLAUDE.md` - Monorepo architecture
- `.claude/LEAN-TDD-WORKFLOW.md` - TDD workflow

### External Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Vertex AI Vector Search](https://cloud.google.com/vertex-ai/docs/vector-search)
- [Gemini API Docs](https://ai.google.dev/docs)

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `make setup` | Install dependencies |
| `make test` | Run all tests |
| `make test-quick` | Fast test subset |
| `make test-cov` | Coverage report |
| `make format` | Format code |
| `make lint` | Lint code |
| `make typecheck` | Type check |
| `make quality` | All quality checks |
| `make build` | Build package |
| `make clean` | Clean artifacts |

---

**Module Path**: `/Users/source-code/vertex-ai-search/worktrees/feature-20/search-api/`

**Status**: ✅ Ready for integration testing and deployment
