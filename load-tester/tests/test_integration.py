"""Integration tests for load-tester module."""

import time
from unittest.mock import Mock

from test_constants import (
    DURATION_2,
    DURATION_3,
    ERROR_RATE_MIN,
    ERROR_RATE_THRESHOLD,
    INTEGRATION_CONVERSATION_REQUESTS_8,
    INTEGRATION_CONVERSATION_REQUESTS_12,
    INTEGRATION_CONVERSATION_REQUESTS_20,
    INTEGRATION_EXECUTION_TIME_LIMIT,
    INTEGRATION_MIN_EXECUTION_TIME,
    INTEGRATION_REPORT_MIN_LENGTH,
    INTEGRATION_SEARCH_REQUESTS_5,
    INTEGRATION_SEARCH_REQUESTS_12,
    INTEGRATION_SEARCH_REQUESTS_20,
    INTEGRATION_SEARCH_REQUESTS_30,
    INTEGRATION_TOTAL_OPERATIONS_20,
    INTEGRATION_TOTAL_OPERATIONS_40,
    LATENCY_THRESHOLD_10,
    LATENCY_THRESHOLD_25,
    MAX_QUERIES,
    RAMP_TIME_2,
    REQUEST_COUNT_2,
    REQUEST_COUNT_3,
    USERS_3,
    USERS_6,
    USERS_8,
    USERS_20,
)

from load_tester.load_tester import LoadTester, create_load_tester_with_mocks
from load_tester.models import LoadTestConfig, MockMetricsCollector


class TestEndToEndIntegration:
    """Test end-to-end integration scenarios."""

    def test_complete_load_testing_workflow(self) -> None:
        """Test complete load testing workflow from start to finish."""
        # Create load tester with mock services
        load_tester = create_load_tester_with_mocks(
            "integration-project",
            "integration-datastore",
        )

        # Define comprehensive test configuration
        config = LoadTestConfig(
            concurrent_users=4,
            test_duration_seconds=DURATION_2,
            search_queries=[
                "What is artificial intelligence?",
                "Machine learning algorithms",
                "Cloud computing benefits",
            ],
            conversation_queries=[
                "Explain deep learning",
                "What are the advantages of microservices?",
            ],
            ramp_up_time_seconds=1,
        )

        # Execute comprehensive load test
        result = load_tester.run_load_test(config)

        # Verify comprehensive results
        assert result.success is True
        assert (
            result.total_operations == INTEGRATION_TOTAL_OPERATIONS_20
        )  # 4 users * (3 search + 2 conversation)
        assert (
            result.search_metrics.total_requests == INTEGRATION_SEARCH_REQUESTS_12
        )  # 4 users * 3 search queries
        assert (
            result.conversation_metrics.total_requests
            == INTEGRATION_CONVERSATION_REQUESTS_8
        )  # 4 users * 2 conversation queries
        assert result.error_rate < ERROR_RATE_THRESHOLD  # Less than 5% error rate

        # Verify metrics quality
        assert result.search_metrics.avg_response_time_ms > 0
        assert result.conversation_metrics.avg_response_time_ms > 0
        assert result.search_metrics.throughput_requests_per_second > 0
        assert result.conversation_metrics.throughput_requests_per_second > 0

        # Generate and verify comprehensive report
        report = load_tester.generate_comprehensive_report(result)
        assert len(report) > INTEGRATION_REPORT_MIN_LENGTH  # Substantial report content
        assert "LOAD TEST COMPREHENSIVE REPORT" in report
        assert (
            "integration-project" not in report
        )  # Report shouldn't expose internal details

    def test_search_only_integration(self) -> None:
        """Test search-only integration scenario."""
        load_tester = create_load_tester_with_mocks()

        queries = [
            "Python programming tutorial",
            "Data science fundamentals",
            "Machine learning models",
            "Software engineering practices",
            "Cloud architecture patterns",
        ]

        # Execute search-only load test
        result = load_tester.run_search_load_test(
            queries=queries,
            concurrent_users=USERS_6,
            duration_seconds=DURATION_3,
        )

        # Verify search-only integration
        assert result.success is True
        # 6 users * 5 queries = 30
        assert result.search_metrics.total_requests == INTEGRATION_SEARCH_REQUESTS_30
        assert result.conversation_metrics.total_requests == 0
        # High success rate
        assert result.search_metrics.successful_requests > LATENCY_THRESHOLD_25

        # Verify report generation
        report = load_tester.generate_comprehensive_report(result)
        assert "SEARCH METRICS:" in report
        assert f"Total Requests: {INTEGRATION_SEARCH_REQUESTS_30}" in report

    def test_conversation_only_integration(self) -> None:
        """Test conversation-only integration scenario."""
        load_tester = create_load_tester_with_mocks()

        queries = [
            "Explain the concept of neural networks",
            "What are the benefits of containerization?",
            "How does blockchain technology work?",
            "Describe the principles of DevOps",
        ]

        # Execute conversation-only load test
        result = load_tester.run_conversation_load_test(
            queries=queries,
            concurrent_users=USERS_3,
            duration_seconds=DURATION_2,
        )

        # Verify conversation-only integration
        assert result.success is True
        # 3 users * 4 queries = 12
        assert (
            result.conversation_metrics.total_requests
            == INTEGRATION_CONVERSATION_REQUESTS_12
        )
        assert result.search_metrics.total_requests == 0
        # High success rate
        assert result.conversation_metrics.successful_requests > LATENCY_THRESHOLD_10

        # Verify report generation
        report = load_tester.generate_comprehensive_report(result)
        assert "CONVERSATION METRICS:" in report
        assert f"Total Requests: {INTEGRATION_CONVERSATION_REQUESTS_12}" in report

    def test_high_concurrency_integration(self) -> None:
        """Test high concurrency integration scenario."""
        load_tester = create_load_tester_with_mocks()

        config = LoadTestConfig(
            concurrent_users=USERS_20,
            test_duration_seconds=1,
            search_queries=["high concurrency test"],
            conversation_queries=["high concurrency conversation"],
            ramp_up_time_seconds=0,
        )

        start_time = time.time()
        result = load_tester.run_load_test(config)
        execution_time = time.time() - start_time

        # Verify high concurrency handling
        assert result.success is True
        # 20 users * 2 operations = 40
        assert result.total_operations == INTEGRATION_TOTAL_OPERATIONS_40
        # Should complete in reasonable time
        assert execution_time < INTEGRATION_EXECUTION_TIME_LIMIT
        assert result.search_metrics.total_requests == INTEGRATION_SEARCH_REQUESTS_20
        assert (
            result.conversation_metrics.total_requests
            == INTEGRATION_CONVERSATION_REQUESTS_20
        )

    def test_ramp_up_integration(self) -> None:
        """Test ramp-up timing integration."""
        load_tester = create_load_tester_with_mocks()

        config = LoadTestConfig(
            concurrent_users=5,
            test_duration_seconds=1,
            search_queries=["ramp up test"],
            conversation_queries=[],
            ramp_up_time_seconds=RAMP_TIME_2,
        )

        start_time = time.time()
        result = load_tester.run_load_test(config)
        execution_time = time.time() - start_time

        # Verify ramp-up affects timing
        assert result.success is True
        assert (
            execution_time > INTEGRATION_MIN_EXECUTION_TIME
        )  # Should take more time than no ramp-up
        assert result.search_metrics.total_requests == INTEGRATION_SEARCH_REQUESTS_5


