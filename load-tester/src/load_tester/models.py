"""Data models for load-tester module."""

import secrets
import time
from dataclasses import dataclass
from typing import Any

# Constants for magic values
MIN_RESPONSE_TIME = 50
MAX_RESPONSE_TIME_SEARCH = 500
MIN_CONVERSATION_RESPONSE_TIME = 100
MAX_CONVERSATION_RESPONSE_TIME = 1000
MIN_RELEVANCE_SCORE = 0.6
MAX_RELEVANCE_SCORE = 1.0
MIN_CONFIDENCE_SCORE = 0.7
MAX_CONFIDENCE_SCORE = 0.95
EMPTY_METRIC_VALUE = 0.0
DEFAULT_RESPONSE_TIME = 100.0
MOCK_THROUGHPUT_DIVISOR = 10.0
PERCENTAGE_CONVERSION = 100.0
PERCENTILE_50 = 0.5
PERCENTILE_95 = 0.95
PERCENTILE_99 = 0.99
MILLISECONDS_TO_SECONDS = 1000


@dataclass
class PerformanceMetrics:
    """Performance metrics data model for load testing results."""

    avg_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    p50_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    throughput_requests_per_second: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    error_rate: float


@dataclass
class LoadTestConfig:
    """Configuration for load testing scenarios."""

    concurrent_users: int
    test_duration_seconds: int
    search_queries: list[str]
    conversation_queries: list[str]
    ramp_up_time_seconds: int


@dataclass
class LoadTestResult:
    """Results from load testing execution."""

    config: LoadTestConfig
    total_operations: int
    search_metrics: PerformanceMetrics
    conversation_metrics: PerformanceMetrics
    error_rate: float
    success: bool


# Mock interfaces for testing (will be replaced by actual modules in integration)
@dataclass
class SearchResult:
    """Mock SearchResult for independent testing."""

    query: str
    results: list[dict[str, Any]]
    result_count: int
    execution_time_ms: float
    relevance_scores: list[float]
    success: bool
    error_message: str | None = None


@dataclass
class ConversationResult:
    """Mock ConversationResult for independent testing."""

    query: str
    answer: str
    sources: list[str]
    confidence_score: float
    execution_time_ms: float
    success: bool
    error_message: str | None = None


class MockSearchEngine:
    """Mock SearchEngine for independent testing."""

    def __init__(self, project_id: str, data_store_id: str) -> None:
        self.project_id = project_id
        self.data_store_id = data_store_id

    def search(self, query: str, max_results: int = 10) -> SearchResult:
        """Mock search implementation for testing."""
        # Simulate realistic response time
        response_time = MIN_RESPONSE_TIME + (
            secrets.randbelow(MAX_RESPONSE_TIME_SEARCH - MIN_RESPONSE_TIME + 1)
        )
        time.sleep(response_time / MILLISECONDS_TO_SECONDS)  # Convert to seconds

        return SearchResult(
            query=query,
            results=[
                {"title": f"Result {i}", "content": f"Content for {query}"}
                for i in range(max_results)
            ],
            result_count=max_results,
            execution_time_ms=float(response_time),
            relevance_scores=[
                MIN_RELEVANCE_SCORE
                + (
                    secrets.randbelow(
                        int(
                            (MAX_RELEVANCE_SCORE - MIN_RELEVANCE_SCORE)
                            * PERCENTAGE_CONVERSION,
                        )
                        + 1,
                    )
                    / PERCENTAGE_CONVERSION
                )
                for _ in range(max_results)
            ],
            success=True,
        )

    def validate_connection(self) -> bool:
        """Mock connection validation."""
        return True


class MockAnswerService:
    """Mock AnswerService for independent testing."""

    def __init__(self, project_id: str, data_store_id: str) -> None:
        self.project_id = project_id
        self.data_store_id = data_store_id

    def answer_query(self, query: str) -> ConversationResult:
        """Mock answer generation for testing."""
        # Simulate realistic response time
        response_time = MIN_CONVERSATION_RESPONSE_TIME + (
            secrets.randbelow(
                MAX_CONVERSATION_RESPONSE_TIME - MIN_CONVERSATION_RESPONSE_TIME + 1,
            )
        )
        time.sleep(response_time / MILLISECONDS_TO_SECONDS)  # Convert to seconds

        return ConversationResult(
            query=query,
            answer=f"This is a mock answer for: {query}",
            sources=["source1.html", "source2.html"],
            confidence_score=MIN_CONFIDENCE_SCORE
            + (
                secrets.randbelow(
                    int(
                        (MAX_CONFIDENCE_SCORE - MIN_CONFIDENCE_SCORE)
                        * PERCENTAGE_CONVERSION,
                    )
                    + 1,
                )
                / PERCENTAGE_CONVERSION
            ),
            execution_time_ms=float(response_time),
            success=True,
        )

    def validate_connection(self) -> bool:
        """Mock connection validation."""
        return True


class MockMetricsCollector:
    """Mock MetricsCollector for independent testing."""

    def __init__(self) -> None:
        self.metrics: list[dict[str, Any]] = []

    def collect_performance_metrics(self, results: list[Any]) -> PerformanceMetrics:
        """Mock metrics collection for testing."""
        if not results:
            return PerformanceMetrics(
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

        response_times = []
        successful = 0
        failed = 0

        for result in results:
            if hasattr(result, "execution_time_ms"):
                response_times.append(result.execution_time_ms)
            if hasattr(result, "success"):
                if result.success:
                    successful += 1
                else:
                    failed += 1

        if not response_times:
            response_times = [DEFAULT_RESPONSE_TIME]  # Default for testing

        response_times.sort()
        total_requests = len(results)

        return PerformanceMetrics(
            avg_response_time_ms=sum(response_times) / len(response_times),
            min_response_time_ms=min(response_times),
            max_response_time_ms=max(response_times),
            p50_response_time_ms=response_times[len(response_times) // 2],
            p95_response_time_ms=response_times[
                int(len(response_times) * PERCENTILE_95)
            ],
            p99_response_time_ms=response_times[
                int(len(response_times) * PERCENTILE_99)
            ],
            throughput_requests_per_second=total_requests / MOCK_THROUGHPUT_DIVISOR,
            total_requests=total_requests,
            successful_requests=successful,
            failed_requests=failed,
            error_rate=(
                failed / total_requests if total_requests > 0 else EMPTY_METRIC_VALUE
            ),
        )
