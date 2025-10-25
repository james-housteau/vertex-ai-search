"""Tests for load-tester data models."""

from test_constants import (
    CONFIDENCE_0_8,
    CONFIDENCE_0_9,
    DURATION_1,
    DURATION_10,
    DURATION_30,
    ERROR_COUNT_1,
    ERROR_COUNT_2,
    ERROR_COUNT_5,
    ERROR_RATE_0_04,
    ERROR_RATE_0_05,
    ERROR_RATE_0_027,
    ERROR_RATE_FRACTION,
    HIGH_CONFIDENCE_0_95,
    HIGH_CONFIDENCE_1_0,
    LOW_CONFIDENCE_0_6,
    MAX_RESULTS_5,
    MID_CONFIDENCE_0_7,
    MIN_METRIC_VALUE,
    PERCENTILE_12_5,
    RAMP_TIME_0,
    RAMP_TIME_1,
    RAMP_TIME_5,
    REQUEST_COUNT_2,
    REQUEST_COUNT_3,
    REQUEST_COUNT_25,
    REQUEST_COUNT_48,
    REQUEST_COUNT_50,
    REQUEST_COUNT_100,
    RESPONSE_TIME_50,
    RESPONSE_TIME_90,
    RESPONSE_TIME_100,
    RESPONSE_TIME_140,
    RESPONSE_TIME_150,
    RESPONSE_TIME_180,
    RESPONSE_TIME_195,
    RESPONSE_TIME_200,
    RESPONSE_TIME_250,
    RESPONSE_TIME_280,
    RESPONSE_TIME_295,
    RESPONSE_TIME_300,
    RESPONSE_TIME_350,
    RESPONSE_TIME_390,
    RESPONSE_TIME_400,
    RESPONSE_TIME_450,
    RESPONSE_TIME_500,
    SUCCESS_COUNT_95,
    THROUGHPUT_5,
    THROUGHPUT_10,
    USERS_1,
    USERS_5,
    USERS_10,
    USERS_75,
)

from load_tester.models import (
    ConversationResult,
    LoadTestConfig,
    LoadTestResult,
    MockAnswerService,
    MockMetricsCollector,
    MockSearchEngine,
    PerformanceMetrics,
    SearchResult,
)


class TestLoadTestConfig:
    """Test LoadTestConfig dataclass."""

    def test_load_test_config_creation(self) -> None:
        """Test LoadTestConfig can be created with all fields."""
        config = LoadTestConfig(
            concurrent_users=USERS_10,
            test_duration_seconds=DURATION_30,
            search_queries=["query1", "query2", "query3"],
            conversation_queries=["conv1", "conv2"],
            ramp_up_time_seconds=RAMP_TIME_5,
        )

        assert config.concurrent_users == USERS_10
        assert config.test_duration_seconds == DURATION_30
        assert config.search_queries == ["query1", "query2", "query3"]
        assert config.conversation_queries == ["conv1", "conv2"]
        assert config.ramp_up_time_seconds == RAMP_TIME_5

    def test_load_test_config_empty_queries(self) -> None:
        """Test LoadTestConfig with empty query lists."""
        config = LoadTestConfig(
            concurrent_users=USERS_1,
            test_duration_seconds=DURATION_1,
            search_queries=[],
            conversation_queries=[],
            ramp_up_time_seconds=RAMP_TIME_0,
        )

        assert config.search_queries == []
        assert config.conversation_queries == []


class TestPerformanceMetrics:
    """Test PerformanceMetrics dataclass."""

    def test_performance_metrics_creation(self) -> None:
        """Test PerformanceMetrics can be created with all fields."""
        metrics = PerformanceMetrics(
            avg_response_time_ms=RESPONSE_TIME_150,
            min_response_time_ms=RESPONSE_TIME_50,
            max_response_time_ms=RESPONSE_TIME_300,
            p50_response_time_ms=RESPONSE_TIME_140,
            p95_response_time_ms=RESPONSE_TIME_280,
            p99_response_time_ms=RESPONSE_TIME_295,
            throughput_requests_per_second=PERCENTILE_12_5,
            total_requests=REQUEST_COUNT_100,
            successful_requests=SUCCESS_COUNT_95,
            failed_requests=ERROR_COUNT_5,
            error_rate=ERROR_RATE_0_05,
        )

        assert metrics.avg_response_time_ms == RESPONSE_TIME_150
        assert metrics.min_response_time_ms == RESPONSE_TIME_50
        assert metrics.max_response_time_ms == RESPONSE_TIME_300
        assert metrics.p50_response_time_ms == RESPONSE_TIME_140
        assert metrics.p95_response_time_ms == RESPONSE_TIME_280
        assert metrics.p99_response_time_ms == RESPONSE_TIME_295
        assert metrics.throughput_requests_per_second == PERCENTILE_12_5
        assert metrics.total_requests == REQUEST_COUNT_100
        assert metrics.successful_requests == SUCCESS_COUNT_95
        assert metrics.failed_requests == ERROR_COUNT_5
        assert metrics.error_rate == ERROR_RATE_0_05

    def test_performance_metrics_zero_values(self) -> None:
        """Test PerformanceMetrics with zero values."""
        metrics = PerformanceMetrics(
            avg_response_time_ms=MIN_METRIC_VALUE,
            min_response_time_ms=MIN_METRIC_VALUE,
            max_response_time_ms=MIN_METRIC_VALUE,
            p50_response_time_ms=MIN_METRIC_VALUE,
            p95_response_time_ms=MIN_METRIC_VALUE,
            p99_response_time_ms=MIN_METRIC_VALUE,
            throughput_requests_per_second=MIN_METRIC_VALUE,
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            error_rate=MIN_METRIC_VALUE,
        )

        assert metrics.total_requests == 0
        assert metrics.error_rate == MIN_METRIC_VALUE


