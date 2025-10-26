# Demo Website - Deployment Guide

Complete guide for deploying the demo-website module to Cloud Run.

## Prerequisites

- [x] Google Cloud SDK installed (`gcloud`)
- [x] Docker installed (for local testing)
- [x] Poetry installed (for development)
- [x] GCP project with billing enabled
- [x] Cloud Run API enabled
- [x] Artifact Registry or Container Registry access

## Pre-Deployment Checklist

### 1. Verify Module Works Locally

```bash
cd demo-website/

# Install dependencies
make setup

# Run tests with coverage
make test-cov
# Expected: All tests pass, coverage ≥80%

# Run quality checks
make quality
# Expected: No errors from black, ruff, mypy

# Start local server
poetry run uvicorn demo_website.main:app --reload --port 8080
# Open http://localhost:8080
# Test search and summary functionality
```

### 2. Test Docker Build

```bash
# Build image
make build

# Run container locally
docker run -p 8080:8080 \
  -e API_URL="https://search-api-546806894637.us-central1.run.app" \
  demo-website:latest

# Test health check
curl http://localhost:8080/health
# Expected: {"status":"healthy"}

# Test config
curl http://localhost:8080/config
# Expected: {"api_url":"https://search-api-546806894637.us-central1.run.app"}

# Open browser to http://localhost:8080
# Test search and summary
```

## Cloud Run Deployment

### Option 1: Automatic Deploy (Recommended)

```bash
cd demo-website/
make deploy
```

This runs:
```bash
gcloud run deploy demo-website \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Option 2: Manual Deploy with Configuration

```bash
gcloud run deploy demo-website \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars API_URL="https://search-api-546806894637.us-central1.run.app" \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 60 \
  --service-account demo-website-sa@PROJECT_ID.iam.gserviceaccount.com
```

Replace `PROJECT_ID` with your actual GCP project ID.

### Option 3: Deploy from Container Registry

```bash
# Build and tag image
docker build -t gcr.io/PROJECT_ID/demo-website:latest .

# Push to Container Registry
docker push gcr.io/PROJECT_ID/demo-website:latest

# Deploy from registry
gcloud run deploy demo-website \
  --image gcr.io/PROJECT_ID/demo-website:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Configuration

### Environment Variables

Set during deployment:

```bash
gcloud run deploy demo-website \
  --source . \
  --set-env-vars API_URL="https://search-api-546806894637.us-central1.run.app"
```

Or update existing service:

```bash
gcloud run services update demo-website \
  --region us-central1 \
  --set-env-vars API_URL="https://search-api-546806894637.us-central1.run.app"
```

### Available Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| API_URL | `https://search-api-546806894637.us-central1.run.app` | Search API endpoint |
| HOST | `0.0.0.0` | Server host |
| PORT | `8080` | Server port |

## Post-Deployment Verification

### 1. Get Service URL

```bash
gcloud run services describe demo-website \
  --region us-central1 \
  --format 'value(status.url)'
```

Example output:
```
https://demo-website-546806894637-uc.a.run.app
```

### 2. Test Health Endpoint

```bash
SERVICE_URL=$(gcloud run services describe demo-website --region us-central1 --format 'value(status.url)')
curl $SERVICE_URL/health
```

Expected:
```json
{"status":"healthy"}
```

### 3. Test Config Endpoint

```bash
curl $SERVICE_URL/config
```

Expected:
```json
{"api_url":"https://search-api-546806894637.us-central1.run.app"}
```

### 4. Test Web UI

```bash
# Open in browser
open $SERVICE_URL  # macOS
xdg-open $SERVICE_URL  # Linux
start $SERVICE_URL  # Windows
```

Manual testing:
- [x] Page loads correctly
- [x] Search tab is active by default
- [x] Search input accepts text
- [x] Search button triggers query
- [x] Results display with title, content, latency, cache status
- [x] Summary tab is clickable
- [x] Summary textarea accepts text
- [x] Summarize button triggers request
- [x] Summary streams in real-time
- [x] Mobile view works (resize browser)
- [x] Tablet view works
- [x] Desktop view works

### 5. Load Testing (Optional)

```bash
# Install hey (HTTP load generator)
# macOS: brew install hey
# Linux: go install github.com/rakyll/hey@latest

# Test health endpoint
hey -n 1000 -c 10 $SERVICE_URL/health

# Test main page
hey -n 100 -c 5 $SERVICE_URL/
```

## Monitoring

### View Logs

