# Search API - Deployment Guide

Quick deployment guide for search-api module.

## Prerequisites

- GCP project configured: `gcloud config set project YOUR_PROJECT_ID`
- Cloud Run API enabled
- Vector Search index and endpoint deployed (see vector-search-index module)

## Quick Deploy

### Option 1: Using Make (Recommended)

```bash
cd search-api/

# Set required environment variables
export INDEX_ENDPOINT_ID="projects/PROJECT_ID/locations/us-central1/indexEndpoints/ENDPOINT_ID"
export DEPLOYED_INDEX_ID="deployed_index_id"

# Deploy
make deploy
```

### Option 2: Using Deploy Script Directly

```bash
cd search-api/

# Set environment variables
export INDEX_ENDPOINT_ID="..."
export DEPLOYED_INDEX_ID="..."

# Run script
./deploy.sh
```

### Option 3: Using .envrc.local

```bash
cd search-api/

# Create local config (not committed to git)
cat > .envrc.local <<EOF
export INDEX_ENDPOINT_ID="projects/PROJECT_ID/locations/us-central1/indexEndpoints/ENDPOINT_ID"
export DEPLOYED_INDEX_ID="deployed_index_id"
EOF

# Allow direnv to load it
direnv allow

# Deploy
make deploy
```

## Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `INDEX_ENDPOINT_ID` | Full path to Vector Search endpoint | `projects/my-project/locations/us-central1/indexEndpoints/123` |
| `DEPLOYED_INDEX_ID` | Deployed index identifier | `deployed_nq_vector_index` |
| `GCP_PROJECT_ID` | GCP project ID (optional, auto-detected) | `my-project-id` |
| `GCP_LOCATION` | GCP region (optional, defaults to us-central1) | `us-central1` |

## Finding Your Index IDs

```bash
# List indexes
gcloud ai indexes list --region=us-central1

# List index endpoints
gcloud ai index-endpoints list --region=us-central1

# Get deployed indexes for an endpoint
gcloud ai index-endpoints describe ENDPOINT_ID \
  --region=us-central1 \
  --format="value(deployedIndexes)"
```

## Deployment Without Vector Search

If you don't have a vector search index yet, you can still deploy:

```bash
# Deploy without env vars (will show 503 until configured)
make deploy

# Update later with correct values
gcloud run services update search-api \
  --region us-central1 \
  --set-env-vars INDEX_ENDPOINT_ID=your-id,DEPLOYED_INDEX_ID=your-id
```

## Post-Deployment

### Get Service URL

```bash
gcloud run services describe search-api \
  --region us-central1 \
  --format 'value(status.url)'
```

### Test Endpoints

```bash
SERVICE_URL=$(gcloud run services describe search-api --region us-central1 --format 'value(status.url)')

# Health check
curl $SERVICE_URL/health

# Search (requires vector search configured)
curl "$SERVICE_URL/search?q=machine+learning&top_k=5"

# Summarize (requires vector search configured)
curl -X POST $SERVICE_URL/summarize \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?", "top_k": 5}'
```

## Update Environment Variables

```bash
gcloud run services update search-api \
  --region us-central1 \
  --set-env-vars INDEX_ENDPOINT_ID=new-id,DEPLOYED_INDEX_ID=new-id
```

## View Logs

```bash
# Recent logs
gcloud run services logs read search-api --region us-central1 --limit 50

# Stream logs
gcloud run services logs tail search-api --region us-central1
```

## Troubleshooting

### 503 Service Unavailable

- Check that INDEX_ENDPOINT_ID and DEPLOYED_INDEX_ID are set correctly
- Verify the vector search index is deployed and accessible
- Check logs: `gcloud run services logs read search-api --region us-central1`

### Build Fails

- Run tests locally first: `make test`
- Check code quality: `make quality`
- Verify all dependencies in pyproject.toml

### Slow Performance

- Check vector search index is properly deployed
- Monitor cache hit rate in logs
- Consider increasing min-instances: `--min-instances 1`

## CI/CD Integration

For automated deployments, set secrets in your CI system:

```yaml
# GitHub Actions example
- name: Deploy to Cloud Run
  env:
    INDEX_ENDPOINT_ID: ${{ secrets.INDEX_ENDPOINT_ID }}
    DEPLOYED_INDEX_ID: ${{ secrets.DEPLOYED_INDEX_ID }}
  run: |
    cd search-api
    ./deploy.sh
```

## Related Documentation

- `README.md` - Module overview
- `CLAUDE.md` - Development guide
- `QUICK_START.md` - Local development
- `../vector-search-index/` - Vector search setup
