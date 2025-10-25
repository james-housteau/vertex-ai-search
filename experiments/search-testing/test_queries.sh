#!/bin/bash
# Test queries for the NQ HTML documents

PROJECT_ID="admin-workstation"
DATASTORE_ID="nq-html-docs-search"

echo "🔍 Testing Vertex AI Search with Natural Questions dataset"
echo "=================================================="
echo ""

# Test 1: Sports query
echo "Query 1: Olympic Games"
poetry run search-engine search \
  --project-id $PROJECT_ID \
  --data-store-id $DATASTORE_ID \
  --query "Olympic Games history" \
  --max-results 3

echo ""
echo "---"
echo ""

# Test 2: Science query
echo "Query 2: Photosynthesis"
poetry run search-engine search \
  --project-id $PROJECT_ID \
  --data-store-id $DATASTORE_ID \
  --query "How does photosynthesis work?" \
  --max-results 3

echo ""
echo "---"
echo ""

# Test 3: History query
echo "Query 3: World War II"
poetry run search-engine search \
  --project-id $PROJECT_ID \
  --data-store-id $DATASTORE_ID \
  --query "World War II major events" \
  --max-results 3

echo ""
echo "=================================================="
echo "✅ Test queries complete!"