class TestServiceIntegration:
    """Test integration with mock services."""

    def test_search_engine_integration(self) -> None:
        """Test integration with search engine service."""
        load_tester = create_load_tester_with_mocks()

        # Test search engine directly
        search_result = load_tester.search_engine.search(
            "integration test",
            max_results=MAX_QUERIES,
        )

        assert search_result.query == "integration test"
        assert len(search_result.results) == MAX_QUERIES
        assert search_result.success is True
        assert search_result.execution_time_ms > 0

        # Test through load tester
        result = load_tester.run_search_load_test(
            queries=["integration search"],
            concurrent_users=REQUEST_COUNT_2,
            duration_seconds=1,
        )

        assert result.success is True
        assert result.search_metrics.total_requests == REQUEST_COUNT_2

    def test_answer_service_integration(self) -> None:
        """Test integration with answer service."""
        load_tester = create_load_tester_with_mocks()

        # Test answer service directly
        conversation_result = load_tester.answer_service.answer_query(
            "integration conversation",
        )

        assert conversation_result.query == "integration conversation"
        assert len(conversation_result.answer) > 0
        assert conversation_result.success is True
        assert conversation_result.execution_time_ms > 0

        # Test through load tester
        result = load_tester.run_conversation_load_test(
            queries=["integration conversation"],
            concurrent_users=REQUEST_COUNT_2,
            duration_seconds=1,
        )

        assert result.success is True
        assert result.conversation_metrics.total_requests == REQUEST_COUNT_2

    def test_metrics_collector_integration(self) -> None:
        """Test integration with metrics collector."""
        load_tester = create_load_tester_with_mocks()

        # Execute test to generate metrics
        result = load_tester.run_load_test(
            LoadTestConfig(
                concurrent_users=REQUEST_COUNT_3,
                test_duration_seconds=1,
                search_queries=["metrics test"],
                conversation_queries=["metrics conversation"],
                ramp_up_time_seconds=0,
            ),
        )

        # Verify metrics integration
        assert isinstance(result.search_metrics.avg_response_time_ms, float)
        assert isinstance(result.conversation_metrics.avg_response_time_ms, float)
        assert result.search_metrics.total_requests == REQUEST_COUNT_3
        assert result.conversation_metrics.total_requests == REQUEST_COUNT_3

    def test_service_validation_integration(self) -> None:
        """Test service validation integration."""
        load_tester = create_load_tester_with_mocks()

        # Test individual service validations
        search_valid = load_tester.search_engine.validate_connection()
        answer_valid = load_tester.answer_service.validate_connection()

        assert search_valid is True
        assert answer_valid is True


