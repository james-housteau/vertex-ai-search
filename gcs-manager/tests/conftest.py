"""Shared test fixtures for GCS Manager tests."""

from unittest.mock import Mock, patch

import pytest
from gcs_manager.models import BucketConfig

# Try to import Google Cloud dependencies, but handle gracefully if not available
try:
    import importlib.util

    GOOGLE_STORAGE_AVAILABLE = importlib.util.find_spec("google.cloud.storage") is not None
except ImportError:
    GOOGLE_STORAGE_AVAILABLE = False


@pytest.fixture
def mock_gcs_client():
    """Mock GCS client for testing."""
    patch_target = (
        "google.cloud.storage.Client"
        if GOOGLE_STORAGE_AVAILABLE
        else "gcs_manager.manager.storage.Client"
    )
    with patch(patch_target) as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_bucket():
    """Mock GCS bucket for testing."""
    bucket = Mock()
    bucket.name = "test-bucket"
    bucket.location = "US"
    bucket.exists.return_value = True
    bucket.lifecycle_rules = []
    bucket.iam_configuration = Mock()
    return bucket


@pytest.fixture
def default_config():
    """Default bucket configuration for testing."""
    return BucketConfig(name="test-bucket")


@pytest.fixture
def custom_config():
    """Custom bucket configuration for testing."""
    return BucketConfig(
        name="custom-test-bucket",
        region="us-central1",
        lifecycle_days=7,
        uniform_access=False,
    )


@pytest.fixture
def project_id():
    """Test project ID."""
    return "test-project-12345"
