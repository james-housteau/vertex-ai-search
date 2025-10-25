"""Test configuration and fixtures for search-engine tests."""

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

# Add src to path for testing
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture
def mock_discovery_client():
    """Mock Google Cloud Discovery Engine client."""
    mock_client = Mock()
    mock_client.serving_config_path = Mock(
        return_value="projects/test-project/locations/global/collections/default_collection/dataStores/test-datastore/servingConfigs/default_config"
    )
    return mock_client


@pytest.fixture
def mock_search_response():
    """Mock search response from Discovery Engine."""
    mock_response = Mock()

    # Create mock results with proper relevance_score attribute handling
    mock_result1 = Mock()
    mock_document1 = Mock()
    mock_document1.id = "doc1"
    mock_document1.derived_struct_data = {
        "title": "Test Document 1",
        "content": "This is test content 1",
        "url": "https://example.com/doc1",
    }
    mock_document1.struct_data = (
        None  # Ensure struct_data is None to test derived_struct_data path
    )
    mock_result1.document = mock_document1
    mock_result1.relevance_score = 0.9

    mock_result2 = Mock()
    mock_document2 = Mock()
    mock_document2.id = "doc2"
    mock_document2.derived_struct_data = {
        "title": "Test Document 2",
        "content": "This is test content 2",
        "url": "https://example.com/doc2",
    }
    mock_document2.struct_data = None
    mock_result2.document = mock_document2
    mock_result2.relevance_score = 0.8

    mock_response.results = [mock_result1, mock_result2]
    mock_response.total_size = 2
    return mock_response


@pytest.fixture
def mock_empty_search_response():
    """Mock empty search response."""
    mock_response = Mock()
    mock_response.results = []
    mock_response.total_size = 0
    return mock_response


@pytest.fixture
def mock_search_response_no_scores():
    """Mock search response without relevance scores for default handling test."""
    mock_response = Mock()

    # Create mock result without relevance_score attribute using spec
    mock_result = Mock(spec=["document"])  # Only specify document attribute
    mock_document = Mock()
    mock_document.id = "doc1"
    mock_document.derived_struct_data = {
        "title": "Test Document",
        "content": "Test content without score",
    }
    mock_document.struct_data = None
    mock_result.document = mock_document

    mock_response.results = [mock_result]
    mock_response.total_size = 1
    return mock_response


@pytest.fixture
def sample_queries():
    """Sample search queries for testing."""
    return [
        "machine learning basics",
        "python programming",
        "data science tutorial",
        "artificial intelligence",
        "deep learning",
    ]
