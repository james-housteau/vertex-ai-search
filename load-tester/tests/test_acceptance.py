"""Acceptance tests for load-tester module API contract validation."""

import time

from test_constants import (
    DEFAULT_CONCURRENT_USERS,
    DEFAULT_RAMP_UP_USERS,
    DEFAULT_SEARCH_QUERIES,
    DURATION_30,
    ERROR_RATE_THRESHOLD,
    EXPECTED_USERS,
    LATENCY_THRESHOLD_30,
    MAX_METRIC_VALUE,
    MAX_QUERIES,
    MIN_METRIC_VALUE,
    RESPONSE_TIME_THRESHOLD,
    SUCCESS_PERCENTAGE,
    TEST_USERS_COUNT,
)

from load_tester.load_tester import LoadTester, create_load_tester_with_mocks
from load_tester.models import LoadTestConfig, LoadTestResult, PerformanceMetrics


class TestLoadTesterAPIContract:
    """Test API contract compliance as specified in Stream 4."""

    def test_load_test_config_dataclass(self) -> None:
        """Test LoadTestConfig dataclass structure."""
        config = LoadTestConfig(
            concurrent_users=DEFAULT_CONCURRENT_USERS,
            test_duration_seconds=DEFAULT_SEARCH_QUERIES,
            search_queries=["query1", "query2"],
            conversation_queries=["conv1", "conv2"],
            ramp_up_time_seconds=DEFAULT_RAMP_UP_USERS,
        )

        assert config.concurrent_users == DEFAULT_CONCURRENT_USERS
        assert config.test_duration_seconds == DEFAULT_SEARCH_QUERIES
        assert config.search_queries == ["query1", "query2"]
        assert config.conversation_queries == ["conv1", "conv2"]
        assert config.ramp_up_time_seconds == DEFAULT_RAMP_UP_USERS

    def test_load_test_result_dataclass(self) -> None:
        """Test LoadTestResult dataclass structure."""
        config = LoadTestConfig(
            concurrent_users=2,
            test_duration_seconds=5,
            search_queries=["test"],
            conversation_queries=["test"],
            ramp_up_time_seconds=0,
        )

        search_metrics = PerformanceMetrics(
            avg_response_time_ms=100.0,
            min_response_time_ms=50.0,
            max_response_time_ms=200.0,
            p50_response_time_ms=90.0,
            p95_response_time_ms=180.0,
            p99_response_time_ms=195.0,
            throughput_requests_per_second=10.0,
            total_requests=20,
            successful_requests=19,
            failed_requests=1,
            error_rate=0.05,
        )

        conversation_metrics = PerformanceMetrics(
            avg_response_time_ms=200.0,
            min_response_time_ms=100.0,
            max_response_time_ms=400.0,
            p50_response_time_ms=180.0,
            p95_response_time_ms=350.0,
            p99_response_time_ms=390.0,
            throughput_requests_per_second=5.0,
            total_requests=10,
            successful_requests=10,
            failed_requests=0,
            error_rate=0.0,
        )

        result = LoadTestResult(
            config=config,
            total_operations=DURATION_30,
            search_metrics=search_metrics,
            conversation_metrics=conversation_metrics,
            error_rate=RESPONSE_TIME_THRESHOLD,
            success=True,
        )

        assert result.config == config
        assert result.total_operations == LATENCY_THRESHOLD_30
        assert result.search_metrics == search_metrics
        assert result.conversation_metrics == conversation_metrics
        assert result.error_rate == RESPONSE_TIME_THRESHOLD
        assert result.success is True

    def test_load_tester_init_signature(self) -> None:
        """Test LoadTester.__init__ signature compliance."""
        # Create mock services
        load_tester = create_load_tester_with_mocks()

        assert hasattr(load_tester, "search_engine")
        assert hasattr(load_tester, "answer_service")
        assert hasattr(load_tester, "metrics_collector")

    def test_run_load_test_signature(self, load_tester: LoadTester) -> None:
        """Test run_load_test method signature compliance."""
        config = LoadTestConfig(
            concurrent_users=2,
            test_duration_seconds=1,
            search_queries=["test"],
            conversation_queries=["test"],
            ramp_up_time_seconds=0,
        )

        result = load_tester.run_load_test(config)

        assert isinstance(result, LoadTestResult)
        assert result.config == config
        assert isinstance(result.total_operations, int)
        assert isinstance(result.search_metrics, PerformanceMetrics)
        assert isinstance(result.conversation_metrics, PerformanceMetrics)
        assert isinstance(result.error_rate, float)
        assert isinstance(result.success, bool)

    def test_run_search_load_test_signature(self, load_tester: LoadTester) -> None:
        """Test run_search_load_test method signature compliance."""
        queries = ["test query 1", "test query 2"]
        concurrent_users = 2
        duration_seconds = 1

        result = load_tester.run_search_load_test(
            queries,
            concurrent_users,
            duration_seconds,
        )

        assert isinstance(result, LoadTestResult)
        assert result.config.search_queries == queries
        assert result.config.concurrent_users == concurrent_users
        assert result.config.test_duration_seconds == duration_seconds
        assert result.config.conversation_queries == []

    def test_run_conversation_load_test_signature(
        self,
        load_tester: LoadTester,
    ) -> None:
        """Test run_conversation_load_test method signature compliance."""
        queries = ["conversation 1", "conversation 2"]
        concurrent_users = 2
        duration_seconds = 1

        result = load_tester.run_conversation_load_test(
            queries,
            concurrent_users,
            duration_seconds,
        )

        assert isinstance(result, LoadTestResult)
        assert result.config.conversation_queries == queries
        assert result.config.concurrent_users == concurrent_users
        assert result.config.test_duration_seconds == duration_seconds
        assert result.config.search_queries == []

    def test_generate_comprehensive_report_signature(
        self,
        load_tester: LoadTester,
    ) -> None:
        """Test generate_comprehensive_report method signature compliance."""
        config = LoadTestConfig(
            concurrent_users=1,
            test_duration_seconds=1,
            search_queries=["test"],
            conversation_queries=["test"],
            ramp_up_time_seconds=0,
        )

        result = load_tester.run_load_test(config)
        report = load_tester.generate_comprehensive_report(result)

        assert isinstance(report, str)
        assert len(report) > 0
        assert "LOAD TEST COMPREHENSIVE REPORT" in report


