"""Unit tests for SearchEngine class."""

from unittest.mock import Mock, patch

from search_engine.models import SearchResult
from search_engine.search_engine import SearchEngine


# Create mock exceptions for use in tests
class MockNotFound(Exception):
    """Mock for google.api_core.exceptions.NotFound."""

    pass


gcp_exceptions = Mock()
gcp_exceptions.NotFound = MockNotFound


class TestSearchEngine:
    """Test SearchEngine functionality."""

    @patch("search_engine.search_engine.discoveryengine")
    def test_initialization(self, mock_discoveryengine):
        """Test SearchEngine initialization."""
        # Setup mock
        mock_client = Mock()
        mock_discoveryengine.SearchServiceClient.return_value = mock_client
        mock_client.serving_config_path.return_value = "mock-serving-config"

        engine = SearchEngine("test-project", "test-datastore")
        assert engine.project_id == "test-project"
        assert engine.data_store_id == "test-datastore"

    @patch("search_engine.search_engine.discoveryengine")
    def test_search_successful(self, mock_discoveryengine, mock_search_response):
        """Test successful search execution."""
        # Setup mock
        mock_client = Mock()
        mock_discoveryengine.SearchServiceClient.return_value = mock_client
        mock_client.serving_config_path.return_value = "mock-serving-config"
        mock_client.search.return_value = mock_search_response

        # Mock SearchRequest
        mock_request = Mock()
        mock_discoveryengine.SearchRequest.return_value = mock_request

        engine = SearchEngine("test-project", "test-datastore")
        result = engine.search("test query", max_results=5)

        # Verify result structure
        assert isinstance(result, SearchResult)
        assert result.query == "test query"
        assert result.success is True
        assert result.error_message is None
        assert isinstance(result.execution_time_ms, float)
        assert result.execution_time_ms > 0

        # Verify client was called correctly
        mock_client.search.assert_called_once()
        call_args = mock_client.search.call_args[0][0]
        assert call_args == mock_request

    @patch("search_engine.search_engine.discoveryengine")
    def test_search_with_default_max_results(
        self, mock_discoveryengine, mock_search_response
    ):
        """Test search with default max_results parameter."""
        mock_client = Mock()
        mock_discoveryengine.SearchServiceClient.return_value = mock_client
        mock_client.serving_config_path.return_value = "mock-serving-config"
        mock_client.search.return_value = mock_search_response

        # Mock SearchRequest to capture parameters
        mock_request = Mock()
        mock_discoveryengine.SearchRequest.return_value = mock_request

        engine = SearchEngine("test-project", "test-datastore")
        engine.search("test query")

        # Verify SearchRequest was called with correct parameters
        mock_discoveryengine.SearchRequest.assert_called_with(
            serving_config="mock-serving-config",
            query="test query",
            page_size=10,
        )

    @patch("search_engine.search_engine.discoveryengine")
    def test_search_with_exception(self, mock_discoveryengine):
        """Test search error handling."""
        mock_client = Mock()
        mock_discoveryengine.SearchServiceClient.return_value = mock_client
        mock_client.serving_config_path.return_value = "mock-serving-config"
        mock_client.search.side_effect = MockNotFound("Data store not found")

        mock_discoveryengine.SearchRequest.return_value = Mock()

        engine = SearchEngine("test-project", "test-datastore")
        result = engine.search("test query")

        assert result.success is False
        assert "not found" in result.error_message.lower()
        assert result.result_count == 0
        assert len(result.results) == 0
        assert isinstance(result.execution_time_ms, float)

    @patch("search_engine.search_engine.discoveryengine")
    def test_batch_search(self, mock_discoveryengine, mock_search_response):
        """Test batch search functionality."""
        mock_client = Mock()
        mock_discoveryengine.SearchServiceClient.return_value = mock_client
        mock_client.serving_config_path.return_value = "mock-serving-config"
        mock_client.search.return_value = mock_search_response

        mock_discoveryengine.SearchRequest.return_value = Mock()

        engine = SearchEngine("test-project", "test-datastore")
        queries = ["query 1", "query 2", "query 3"]
        results = engine.batch_search(queries)

        assert len(results) == 3
        assert all(isinstance(result, SearchResult) for result in results)
        assert [result.query for result in results] == queries
        assert mock_client.search.call_count == 3

    @patch("search_engine.search_engine.discoveryengine")
    def test_validate_connection_success(
        self, mock_discoveryengine, mock_search_response
    ):
        """Test successful connection validation."""
        mock_client = Mock()
        mock_discoveryengine.SearchServiceClient.return_value = mock_client
        mock_client.serving_config_path.return_value = "mock-serving-config"
        mock_client.search.return_value = mock_search_response

        mock_discoveryengine.SearchRequest.return_value = Mock()

        engine = SearchEngine("test-project", "test-datastore")
        is_valid = engine.validate_connection()

        assert is_valid is True

    @patch("search_engine.search_engine.discoveryengine")
    def test_validate_connection_failure(self, mock_discoveryengine):
        """Test connection validation failure."""
        mock_client = Mock()
        mock_discoveryengine.SearchServiceClient.return_value = mock_client
        mock_client.serving_config_path.return_value = "mock-serving-config"
        mock_client.search.side_effect = Exception("Connection failed")

        mock_discoveryengine.SearchRequest.return_value = Mock()

        engine = SearchEngine("test-project", "test-datastore")
        is_valid = engine.validate_connection()

        assert is_valid is False

    @patch("search_engine.search_engine.discoveryengine")
    def test_validate_connection_with_not_found_error(self, mock_discoveryengine):
        """Test connection validation with not found error still validates connectivity."""
        mock_client = Mock()
        mock_discoveryengine.SearchServiceClient.return_value = mock_client
        mock_client.serving_config_path.return_value = "mock-serving-config"

        mock_discoveryengine.SearchRequest.return_value = Mock()

        engine = SearchEngine("test-project", "test-datastore")

        # Mock the search method to return a failed result
        with patch.object(engine, "search") as mock_search:
            mock_search.return_value = SearchResult(
                query="test",
                results=[],
                result_count=0,
                execution_time_ms=50.0,
                relevance_scores=[],
                success=False,
                error_message="Data store not found",
            )

            is_valid = engine.validate_connection()
            # Should return True because we can connect, even if datastore is not found
            assert is_valid is True

    @patch("search_engine.search_engine.discoveryengine")
    def test_serving_config_path_construction(self, mock_discoveryengine):
        """Test that serving config path is constructed correctly."""
        mock_client = Mock()
        mock_discoveryengine.SearchServiceClient.return_value = mock_client
        mock_client.serving_config_path.return_value = "test-serving-config-path"

        SearchEngine("my-project", "my-datastore")

        # Verify serving_config_path was called with correct parameters
        mock_client.serving_config_path.assert_called_once_with(
            project="my-project",
            location="global",
            data_store="my-datastore",
            serving_config="default_config",
        )

    @patch("search_engine.search_engine.discoveryengine")
    def test_relevance_scores_extraction(
        self, mock_discoveryengine, mock_search_response_no_scores
    ):
        """Test extraction of relevance scores from search results."""
        mock_client = Mock()
        mock_discoveryengine.SearchServiceClient.return_value = mock_client
        mock_client.serving_config_path.return_value = "mock-serving-config"

        # Create mock response with mixed relevance score availability
        mock_result1 = Mock()
        mock_result1.document.struct_data = {"title": "Doc 1"}
        mock_result1.relevance_score = 0.95

        mock_result2 = Mock(spec=["document"])  # No relevance_score attribute
        mock_result2.document.struct_data = {"title": "Doc 2"}

        mock_response = Mock()
        mock_response.results = [mock_result1, mock_result2]

        mock_client.search.return_value = mock_response
        mock_discoveryengine.SearchRequest.return_value = Mock()

        engine = SearchEngine("test-project", "test-datastore")
        result = engine.search("test query")

        assert len(result.relevance_scores) == 2
        assert result.relevance_scores[0] == 0.95
        assert result.relevance_scores[1] == 0.5  # default value
