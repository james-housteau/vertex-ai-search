"""Acceptance tests for search-engine module API contract."""

from unittest.mock import Mock, patch

from search_engine import SearchEngine, SearchResult


# Create mock exceptions for use in tests
class MockNotFound(Exception):
    """Mock for google.api_core.exceptions.NotFound."""

    pass


class MockInvalidArgument(Exception):
    """Mock for google.api_core.exceptions.InvalidArgument."""

    pass


gcp_exceptions = Mock()
gcp_exceptions.NotFound = MockNotFound
gcp_exceptions.InvalidArgument = MockInvalidArgument


class TestSearchEngineAPIContract:
    """Test the exact API contract as specified in Stream 4."""

    def test_search_result_dataclass_structure(self):
        """Test SearchResult dataclass has all required fields."""
        # Create a SearchResult instance
        result = SearchResult(
            query="test query",
            results=[{"title": "Test", "content": "Test content"}],
            result_count=1,
            execution_time_ms=150.5,
            relevance_scores=[0.95],
            success=True,
            error_message=None,
        )

        # Verify all required fields exist and have correct types
        assert isinstance(result.query, str)
        assert isinstance(result.results, list)
        assert isinstance(result.result_count, int)
        assert isinstance(result.execution_time_ms, float)
        assert isinstance(result.relevance_scores, list)
        assert isinstance(result.success, bool)
        assert result.error_message is None or isinstance(result.error_message, str)

    def test_search_result_with_error(self):
        """Test SearchResult can handle error scenarios."""
        result = SearchResult(
            query="failed query",
            results=[],
            result_count=0,
            execution_time_ms=50.0,
            relevance_scores=[],
            success=False,
            error_message="Connection timeout",
        )

        assert not result.success
        assert result.error_message == "Connection timeout"
        assert result.result_count == 0

    @patch("search_engine.search_engine.discoveryengine")
    def test_search_engine_initialization(self, mock_discoveryengine):
        """Test SearchEngine can be initialized with required parameters."""
        # Setup mock
        mock_client = Mock()
        mock_discoveryengine.SearchServiceClient.return_value = mock_client
        mock_client.serving_config_path.return_value = "mock-serving-config"

        # This should not raise an exception
        engine = SearchEngine(
            project_id="test-project-123", data_store_id="test-datastore-456"
        )

        assert engine.project_id == "test-project-123"
        assert engine.data_store_id == "test-datastore-456"

    @patch("search_engine.search_engine.discoveryengine")
    def test_search_method_signature_and_return_type(
        self, mock_discoveryengine, mock_discovery_client, mock_search_response
    ):
        """Test search method has correct signature and returns SearchResult."""
        mock_discoveryengine.SearchServiceClient.return_value = mock_discovery_client
        mock_discovery_client.search.return_value = mock_search_response
        mock_discovery_client.serving_config_path.return_value = "mock-serving-config"

        mock_discoveryengine.SearchRequest.return_value = Mock()

        engine = SearchEngine("test-project", "test-datastore")

        # Test with default max_results
        result = engine.search("test query")
        assert isinstance(result, SearchResult)
        assert result.query == "test query"

        # Test with custom max_results
        result = engine.search("test query", max_results=5)
        assert isinstance(result, SearchResult)
        assert result.query == "test query"

    @patch("search_engine.search_engine.discoveryengine")
    def test_batch_search_method_signature_and_return_type(
        self, mock_discoveryengine, mock_discovery_client, mock_search_response
    ):
        """Test batch_search method has correct signature and returns List[SearchResult]."""
        mock_discoveryengine.SearchServiceClient.return_value = mock_discovery_client
        mock_discovery_client.search.return_value = mock_search_response
        mock_discovery_client.serving_config_path.return_value = "mock-serving-config"

        mock_discoveryengine.SearchRequest.return_value = Mock()

        engine = SearchEngine("test-project", "test-datastore")
        queries = ["query 1", "query 2", "query 3"]

        results = engine.batch_search(queries)

        assert isinstance(results, list)
        assert len(results) == 3
        for i, result in enumerate(results):
            assert isinstance(result, SearchResult)
            assert result.query == queries[i]

    @patch("search_engine.search_engine.discoveryengine")
    def test_validate_connection_method_signature_and_return_type(
        self, mock_discoveryengine, mock_discovery_client
    ):
        """Test validate_connection method returns boolean."""
        mock_discoveryengine.SearchServiceClient.return_value = mock_discovery_client
        mock_discovery_client.serving_config_path.return_value = "mock-serving-config"

        engine = SearchEngine("test-project", "test-datastore")

        # Mock successful connection validation
        mock_discovery_client.search.return_value = Mock(results=[], total_size=0)
        result = engine.validate_connection()
        assert isinstance(result, bool)

    @patch("search_engine.search_engine.discoveryengine")
    def test_search_result_timing_metrics(
        self, mock_discoveryengine, mock_discovery_client, mock_search_response
    ):
        """Test that search operations measure execution time."""
        mock_discoveryengine.SearchServiceClient.return_value = mock_discovery_client
        mock_discovery_client.serving_config_path.return_value = "mock-serving-config"
        mock_discovery_client.search.return_value = mock_search_response

        mock_discoveryengine.SearchRequest.return_value = Mock()

        engine = SearchEngine("test-project", "test-datastore")
        result = engine.search("test query")

        # Execution time should be positive float
        assert isinstance(result.execution_time_ms, float)
        assert result.execution_time_ms > 0

    @patch("search_engine.search_engine.discoveryengine")
    def test_search_result_relevance_scores(
        self, mock_discoveryengine, mock_discovery_client, mock_search_response
    ):
        """Test that search results include relevance scores."""
        mock_discoveryengine.SearchServiceClient.return_value = mock_discovery_client
        mock_discovery_client.serving_config_path.return_value = "mock-serving-config"
        mock_discovery_client.search.return_value = mock_search_response

        mock_discoveryengine.SearchRequest.return_value = Mock()

        engine = SearchEngine("test-project", "test-datastore")
        result = engine.search("test query")

        # Relevance scores should be a list of floats
        assert isinstance(result.relevance_scores, list)
        for score in result.relevance_scores:
            assert isinstance(score, float)
            assert 0.0 <= score <= 1.0

    @patch("search_engine.search_engine.discoveryengine")
    def test_search_error_handling(self, mock_discoveryengine, mock_discovery_client):
        """Test that search errors are properly handled and reported."""
        mock_discoveryengine.SearchServiceClient.return_value = mock_discovery_client
        mock_discovery_client.serving_config_path.return_value = "mock-serving-config"

        # Mock an exception during search
        mock_discovery_client.search.side_effect = MockNotFound("Data store not found")

        mock_discoveryengine.SearchRequest.return_value = Mock()

        engine = SearchEngine("test-project", "invalid-datastore")
        result = engine.search("test query")

        assert not result.success
        assert result.error_message is not None
        assert "not found" in result.error_message.lower()
        assert result.result_count == 0
        assert len(result.results) == 0

    @patch("search_engine.search_engine.discoveryengine")
    def test_batch_search_partial_failures(
        self, mock_discoveryengine, mock_discovery_client, mock_search_response
    ):
        """Test batch search handles partial failures gracefully."""
        mock_discoveryengine.SearchServiceClient.return_value = mock_discovery_client
        mock_discovery_client.serving_config_path.return_value = "mock-serving-config"

        # Track the request objects to determine behavior
        request_objects = []

        def create_request_side_effect(*args, **kwargs):
            request = Mock()
            request.query = kwargs.get("query", "")
            request_objects.append(request)
            return request

        mock_discoveryengine.SearchRequest.side_effect = create_request_side_effect

        # Mock mixed success/failure responses
        def side_effect(request):
            if "fail" in request.query:
                raise MockInvalidArgument("Invalid query")
            return mock_search_response

        mock_discovery_client.search.side_effect = side_effect

        engine = SearchEngine("test-project", "test-datastore")
        queries = ["good query", "fail query", "another good query"]

        results = engine.batch_search(queries)

        assert len(results) == 3
        assert results[0].success  # first query should succeed
        assert not results[1].success  # second query should fail
        assert results[2].success  # third query should succeed

    def test_search_engine_type_annotations(self):
        """Test that all methods have proper type annotations."""
        from typing import get_type_hints

        # Test SearchEngine.__init__ annotations
        init_hints = get_type_hints(SearchEngine.__init__)
        assert init_hints.get("project_id") is str
        assert init_hints.get("data_store_id") is str
        assert init_hints.get("return") is None

        # Test search method annotations
        search_hints = get_type_hints(SearchEngine.search)
        assert search_hints.get("query") is str
        assert search_hints.get("max_results") is int
        assert search_hints.get("return") is SearchResult

        # Test batch_search method annotations
        batch_hints = get_type_hints(SearchEngine.batch_search)
        assert batch_hints.get("queries") == list[str]
        assert batch_hints.get("return") == list[SearchResult]

        # Test validate_connection method annotations
        validate_hints = get_type_hints(SearchEngine.validate_connection)
        assert validate_hints.get("return") is bool
