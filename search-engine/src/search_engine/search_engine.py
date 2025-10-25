"""SearchEngine implementation for Vertex AI Agent Builder API."""

import time

try:
    from google.cloud import discoveryengine_v1 as discoveryengine
except ImportError:
    # Allow for testing with mocked dependencies
    discoveryengine = None

from .models import SearchResult


class SearchEngine:
    """Pure search functionality testing using Vertex AI Agent Builder API."""

    def __init__(self, project_id: str, data_store_id: str):
        """Initialize SearchEngine with project and datastore configuration."""
        self.project_id = project_id
        self.data_store_id = data_store_id

        if discoveryengine is None:
            raise ImportError(
                "google-cloud-discoveryengine is not installed. "
                "Install it with: pip install google-cloud-discoveryengine"
            )

        self._client = discoveryengine.SearchServiceClient()
        # Construct serving config path manually to include collection
        self._serving_config = (
            f"projects/{project_id}/locations/global/collections/default_collection/"
            f"dataStores/{data_store_id}/servingConfigs/default_search"
        )

    def search(self, query: str, max_results: int = 10) -> SearchResult:
        """Execute a search query and return structured results."""
        start_time = time.time()

        try:
            # Create search request
            request = discoveryengine.SearchRequest(
                serving_config=self._serving_config,
                query=query,
                page_size=max_results,
            )

            # Execute search
            response = self._client.search(request)

            # Process results
            results = []
            relevance_scores = []

            for result in response.results:
                # For unstructured content, use derived_struct_data instead of struct_data
                doc = result.document

                # Try derived_struct_data first (for unstructured HTML content)
                if hasattr(doc, "derived_struct_data") and doc.derived_struct_data:
                    doc_data = dict(doc.derived_struct_data)
                    # Add document ID
                    doc_data["id"] = doc.id
                    results.append(doc_data)
                # Fallback to struct_data (for structured content)
                elif doc.struct_data:
                    doc_data = dict(doc.struct_data)
                    doc_data["id"] = doc.id
                    results.append(doc_data)
                else:
                    # No data available
                    results.append({"id": doc.id})

                # Extract relevance score (default to 0.5 if not available)
                relevance_score = getattr(result, "relevance_score", 0.5)
                # Ensure we can convert to float, default to 0.5 if not
                try:
                    relevance_scores.append(float(relevance_score))
                except (ValueError, TypeError):
                    relevance_scores.append(0.5)

            execution_time = (
                time.time() - start_time
            ) * 1000  # Convert to milliseconds

            return SearchResult(
                query=query,
                results=results,
                result_count=len(results),
                execution_time_ms=execution_time,
                relevance_scores=relevance_scores,
                success=True,
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return SearchResult(
                query=query,
                results=[],
                result_count=0,
                execution_time_ms=execution_time,
                relevance_scores=[],
                success=False,
                error_message=str(e),
            )

    def batch_search(self, queries: list[str]) -> list[SearchResult]:
        """Execute multiple search queries and return results for each."""
        return [self.search(query) for query in queries]

    def validate_connection(self) -> bool:
        """Test connection to Vertex AI search service."""
        try:
            # Perform a minimal test search
            test_result = self.search("test", max_results=1)
            # Connection is valid if:
            # 1. Search succeeds, OR
            # 2. Search fails but we can connect (e.g., "not found" means we connected but datastore doesn't exist)
            if test_result.success:
                return True
            elif (
                test_result.error_message
                and "not found" in test_result.error_message.lower()
            ):
                return True
            else:
                return False
        except Exception:
            return False
