"""
Shared test configuration and fixtures for NQ Downloader tests.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock


@pytest.fixture
def temp_output_dir():
    """Provide a temporary directory for test downloads."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def mock_gcs_client():
    """Provide a mock GCS client for testing."""
    mock_client = Mock()
    mock_bucket = Mock()
    mock_blob = Mock()

    # Configure mock behavior
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    mock_blob.size = 1024000  # 1MB default size
    mock_blob.reload.return_value = None  # Mock blob.reload()

    return mock_client


@pytest.fixture
def sample_project_id():
    """Provide a sample GCP project ID for testing."""
    return "test-nq-project-123"


@pytest.fixture
def mock_storage_client():
    """Provide a mock StorageClient for testing that prevents network calls."""
    from unittest.mock import patch, Mock

    with patch("nq_downloader.downloader.StorageClient") as mock_client_class:
        # Create mocks for the chain: client -> bucket -> blob
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()

        # Configure the mock chain
        mock_client_class.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        # Configure blob behavior
        mock_blob.size = 1024000  # 1MB default size
        mock_blob.reload.return_value = None  # Mock blob.reload()

        # Mock download_to_filename to create a dummy file
        def mock_download(filename, **kwargs):
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            Path(filename).write_text("dummy content for testing")

        mock_blob.download_to_filename.side_effect = mock_download

        yield {
            "client_class": mock_client_class,
            "client": mock_client,
            "bucket": mock_bucket,
            "blob": mock_blob,
        }