```bash
gcloud run services logs read demo-website \
  --region us-central1 \
  --limit 50
```

### Real-time Logs

```bash
gcloud run services logs tail demo-website \
  --region us-central1
```

### Metrics in Console

```bash
# Open Cloud Run console
gcloud run services describe demo-website \
  --region us-central1 \
  --format 'value(status.url)' | \
  sed 's|https://||' | \
  xargs -I {} echo "https://console.cloud.google.com/run/detail/us-central1/demo-website"
```

Monitor:
- Request count
- Request latency (p50, p95, p99)
- Error rate
- Container startup latency
- Instance count

## Troubleshooting

### Deployment Fails

**Check logs:**
```bash
gcloud builds list --limit 5
gcloud builds log BUILD_ID
```

**Common issues:**
- Missing dependencies in pyproject.toml
- Dockerfile errors
- Port configuration mismatch
- Missing environment variables

### Health Check Fails

**Test locally:**
```bash
docker run -p 8080:8080 demo-website:latest &
sleep 5
curl http://localhost:8080/health
docker stop $(docker ps -q --filter ancestor=demo-website:latest)
```

**Check:**
- Port 8080 exposed in Dockerfile
- Health endpoint returns 200
- Application starts without errors

### Static Files Not Loading

**Check:**
- Files exist in `src/demo_website/static/`
- StaticFiles mount in main.py
- Paths use `/static/` prefix
- Content-Type headers correct

**Test:**
```bash
curl -I $SERVICE_URL/static/style.css
# Should show Content-Type: text/css
```

### API Connection Errors

**Verify API URL:**
```bash
curl $SERVICE_URL/config
```

**Test search-api:**
```bash
curl "https://search-api-546806894637.us-central1.run.app/health"
```

**Check CORS (if needed):**
- search-api should allow requests from demo-website URL
- Check browser console for CORS errors

### High Latency

**Check:**
- Cold start time (first request slow)
- Min instances setting (increase for production)
- API response time
- Network latency

**Optimize:**
```bash
# Increase min instances to reduce cold starts
gcloud run services update demo-website \
  --region us-central1 \
  --min-instances 1
```

## Scaling Configuration

### Development

```bash
gcloud run services update demo-website \
  --region us-central1 \
  --min-instances 0 \
  --max-instances 2 \
  --memory 256Mi \
  --cpu 1
```

### Production

```bash
gcloud run services update demo-website \
  --region us-central1 \
  --min-instances 1 \
  --max-instances 10 \
  --memory 512Mi \
  --cpu 2 \
  --concurrency 80
```

## Security

### Authentication (Optional)

If you need to restrict access:

```bash
# Deploy with authentication required
gcloud run deploy demo-website \
  --source . \
  --region us-central1 \
  --no-allow-unauthenticated

# Access with authentication
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  $SERVICE_URL/health
```

### Custom Domain (Optional)

```bash
# Map custom domain
gcloud run domain-mappings create \
  --service demo-website \
  --domain demo.example.com \
  --region us-central1
```

## Cleanup

### Delete Service

```bash
gcloud run services delete demo-website \
  --region us-central1
```

### Delete Images

```bash
# List images
gcloud artifacts docker images list gcr.io/PROJECT_ID/demo-website

# Delete specific version
gcloud artifacts docker images delete \
  gcr.io/PROJECT_ID/demo-website:TAG
```

## Rollback

### List Revisions

```bash
gcloud run revisions list \
  --service demo-website \
  --region us-central1
```

### Rollback to Previous Revision

```bash
gcloud run services update-traffic demo-website \
  --region us-central1 \
  --to-revisions REVISION_NAME=100
```

## CI/CD Integration (Optional)

### GitHub Actions Example

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]
    paths:
      - 'demo-website/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ secrets.GCP_PROJECT_ID }}

      - name: Deploy to Cloud Run
        run: |
          cd demo-website
          gcloud run deploy demo-website \
            --source . \
            --region us-central1 \
            --allow-unauthenticated
```

## Support

For issues:
1. Check `TROUBLESHOOTING.md` (if exists)
2. Review logs: `gcloud run services logs read demo-website`
3. Test locally: `make build && docker run -p 8080:8080 demo-website`
4. Verify tests pass: `make test-cov`
5. Check documentation: `README.md`, `CLAUDE.md`

---

**Last Updated**: 2025-10-26

**Service**: demo-website

**Region**: us-central1

**Platform**: Cloud Run (managed)
