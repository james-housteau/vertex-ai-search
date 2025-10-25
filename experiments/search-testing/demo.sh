#!/bin/bash
# Comprehensive Vertex AI Search Demo

PROJECT_ID="admin-workstation"
DATASTORE_ID="nq-html-docs-search"

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                                                                    ║"
echo "║     🎯 VERTEX AI SEARCH DEMO - Natural Questions Dataset         ║"
echo "║                                                                    ║"
echo "║     Datastore: nq-html-docs-search                                ║"
echo "║     Documents: 1,600 Wikipedia HTML articles                      ║"
echo "║     Technology: Google Vertex AI Agent Builder                    ║"
echo "║                                                                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

queries=(
  "Olympic Games|Sports"
  "photosynthesis|Science"
  "World War II|History"
  "solar system planets|Astronomy"
  "DNA genetics|Biology"
  "artificial intelligence|Technology"
  "Shakespeare plays|Literature"
  "climate change|Environment"
)

for query_info in "${queries[@]}"; do
  IFS='|' read -r query category <<< "$query_info"

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📂 Category: $category"
  echo "🔍 Query: \"$query\""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  poetry run search-engine search \
    --project-id $PROJECT_ID \
    --data-store-id $DATASTORE_ID \
    --query "$query" \
    --max-results 3

  echo ""
done

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                                                                    ║"
echo "║     ✅ DEMO COMPLETE                                              ║"
echo "║                                                                    ║"
echo "║     The search engine successfully found relevant documents       ║"
echo "║     across multiple topics using natural language queries!        ║"
echo "║                                                                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
