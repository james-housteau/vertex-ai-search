"""Test data models for metrics-collector module."""

from datetime import UTC, datetime

from metrics_collector.models import (
    ConversationResult,
    PerformanceMetrics,
    SearchResult,
)


class TestSearchResult:
    """Test SearchResult dataclass."""

    def test_search_result_creation_with_all_fields(self) -> None:
        """Test creating SearchResult with all fields."""
        result = SearchResult(
            query="test query",
            results=[{"title": "Test", "content": "Content"}],
            result_count=1,
            execution_time_ms=150.5,
            relevance_scores=[0.95, 0.87],
            success=True,
            error_message=None,
        )

        assert result.query == "test query"
        assert len(result.results) == 1
        assert result.result_count == 1
        assert result.execution_time_ms == 150.5
        assert len(result.relevance_scores) == 2
        assert result.success is True
        assert result.error_message is None

    def test_search_result_creation_with_error(self) -> None:
        """Test creating SearchResult with error."""
        result = SearchResult(
            query="failed query",
            results=[],
            result_count=0,
            execution_time_ms=50.0,
            relevance_scores=[],
            success=False,
            error_message="API timeout",
        )

        assert result.query == "failed query"
        assert result.results == []
        assert result.result_count == 0
        assert result.success is False
        assert result.error_message == "API timeout"

    def test_search_result_default_error_message(self) -> None:
        """Test SearchResult with default None error message."""
        result = SearchResult(
            query="test",
            results=[],
            result_count=0,
            execution_time_ms=100.0,
            relevance_scores=[],
            success=True,
        )

        assert result.error_message is None


class TestConversationResult:
    """Test ConversationResult dataclass."""

    def test_conversation_result_creation_with_all_fields(self) -> None:
        """Test creating ConversationResult with all fields."""
        result = ConversationResult(
            query="What is the weather?",
            answer="It's sunny today.",
            response_time_ms=200.0,
            success=True,
            error_message=None,
            context_used=True,
        )

        assert result.query == "What is the weather?"
        assert result.answer == "It's sunny today."
        assert result.response_time_ms == 200.0
        assert result.success is True
        assert result.error_message is None
        assert result.context_used is True

    def test_conversation_result_creation_with_error(self) -> None:
        """Test creating ConversationResult with error."""
        result = ConversationResult(
            query="Complex question",
            answer="",
            response_time_ms=5000.0,
            success=False,
            error_message="Processing timeout",
            context_used=False,
        )

        assert result.query == "Complex question"
        assert result.answer == ""
        assert result.success is False
        assert result.error_message == "Processing timeout"
        assert result.context_used is False

    def test_conversation_result_default_values(self) -> None:
        """Test ConversationResult with default values."""
        result = ConversationResult(
            query="test question",
            answer="test answer",
            response_time_ms=150.0,
            success=True,
        )

        assert result.error_message is None
        assert result.context_used is True


class TestPerformanceMetrics:
    """Test PerformanceMetrics dataclass."""

    def test_performance_metrics_creation(self) -> None:
        """Test creating PerformanceMetrics with all fields."""
        timestamp = datetime.now(tz=UTC)
        metrics = PerformanceMetrics(
            operation_type="search",
            total_operations=100,
            success_rate=95.0,
            avg_response_time_ms=150.5,
            median_response_time_ms=140.0,
            p95_response_time_ms=300.0,
            error_count=5,
            timestamp=timestamp,
        )

        assert metrics.operation_type == "search"
        assert metrics.total_operations == 100
        assert metrics.success_rate == 95.0
        assert metrics.avg_response_time_ms == 150.5
        assert metrics.median_response_time_ms == 140.0
        assert metrics.p95_response_time_ms == 300.0
        assert metrics.error_count == 5
        assert metrics.timestamp == timestamp

    def test_performance_metrics_conversation_type(self) -> None:
        """Test PerformanceMetrics for conversation operations."""
        timestamp = datetime.now(tz=UTC)
        metrics = PerformanceMetrics(
            operation_type="conversation",
            total_operations=50,
            success_rate=98.0,
            avg_response_time_ms=200.0,
            median_response_time_ms=180.0,
            p95_response_time_ms=400.0,
            error_count=1,
            timestamp=timestamp,
        )

        assert metrics.operation_type == "conversation"
        assert metrics.total_operations == 50
        assert metrics.success_rate == 98.0

    def test_performance_metrics_mixed_type(self) -> None:
        """Test PerformanceMetrics for mixed operations."""
        timestamp = datetime.now(tz=UTC)
        metrics = PerformanceMetrics(
            operation_type="mixed",
            total_operations=150,
            success_rate=96.0,
            avg_response_time_ms=175.0,
            median_response_time_ms=160.0,
            p95_response_time_ms=350.0,
            error_count=6,
            timestamp=timestamp,
        )

        assert metrics.operation_type == "mixed"
        assert metrics.total_operations == 150
