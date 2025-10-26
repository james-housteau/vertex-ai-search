# Demo Website - Quick Start Guide

Get the demo website running in 5 minutes.

## Prerequisites

- Python 3.13+
- Poetry installed
- Docker (optional, for containerized deployment)
- gcloud CLI (optional, for Cloud Run deployment)

## Local Development

### 1. Install Dependencies

```bash
cd demo-website/
make setup
```

### 2. Run Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run quick subset
make test-quick
```

### 3. Start Development Server

```bash
poetry run uvicorn demo_website.main:app --reload --host 0.0.0.0 --port 8080
```

Open browser to: http://localhost:8080

### 4. Configure API URL (Optional)

Create `.env` file:

```bash
API_URL=https://search-api-546806894637.us-central1.run.app
```

Or set environment variable:

```bash
export API_URL="https://search-api-546806894637.us-central1.run.app"
```

## Docker Deployment

### 1. Build Image

```bash
make build
# OR
docker build -t demo-website:latest .
```

### 2. Run Container

```bash
docker run -p 8080:8080 \
  -e API_URL="https://search-api-546806894637.us-central1.run.app" \
  demo-website:latest
```

Open browser to: http://localhost:8080

## Cloud Run Deployment

### 1. Deploy

```bash
make deploy
# OR
gcloud run deploy demo-website \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars API_URL="https://search-api-546806894637.us-central1.run.app"
```

### 2. Access

Cloud Run will provide a URL like:
```
https://demo-website-XXXXXXXXXX-uc.a.run.app
```

## Usage Guide

### Search Tab

1. Enter search query in the input field
2. Click "Search" button or press Enter
3. View results with:
   - Title
   - Content/snippet
   - Latency (milliseconds)
   - Cache status (HIT/MISS)

### Summarize Tab

1. Paste content into the textarea
2. Click "Summarize" button
3. Watch streaming summary appear in real-time
4. Summary completes when streaming stops

## Troubleshooting

### Tests Failing

```bash
# Check detailed output
poetry run pytest -v

# Check specific test
poetry run pytest tests/test_api.py::test_health_check -v
```

### Static Files Not Loading

Check that files exist:
```bash
ls -la src/demo_website/static/
```

Should show:
- index.html
- style.css
- app.js

### API Connection Issues

1. Check API_URL configuration:
   ```bash
   curl http://localhost:8080/config
   ```

2. Verify search-api is accessible:
   ```bash
   curl "https://search-api-546806894637.us-central1.run.app/health"
   ```

3. Check browser console for CORS errors

### Port Already in Use

Change port:
```bash
poetry run uvicorn demo_website.main:app --port 8081
```

Or in `.env`:
```
PORT=8081
```

## Code Quality Checks

```bash
# Run all quality checks
make quality

# Individual checks
make format      # Format with black and ruff
make lint        # Lint with ruff
make typecheck   # Type check with mypy
```

## Clean Up

```bash
# Remove build artifacts
make clean

# Remove virtual environment
poetry env remove python
```

## Module Structure

```
demo-website/
├── src/demo_website/
│   ├── __init__.py
│   ├── config.py           # Settings
│   ├── main.py             # FastAPI app
│   └── static/
│       ├── index.html      # UI
│       ├── style.css       # Styling
│       └── app.js          # Logic
├── tests/
│   ├── test_api.py
│   ├── test_config.py
│   ├── test_integration.py
│   └── test_static_content.py
├── Dockerfile
├── Makefile
└── pyproject.toml
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| API_URL | `https://search-api-546806894637.us-central1.run.app` | Search API endpoint |
| HOST | `0.0.0.0` | Server host |
| PORT | `8080` | Server port |

## Health Check

```bash
curl http://localhost:8080/health
# {"status":"healthy"}
```

## Need Help?

1. Check `README.md` for detailed documentation
2. Check `CLAUDE.md` for development guidance
3. Check `VALIDATION.md` for acceptance criteria
4. Run tests to identify issues: `make test -v`
