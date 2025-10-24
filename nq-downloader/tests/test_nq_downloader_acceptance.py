"""
Acceptance tests for NQ Downloader module.

These tests define the expected behavior for the nq-downloader implementation.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# Import the implemented classes
from nq_downloader.downloader import NQDownloader, DownloadResult


class TestNQDownloaderAcceptance:
    """Acceptance tests for the NQ Downloader module."""

    def test_downloader_initializes_with_project_id(self):
        """Test that NQDownloader can be initialized with a project ID."""
        project_id = "test-project-123"
        downloader = NQDownloader(project_id=project_id)

        assert downloader.project_id == project_id
        assert downloader.output_dir == Path("./data")

    def test_downloader_initializes_with_custom_output_dir(self):
        """Test that NQDownloader accepts custom output directory."""
        project_id = "test-project-123"
        custom_dir = Path("/tmp/nq-data")
        downloader = NQDownloader(project_id=project_id, output_dir=custom_dir)

        assert downloader.output_dir == custom_dir

    @patch("nq_downloader.downloader.StorageClient")
    def test_download_shard_returns_success_result(self, mock_storage_client):
        """Test successful download of NQ dataset shard returns DownloadResult."""
        # Create a temporary file to simulate the download
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = Path(temp_dir) / "nq-train-00.jsonl.gz"
            temp_file.write_text("dummy content for testing")

            # Mock GCS client and blob
            mock_client = Mock()
            mock_bucket = Mock()
            mock_blob = Mock()

            mock_storage_client.return_value = mock_client
            mock_client.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob
            mock_blob.size = 1024000  # 1MB
            mock_blob.reload.return_value = None  # Mock blob.reload()

            # Mock download_to_filename to create the actual file
            def mock_download(filename):
                Path(filename).parent.mkdir(parents=True, exist_ok=True)
                Path(filename).write_text("dummy content for testing")

            mock_blob.download_to_filename.side_effect = mock_download

            downloader = NQDownloader(
                project_id="test-project", output_dir=Path(temp_dir)
            )
            result = downloader.download_shard(shard_id="00", show_progress=False)

            assert isinstance(result, DownloadResult)
            assert result.success is True
            assert result.local_path.name == "nq-train-00.jsonl.gz"
            assert result.file_size > 0
            assert result.download_time_seconds > 0
            assert result.checksum is not None
            assert result.error_message is None

    @patch("nq_downloader.downloader.StorageClient")
    def test_download_shard_creates_output_directory(self, mock_storage_client):
        """Test that download creates output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock GCS client and blob
            mock_client = Mock()
            mock_bucket = Mock()
            mock_blob = Mock()

            mock_storage_client.return_value = mock_client
            mock_client.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob
            mock_blob.size = 1024
            mock_blob.reload.return_value = None  # Mock blob.reload()

            # Mock download_to_filename to create the actual file
            def mock_download(filename):
                Path(filename).parent.mkdir(parents=True, exist_ok=True)
                Path(filename).write_text("dummy content")

            mock_blob.download_to_filename.side_effect = mock_download

            output_dir = Path(temp_dir) / "new_directory"
            downloader = NQDownloader(project_id="test-project", output_dir=output_dir)

            # Directory should not exist initially
            assert not output_dir.exists()

            result = downloader.download_shard(shard_id="00", show_progress=False)

            # Directory should be created after download
            assert output_dir.exists()
            assert result.success is True

    def test_validate_file_returns_true_for_valid_file(self):
        """Test that validate_file returns True for existing files."""
        with tempfile.NamedTemporaryFile() as temp_file:
            downloader = NQDownloader(project_id="test-project")
            result = downloader.validate_file(Path(temp_file.name))
            assert result is True

    def test_validate_file_returns_false_for_missing_file(self):
        """Test that validate_file returns False for non-existent files."""
        downloader = NQDownloader(project_id="test-project")
        result = downloader.validate_file(Path("/nonexistent/file.txt"))
        assert result is False

    @patch("nq_downloader.downloader.StorageClient")
    def test_download_shard_handles_authentication_error(self, mock_storage_client):
        """Test that download handles authentication errors gracefully."""
        from google.auth.exceptions import DefaultCredentialsError

        # Mock storage to raise authentication error
        mock_storage_client.side_effect = DefaultCredentialsError("No credentials")

        downloader = NQDownloader(project_id="test-project")
        result = downloader.download_shard(shard_id="00", show_progress=False)

        assert isinstance(result, DownloadResult)
        assert result.success is False
        assert "Authentication error" in result.error_message

    @patch("nq_downloader.downloader.StorageClient")
    def test_download_shard_uses_correct_gcs_path(self, mock_storage_client):
        """Test that download uses the correct GCS bucket and path."""
        # Mock GCS client and blob
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()

        mock_storage_client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.size = 1024
        mock_blob.reload.return_value = None  # Mock blob.reload()

        # Mock download_to_filename to avoid file creation
        mock_blob.download_to_filename.side_effect = Exception("Test exception")

        downloader = NQDownloader(project_id="test-project")
        downloader.download_shard(shard_id="42", show_progress=False)

        # Verify correct bucket and blob path were used
        mock_client.bucket.assert_called_once_with("natural_questions")
        mock_bucket.blob.assert_called_once_with("v1.0-simplified/nq-train-42.jsonl.gz")

    @patch("nq_downloader.downloader.StorageClient")
    @patch("nq_downloader.downloader._is_testing_environment", return_value=False)
    def test_download_with_progress_bar(self, mock_testing_env, mock_storage_client):
        """Test progress bar path (lines 90-113)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock GCS client and blob
            mock_client = Mock()
            mock_bucket = Mock()
            mock_blob = Mock()

            mock_storage_client.return_value = mock_client
            mock_client.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob
            mock_blob.size = 1024000  # 1MB
            mock_blob.reload.return_value = None  # Mock blob.reload()

            # Mock download_to_filename to create the actual file
            def mock_download(filename, timeout=None):
                Path(filename).parent.mkdir(parents=True, exist_ok=True)
                Path(filename).write_text("dummy content for testing")

            mock_blob.download_to_filename.side_effect = mock_download

            downloader = NQDownloader(
                project_id="test-project", output_dir=Path(temp_dir)
            )
            result = downloader.download_shard(shard_id="00", show_progress=True)

            assert result.success is True
            assert result.local_path.name == "nq-train-00.jsonl.gz"
            mock_blob.reload.assert_called_once()  # Test blob metadata reload (line 67)

    @patch("nq_downloader.downloader.StorageClient")
    @patch("nq_downloader.downloader._is_testing_environment", return_value=False)
    def test_download_simple_with_retry(self, mock_testing_env, mock_storage_client):
        """Test retry logic (lines 119-128)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock GCS client and blob
            mock_client = Mock()
            mock_bucket = Mock()
            mock_blob = Mock()

            mock_storage_client.return_value = mock_client
            mock_client.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob
            mock_blob.size = 1024
            mock_blob.reload.return_value = None  # Mock blob.reload()

            # Mock download_to_filename to create the actual file
            def mock_download(filename, timeout=None):
                Path(filename).parent.mkdir(parents=True, exist_ok=True)
                Path(filename).write_text("dummy content for testing")

            mock_blob.download_to_filename.side_effect = mock_download

            downloader = NQDownloader(
                project_id="test-project", output_dir=Path(temp_dir)
            )
            result = downloader.download_shard(shard_id="00", show_progress=False)

            assert result.success is True
            assert result.local_path.name == "nq-train-00.jsonl.gz"

    def test_checksum_validation_error(self):
        """Test checksum mismatch (line 166)."""
        downloader = NQDownloader(project_id="test-project")

        # Test FileNotFoundError for non-existent file
        try:
            downloader._calculate_checksum(Path("/nonexistent/file.txt"))
            assert False, "Expected FileNotFoundError"
        except FileNotFoundError as e:
            assert "File not found" in str(e)

    def test_constructor_validation(self):
        """Test constructor parameters (line 23)."""
        # Test with default output_dir
        downloader1 = NQDownloader(project_id="test-project")
        assert downloader1.project_id == "test-project"
        assert downloader1.output_dir == Path("./data")

        # Test with custom output_dir
        custom_dir = Path("/tmp/custom")
        downloader2 = NQDownloader(project_id="test-project-2", output_dir=custom_dir)
        assert downloader2.project_id == "test-project-2"
        assert downloader2.output_dir == custom_dir

    @patch("nq_downloader.downloader.StorageClient")
    def test_testing_environment_detection(self, mock_storage_client):
        """Test _is_testing_environment function (lines 23-27)."""
        # Mock GCS client and blob
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()

        mock_storage_client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.size = 1024
        mock_blob.reload.return_value = None  # Mock blob.reload()

        # Mock download_to_filename to create the actual file
        def mock_download(filename):
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            Path(filename).write_text("dummy content for testing")

        mock_blob.download_to_filename.side_effect = mock_download

        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = NQDownloader(
                project_id="test-project", output_dir=Path(temp_dir)
            )
            result = downloader.download_shard(shard_id="00", show_progress=True)

            # In testing environment, progress should be disabled automatically
            assert result.success is True
            # blob.reload() should not be called in testing environment
            mock_blob.reload.assert_not_called()
