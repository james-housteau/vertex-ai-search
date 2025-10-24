"""Acceptance tests for metrics-collector API contract validation."""

import csv
import json
import threading
from datetime import datetime
from pathlib import Path

from metrics_collector import (
    ConversationResult,
    MetricsCollector,
    PerformanceMetrics,
    SearchResult,
)


class TestMetricsCollectorAPIContract:
    """Test the complete API contract as specified in Stream 4."""

    def test_metrics_collector_initialization_with_default_output_dir(self) -> None:
        """Test MetricsCollector can be initialized with default output directory."""
        collector = MetricsCollector()
        assert collector is not None

    def test_metrics_collector_initialization_with_custom_output_dir(self) -> None:
        """Test MetricsCollector can be initialized with custom output directory."""
        output_dir = Path("./custom_metrics")
        collector = MetricsCollector(output_dir=output_dir)
        assert collector is not None

    def test_record_search_metric_accepts_search_result(self) -> None:
        """Test recording search metrics with SearchResult object."""
        collector = MetricsCollector()
        search_result = SearchResult(
            query="test query",
            results=[{"title": "Test", "content": "Test content"}],
            result_count=1,
            execution_time_ms=150.5,
            relevance_scores=[0.95],
            success=True,
            error_message=None,
        )

        # Should not raise any exception
        collector.record_search_metric(search_result)

    def test_record_conversation_metric_accepts_conversation_result(self) -> None:
        """Test recording conversation metrics with ConversationResult object."""
        collector = MetricsCollector()
        conversation_result = ConversationResult(
            query="What is the weather like?",
            answer="The weather is sunny today.",
            response_time_ms=200.0,
            success=True,
            error_message=None,
            context_used=True,
        )

        # Should not raise any exception
        collector.record_conversation_metric(conversation_result)

    def test_generate_report_returns_performance_metrics(self) -> None:
        """Test generate_report returns PerformanceMetrics with correct structure."""
        collector = MetricsCollector()

        # Add some test data
        search_result = SearchResult(
            query="test",
            results=[],
            result_count=0,
            execution_time_ms=100.0,
            relevance_scores=[],
            success=True,
        )
        collector.record_search_metric(search_result)

        metrics = collector.generate_report()

        assert isinstance(metrics, PerformanceMetrics)
        assert isinstance(metrics.operation_type, str)
        assert isinstance(metrics.total_operations, int)
        assert isinstance(metrics.success_rate, float)
        assert isinstance(metrics.avg_response_time_ms, float)
        assert isinstance(metrics.median_response_time_ms, float)
        assert isinstance(metrics.p95_response_time_ms, float)
        assert isinstance(metrics.error_count, int)
        assert isinstance(metrics.timestamp, datetime)

    def test_export_to_json_returns_boolean_success(self, tmp_path: Path) -> None:
        """Test export_to_json returns boolean indicating success."""
        collector = MetricsCollector()

        # Add test data
        search_result = SearchResult(
            query="test",
            results=[],
            result_count=0,
            execution_time_ms=100.0,
            relevance_scores=[],
            success=True,
        )
        collector.record_search_metric(search_result)

        json_file = tmp_path / "test_metrics.json"
        result = collector.export_to_json(json_file)

        assert isinstance(result, bool)
        assert result is True
        assert json_file.exists()

    def test_export_to_csv_returns_boolean_success(self, tmp_path: Path) -> None:
        """Test export_to_csv returns boolean indicating success."""
        collector = MetricsCollector()

        # Add test data
        search_result = SearchResult(
            query="test",
            results=[],
            result_count=0,
            execution_time_ms=100.0,
            relevance_scores=[],
            success=True,
        )
        collector.record_search_metric(search_result)

        csv_file = tmp_path / "test_metrics.csv"
        result = collector.export_to_csv(csv_file)

        assert isinstance(result, bool)
        assert result is True
        assert csv_file.exists()


