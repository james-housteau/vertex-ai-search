"""Tests for LoadTester core functionality."""

import time
from unittest.mock import Mock

from src.load_tester.load_tester import LoadTester, create_load_tester_with_mocks
from src.load_tester.models import (
    LoadTestConfig,
    LoadTestResult,
    MockAnswerService,
    MockMetricsCollector,
    MockSearchEngine,
    PerformanceMetrics,
)
from tests.test_constants import (
    CONCURRENT_USERS_5,
    ERROR_RATE_MAX,
    ERROR_RATE_MIN,
    EXECUTION_TIME_THRESHOLD_1_5,
    EXECUTION_TIME_THRESHOLD_2_0,
    EXECUTION_TIME_THRESHOLD_3_0,
    TOTAL_OPERATIONS_6,
    USER_COUNT_2,
    USER_COUNT_3,
)


class TestLoadTesterCore:
    """Test core LoadTester functionality."""

    def test_load_tester_initialization(self) -> None:
        """Test LoadTester proper initialization."""
        search_engine = MockSearchEngine("project", "datastore")
        answer_service = MockAnswerService("project", "datastore")
        metrics_collector = MockMetricsCollector()

        load_tester = LoadTester(search_engine, answer_service, metrics_collector)

        assert load_tester.search_engine == search_engine
        assert load_tester.answer_service == answer_service
        assert load_tester.metrics_collector == metrics_collector

    def test_factory_function(self) -> None:
        """Test create_load_tester_with_mocks factory function."""
        load_tester = create_load_tester_with_mocks(
            "custom-project",
            "custom-datastore",
        )

        assert isinstance(load_tester, LoadTester)
        assert isinstance(load_tester.search_engine, MockSearchEngine)
        assert isinstance(load_tester.answer_service, MockAnswerService)
        assert isinstance(load_tester.metrics_collector, MockMetricsCollector)
        assert load_tester.search_engine.project_id == "custom-project"
        assert load_tester.search_engine.data_store_id == "custom-datastore"

    def test_factory_function_defaults(self) -> None:
        """Test factory function with default parameters."""
        load_tester = create_load_tester_with_mocks()

        assert load_tester.search_engine.project_id == "test-project"
        assert load_tester.search_engine.data_store_id == "test-datastore"


class TestLoadTestExecution:
    """Test load test execution scenarios."""

    def test_run_load_test_basic(self, load_tester: LoadTester) -> None:
        """Test basic load test execution."""
        config = LoadTestConfig(
            concurrent_users=2,
            test_duration_seconds=1,
            search_queries=["test search"],
            conversation_queries=["test conversation"],
            ramp_up_time_seconds=0,
        )

        result = load_tester.run_load_test(config)

        assert isinstance(result, LoadTestResult)
        assert result.config == config
        assert result.total_operations > 0
        assert isinstance(result.search_metrics, PerformanceMetrics)
        assert isinstance(result.conversation_metrics, PerformanceMetrics)
        assert ERROR_RATE_MIN <= result.error_rate <= ERROR_RATE_MAX
        assert isinstance(result.success, bool)

    def test_run_load_test_multiple_queries(self, load_tester: LoadTester) -> None:
        """Test load test with multiple queries."""
        config = LoadTestConfig(
            concurrent_users=2,
            test_duration_seconds=1,
            search_queries=["search1", "search2", "search3"],
            conversation_queries=["conv1", "conv2"],
            ramp_up_time_seconds=0,
        )

        result = load_tester.run_load_test(config)

        # Should execute all queries for all users
        expected_search_ops = 2 * 3  # 2 users * 3 search queries
        expected_conv_ops = 2 * 2  # 2 users * 2 conversation queries
        expected_total = expected_search_ops + expected_conv_ops

        assert result.total_operations == expected_total
        assert result.search_metrics.total_requests == expected_search_ops
        assert result.conversation_metrics.total_requests == expected_conv_ops

    def test_run_load_test_empty_queries(self, load_tester: LoadTester) -> None:
        """Test load test with empty query lists."""
        config = LoadTestConfig(
            concurrent_users=2,
            test_duration_seconds=1,
            search_queries=[],
            conversation_queries=[],
            ramp_up_time_seconds=0,
        )

        result = load_tester.run_load_test(config)

        assert result.total_operations == 0
        assert result.search_metrics.total_requests == 0
        assert result.conversation_metrics.total_requests == 0

    def test_run_search_load_test(self, load_tester: LoadTester) -> None:
        """Test search-only load test."""
        queries = ["search1", "search2"]
        result = load_tester.run_search_load_test(
            queries,
            concurrent_users=2,
            duration_seconds=1,
        )

        assert isinstance(result, LoadTestResult)
        assert result.config.search_queries == queries
        assert result.config.conversation_queries == []
        assert result.config.concurrent_users == USER_COUNT_2
        assert result.config.test_duration_seconds == 1
        assert result.search_metrics.total_requests > 0
        assert result.conversation_metrics.total_requests == 0

    def test_run_conversation_load_test(self, load_tester: LoadTester) -> None:
        """Test conversation-only load test."""
        queries = ["conv1", "conv2"]
        result = load_tester.run_conversation_load_test(
            queries,
            concurrent_users=2,
            duration_seconds=1,
        )

        assert isinstance(result, LoadTestResult)
        assert result.config.conversation_queries == queries
        assert result.config.search_queries == []
        assert result.config.concurrent_users == USER_COUNT_2
        assert result.config.test_duration_seconds == 1
        assert result.conversation_metrics.total_requests > 0
        assert result.search_metrics.total_requests == 0


