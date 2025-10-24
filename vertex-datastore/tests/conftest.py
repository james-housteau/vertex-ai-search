"""Test configuration and fixtures for vertex-datastore tests."""

import pytest

from vertex_datastore import VertexDataStoreManager


@pytest.fixture
def mock_manager() -> VertexDataStoreManager:
    """Create a VertexDataStoreManager instance for testing."""
    return VertexDataStoreManager(project_id="test-project", location="global")


@pytest.fixture
def mock_manager_us_central() -> VertexDataStoreManager:
    """Create a VertexDataStoreManager instance with us-central1 location."""
    return VertexDataStoreManager(project_id="test-project", location="us-central1")


@pytest.fixture
def sample_gcs_path() -> str:
    """Return a sample GCS path for testing."""
    return "gs://test-bucket/html-documents/"


@pytest.fixture
def sample_display_name() -> str:
    """Return a sample display name for testing."""
    return "test-html-datastore"
