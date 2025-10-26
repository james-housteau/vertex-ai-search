"""Pytest configuration and fixtures for load-tester tests."""

import pytest

from load_tester.load_tester import LoadTester
from load_tester.models import (
    LoadTestConfig,
    MockAnswerService,
    MockMetricsCollector,
    MockSearchEngine,
)


@pytest.fixture
def sample_config() -> LoadTestConfig:
    """Provide sample load test configuration."""
    return LoadTestConfig(
        concurrent_users=3,
        test_duration_seconds=5,
        search_queries=["test query 1", "test query 2"],
        conversation_queries=["conversation 1", "conversation 2"],
        ramp_up_time_seconds=1,
    )


@pytest.fixture
def mock_search_engine() -> MockSearchEngine:
    """Provide mock search engine."""
    return MockSearchEngine("test-project", "test-datastore")


@pytest.fixture
def mock_answer_service() -> MockAnswerService:
    """Provide mock answer service."""
    return MockAnswerService("test-project", "test-datastore")


@pytest.fixture
def mock_metrics_collector() -> MockMetricsCollector:
    """Provide mock metrics collector."""
    return MockMetricsCollector()


@pytest.fixture
def load_tester(
    mock_search_engine: MockSearchEngine,
    mock_answer_service: MockAnswerService,
    mock_metrics_collector: MockMetricsCollector,
) -> LoadTester:
    """Provide configured LoadTester instance."""
    return LoadTester(
        mock_search_engine,
        mock_answer_service,
        mock_metrics_collector,
    )


@pytest.fixture
def sample_search_queries() -> list[str]:
    """Provide sample search queries."""
    return [
        "What is machine learning?",
        "How does AI work?",
        "Python programming basics",
    ]


@pytest.fixture
def sample_conversation_queries() -> list[str]:
    """Provide sample conversation queries."""
    return [
        "Explain artificial intelligence",
        "What are the benefits of cloud computing?",
        "How to get started with programming?",
    ]
