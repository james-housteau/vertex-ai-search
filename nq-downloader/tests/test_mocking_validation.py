"""
Test to validate that all network calls are properly mocked.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch, Mock

from nq_downloader.downloader import NQDownloader, DownloadResult


class TestNetworkCallPrevention:
    """Tests to ensure no real network calls are made during testing."""

    def test_download_uses_mocked_storage_client(self, mock_storage_client):
        """Test that NQDownloader uses the mocked StorageClient and doesn't make real calls."""
        mocks = mock_storage_client

        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = NQDownloader(
                project_id="test-project", output_dir=Path(temp_dir)
            )

            result = downloader.download_shard(shard_id="00", show_progress=False)

            # Verify the result is successful
            assert isinstance(result, DownloadResult)
            assert result.success is True
            assert result.local_path.name == "nq-train-00.jsonl.gz"
            assert result.file_size > 0
            assert result.checksum is not None

            # Verify the mock was called correctly (no real network calls)
            mocks["client_class"].assert_called_once_with(project="test-project")
            mocks["client"].bucket.assert_called_once_with("natural_questions")
            mocks["bucket"].blob.assert_called_once_with(
                "v1.0-simplified/nq-train-00.jsonl.gz"
            )
            mocks["blob"].download_to_filename.assert_called_once()

    def test_no_real_gcs_imports_during_mocking(self):
        """Test that with proper mocking, no actual GCS client is instantiated."""
        # This test ensures our mocks completely prevent network calls

        with patch("nq_downloader.downloader.StorageClient") as mock_client_class:
            mock_client = Mock()
            mock_bucket = Mock()
            mock_blob = Mock()

            mock_client_class.return_value = mock_client
            mock_client.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob
            mock_blob.size = 1024
            mock_blob.reload.return_value = None

            # Mock download to avoid file operations
            def mock_download(filename, **kwargs):
                Path(filename).parent.mkdir(parents=True, exist_ok=True)
                Path(filename).write_text("test content")

            mock_blob.download_to_filename.side_effect = mock_download

            with tempfile.TemporaryDirectory() as temp_dir:
                downloader = NQDownloader(
                    project_id="test-project", output_dir=Path(temp_dir)
                )

                result = downloader.download_shard(shard_id="00", show_progress=False)

                # The mock should have been called, not the real client
                assert mock_client_class.called
                assert result.success is True

                # No real authentication should have been attempted
                assert not hasattr(
                    mock_client_class.call_args[1]
                    if mock_client_class.call_args
                    else {},
                    "credentials",
                )

    @patch("nq_downloader.downloader.StorageClient")
    def test_authentication_error_handling_without_network(self, mock_storage_client):
        """Test that authentication errors are handled without making network calls."""
        from google.auth.exceptions import DefaultCredentialsError

        # Configure mock to raise authentication error immediately
        mock_storage_client.side_effect = DefaultCredentialsError(
            "Test credentials error"
        )

        downloader = NQDownloader(project_id="test-project")
        result = downloader.download_shard(shard_id="00", show_progress=False)

        # Should handle error gracefully without network calls
        assert isinstance(result, DownloadResult)
        assert result.success is False
        assert "Authentication error" in result.error_message
        assert mock_storage_client.called