class TestLoadTestingScenarios:
    """Test realistic load testing scenarios."""

    def test_comprehensive_mixed_load_test(self, load_tester: LoadTester) -> None:
        """Test comprehensive load test with mixed operations."""
        config = LoadTestConfig(
            concurrent_users=3,
            test_duration_seconds=2,
            search_queries=["AI basics", "ML concepts"],
            conversation_queries=["Explain AI", "What is ML?"],
            ramp_up_time_seconds=1,
        )

        result = load_tester.run_load_test(config)

        # Verify test execution
        assert result.success is True
        assert result.total_operations > 0
        assert result.search_metrics.total_requests > 0
        assert result.conversation_metrics.total_requests > 0
        assert result.error_rate < ERROR_RATE_THRESHOLD  # Less than 5% error rate

    def test_search_only_load_test(self, load_tester: LoadTester) -> None:
        """Test search-only load testing scenario."""
        queries = ["search query 1", "search query 2", "search query 3"]
        result = load_tester.run_search_load_test(
            queries,
            concurrent_users=2,
            duration_seconds=1,
        )

        # Verify search-only execution
        assert result.success is True
        assert result.search_metrics.total_requests > 0
        assert result.conversation_metrics.total_requests == 0
        assert len(result.config.search_queries) == MAX_QUERIES
        assert len(result.config.conversation_queries) == 0

    def test_conversation_only_load_test(self, load_tester: LoadTester) -> None:
        """Test conversation-only load testing scenario."""
        queries = ["conversation 1", "conversation 2", "conversation 3"]
        result = load_tester.run_conversation_load_test(
            queries,
            concurrent_users=2,
            duration_seconds=1,
        )

        # Verify conversation-only execution
        assert result.success is True
        assert result.conversation_metrics.total_requests > 0
        assert result.search_metrics.total_requests == 0
        assert len(result.config.conversation_queries) == MAX_QUERIES
        assert len(result.config.search_queries) == 0

    def test_high_concurrency_load_test(self, load_tester: LoadTester) -> None:
        """Test high concurrency load testing scenario."""
        config = LoadTestConfig(
            concurrent_users=10,
            test_duration_seconds=1,
            search_queries=["test"],
            conversation_queries=["test"],
            ramp_up_time_seconds=0,
        )

        result = load_tester.run_load_test(config)

        # Verify high concurrency handling
        assert result.success is True
        assert (
            result.total_operations >= TEST_USERS_COUNT
        )  # 10 users * 2 operations each
        assert result.search_metrics.total_requests >= EXPECTED_USERS
        assert result.conversation_metrics.total_requests >= EXPECTED_USERS

    def test_ramp_up_timing_scenario(self, load_tester: LoadTester) -> None:
        """Test ramp-up timing implementation."""
        config = LoadTestConfig(
            concurrent_users=2,
            test_duration_seconds=1,
            search_queries=["test"],
            conversation_queries=[],
            ramp_up_time_seconds=1,
        )

        start_time = time.time()
        result = load_tester.run_load_test(config)
        execution_time = time.time() - start_time

        # Verify ramp-up affects execution time
        assert result.success is True
        assert (
            execution_time > SUCCESS_PERCENTAGE
        )  # Should take at least most of ramp-up time (allow some variance)


