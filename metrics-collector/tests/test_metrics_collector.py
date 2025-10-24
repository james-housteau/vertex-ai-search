"""Test the MetricsCollector class functionality."""

import threading
import time
from datetime import datetime
from pathlib import Path

from metrics_collector import ConversationResult, MetricsCollector, SearchResult


class TestMetricsCollectorInitialization:
    """Test MetricsCollector initialization and setup."""

    def test_initialization_with_default_output_dir(self) -> None:
        """Test initialization with default output directory."""
        collector = MetricsCollector()
        assert collector.output_dir == Path("./metrics")

    def test_initialization_with_custom_output_dir(self, tmp_path: Path) -> None:
        """Test initialization with custom output directory."""
        custom_dir = tmp_path / "custom_metrics"
        collector = MetricsCollector(output_dir=custom_dir)
        assert collector.output_dir == custom_dir
        assert custom_dir.exists()  # Should be created automatically

    def test_output_directory_creation(self, tmp_path: Path) -> None:
        """Test that output directory is created if it doesn't exist."""
        non_existent_dir = tmp_path / "new_dir" / "metrics"
        assert not non_existent_dir.exists()

        MetricsCollector(output_dir=non_existent_dir)
        assert non_existent_dir.exists()


class TestMetricsRecording:
    """Test recording of search and conversation metrics."""

    def test_record_single_search_metric(self) -> None:
        """Test recording a single search metric."""
        collector = MetricsCollector()
        search_result = SearchResult(
            query="test query",
            results=[],
            result_count=0,
            execution_time_ms=100.0,
            relevance_scores=[],
            success=True,
        )

        collector.record_search_metric(search_result)
        metrics = collector.generate_report()

        assert metrics.total_operations == 1
        assert metrics.operation_type == "search"
        assert metrics.success_rate == 100.0

    def test_record_single_conversation_metric(self) -> None:
        """Test recording a single conversation metric."""
        collector = MetricsCollector()
        conversation_result = ConversationResult(
            query="test question",
            answer="test answer",
            response_time_ms=200.0,
            success=True,
        )

        collector.record_conversation_metric(conversation_result)
        metrics = collector.generate_report()

        assert metrics.total_operations == 1
        assert metrics.operation_type == "conversation"
        assert metrics.success_rate == 100.0

    def test_record_multiple_search_metrics(self) -> None:
        """Test recording multiple search metrics."""
        collector = MetricsCollector()

        for i in range(5):
            search_result = SearchResult(
                query=f"query {i}",
                results=[],
                result_count=0,
                execution_time_ms=100.0 + i * 10,
                relevance_scores=[],
                success=i % 2 == 0,  # Alternating success/failure
            )
            collector.record_search_metric(search_result)

        metrics = collector.generate_report()
        assert metrics.total_operations == 5
        assert metrics.success_rate == 60.0  # 3 out of 5 successful

    def test_record_mixed_metrics(self) -> None:
        """Test recording both search and conversation metrics."""
        collector = MetricsCollector()

        # Add search results
        for i in range(3):
            search_result = SearchResult(
                query=f"search {i}",
                results=[],
                result_count=0,
                execution_time_ms=100.0,
                relevance_scores=[],
                success=True,
            )
            collector.record_search_metric(search_result)

        # Add conversation results
        for i in range(2):
            conversation_result = ConversationResult(
                query=f"conversation {i}",
                answer="answer",
                response_time_ms=200.0,
                success=True,
            )
            collector.record_conversation_metric(conversation_result)

        metrics = collector.generate_report()
        assert metrics.total_operations == 5
        assert metrics.operation_type == "mixed"
        assert metrics.success_rate == 100.0


