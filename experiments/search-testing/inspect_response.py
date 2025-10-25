#!/usr/bin/env python3
"""Inspect the full search response structure."""
import sys
from pathlib import Path

_project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_project_root / "search-engine" / "src"))

from google.cloud import discoveryengine_v1 as discoveryengine

PROJECT_ID = "admin-workstation"
DATASTORE_ID = "nq-html-docs-search"

client = discoveryengine.SearchServiceClient()
serving_config = (
    f"projects/{PROJECT_ID}/locations/global/collections/default_collection/"
    f"dataStores/{DATASTORE_ID}/servingConfigs/default_search"
)

# Create search request
request = discoveryengine.SearchRequest(
    serving_config=serving_config,
    query="Olympic Games",
    page_size=2,
)

print("=" * 70)
print("🔍 INSPECTING VERTEX AI SEARCH RESPONSE")
print("=" * 70)

response = client.search(request)

for i, result in enumerate(response.results, 1):
    print(f"\n{'='*70}")
    print(f"RESULT {i}")
    print("=" * 70)

    print(f"\nResult object type: {type(result)}")
    print(f"Available attributes: {dir(result)}")

    print("\n--- Document Info ---")
    doc = result.document
    print(f"Document ID: {doc.id}")
    print(f"Document name: {doc.name}")

    print("\n--- struct_data ---")
    print(f"struct_data: {doc.struct_data}")

    print("\n--- derived_struct_data ---")
    if hasattr(doc, "derived_struct_data") and doc.derived_struct_data:
        print(f"derived_struct_data fields: {dict(doc.derived_struct_data)}")
    else:
        print("No derived_struct_data")

    print("\n--- content ---")
    if hasattr(doc, "content"):
        print(f"content type: {type(doc.content)}")
        if doc.content:
            print(f"content: {doc.content}")

    print("\n--- json_data ---")
    if hasattr(doc, "json_data"):
        print(f"json_data: {doc.json_data}")

    if i >= 1:  # Just show first result in detail
        break

print("\n" + "=" * 70)
