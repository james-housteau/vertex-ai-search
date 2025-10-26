# CLAUDE.md - Demo Website Module

## Module Overview

**demo-website** is a Pure Module Isolation component providing a web interface for the Vertex AI Search API.

## Purpose

Provide a user-friendly demo interface for:
- Executing search queries against the `/search` endpoint
- Testing streaming summarization via `/summarize` endpoint
- Visualizing latency and cache performance metrics

## Architecture

### Pure Module Isolation
- Standalone FastAPI application
- Serves static HTML/CSS/JavaScript files
- No imports from parent or sibling modules
- Configurable API URL via environment variable
- Can build, test, and deploy independently

### Technology Stack
- **Backend**: FastAPI + Uvicorn (Python 3.13)
- **Frontend**: Vanilla HTML/CSS/JavaScript (no frameworks)
- **Configuration**: Pydantic Settings with environment variables
- **Testing**: pytest with TestClient
- **Deployment**: Docker + Cloud Run

## Key Components

### Backend (FastAPI)

**src/demo_website/main.py**
- `GET /` - Serve index.html
- `GET /health` - Health check endpoint
- `GET /config` - Return API URL for frontend
- `StaticFiles` mount for CSS/JS

**src/demo_website/config.py**
- Settings class with API_URL configuration
- Loads from environment or .env file
- Default: production search-api URL

### Frontend (Static Files)

**src/demo_website/static/index.html**
- Tab-based navigation (Search / Summarize)
- Search: input field + button
- Summarize: textarea + button
- Results containers for both modes

**src/demo_website/static/style.css**
- Responsive design with @media queries
- Mobile breakpoints: 768px, 480px
- Modern gradient styling
- Loading and error states

**src/demo_website/static/app.js**
- `loadConfig()` - Fetch API URL from backend
- `performSearch(query)` - GET /search with fetch()
- `performSummarize(content)` - POST /summarize with SSE streaming
- Event listeners for user interactions

## Testing Strategy

### API Tests (test_api.py)
- Health check returns healthy status
- Config endpoint returns API URL
- Root serves index.html
- Static files are accessible

### Static Content Tests (test_static_content.py)
- All required files exist
- HTML contains required elements (search, summary, tabs)
- CSS includes responsive media queries
- JavaScript includes fetch calls and endpoints
- JavaScript handles SSE streaming

### Coverage Requirement
- Minimum 80% code coverage
- Run with: `make test-cov`

## Development Workflow

### Standard Commands
```bash
cd demo-website/

make setup       # Install dependencies
make test        # Run all tests
make test-quick  # Run quick subset
make quality     # Format + lint + typecheck
make build       # Build Docker image
make deploy      # Deploy to Cloud Run
```

### Local Development
```bash
# Start dev server with hot reload
poetry run uvicorn demo_website.main:app --reload

# Access at http://localhost:8000
# API config loaded from environment
```

### Testing
```bash
# All tests with coverage
make test-cov

# Specific test file
poetry run pytest tests/test_api.py -v

# Specific test function
poetry run pytest tests/test_api.py::test_health_check -v
```

## Configuration

### Environment Variables
```bash
API_URL=https://search-api-546806894637.us-central1.run.app
HOST=0.0.0.0
PORT=8080
```

### .env File
```
API_URL=https://search-api-546806894637.us-central1.run.app
```

## API Integration

### Search Endpoint
```
GET {API_URL}/search?query=YOUR_QUERY

Response:
{
  "results": [...],
  "latency_ms": 120,
  "cache_hit": true
}
```

### Summarize Endpoint
```
POST {API_URL}/summarize
Content-Type: application/json

{"content": "YOUR_CONTENT"}

Response: SSE stream
data: {"text": "chunk1"}
data: {"text": "chunk2"}
data: [DONE]
```

## Code Quality Standards

### Type Safety
- All functions have type annotations
- Mypy strict mode enforced
- No `Any` types without justification

### Code Style
- Black formatting (88 chars)
- Ruff linting
- Consistent naming conventions

### Testing
- 80% minimum coverage
- Test critical paths
- No edge case over-testing

## Deployment

### Docker Build
```bash
docker build -t demo-website:latest .
```

### Cloud Run Deployment
```bash
gcloud run deploy demo-website \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars API_URL="https://search-api-546806894637.us-central1.run.app"
```

### Health Checks
- Endpoint: `GET /health`
- Returns: `{"status": "healthy"}`
- Used by Docker HEALTHCHECK and Cloud Run probes

## Module Constraints

### Pure Module Isolation Rules
1. No `../` imports - module is self-contained
2. No shared dependencies with other modules
3. Must build independently: `cd demo-website && make build`
4. Must test independently: `cd demo-website && make test`
5. Keep under 60 files for AI-safe development

### File Count
Current: ~10 files (well under limit)

## Common Tasks

### Add New Feature
1. Write failing test first (TDD)
2. Implement minimal code to pass
3. Run `make test` to verify
4. Run `make quality` for code standards
5. Update README if public-facing

### Fix Bug
1. Write test that reproduces bug
2. Fix code to make test pass
3. Verify all tests still pass
4. Check coverage didn't drop

### Update API Integration
1. Update API_URL in config.py or .env
2. Test with new endpoint
3. Update frontend if response format changed
4. Update tests if needed

## Troubleshooting

### Tests Failing
```bash
# Check test output
make test -v

# Check coverage
make test-cov

# Run specific failing test
poetry run pytest tests/test_api.py::test_name -v
```

### Static Files Not Loading
- Verify files exist in `src/demo_website/static/`
- Check StaticFiles mount in main.py
- Ensure paths start with `/static/`

### API Connection Issues
- Check API_URL configuration
- Verify search-api is deployed and accessible
- Check CORS settings if needed
- Review network errors in browser console

## Future Considerations

This module is designed for simplicity:
- No build tools (webpack, etc.)
- No frontend frameworks (React, Vue, etc.)
- No complex state management
- No authentication (relies on search-api)

Keep it simple - only add complexity when absolutely necessary.