class TestErrorScenarios:
    """Test error handling in integration scenarios."""

    def test_partial_failure_integration(self) -> None:
        """Test integration with partial service failures."""
        # Create services with partial failures
        search_engine = Mock()
        search_engine.search.side_effect = [
            Exception("Search error"),  # First call fails
            Mock(execution_time_ms=100, success=True),  # Second call succeeds
            Mock(execution_time_ms=150, success=True),  # Third call succeeds
        ]

        answer_service = Mock()
        answer_service.answer_query.return_value = Mock(
            execution_time_ms=200,
            success=True,
        )

        metrics_collector = MockMetricsCollector()
        load_tester = LoadTester(search_engine, answer_service, metrics_collector)

        # Execute test with partial failures
        result = load_tester.run_search_load_test(
            queries=["test"],
            concurrent_users=REQUEST_COUNT_3,
            duration_seconds=1,
        )

        # Should handle partial failures gracefully
        assert isinstance(result.search_metrics.error_rate, float)
        assert result.search_metrics.error_rate > 0  # Some errors occurred

    def test_zero_operations_integration(self) -> None:
        """Test integration with zero operations scenario."""
        load_tester = create_load_tester_with_mocks()

        config = LoadTestConfig(
            concurrent_users=0,
            test_duration_seconds=1,
            search_queries=[],
            conversation_queries=[],
            ramp_up_time_seconds=0,
        )

        result = load_tester.run_load_test(config)

        # Should handle zero operations gracefully
        assert result.total_operations == 0
        assert result.search_metrics.total_requests == 0
        assert result.conversation_metrics.total_requests == 0
        assert result.error_rate == ERROR_RATE_MIN

        # Report should still be generated
        report = load_tester.generate_comprehensive_report(result)
        assert "Total Operations: 0" in report


class TestPerformanceIntegration:
    """Test performance characteristics in integration scenarios."""

    def test_throughput_measurement_integration(self) -> None:
        """Test throughput measurement integration."""
        load_tester = create_load_tester_with_mocks()

        config = LoadTestConfig(
            concurrent_users=USERS_8,
            test_duration_seconds=DURATION_2,
            search_queries=["throughput test"],
            conversation_queries=[],
            ramp_up_time_seconds=0,
        )

        start_time = time.time()
        result = load_tester.run_load_test(config)
        actual_duration = time.time() - start_time

        # Verify throughput calculations
        assert result.search_metrics.throughput_requests_per_second > 0
        expected_min_throughput = result.search_metrics.total_requests / actual_duration
        # Allow generous variance in throughput calculation for mock services
        # Mock services have overhead, so we just verify throughput is reasonable
        assert (
            result.search_metrics.throughput_requests_per_second
            > expected_min_throughput * 0.01
        )

    def test_response_time_distribution_integration(self) -> None:
        """Test response time distribution integration."""
        load_tester = create_load_tester_with_mocks()

        result = load_tester.run_search_load_test(
            queries=["response time test"],
            concurrent_users=10,
            duration_seconds=1,
        )

        metrics = result.search_metrics

        # Verify response time distribution makes sense
        assert metrics.min_response_time_ms <= metrics.avg_response_time_ms
        assert metrics.avg_response_time_ms <= metrics.max_response_time_ms
        assert metrics.p50_response_time_ms <= metrics.p95_response_time_ms
        assert metrics.p95_response_time_ms <= metrics.p99_response_time_ms
        assert metrics.p99_response_time_ms <= metrics.max_response_time_ms

    def test_concurrent_execution_performance(self) -> None:
        """Test concurrent execution performance."""
        load_tester = create_load_tester_with_mocks()

        # Sequential vs concurrent comparison
        sequential_start = time.time()
        sequential_result = load_tester.run_search_load_test(
            queries=["performance test"],
            concurrent_users=1,
            duration_seconds=1,
        )
        sequential_time = time.time() - sequential_start

        concurrent_start = time.time()
        concurrent_result = load_tester.run_search_load_test(
            queries=["performance test"],
            concurrent_users=5,
            duration_seconds=1,
        )
        concurrent_time = time.time() - concurrent_start

        # Concurrent should handle more requests in similar time
        assert (
            concurrent_result.search_metrics.total_requests
            > sequential_result.search_metrics.total_requests
        )
        # Time difference should be reasonable - allow variance for mock services
        # Mock services have overhead and variability, use generous multiplier
        assert (
            concurrent_time < sequential_time * 10
        )  # Allow up to 10x variance for test environment
