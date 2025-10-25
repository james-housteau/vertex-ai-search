#!/usr/bin/env python3
"""Show detailed search results."""
import json
import sys
from pathlib import Path

_project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_project_root / "search-engine" / "src"))

from search_engine import SearchEngine

PROJECT_ID = "admin-workstation"
DATASTORE_ID = "nq-html-docs-search"

engine = SearchEngine(PROJECT_ID, DATASTORE_ID)

print("=" * 70)
print("🔍 DETAILED SEARCH RESULTS")
print("=" * 70)

# Test query
result = engine.search("Olympic Games", max_results=3)

print(f"\nQuery: {result.query}")
print(f"Success: {result.success}")
print(f"Results found: {result.result_count}")
print(f"Execution time: {result.execution_time_ms:.2f}ms")
print(f"\nRelevance scores: {result.relevance_scores}")

print("\n" + "=" * 70)
print("RAW RESULT DATA:")
print("=" * 70)

for i, doc in enumerate(result.results, 1):
    print(f"\n--- Result {i} ---")
    print(json.dumps(doc, indent=2, default=str))

print("\n" + "=" * 70)
