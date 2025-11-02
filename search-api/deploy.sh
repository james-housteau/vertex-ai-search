#!/bin/bash
set -euo pipefail

# Deploy search-api to Cloud Run
# Usage: ./deploy.sh

echo "🚀 Deploying search-api to Cloud Run..."

# Get GCP project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "")
if [[ -z "$PROJECT_ID" ]]; then
    echo "❌ Error: No GCP project configured"
    echo "Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📦 Project: $PROJECT_ID"
echo "📍 Region: us-central1"

# Check for required environment variables
MISSING_VARS=()

if [[ -z "${GCP_PROJECT_ID:-}" ]]; then
    echo "⚠️  GCP_PROJECT_ID not set, using: $PROJECT_ID"
    GCP_PROJECT_ID="$PROJECT_ID"
fi

if [[ -z "${GCP_LOCATION:-}" ]]; then
    echo "⚠️  GCP_LOCATION not set, using: us-central1"
    GCP_LOCATION="us-central1"
fi

if [[ -z "${INDEX_ENDPOINT_ID:-}" ]]; then
    MISSING_VARS+=("INDEX_ENDPOINT_ID")
fi

if [[ -z "${DEPLOYED_INDEX_ID:-}" ]]; then
    MISSING_VARS+=("DEPLOYED_INDEX_ID")
fi

# If missing required vars, show helpful message
if [[ ${#MISSING_VARS[@]} -gt 0 ]]; then
    echo ""
    echo "⚠️  Missing required environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "💡 Options to fix:"
    echo ""
    echo "1. Set environment variables before deploying:"
    echo "   export INDEX_ENDPOINT_ID='your-endpoint-id'"
    echo "   export DEPLOYED_INDEX_ID='your-index-id'"
    echo "   ./deploy.sh"
    echo ""
    echo "2. Create a .envrc.local file:"
    echo "   echo 'export INDEX_ENDPOINT_ID=\"your-endpoint-id\"' > .envrc.local"
    echo "   echo 'export DEPLOYED_INDEX_ID=\"your-index-id\"' >> .envrc.local"
    echo "   direnv allow"
    echo "   ./deploy.sh"
    echo ""
    echo "3. Find your index IDs:"
    echo "   gcloud ai indexes list --region=us-central1"
    echo "   gcloud ai index-endpoints list --region=us-central1"
    echo ""

    # Ask if user wants to deploy anyway (will fail at runtime but container will build)
    read -p "Deploy anyway? (Service will return 503 until env vars are set) [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment cancelled"
        exit 1
    fi

    # Set placeholder values for deployment
    INDEX_ENDPOINT_ID="${INDEX_ENDPOINT_ID:-PLACEHOLDER_SET_VIA_GCLOUD}"
    DEPLOYED_INDEX_ID="${DEPLOYED_INDEX_ID:-PLACEHOLDER_SET_VIA_GCLOUD}"
fi

echo ""
echo "🔧 Configuration:"
echo "   GCP_PROJECT_ID: $GCP_PROJECT_ID"
echo "   GCP_LOCATION: $GCP_LOCATION"
echo "   INDEX_ENDPOINT_ID: ${INDEX_ENDPOINT_ID:0:20}..."
echo "   DEPLOYED_INDEX_ID: ${DEPLOYED_INDEX_ID:0:20}..."
echo ""

# Deploy to Cloud Run
echo "📤 Deploying to Cloud Run..."
gcloud run deploy search-api \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars "GCP_PROJECT_ID=$GCP_PROJECT_ID,GCP_LOCATION=$GCP_LOCATION,INDEX_ENDPOINT_ID=$INDEX_ENDPOINT_ID,DEPLOYED_INDEX_ID=$DEPLOYED_INDEX_ID" \
    --memory 1Gi \
    --cpu 2 \
    --timeout 60 \
    --min-instances 0 \
    --max-instances 10

# Get service URL
SERVICE_URL=$(gcloud run services describe search-api --region us-central1 --format 'value(status.url)' 2>/dev/null || echo "")

if [[ -n "$SERVICE_URL" ]]; then
    echo ""
    echo "✅ Deployment successful!"
    echo "🌐 Service URL: $SERVICE_URL"
    echo ""
    echo "🧪 Test endpoints:"
    echo "   Health: curl $SERVICE_URL/health"
    echo "   Search: curl \"$SERVICE_URL/search?q=test&top_k=5\""
    echo ""

    # Test health endpoint
    echo "🏥 Testing health endpoint..."
    if curl -s -f "$SERVICE_URL/health" > /dev/null 2>&1; then
        echo "✅ Health check passed"
    else
        echo "⚠️  Health check failed (this is expected if vector search is not configured)"
    fi
else
    echo "⚠️  Deployment completed but couldn't get service URL"
fi

echo ""
echo "📝 To update environment variables later:"
echo "   gcloud run services update search-api --region us-central1 \\"
echo "     --set-env-vars INDEX_ENDPOINT_ID=your-id,DEPLOYED_INDEX_ID=your-id"