class TestConcurrentExecution:
    """Test concurrent execution capabilities."""

    def test_concurrent_search_execution(self, load_tester: LoadTester) -> None:
        """Test concurrent search operation execution."""
        start_time = time.time()

        result = load_tester.run_search_load_test(
            queries=["concurrent test"],
            concurrent_users=5,
            duration_seconds=1,
        )

        execution_time = time.time() - start_time

        # With 5 concurrent users, should be faster than sequential execution
        # (mock has sleep, so concurrent should show performance benefit)
        assert result.search_metrics.total_requests == CONCURRENT_USERS_5
        assert (
            execution_time < EXECUTION_TIME_THRESHOLD_2_0
        )  # Should complete in reasonable time

    def test_concurrent_conversation_execution(self, load_tester: LoadTester) -> None:
        """Test concurrent conversation operation execution."""
        start_time = time.time()

        result = load_tester.run_conversation_load_test(
            queries=["concurrent conversation"],
            concurrent_users=3,
            duration_seconds=1,
        )

        execution_time = time.time() - start_time

        assert result.conversation_metrics.total_requests == USER_COUNT_3
        assert (
            execution_time < EXECUTION_TIME_THRESHOLD_2_0
        )  # Should complete in reasonable time

    def test_mixed_concurrent_execution(self, load_tester: LoadTester) -> None:
        """Test mixed concurrent execution of search and conversation."""
        config = LoadTestConfig(
            concurrent_users=3,
            test_duration_seconds=1,
            search_queries=["search"],
            conversation_queries=["conversation"],
            ramp_up_time_seconds=0,
        )

        start_time = time.time()
        result = load_tester.run_load_test(config)
        execution_time = time.time() - start_time

        # Should execute both types concurrently
        assert result.search_metrics.total_requests == USER_COUNT_3
        assert result.conversation_metrics.total_requests == USER_COUNT_3
        assert result.total_operations == TOTAL_OPERATIONS_6
        assert (
            execution_time < EXECUTION_TIME_THRESHOLD_3_0
        )  # Should be reasonably fast


