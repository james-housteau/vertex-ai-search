# Demo Website - Deployment Guide

Quick deployment guide for demo-website module.

## Prerequisites

- GCP project configured: `gcloud config set project YOUR_PROJECT_ID`
- Cloud Run API enabled
- search-api deployed (or URL of existing search API)

## Quick Deploy

### Option 1: Using Make (Auto-detects search-api)

```bash
cd demo-website/

# Automatically finds deployed search-api
make deploy
```

### Option 2: Using Deploy Script with Custom API URL

```bash
cd demo-website/

# Deploy with specific API URL
./deploy.sh https://your-search-api-url.run.app
```

### Option 3: Using Environment Variable

```bash
cd demo-website/

# Set API URL
export API_URL="https://your-search-api-url.run.app"

# Deploy
make deploy
```

## Configuration

### API URL Priority

The deploy script determines the API URL in this order:

1. **Command line argument**: `./deploy.sh https://api-url.run.app`
2. **Environment variable**: `export API_URL="https://api-url.run.app"`
3. **Auto-detect**: Finds deployed search-api in same project
4. **Default**: Uses value from `src/demo_website/config.py`

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_URL` | Search API endpoint | Auto-detected or default |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8080` |

## Deployment Scenarios

### Scenario 1: Deploy with search-api in Same Project

```bash
# Deploy search-api first
cd ../search-api
make deploy

# Deploy demo-website (auto-detects search-api)
cd ../demo-website
make deploy
```

### Scenario 2: Deploy with External API URL

```bash
cd demo-website/

# Deploy with external API
./deploy.sh https://external-search-api.example.com
```

### Scenario 3: Update API URL After Deployment

```bash
# Deploy first
cd demo-website/
make deploy

# Update API URL later
gcloud run services update demo-website \
  --region us-central1 \
  --set-env-vars API_URL="https://new-api-url.run.app"
```

## Post-Deployment

### Get Service URL

```bash
gcloud run services describe demo-website \
  --region us-central1 \
  --format 'value(status.url)'
```

### Test Endpoints

```bash
SERVICE_URL=$(gcloud run services describe demo-website --region us-central1 --format 'value(status.url)')

# Health check
curl $SERVICE_URL/health

# Config check
curl $SERVICE_URL/config

# Open in browser
open $SERVICE_URL  # macOS
xdg-open $SERVICE_URL  # Linux
```

### Verify Configuration

```bash
# Check what API URL is configured
SERVICE_URL=$(gcloud run services describe demo-website --region us-central1 --format 'value(status.url)')
curl -s $SERVICE_URL/config | jq
```

Expected output:
```json
{
  "api_url": "https://search-api-xxx.run.app"
}
```

## Update Configuration

### Update API URL

```bash
gcloud run services update demo-website \
  --region us-central1 \
  --set-env-vars API_URL="https://new-search-api-url.run.app"
```

### Update Other Settings

```bash
gcloud run services update demo-website \
  --region us-central1 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10
```

## View Logs

```bash
# Recent logs
gcloud run services logs read demo-website --region us-central1 --limit 50

# Stream logs
gcloud run services logs tail demo-website --region us-central1
```

## Troubleshooting

### UI Loads but Search Fails

- Check API URL configuration: `curl $SERVICE_URL/config`
- Verify search-api is accessible: `curl API_URL/health`
- Check browser console for CORS or network errors
- Review logs: `gcloud run services logs read demo-website --region us-central1`

### Static Files Not Loading

- Check that files exist in `src/demo_website/static/`
- Verify StaticFiles mount in `main.py`
- Test static file: `curl $SERVICE_URL/static/style.css`

### Build Fails

- Run tests locally first: `make test`
- Check code quality: `make quality`
- Verify Dockerfile and pyproject.toml

## Custom Domain

```bash
# Map custom domain
gcloud run domain-mappings create \
  --service demo-website \
  --domain demo.example.com \
  --region us-central1
```

## CI/CD Integration

For automated deployments:

```yaml
# GitHub Actions example
- name: Deploy Demo Website
  env:
    API_URL: ${{ secrets.SEARCH_API_URL }}
  run: |
    cd demo-website
    ./deploy.sh $API_URL
```

## Related Documentation

- `README.md` - Module overview
- `CLAUDE.md` - Development guide
- `DEPLOYMENT.md` - Detailed deployment guide
- `../search-api/` - Backend API
