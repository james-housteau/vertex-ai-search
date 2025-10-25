"""Test configuration and fixtures for document uploader tests."""

from unittest.mock import Mock, patch

import pytest

# Try to import Google Cloud dependencies, but handle gracefully if not available
try:
    from google.auth.exceptions import DefaultCredentialsError

    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False

    # Create a mock exception class when google.auth is not available
    class DefaultCredentialsError(Exception):
        """Mock DefaultCredentialsError for when google.auth is not installed."""

        pass


@pytest.fixture(autouse=True)
def mock_gcs_globally():
    """Automatically mock Google Cloud Storage to prevent real API calls."""
    with patch("document_uploader.uploader.storage") as mock_storage:
        # Configure mock to simulate no credentials by default
        mock_storage.Client.side_effect = DefaultCredentialsError(
            "No credentials for testing"
        )
        yield mock_storage


@pytest.fixture
def mock_gcs_with_credentials():
    """Mock GCS with credentials available for testing upload functionality."""
    with patch("document_uploader.uploader.storage") as mock_storage:
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()

        mock_storage.Client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        # Configure blob for successful operations
        mock_blob.exists.return_value = True
        mock_blob.size = 100

        yield {
            "storage": mock_storage,
            "client": mock_client,
            "bucket": mock_bucket,
            "blob": mock_blob,
        }


@pytest.fixture
def mock_gcs_with_upload_error():
    """Mock GCS with upload errors for testing error handling."""
    with patch("document_uploader.uploader.storage") as mock_storage:
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()

        mock_storage.Client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        # Configure blob to fail uploads
        mock_blob.upload_from_filename.side_effect = Exception("Upload failed")

        yield {
            "storage": mock_storage,
            "client": mock_client,
            "bucket": mock_bucket,
            "blob": mock_blob,
        }