class TestMetricsCollectorFunctionality:
    """Test the functional behavior of the metrics collector."""

    def test_metrics_calculation_with_multiple_search_results(self) -> None:
        """Test metrics calculation with multiple search operations."""
        collector = MetricsCollector()

        # Add multiple search results with different response times
        search_results = [
            SearchResult("query1", [], 0, 100.0, [], success=True),
            SearchResult("query2", [], 0, 200.0, [], success=True),
            SearchResult(
                "query3", [], 0, 150.0, [], success=False, error_message="Error"
            ),
            SearchResult("query4", [], 0, 300.0, [], success=True),
            SearchResult("query5", [], 0, 250.0, [], success=True),
        ]

        for result in search_results:
            collector.record_search_metric(result)

        metrics = collector.generate_report()

        assert metrics.total_operations == 5
        assert metrics.success_rate == 80.0  # 4 out of 5 successful
        assert metrics.error_count == 1
        assert metrics.avg_response_time_ms == 200.0  # (100+200+150+300+250)/5
        assert metrics.median_response_time_ms == 200.0  # Middle value when sorted
        # For p95 with 5 values, it should be close to the 5th value (95th percentile)
        assert metrics.p95_response_time_ms >= 250.0

    def test_metrics_calculation_with_mixed_operations(self) -> None:
        """Test metrics calculation with both search and conversation operations."""
        collector = MetricsCollector()

        # Add search results
        search_result = SearchResult("search query", [], 0, 100.0, [], success=True)
        collector.record_search_metric(search_result)

        # Add conversation results
        conversation_result = ConversationResult(
            "conversation query",
            "response",
            200.0,
            success=True,
            error_message=None,
            context_used=True,
        )
        collector.record_conversation_metric(conversation_result)

        metrics = collector.generate_report()

        assert metrics.total_operations == 2
        assert metrics.success_rate == 100.0
        assert metrics.error_count == 0

    def test_json_export_contains_valid_data(self, tmp_path: Path) -> None:
        """Test that JSON export contains valid metric data."""
        collector = MetricsCollector()

        search_result = SearchResult("test", [], 0, 100.0, [], success=True)
        collector.record_search_metric(search_result)

        json_file = tmp_path / "metrics.json"
        collector.export_to_json(json_file)

        # Verify JSON content
        with Path(json_file).open() as f:
            data = json.load(f)

        assert "metrics" in data
        assert data["metrics"]["total_operations"] == 1
        assert data["metrics"]["success_rate"] == 100.0

    def test_csv_export_contains_valid_data(self, tmp_path: Path) -> None:
        """Test that CSV export contains valid metric data."""
        collector = MetricsCollector()

        search_result = SearchResult("test", [], 0, 100.0, [], success=True)
        collector.record_search_metric(search_result)

        csv_file = tmp_path / "metrics.csv"
        collector.export_to_csv(csv_file)

        # Verify CSV content
        with Path(csv_file).open() as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert "query" in reader.fieldnames
        assert "execution_time_ms" in reader.fieldnames
        assert "success" in reader.fieldnames

    def test_thread_safety_with_concurrent_operations(self) -> None:
        """Test that metrics collection is thread-safe."""
        collector = MetricsCollector()

        def add_search_metrics() -> None:
            for i in range(10):
                result = SearchResult(f"query{i}", [], 0, 100.0, [], success=True)
                collector.record_search_metric(result)

        def add_conversation_metrics() -> None:
            for i in range(10):
                result = ConversationResult(
                    f"conv{i}",
                    "answer",
                    200.0,
                    success=True,
                    error_message=None,
                    context_used=True,
                )
                collector.record_conversation_metric(result)

        # Run concurrent operations
        threads = [
            threading.Thread(target=add_search_metrics),
            threading.Thread(target=add_conversation_metrics),
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        metrics = collector.generate_report()
        assert metrics.total_operations == 20
        assert metrics.success_rate == 100.0

    def test_empty_metrics_generation(self) -> None:
        """Test generating report with no recorded metrics."""
        collector = MetricsCollector()
        metrics = collector.generate_report()

        assert metrics.total_operations == 0
        assert metrics.success_rate == 0.0
        assert metrics.error_count == 0
        assert metrics.avg_response_time_ms == 0.0
        assert metrics.median_response_time_ms == 0.0
        assert metrics.p95_response_time_ms == 0.0