class TestLoadTestResult:
    """Test LoadTestResult dataclass."""

    def test_load_test_result_creation(self) -> None:
        """Test LoadTestResult can be created with all fields."""
        config = LoadTestConfig(
            concurrent_users=USERS_5,
            test_duration_seconds=DURATION_10,
            search_queries=["test"],
            conversation_queries=["test"],
            ramp_up_time_seconds=RAMP_TIME_1,
        )

        search_metrics = PerformanceMetrics(
            avg_response_time_ms=RESPONSE_TIME_100,
            min_response_time_ms=RESPONSE_TIME_50,
            max_response_time_ms=RESPONSE_TIME_200,
            p50_response_time_ms=RESPONSE_TIME_90,
            p95_response_time_ms=RESPONSE_TIME_180,
            p99_response_time_ms=RESPONSE_TIME_195,
            throughput_requests_per_second=THROUGHPUT_10,
            total_requests=REQUEST_COUNT_50,
            successful_requests=REQUEST_COUNT_48,
            failed_requests=ERROR_COUNT_2,
            error_rate=ERROR_RATE_0_04,
        )

        conversation_metrics = PerformanceMetrics(
            avg_response_time_ms=RESPONSE_TIME_200,
            min_response_time_ms=RESPONSE_TIME_100,
            max_response_time_ms=RESPONSE_TIME_400,
            p50_response_time_ms=RESPONSE_TIME_180,
            p95_response_time_ms=RESPONSE_TIME_350,
            p99_response_time_ms=RESPONSE_TIME_390,
            throughput_requests_per_second=THROUGHPUT_5,
            total_requests=REQUEST_COUNT_25,
            successful_requests=REQUEST_COUNT_25,
            failed_requests=0,
            error_rate=MIN_METRIC_VALUE,
        )

        result = LoadTestResult(
            config=config,
            total_operations=USERS_75,
            search_metrics=search_metrics,
            conversation_metrics=conversation_metrics,
            error_rate=ERROR_RATE_0_027,
            success=True,
        )

        assert result.config == config
        assert result.total_operations == USERS_75
        assert result.search_metrics == search_metrics
        assert result.conversation_metrics == conversation_metrics
        assert result.error_rate == ERROR_RATE_0_027
        assert result.success is True


class TestMockSearchEngine:
    """Test MockSearchEngine implementation."""

    def test_mock_search_engine_init(self) -> None:
        """Test MockSearchEngine initialization."""
        engine = MockSearchEngine("test-project", "test-datastore")

        assert engine.project_id == "test-project"
        assert engine.data_store_id == "test-datastore"

    def test_mock_search_engine_search(self) -> None:
        """Test MockSearchEngine search method."""
        engine = MockSearchEngine("test-project", "test-datastore")
        result = engine.search("test query", max_results=MAX_RESULTS_5)

        assert isinstance(result, SearchResult)
        assert result.query == "test query"
        assert len(result.results) == MAX_RESULTS_5
        assert result.result_count == MAX_RESULTS_5
        assert result.execution_time_ms > 0
        assert len(result.relevance_scores) == MAX_RESULTS_5
        assert result.success is True
        assert result.error_message is None

        # Verify result structure
        for res in result.results:
            assert isinstance(res, dict)
            assert "title" in res
            assert "content" in res

        # Verify relevance scores are realistic
        for score in result.relevance_scores:
            assert LOW_CONFIDENCE_0_6 <= score <= HIGH_CONFIDENCE_1_0

    def test_mock_search_engine_validate_connection(self) -> None:
        """Test MockSearchEngine connection validation."""
        engine = MockSearchEngine("test-project", "test-datastore")
        assert engine.validate_connection() is True