class TestStatisticalCalculations:
    """Test statistical calculations for metrics."""

    def test_average_calculation(self) -> None:
        """Test average response time calculation."""
        collector = MetricsCollector()

        response_times = [100.0, 200.0, 300.0, 400.0, 500.0]
        for i, time_ms in enumerate(response_times):
            search_result = SearchResult(
                query=f"query {i}",
                results=[],
                result_count=0,
                execution_time_ms=time_ms,
                relevance_scores=[],
                success=True,
            )
            collector.record_search_metric(search_result)

        metrics = collector.generate_report()
        assert metrics.avg_response_time_ms == 300.0  # (100+200+300+400+500)/5

    def test_median_calculation(self) -> None:
        """Test median response time calculation."""
        collector = MetricsCollector()

        response_times = [100.0, 200.0, 300.0, 400.0, 500.0]
        for i, time_ms in enumerate(response_times):
            search_result = SearchResult(
                query=f"query {i}",
                results=[],
                result_count=0,
                execution_time_ms=time_ms,
                relevance_scores=[],
                success=True,
            )
            collector.record_search_metric(search_result)

        metrics = collector.generate_report()
        assert metrics.median_response_time_ms == 300.0  # Middle value

    def test_p95_calculation(self) -> None:
        """Test 95th percentile calculation."""
        collector = MetricsCollector()

        # Add 20 operations with response times from 100 to 2000ms
        for i in range(20):
            search_result = SearchResult(
                query=f"query {i}",
                results=[],
                result_count=0,
                execution_time_ms=100.0 + i * 100,  # 100, 200, 300, ..., 2000
                relevance_scores=[],
                success=True,
            )
            collector.record_search_metric(search_result)

        metrics = collector.generate_report()
        # For 20 values, p95 index = min(int(0.95 * 20), 19) = 19
        # So it should be the 19th element (0-indexed) which is 2000ms
        assert metrics.p95_response_time_ms == 2000.0

    def test_success_rate_calculation(self) -> None:
        """Test success rate calculation."""
        collector = MetricsCollector()

        # Add 10 operations, 7 successful, 3 failed
        for i in range(10):
            search_result = SearchResult(
                query=f"query {i}",
                results=[],
                result_count=0,
                execution_time_ms=100.0,
                relevance_scores=[],
                success=i < 7,  # First 7 are successful
            )
            collector.record_search_metric(search_result)

        metrics = collector.generate_report()
        assert metrics.success_rate == 70.0
        assert metrics.error_count == 3

    def test_mixed_operation_statistics(self) -> None:
        """Test statistics calculation with mixed operation types."""
        collector = MetricsCollector()

        # Add search results with response times: 100, 200, 300
        search_times = [100.0, 200.0, 300.0]
        for i, time_ms in enumerate(search_times):
            search_result = SearchResult(
                query=f"search {i}",
                results=[],
                result_count=0,
                execution_time_ms=time_ms,
                relevance_scores=[],
                success=True,
            )
            collector.record_search_metric(search_result)

        # Add conversation results with response times: 400, 500
        conversation_times = [400.0, 500.0]
        for i, time_ms in enumerate(conversation_times):
            conversation_result = ConversationResult(
                query=f"conversation {i}",
                answer="answer",
                response_time_ms=time_ms,
                success=True,
            )
            collector.record_conversation_metric(conversation_result)

        metrics = collector.generate_report()
        # Combined times: [100, 200, 300, 400, 500]
        assert metrics.avg_response_time_ms == 300.0  # (100+200+300+400+500)/5
        assert metrics.median_response_time_ms == 300.0
        assert metrics.operation_type == "mixed"


class TestEmptyMetrics:
    """Test behavior with empty metrics."""

    def test_empty_metrics_report(self) -> None:
        """Test generating report with no recorded metrics."""
        collector = MetricsCollector()
        metrics = collector.generate_report()

        assert metrics.total_operations == 0
        assert metrics.success_rate == 0.0
        assert metrics.error_count == 0
        assert metrics.avg_response_time_ms == 0.0
        assert metrics.median_response_time_ms == 0.0
        assert metrics.p95_response_time_ms == 0.0
        assert metrics.operation_type == "mixed"
        assert isinstance(metrics.timestamp, datetime)


class TestThreadSafety:
    """Test thread safety of metrics collection."""

    def test_concurrent_search_metric_recording(self) -> None:
        """Test concurrent recording of search metrics."""
        collector = MetricsCollector()
        num_threads = 5
        metrics_per_thread = 10

        def add_search_metrics(thread_id: int) -> None:
            for i in range(metrics_per_thread):
                search_result = SearchResult(
                    query=f"thread{thread_id}_query{i}",
                    results=[],
                    result_count=0,
                    execution_time_ms=100.0 + thread_id * 10,
                    relevance_scores=[],
                    success=True,
                )
                collector.record_search_metric(search_result)

        threads = []
        for thread_id in range(num_threads):
            thread = threading.Thread(target=add_search_metrics, args=(thread_id,))
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        metrics = collector.generate_report()
        assert metrics.total_operations == num_threads * metrics_per_thread
        assert metrics.success_rate == 100.0

    def test_concurrent_mixed_metric_recording(self) -> None:
        """Test concurrent recording of mixed metrics."""
        collector = MetricsCollector()

        def add_search_metrics() -> None:
            for i in range(10):
                search_result = SearchResult(
                    query=f"search{i}",
                    results=[],
                    result_count=0,
                    execution_time_ms=100.0,
                    relevance_scores=[],
                    success=True,
                )
                collector.record_search_metric(search_result)
                time.sleep(0.001)  # Small delay to interleave operations

        def add_conversation_metrics() -> None:
            for i in range(10):
                conversation_result = ConversationResult(
                    query=f"conversation{i}",
                    answer="answer",
                    response_time_ms=200.0,
                    success=True,
                )
                collector.record_conversation_metric(conversation_result)
                time.sleep(0.001)  # Small delay to interleave operations

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
        assert metrics.operation_type == "mixed"
        assert metrics.success_rate == 100.0
