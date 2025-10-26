# Demo Website

Demo website with search and streaming summary UI for the deployed search-api.

## Overview

This module provides a web interface for testing the Vertex AI Search API. It features:

- **Search Interface**: Query the `/search` endpoint and display results with latency/cache indicators
- **Summary Interface**: Send content to `/summarize` and display streaming SSE responses
- **Responsive Design**: Works on mobile and desktop
- **Health Checks**: Readiness probes for Cloud Run deployment

## Architecture

This is a Pure Module Isolation component:
- Standalone FastAPI application serving static files
- No dependencies on other modules
- Configurable API URL via environment variable
- Can be built, tested, and deployed independently

## Quick Start

```bash
cd demo-website/

# Install dependencies
make setup

# Run tests
make test

# Start development server
poetry run uvicorn demo_website.main:app --reload

# Build Docker image
make build

# Deploy to Cloud Run
make deploy
```

## API Configuration

The search-api URL can be configured via environment variable:

```bash
export API_URL="https://search-api-546806894637.us-central1.run.app"
```

Or in a `.env` file:

```
API_URL=https://search-api-546806894637.us-central1.run.app
```

Default: `https://search-api-546806894637.us-central1.run.app`

## Features

### Search Interface

- Query input with enter key support
- Results display with title, content, and metadata
- Latency indicator (milliseconds)
- Cache hit/miss indicator
- Error handling for network failures

### Summary Interface

- Textarea for content input
- Streaming SSE response display
- Real-time text streaming
- Error handling for network failures

### Responsive Design

- Mobile-first approach
- Breakpoints at 768px and 480px
- Touch-friendly controls
- Adaptive layout

## Endpoints

- `GET /` - Serve main index.html
- `GET /health` - Health check (returns `{"status": "healthy"}`)
- `GET /config` - Return API URL configuration
- `GET /static/*` - Serve static files (CSS, JS)

## Testing

```bash
# Run all tests with coverage
make test-cov

# Run quick tests only
make test-quick

# Run specific test
poetry run pytest tests/test_api.py::test_health_check -v
```

## Code Quality

```bash
# Run all quality checks
make quality

# Individual checks
make format      # Format with black and ruff
make lint        # Lint with ruff
make typecheck   # Type check with mypy
```

## Deployment

### Local Docker

```bash
docker build -t demo-website:latest .
docker run -p 8080:8080 -e API_URL="https://search-api-546806894637.us-central1.run.app" demo-website:latest
```

### Cloud Run

```bash
make deploy
```

Or manually:

```bash
gcloud run deploy demo-website \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars API_URL="https://search-api-546806894637.us-central1.run.app"
```

## Technology Stack

- **Python**: 3.13+
- **Framework**: FastAPI with Uvicorn
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Configuration**: Pydantic Settings
- **Testing**: pytest with 80% coverage requirement
- **Code Quality**: black, ruff, mypy

## Module Structure

```
demo-website/
├── src/demo_website/
│   ├── __init__.py
│   ├── config.py           # Settings management
│   ├── main.py             # FastAPI application
│   └── static/
│       ├── index.html      # Main page with tabs
│       ├── style.css       # Responsive styling
│       └── app.js          # Fetch API calls
├── tests/
│   ├── test_api.py         # API endpoint tests
│   └── test_static_content.py  # Static file tests
├── Dockerfile              # Cloud Run deployment
├── Makefile                # Standard targets
├── pyproject.toml          # Dependencies
├── CLAUDE.md               # Module guidance
└── README.md               # This file
```

## Development Notes

- Module follows Pure Module Isolation - no `../` imports
- All tests must pass with 80% coverage
- Static files served via FastAPI StaticFiles
- API URL loaded dynamically via `/config` endpoint
- SSE streaming handled via fetch() ReadableStream
- Mobile-first responsive design with media queries

## License

Internal use only.
