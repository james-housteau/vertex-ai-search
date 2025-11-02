#!/bin/bash
set -euo pipefail

# Deploy demo-website to Cloud Run
# Usage: ./deploy.sh [SEARCH_API_URL]

echo "🚀 Deploying demo-website to Cloud Run..."

# Get GCP project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "")
if [[ -z "$PROJECT_ID" ]]; then
    echo "❌ Error: No GCP project configured"
    echo "Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📦 Project: $PROJECT_ID"
echo "📍 Region: us-central1"

# Determine API URL
if [[ -n "${1:-}" ]]; then
    # Use command line argument
    API_URL="$1"
    echo "📡 Using API URL from argument: $API_URL"
elif [[ -n "${API_URL:-}" ]]; then
    # Use environment variable
    echo "📡 Using API URL from environment: $API_URL"
else
    # Try to get search-api URL
    echo "🔍 Looking for deployed search-api..."
    SEARCH_API_URL=$(gcloud run services describe search-api --region us-central1 --format 'value(status.url)' 2>/dev/null || echo "")

    if [[ -n "$SEARCH_API_URL" ]]; then
        API_URL="$SEARCH_API_URL"
        echo "✅ Found search-api: $API_URL"
    else
        # Use default from config.py
        API_URL="https://search-api-645846618640.us-central1.run.app"
        echo "⚠️  search-api not found, using default: $API_URL"
        echo ""
        echo "💡 To use a different API URL:"
        echo "   ./deploy.sh https://your-search-api-url.run.app"
        echo "   OR"
        echo "   export API_URL=\"https://your-search-api-url.run.app\" && ./deploy.sh"
    fi
fi

echo ""
echo "🔧 Configuration:"
echo "   API_URL: $API_URL"
echo ""

# Verify API URL is accessible (optional)
echo "🏥 Testing API URL..."
if curl -s -f -m 5 "$API_URL/health" > /dev/null 2>&1; then
    echo "✅ API health check passed"
else
    echo "⚠️  API health check failed (might be cold start or not deployed)"
    read -p "Continue deployment anyway? [Y/n] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        echo "❌ Deployment cancelled"
        exit 1
    fi
fi

# Deploy to Cloud Run
echo ""
echo "📤 Deploying to Cloud Run..."
gcloud run deploy demo-website \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars "API_URL=$API_URL" \
    --memory 512Mi \
    --cpu 1 \
    --timeout 60 \
    --min-instances 0 \
    --max-instances 10

# Get service URL
SERVICE_URL=$(gcloud run services describe demo-website --region us-central1 --format 'value(status.url)' 2>/dev/null || echo "")

if [[ -n "$SERVICE_URL" ]]; then
    echo ""
    echo "✅ Deployment successful!"
    echo "🌐 Demo Website: $SERVICE_URL"
    echo "🔗 API Backend: $API_URL"
    echo ""
    echo "🧪 Test endpoints:"
    echo "   Health: curl $SERVICE_URL/health"
    echo "   Config: curl $SERVICE_URL/config"
    echo "   Open in browser: $SERVICE_URL"
    echo ""

    # Test health endpoint
    echo "🏥 Testing health endpoint..."
    if curl -s -f "$SERVICE_URL/health" > /dev/null 2>&1; then
        echo "✅ Health check passed"
    else
        echo "⚠️  Health check failed"
    fi

    echo ""
    echo "🎉 Demo website is ready!"
    echo "   Visit: $SERVICE_URL"
else
    echo "⚠️  Deployment completed but couldn't get service URL"
fi

echo ""
echo "📝 To update API URL later:"
echo "   gcloud run services update demo-website --region us-central1 \\"
echo "     --set-env-vars API_URL=your-api-url"