class TestPerformanceMetrics:
    """Test performance metrics collection and calculation."""

    def test_performance_metrics_calculation(self, load_tester: LoadTester) -> None:
        """Test performance metrics are calculated correctly."""
        queries = ["metric test 1", "metric test 2"]
        result = load_tester.run_search_load_test(
            queries,
            concurrent_users=2,
            duration_seconds=1,
        )

        metrics = result.search_metrics

        # Verify metric structure
        assert metrics.avg_response_time_ms > 0
        assert metrics.min_response_time_ms >= 0
        assert metrics.max_response_time_ms >= metrics.avg_response_time_ms
        assert metrics.p50_response_time_ms > 0
        assert metrics.p95_response_time_ms >= metrics.p50_response_time_ms
        assert metrics.p99_response_time_ms >= metrics.p95_response_time_ms
        assert metrics.throughput_requests_per_second > 0
        assert metrics.total_requests > 0
        assert metrics.successful_requests <= metrics.total_requests
        assert metrics.failed_requests <= metrics.total_requests
        assert metrics.error_rate >= MIN_METRIC_VALUE
        assert metrics.error_rate <= MAX_METRIC_VALUE

    def test_comprehensive_report_generation(self, load_tester: LoadTester) -> None:
        """Test comprehensive report contains all required sections."""
        config = LoadTestConfig(
            concurrent_users=2,
            test_duration_seconds=1,
            search_queries=["test"],
            conversation_queries=["test"],
            ramp_up_time_seconds=0,
        )

        result = load_tester.run_load_test(config)
        report = load_tester.generate_comprehensive_report(result)

        # Verify report sections
        assert "LOAD TEST COMPREHENSIVE REPORT" in report
        assert "TEST CONFIGURATION:" in report
        assert "OVERALL RESULTS:" in report
        assert "SEARCH METRICS:" in report
        assert "CONVERSATION METRICS:" in report
        assert "Concurrent Users:" in report
        assert "Test Duration:" in report
        assert "Total Operations:" in report
        assert "Error Rate:" in report


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_empty_query_lists(self, load_tester: LoadTester) -> None:
        """Test handling of empty query lists."""
        config = LoadTestConfig(
            concurrent_users=1,
            test_duration_seconds=1,
            search_queries=[],
            conversation_queries=[],
            ramp_up_time_seconds=0,
        )

        result = load_tester.run_load_test(config)

        # Should handle empty queries gracefully
        assert isinstance(result, LoadTestResult)
        assert result.search_metrics.total_requests == 0
        assert result.conversation_metrics.total_requests == 0
        assert result.total_operations == 0

    def test_zero_concurrent_users(self, load_tester: LoadTester) -> None:
        """Test handling of zero concurrent users."""
        result = load_tester.run_search_load_test(
            ["test"],
            concurrent_users=0,
            duration_seconds=1,
        )

        # Should handle zero users gracefully
        assert isinstance(result, LoadTestResult)
        assert result.search_metrics.total_requests == 0

    def test_factory_function(self) -> None:
        """Test factory function for mock services."""
        load_tester = create_load_tester_with_mocks(
            "custom-project",
            "custom-datastore",
        )

        assert isinstance(load_tester, LoadTester)
        assert load_tester.search_engine.project_id == "custom-project"
        assert load_tester.search_engine.data_store_id == "custom-datastore"
        assert load_tester.answer_service.project_id == "custom-project"
        assert load_tester.answer_service.data_store_id == "custom-datastore"
