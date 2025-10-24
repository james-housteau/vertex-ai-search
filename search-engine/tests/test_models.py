"""Tests for search-engine models."""

from search_engine.models import SearchResult


class TestSearchResult:
    """Test SearchResult dataclass."""

    def test_search_result_creation_success(self):
        """Test creating a successful SearchResult."""
        result = SearchResult(
            query="test query",
            results=[{"title": "Test Doc", "content": "Test content"}],
            result_count=1,
            execution_time_ms=123.45,
            relevance_scores=[0.89],
            success=True,
        )

        assert result.query == "test query"
        assert len(result.results) == 1
        assert result.result_count == 1
        assert result.execution_time_ms == 123.45
        assert result.relevance_scores == [0.89]
        assert result.success is True
        assert result.error_message is None

    def test_search_result_creation_failure(self):
        """Test creating a failed SearchResult."""
        result = SearchResult(
            query="failed query",
            results=[],
            result_count=0,
            execution_time_ms=50.0,
            relevance_scores=[],
            success=False,
            error_message="Connection failed",
        )

        assert result.query == "failed query"
        assert result.results == []
        assert result.result_count == 0
        assert result.execution_time_ms == 50.0
        assert result.relevance_scores == []
        assert result.success is False
        assert result.error_message == "Connection failed"

    def test_search_result_dataclass_equality(self):
        """Test SearchResult equality comparison."""
        result1 = SearchResult(
            query="test",
            results=[],
            result_count=0,
            execution_time_ms=100.0,
            relevance_scores=[],
            success=True,
        )

        result2 = SearchResult(
            query="test",
            results=[],
            result_count=0,
            execution_time_ms=100.0,
            relevance_scores=[],
            success=True,
        )

        assert result1 == result2

    def test_search_result_with_multiple_results(self):
        """Test SearchResult with multiple search results."""
        results_data = [
            {"title": "Doc 1", "content": "Content 1"},
            {"title": "Doc 2", "content": "Content 2"},
            {"title": "Doc 3", "content": "Content 3"},
        ]

        result = SearchResult(
            query="multi test",
            results=results_data,
            result_count=3,
            execution_time_ms=200.0,
            relevance_scores=[0.95, 0.87, 0.72],
            success=True,
        )

        assert len(result.results) == 3
        assert result.result_count == 3
        assert len(result.relevance_scores) == 3
        assert all(isinstance(score, float) for score in result.relevance_scores)
