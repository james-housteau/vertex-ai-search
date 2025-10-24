"""Test configuration and fixtures for metrics-collector tests."""

import shutil
import tempfile
from pathlib import Path

import pytest

from metrics_collector.models import ConversationResult, SearchResult


@pytest.fixture
def temp_metrics_dir():
    """Create a temporary directory for metrics testing."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_search_result():
    """Create a sample SearchResult for testing."""
    return SearchResult(
        query="sample search query",
        results=[
            {"title": "Test Result 1", "content": "Content 1"},
            {"title": "Test Result 2", "content": "Content 2"},
        ],
        result_count=2,
        execution_time_ms=125.5,
        relevance_scores=[0.95, 0.87],
        success=True,
        error_message=None,
    )


@pytest.fixture
def sample_conversation_result():
    """Create a sample ConversationResult for testing."""
    return ConversationResult(
        query="What is the weather like today?",
        answer="The weather is sunny and warm today.",
        response_time_ms=250.0,
        success=True,
        error_message=None,
        context_used=True,
    )


@pytest.fixture
def failed_search_result():
    """Create a failed SearchResult for testing."""
    return SearchResult(
        query="failed search query",
        results=[],
        result_count=0,
        execution_time_ms=5000.0,
        relevance_scores=[],
        success=False,
        error_message="Request timeout",
    )


@pytest.fixture
def failed_conversation_result():
    """Create a failed ConversationResult for testing."""
    return ConversationResult(
        query="Complex unanswerable question?",
        answer="",
        response_time_ms=10000.0,
        success=False,
        error_message="Processing timeout",
        context_used=False,
    )
