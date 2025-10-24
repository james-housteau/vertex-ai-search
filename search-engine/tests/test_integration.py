"""Integration tests for search-engine module."""

from unittest.mock import Mock, patch

import pytest

from search_engine import SearchEngine, SearchResult


# Create mock exceptions for use in tests
class MockInvalidArgument(Exception):
    """Mock for google.api_core.exceptions.InvalidArgument."""

    pass


class MockDeadlineExceeded(Exception):
    """Mock for google.api_core.exceptions.DeadlineExceeded."""

    pass


gcp_exceptions = Mock()
gcp_exceptions.InvalidArgument = MockInvalidArgument
gcp_exceptions.DeadlineExceeded = MockDeadlineExceeded


@pytest.mark.integration
class TestSearchEngineIntegration:
    """Integration tests for complete SearchEngine workflows."""

    @patch("search_engine.search_engine.discoveryengine")
    def test_complete_search_workflow(self, mock_discoveryengine, mock_search_response):
        """Test complete search workflow from initialization to results."""
        # Setup
        mock_client = Mock()
        mock_discoveryengine.SearchServiceClient.return_value = mock_client
        mock_client.serving_config_path.return_value = "projects/test/locations/global/collections/default_collection/dataStores/test/servingConfigs/default_config"
        mock_client.search.return_value = mock_search_response

        mock_discoveryengine.SearchRequest.return_value = Mock()

        # Execute
        engine = SearchEngine("test-project-123", "test-datastore-456")
        result = engine.search("machine learning tutorial", max_results=5)

        # Verify initialization
        mock_client.serving_config_path.assert_called_once_with(
            project="test-project-123",
            location="global",
            data_store="test-datastore-456",
            serving_config="default_config",
        )

        # Verify search execution
        assert result.success
        assert result.query == "machine learning tutorial"
        assert isinstance(result.execution_time_ms, float)
        assert result.execution_time_ms > 0

    @patch("search_engine.search_engine.discoveryengine")
    def test_end_to_end_batch_processing(
        self, mock_discoveryengine, mock_search_response
    ):
        """Test end-to-end batch processing workflow."""
        mock_client = Mock()
        mock_discoveryengine.SearchServiceClient.return_value = mock_client
        mock_client.serving_config_path.return_value = "mock-config"
        mock_client.search.return_value = mock_search_response

        mock_discoveryengine.SearchRequest.return_value = Mock()

        engine = SearchEngine("test-project", "test-datastore")
        queries = [
            "artificial intelligence",
            "machine learning",
            "deep learning",
            "neural networks",
            "data science",
        ]

        results = engine.batch_search(queries)

        # Verify batch processing
        assert len(results) == 5
        assert all(isinstance(r, SearchResult) for r in results)
        assert all(r.success for r in results)
        assert [r.query for r in results] == queries
        assert mock_client.search.call_count == 5

        # Verify all results have proper metrics
        for result in results:
            assert isinstance(result.execution_time_ms, float)
            assert result.execution_time_ms > 0
            assert isinstance(result.relevance_scores, list)

    @patch("search_engine.search_engine.discoveryengine")
    def test_error_recovery_and_resilience(self, mock_discoveryengine):
        """Test error recovery and resilience in batch operations."""
        mock_client = Mock()
        mock_discoveryengine.SearchServiceClient.return_value = mock_client
        mock_client.serving_config_path.return_value = "mock-config"

        # Track the request objects to determine behavior
        request_objects = []

        def create_request_side_effect(*args, **kwargs):
            request = Mock()
            request.query = kwargs.get("query", "")
            request_objects.append(request)
            return request

        mock_discoveryengine.SearchRequest.side_effect = create_request_side_effect

        # Configure mixed success/failure responses
        def search_side_effect(request):
            if "fail" in request.query:
                raise MockInvalidArgument("Invalid query format")
            elif "timeout" in request.query:
                raise MockDeadlineExceeded("Request timeout")
            else:
                # Return successful response
                mock_response = Mock()
                mock_response.results = [
                    Mock(document=Mock(struct_data={"title": "Success"}))
                ]
                return mock_response

        mock_client.search.side_effect = search_side_effect

        engine = SearchEngine("test-project", "test-datastore")
        queries = [
            "good query",
            "fail query",
            "another good query",
            "timeout query",
            "final good query",
        ]

        results = engine.batch_search(queries)

        # Verify mixed results
        assert len(results) == 5
        assert results[0].success  # good query
        assert not results[1].success  # fail query
        assert "invalid" in results[1].error_message.lower()
        assert results[2].success  # another good query
        assert not results[3].success  # timeout query
        assert "timeout" in results[3].error_message.lower()
        assert results[4].success  # final good query

    @patch("search_engine.search_engine.discoveryengine")
    def test_connection_validation_scenarios(self, mock_discoveryengine):
        """Test various connection validation scenarios."""
        mock_client = Mock()
        mock_discoveryengine.SearchServiceClient.return_value = mock_client
        mock_client.serving_config_path.return_value = "mock-config"

        engine = SearchEngine("test-project", "test-datastore")

        # Scenario 1: Successful connection
        mock_response = Mock()
        mock_response.results = []
        mock_client.search.return_value = mock_response

        with patch.object(engine, "search") as mock_search:
            mock_search.return_value = SearchResult(
                query="test",
                results=[],
                result_count=0,
                execution_time_ms=50.0,
                relevance_scores=[],
                success=True,
            )
            assert engine.validate_connection() is True

        # Scenario 2: Connection failure
        with patch.object(engine, "search") as mock_search:
            mock_search.side_effect = Exception("Network error")
            assert engine.validate_connection() is False

        # Scenario 3: Datastore not found (but connection works)
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
            assert engine.validate_connection() is True

    @patch("search_engine.search_engine.discoveryengine")
    def test_performance_metrics_accuracy(self, mock_discoveryengine):
        """Test accuracy of performance metrics collection."""
        mock_client = Mock()
        mock_discoveryengine.SearchServiceClient.return_value = mock_client
        mock_client.serving_config_path.return_value = "mock-config"

        # Mock a response with known structure
        mock_result = Mock()
        mock_result.document.struct_data = {"title": "Test Doc", "content": "Content"}
        mock_result.relevance_score = 0.85

        mock_response = Mock()
        mock_response.results = [mock_result, mock_result, mock_result]
        mock_client.search.return_value = mock_response

        mock_discoveryengine.SearchRequest.return_value = Mock()

        engine = SearchEngine("test-project", "test-datastore")
        result = engine.search("performance test")

        # Verify metrics
        assert result.result_count == 3
        assert len(result.results) == 3
        assert len(result.relevance_scores) == 3
        assert all(score == 0.85 for score in result.relevance_scores)
        assert result.execution_time_ms > 0

        # Verify result structure
        for doc in result.results:
            assert doc["title"] == "Test Doc"
            assert doc["content"] == "Content"

    @patch("search_engine.search_engine.discoveryengine")
    def test_large_batch_processing(self, mock_discoveryengine, mock_search_response):
        """Test processing of large query batches."""
        mock_client = Mock()
        mock_discoveryengine.SearchServiceClient.return_value = mock_client
        mock_client.serving_config_path.return_value = "mock-config"
        mock_client.search.return_value = mock_search_response

        mock_discoveryengine.SearchRequest.return_value = Mock()

        engine = SearchEngine("test-project", "test-datastore")

        # Test with larger batch
        large_queries = [f"query {i}" for i in range(20)]
        results = engine.batch_search(large_queries)

        assert len(results) == 20
        assert all(r.success for r in results)
        assert mock_client.search.call_count == 20

        # Verify query ordering is preserved
        for i, result in enumerate(results):
            assert result.query == f"query {i}"
