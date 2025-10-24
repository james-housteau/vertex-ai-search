"""LoadTester implementation for End-to-End Load Testing."""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from .models import (
    LoadTestConfig,
    LoadTestResult,
    MockAnswerService,
    MockMetricsCollector,
    MockSearchEngine,
    PerformanceMetrics,
)

# Constants for magic values
DEFAULT_ERROR_THRESHOLD = 0.05
SEARCH_TIMEOUT_SECONDS = 30
CONVERSATION_TIMEOUT_SECONDS = 60
MIN_THREAD_POOL_SIZE = 1
EMPTY_METRIC_VALUE = 0.0
REPORT_DIVIDER_LENGTH = 80


class LoadTester:
    """Execute comprehensive load testing scenarios against Vertex AI Search system."""

    def __init__(
        self,
        search_engine: Any,
        answer_service: Any,
        metrics_collector: Any,
    ) -> None:
        """Initialize LoadTester with service dependencies."""
        self.search_engine = search_engine
        self.answer_service = answer_service
        self.metrics_collector = metrics_collector

    def run_load_test(self, config: LoadTestConfig) -> LoadTestResult:
        """Execute comprehensive load test with mixed search and conversation ops."""

        # Calculate operations distribution
        total_operations = (
            len(config.search_queries) + len(config.conversation_queries)
        ) * config.concurrent_users

        # Execute mixed load test
        search_results = self._execute_search_load(config)
        conversation_results = self._execute_conversation_load(config)

        # Collect metrics
        search_metrics = self.metrics_collector.collect_performance_metrics(
            search_results,
        )
        conversation_metrics = self.metrics_collector.collect_performance_metrics(
            conversation_results,
        )

        # Calculate overall error rate
        total_requests = len(search_results) + len(conversation_results)
        failed_requests = (
            search_metrics.failed_requests + conversation_metrics.failed_requests
        )
        overall_error_rate = (
            failed_requests / total_requests
            if total_requests > 0
            else EMPTY_METRIC_VALUE
        )

        return LoadTestResult(
            config=config,
            total_operations=total_operations,
            search_metrics=search_metrics,
            conversation_metrics=conversation_metrics,
            error_rate=overall_error_rate,
            success=overall_error_rate < DEFAULT_ERROR_THRESHOLD,
        )

    def run_search_load_test(
        self,
        queries: list[str],
        concurrent_users: int,
        duration_seconds: int,
    ) -> LoadTestResult:
        """Execute search-only load test."""
        config = LoadTestConfig(
            concurrent_users=concurrent_users,
            test_duration_seconds=duration_seconds,
            search_queries=queries,
            conversation_queries=[],
            ramp_up_time_seconds=0,
        )

        search_results = self._execute_search_load(config)
        search_metrics = self.metrics_collector.collect_performance_metrics(
            search_results,
        )

        # Empty conversation metrics for search-only test
        empty_metrics = PerformanceMetrics(
            avg_response_time_ms=EMPTY_METRIC_VALUE,
            min_response_time_ms=EMPTY_METRIC_VALUE,
            max_response_time_ms=EMPTY_METRIC_VALUE,
            p50_response_time_ms=EMPTY_METRIC_VALUE,
            p95_response_time_ms=EMPTY_METRIC_VALUE,
            p99_response_time_ms=EMPTY_METRIC_VALUE,
            throughput_requests_per_second=EMPTY_METRIC_VALUE,
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            error_rate=EMPTY_METRIC_VALUE,
        )

        return LoadTestResult(
            config=config,
            total_operations=len(search_results),
            search_metrics=search_metrics,
            conversation_metrics=empty_metrics,
            error_rate=search_metrics.error_rate,
            success=search_metrics.error_rate < DEFAULT_ERROR_THRESHOLD,
        )

    def run_conversation_load_test(
        self,
        queries: list[str],
        concurrent_users: int,
        duration_seconds: int,
    ) -> LoadTestResult:
        """Execute conversation-only load test."""
        config = LoadTestConfig(
            concurrent_users=concurrent_users,
            test_duration_seconds=duration_seconds,
            search_queries=[],
            conversation_queries=queries,
            ramp_up_time_seconds=0,
        )

        conversation_results = self._execute_conversation_load(config)
        conversation_metrics = self.metrics_collector.collect_performance_metrics(
            conversation_results,
        )

        # Empty search metrics for conversation-only test
        empty_metrics = PerformanceMetrics(
            avg_response_time_ms=EMPTY_METRIC_VALUE,
            min_response_time_ms=EMPTY_METRIC_VALUE,
            max_response_time_ms=EMPTY_METRIC_VALUE,
            p50_response_time_ms=EMPTY_METRIC_VALUE,
            p95_response_time_ms=EMPTY_METRIC_VALUE,
            p99_response_time_ms=EMPTY_METRIC_VALUE,
            throughput_requests_per_second=EMPTY_METRIC_VALUE,
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            error_rate=EMPTY_METRIC_VALUE,
        )

        return LoadTestResult(
            config=config,
            total_operations=len(conversation_results),
            search_metrics=empty_metrics,
            conversation_metrics=conversation_metrics,
            error_rate=conversation_metrics.error_rate,
            success=conversation_metrics.error_rate < DEFAULT_ERROR_THRESHOLD,
        )

    def generate_comprehensive_report(self, result: LoadTestResult) -> str:
        """Generate comprehensive test report combining all metrics."""
        report_lines = [
            "=" * REPORT_DIVIDER_LENGTH,
            "LOAD TEST COMPREHENSIVE REPORT",
            "=" * REPORT_DIVIDER_LENGTH,
            "",
            "TEST CONFIGURATION:",
            f"  Concurrent Users: {result.config.concurrent_users}",
            f"  Test Duration: {result.config.test_duration_seconds}s",
            f"  Ramp-up Time: {result.config.ramp_up_time_seconds}s",
            f"  Search Queries: {len(result.config.search_queries)}",
            f"  Conversation Queries: {len(result.config.conversation_queries)}",
            "",
            "OVERALL RESULTS:",
            f"  Total Operations: {result.total_operations}",
            f"  Overall Error Rate: {result.error_rate:.2%}",
            f"  Test Success: {'✅ PASS' if result.success else '❌ FAIL'}",
            "",
            "SEARCH METRICS:",
            f"  Total Requests: {result.search_metrics.total_requests}",
            f"  Successful: {result.search_metrics.successful_requests}",
            f"  Failed: {result.search_metrics.failed_requests}",
            f"  Error Rate: {result.search_metrics.error_rate:.2%}",
            f"  Avg Response Time: {result.search_metrics.avg_response_time_ms:.2f}ms",
            f"  Min Response Time: {result.search_metrics.min_response_time_ms:.2f}ms",
            f"  Max Response Time: {result.search_metrics.max_response_time_ms:.2f}ms",
            f"  P50 Response Time: {result.search_metrics.p50_response_time_ms:.2f}ms",
            f"  P95 Response Time: {result.search_metrics.p95_response_time_ms:.2f}ms",
            f"  P99 Response Time: {result.search_metrics.p99_response_time_ms:.2f}ms",
            f"  Throughput: "
            f"{result.search_metrics.throughput_requests_per_second:.2f} req/s",
            "",
            "CONVERSATION METRICS:",
            f"  Total Requests: {result.conversation_metrics.total_requests}",
            f"  Successful: {result.conversation_metrics.successful_requests}",
            f"  Failed: {result.conversation_metrics.failed_requests}",
            f"  Error Rate: {result.conversation_metrics.error_rate:.2%}",
            f"  Avg Response Time: "
            f"{result.conversation_metrics.avg_response_time_ms:.2f}ms",
            f"  Min Response Time: "
            f"{result.conversation_metrics.min_response_time_ms:.2f}ms",
            f"  Max Response Time: "
            f"{result.conversation_metrics.max_response_time_ms:.2f}ms",
            f"  P50 Response Time: "
            f"{result.conversation_metrics.p50_response_time_ms:.2f}ms",
            f"  P95 Response Time: "
            f"{result.conversation_metrics.p95_response_time_ms:.2f}ms",
            f"  P99 Response Time: "
            f"{result.conversation_metrics.p99_response_time_ms:.2f}ms",
            f"  Throughput: "
            f"{result.conversation_metrics.throughput_requests_per_second:.2f} req/s",
            "",
            "=" * REPORT_DIVIDER_LENGTH,
        ]

        return "\n".join(report_lines)

    def _execute_search_load(self, config: LoadTestConfig) -> list[Any]:
        """Execute search operations with concurrent users and ramp-up."""
        if not config.search_queries or config.concurrent_users == 0:
            return []

        results = []

        # Apply ramp-up timing
        if config.ramp_up_time_seconds > 0:
            self._apply_ramp_up(config.ramp_up_time_seconds, config.concurrent_users)

        # Execute concurrent search operations
        # Ensure max_workers is at least 1 to prevent ThreadPoolExecutor errors
        max_workers = max(MIN_THREAD_POOL_SIZE, config.concurrent_users)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []

            for _ in range(config.concurrent_users):
                for query in config.search_queries:
                    future = executor.submit(self.search_engine.search, query)
                    futures.append(future)

            # Collect results
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=SEARCH_TIMEOUT_SECONDS)
                    results.append(result)
                except (TimeoutError, RuntimeError) as e:
                    # Create failed result for error tracking
                    error_result = type(
                        "ErrorResult",
                        (),
                        {
                            "execution_time_ms": EMPTY_METRIC_VALUE,
                            "success": False,
                            "error_message": str(e),
                        },
                    )()
                    results.append(error_result)

        return results

    def _execute_conversation_load(self, config: LoadTestConfig) -> list[Any]:
        """Execute conversation operations with concurrent users and ramp-up."""
        if not config.conversation_queries or config.concurrent_users == 0:
            return []

        results = []

        # Apply ramp-up timing
        if config.ramp_up_time_seconds > 0:
            self._apply_ramp_up(config.ramp_up_time_seconds, config.concurrent_users)

        # Execute concurrent conversation operations
        # Ensure max_workers is at least 1 to prevent ThreadPoolExecutor errors
        max_workers = max(MIN_THREAD_POOL_SIZE, config.concurrent_users)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []

            for _ in range(config.concurrent_users):
                for query in config.conversation_queries:
                    future = executor.submit(self.answer_service.answer_query, query)
                    futures.append(future)

            # Collect results
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=CONVERSATION_TIMEOUT_SECONDS)
                    results.append(result)
                except (TimeoutError, RuntimeError) as e:
                    # Create failed result for error tracking
                    error_result = type(
                        "ErrorResult",
                        (),
                        {
                            "execution_time_ms": EMPTY_METRIC_VALUE,
                            "success": False,
                            "error_message": str(e),
                        },
                    )()
                    results.append(error_result)

        return results

    def _apply_ramp_up(self, ramp_up_seconds: int, concurrent_users: int) -> None:
        """Apply gradual ramp-up of concurrent users."""
        min_users_for_ramp_up = 1
        if ramp_up_seconds <= 0 or concurrent_users <= min_users_for_ramp_up:
            return

        delay_per_user = ramp_up_seconds / concurrent_users
        time.sleep(delay_per_user)


# Factory function for easy instantiation with mock services
def create_load_tester_with_mocks(
    project_id: str = "test-project",
    data_store_id: str = "test-datastore",
) -> LoadTester:
    """Create LoadTester instance with mock services for independent testing."""
    search_engine = MockSearchEngine(project_id, data_store_id)
    answer_service = MockAnswerService(project_id, data_store_id)
    metrics_collector = MockMetricsCollector()

    return LoadTester(search_engine, answer_service, metrics_collector)