class TestRampUpTiming:
    """Test ramp-up timing functionality."""

    def test_ramp_up_timing_application(self, load_tester: LoadTester) -> None:
        """Test that ramp-up timing affects execution time."""
        config_no_ramp = LoadTestConfig(
            concurrent_users=2,
            test_duration_seconds=1,
            search_queries=["ramp test"],
            conversation_queries=[],
            ramp_up_time_seconds=0,
        )

        config_with_ramp = LoadTestConfig(
            concurrent_users=2,
            test_duration_seconds=1,
            search_queries=["ramp test"],
            conversation_queries=[],
            ramp_up_time_seconds=1,
        )

        # Measure execution times
        start_time = time.time()
        result_no_ramp = load_tester.run_load_test(config_no_ramp)
        no_ramp_time = time.time() - start_time

        start_time = time.time()
        result_with_ramp = load_tester.run_load_test(config_with_ramp)
        with_ramp_time = time.time() - start_time

        # Ramp-up version should take longer
        assert with_ramp_time > no_ramp_time
        assert (
            result_no_ramp.search_metrics.total_requests
            == result_with_ramp.search_metrics.total_requests
        )

    def test_ramp_up_zero_duration(self, load_tester: LoadTester) -> None:
        """Test ramp-up with zero duration has no effect."""
        config = LoadTestConfig(
            concurrent_users=3,
            test_duration_seconds=1,
            search_queries=["test"],
            conversation_queries=[],
            ramp_up_time_seconds=0,
        )

        # Should complete without delay
        start_time = time.time()
        result = load_tester.run_load_test(config)
        execution_time = time.time() - start_time

        assert result.search_metrics.total_requests == USER_COUNT_3
        assert (
            execution_time < EXECUTION_TIME_THRESHOLD_1_5
        )  # Should be quick without ramp-up


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_zero_concurrent_users(self, load_tester: LoadTester) -> None:
        """Test handling of zero concurrent users."""
        result = load_tester.run_search_load_test(
            queries=["test"],
            concurrent_users=0,
            duration_seconds=1,
        )

        assert result.search_metrics.total_requests == 0
        assert result.total_operations == 0

    def test_empty_search_queries(self, load_tester: LoadTester) -> None:
        """Test handling of empty search queries."""
        result = load_tester.run_search_load_test(
            queries=[],
            concurrent_users=2,
            duration_seconds=1,
        )

        assert result.search_metrics.total_requests == 0
        assert result.total_operations == 0

    def test_empty_conversation_queries(self, load_tester: LoadTester) -> None:
        """Test handling of empty conversation queries."""
        result = load_tester.run_conversation_load_test(
            queries=[],
            concurrent_users=2,
            duration_seconds=1,
        )

        assert result.conversation_metrics.total_requests == 0
        assert result.total_operations == 0

    def test_service_error_handling(self) -> None:
        """Test handling of service errors during execution."""
        # Create mock services that raise exceptions
        failing_search_engine = Mock()
        failing_search_engine.search.side_effect = Exception("Search service error")

        failing_answer_service = Mock()
        failing_answer_service.answer_query.side_effect = Exception(
            "Answer service error",
        )

        metrics_collector = MockMetricsCollector()

        load_tester = LoadTester(
            failing_search_engine,
            failing_answer_service,
            metrics_collector,
        )

        # Test that errors are handled gracefully
        result = load_tester.run_search_load_test(
            queries=["test"],
            concurrent_users=1,
            duration_seconds=1,
        )

        # Should create error results instead of crashing
        assert result.search_metrics.total_requests > 0
        # Error rate should be high due to failing service
        assert result.search_metrics.error_rate > 0


class TestReportGeneration:
    """Test comprehensive report generation."""

    def test_generate_comprehensive_report(self, load_tester: LoadTester) -> None:
        """Test comprehensive report generation."""
        config = LoadTestConfig(
            concurrent_users=2,
            test_duration_seconds=1,
            search_queries=["test search"],
            conversation_queries=["test conversation"],
            ramp_up_time_seconds=0,
        )

        result = load_tester.run_load_test(config)
        report = load_tester.generate_comprehensive_report(result)

        # Verify report structure and content
        assert isinstance(report, str)
        assert len(report) > 0

        # Check for required sections
        assert "LOAD TEST COMPREHENSIVE REPORT" in report
        assert "TEST CONFIGURATION:" in report
        assert "OVERALL RESULTS:" in report
        assert "SEARCH METRICS:" in report
        assert "CONVERSATION METRICS:" in report

        # Check for configuration details
        assert "Concurrent Users: 2" in report
        assert "Test Duration: 1s" in report
        assert "Search Queries: 1" in report
        assert "Conversation Queries: 1" in report

        # Check for metrics details
        assert "Total Operations:" in report
        assert "Error Rate:" in report
        assert "Avg Response Time:" in report
        assert "Throughput:" in report

    def test_report_formatting(self, load_tester: LoadTester) -> None:
        """Test report formatting and structure."""
        config = LoadTestConfig(
            concurrent_users=1,
            test_duration_seconds=1,
            search_queries=["format test"],
            conversation_queries=[],
            ramp_up_time_seconds=0,
        )

        result = load_tester.run_load_test(config)
        report = load_tester.generate_comprehensive_report(result)

        # Verify formatting elements
        assert "=" * 80 in report  # Header separator
        assert "✅ PASS" in report or "❌ FAIL" in report  # Success indicator
        assert "req/s" in report  # Throughput units
        assert "ms" in report  # Time units
        assert "%" in report  # Percentage formatting

    def test_report_with_no_operations(self, load_tester: LoadTester) -> None:
        """Test report generation with no operations."""
        config = LoadTestConfig(
            concurrent_users=0,
            test_duration_seconds=1,
            search_queries=[],
            conversation_queries=[],
            ramp_up_time_seconds=0,
        )

        result = load_tester.run_load_test(config)
        report = load_tester.generate_comprehensive_report(result)

        # Should still generate valid report
        assert isinstance(report, str)
        assert "Total Operations: 0" in report
        assert "0.00ms" in report or "0.00 req/s" in report