class TestMockAnswerService:
    """Test MockAnswerService implementation."""

    def test_mock_answer_service_init(self) -> None:
        """Test MockAnswerService initialization."""
        service = MockAnswerService("test-project", "test-datastore")

        assert service.project_id == "test-project"
        assert service.data_store_id == "test-datastore"

    def test_mock_answer_service_answer_query(self) -> None:
        """Test MockAnswerService answer_query method."""
        service = MockAnswerService("test-project", "test-datastore")
        result = service.answer_query("What is AI?")

        assert isinstance(result, ConversationResult)
        assert result.query == "What is AI?"
        assert "What is AI?" in result.answer
        assert len(result.sources) > 0
        assert MID_CONFIDENCE_0_7 <= result.confidence_score <= HIGH_CONFIDENCE_0_95
        assert result.execution_time_ms > 0
        assert result.success is True
        assert result.error_message is None

    def test_mock_answer_service_validate_connection(self) -> None:
        """Test MockAnswerService connection validation."""
        service = MockAnswerService("test-project", "test-datastore")
        assert service.validate_connection() is True


class TestMockMetricsCollector:
    """Test MockMetricsCollector implementation."""

    def test_mock_metrics_collector_init(self) -> None:
        """Test MockMetricsCollector initialization."""
        collector = MockMetricsCollector()
        assert collector.metrics == []

    def test_mock_metrics_collector_empty_results(self) -> None:
        """Test MockMetricsCollector with empty results."""
        collector = MockMetricsCollector()
        metrics = collector.collect_performance_metrics([])

        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.total_requests == 0
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 0
        assert metrics.error_rate == MIN_METRIC_VALUE
        assert metrics.avg_response_time_ms == MIN_METRIC_VALUE

    def test_mock_metrics_collector_with_search_results(self) -> None:
        """Test MockMetricsCollector with search results."""
        collector = MockMetricsCollector()

        # Create mock search results
        results = [
            SearchResult(
                query="test1",
                results=[],
                result_count=0,
                execution_time_ms=RESPONSE_TIME_100,
                relevance_scores=[],
                success=True,
            ),
            SearchResult(
                query="test2",
                results=[],
                result_count=0,
                execution_time_ms=RESPONSE_TIME_200,
                relevance_scores=[],
                success=True,
            ),
            SearchResult(
                query="test3",
                results=[],
                result_count=0,
                execution_time_ms=RESPONSE_TIME_150,
                relevance_scores=[],
                success=False,
            ),
        ]

        metrics = collector.collect_performance_metrics(results)

        assert metrics.total_requests == REQUEST_COUNT_3
        assert metrics.successful_requests == REQUEST_COUNT_2
        assert metrics.failed_requests == ERROR_COUNT_1
        assert metrics.error_rate == ERROR_RATE_FRACTION
        assert metrics.avg_response_time_ms == RESPONSE_TIME_150
        assert metrics.min_response_time_ms == RESPONSE_TIME_100
        assert metrics.max_response_time_ms == RESPONSE_TIME_200

    def test_mock_metrics_collector_with_conversation_results(self) -> None:
        """Test MockMetricsCollector with conversation results."""
        collector = MockMetricsCollector()

        # Create mock conversation results
        results = [
            ConversationResult(
                query="conv1",
                answer="answer1",
                sources=[],
                confidence_score=CONFIDENCE_0_8,
                execution_time_ms=RESPONSE_TIME_300,
                success=True,
            ),
            ConversationResult(
                query="conv2",
                answer="answer2",
                sources=[],
                confidence_score=CONFIDENCE_0_9,
                execution_time_ms=RESPONSE_TIME_400,
                success=True,
            ),
        ]

        metrics = collector.collect_performance_metrics(results)

        assert metrics.total_requests == REQUEST_COUNT_2
        assert metrics.successful_requests == REQUEST_COUNT_2
        assert metrics.failed_requests == 0
        assert metrics.error_rate == MIN_METRIC_VALUE
        assert metrics.avg_response_time_ms == RESPONSE_TIME_350
        assert metrics.min_response_time_ms == RESPONSE_TIME_300
        assert metrics.max_response_time_ms == RESPONSE_TIME_400

    def test_mock_metrics_collector_percentile_calculation(self) -> None:
        """Test MockMetricsCollector percentile calculations."""
        collector = MockMetricsCollector()

        # Create results with known response times for percentile testing
        results = []
        response_times = [
            RESPONSE_TIME_50,
            RESPONSE_TIME_100,
            RESPONSE_TIME_150,
            RESPONSE_TIME_200,
            RESPONSE_TIME_250,
            RESPONSE_TIME_300,
            RESPONSE_TIME_350,
            RESPONSE_TIME_400,
            RESPONSE_TIME_450,
            RESPONSE_TIME_500,
        ]

        for i, rt in enumerate(response_times):
            results.append(
                SearchResult(
                    query=f"test{i}",
                    results=[],
                    result_count=0,
                    execution_time_ms=rt,
                    relevance_scores=[],
                    success=True,
                ),
            )

        metrics = collector.collect_performance_metrics(results)

        # Verify percentile calculations
        assert metrics.p50_response_time_ms == RESPONSE_TIME_300  # 50th percentile
        assert metrics.p95_response_time_ms == RESPONSE_TIME_500  # 95th percentile
        assert (
            metrics.p99_response_time_ms == RESPONSE_TIME_500
        )  # 99th percentile (same for small dataset)
