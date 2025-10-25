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
    def test_search_successful(self, mock_discoveryengine):
        """Test successful search execution."""
        # Setup mock client
        mock_client = Mock()
        mock_discoveryengine.SearchServiceClient.return_value = mock_client
        mock_client.serving_config_path.return_value = "mock-serving-config"

        # Setup proper mock search response structure
        mock_result = Mock()
        mock_document = Mock()
        mock_document.id = "doc123"
        mock_document.derived_struct_data = {
            "title": "Test Result",
            "content": "Test content",
        }
        mock_result.document = mock_document
        mock_result.relevance_score = 0.85

        mock_search_response = Mock()
        mock_search_response.results = [mock_result]
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
    def test_search_with_default_max_results(self, mock_discoveryengine):
        """Test search with default max_results parameter."""
        mock_client = Mock()
        mock_discoveryengine.SearchServiceClient.return_value = mock_client

        # Setup proper mock search response
        mock_result = Mock()
        mock_document = Mock()
        mock_document.id = "doc123"
        mock_document.derived_struct_data = {"title": "Test Result"}
        mock_result.document = mock_document
        mock_result.relevance_score = 0.85

        mock_search_response = Mock()
        mock_search_response.results = [mock_result]
        mock_client.search.return_value = mock_search_response

        # Mock SearchRequest to capture parameters
        mock_request = Mock()
        mock_discoveryengine.SearchRequest.return_value = mock_request

        engine = SearchEngine("test-project", "test-datastore")
        engine.search("test query")

        # Verify SearchRequest was called with correct serving config path
        expected_serving_config = (
            "projects/test-project/locations/global/collections/default_collection/"
            "dataStores/test-datastore/servingConfigs/default_search"
        )
        mock_discoveryengine.SearchRequest.assert_called_with(
            serving_config=expected_serving_config,
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
    def test_relevance_scores_extraction(
        self, mock_discoveryengine, mock_search_response_no_scores
    ):
        """Test extraction of relevance scores from search results."""
        mock_client = Mock()
        mock_discoveryengine.SearchServiceClient.return_value = mock_client
        mock_client.serving_config_path.return_value = "mock-serving-config"

        # Create mock response with mixed relevance score availability
        mock_result1 = Mock()
        mock_document1 = Mock()
        mock_document1.id = "doc1"
        mock_document1.derived_struct_data = {"title": "Doc 1"}
        mock_document1.struct_data = None
        mock_result1.document = mock_document1
        mock_result1.relevance_score = 0.95

        mock_result2 = Mock(spec=["document"])  # No relevance_score attribute
        mock_document2 = Mock()
        mock_document2.id = "doc2"
        mock_document2.derived_struct_data = {"title": "Doc 2"}
        mock_document2.struct_data = None
        mock_result2.document = mock_document2

        mock_response = Mock()
        mock_response.results = [mock_result1, mock_result2]

        mock_client.search.return_value = mock_response
        mock_discoveryengine.SearchRequest.return_value = Mock()

        engine = SearchEngine("test-project", "test-datastore")
        result = engine.search("test query")

        assert len(result.relevance_scores) == 2
        assert result.relevance_scores[0] == 0.95
        assert result.relevance_scores[1] == 0.5  # default value
