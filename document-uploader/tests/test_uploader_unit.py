"""Unit tests for document uploader module."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from document_uploader.uploader import DocumentUploader, UploadResult, BatchUploadResult


class TestDocumentUploaderUnit:
    """Unit tests for DocumentUploader class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.bucket_name = "test-bucket"
        self.project_id = "test-project"

        # Mock credentials to not be available for base tests
        with patch("document_uploader.uploader.storage") as mock_storage:
            from google.auth.exceptions import DefaultCredentialsError

            mock_storage.Client.side_effect = DefaultCredentialsError("No credentials")
            self.uploader = DocumentUploader(
                bucket_name=self.bucket_name, project_id=self.project_id, max_workers=2
            )

    def test_init_with_credentials_error(self) -> None:
        """Test initialization when credentials are not available."""
        # When no credentials are available, client should be None
        assert self.uploader.bucket_name == self.bucket_name
        assert self.uploader.project_id == self.project_id
        assert self.uploader.max_workers == 2
        # In test environment, client will be None due to no credentials
        assert self.uploader.client is None
        assert self.uploader.bucket is None

    def test_upload_result_dataclass(self) -> None:
        """Test UploadResult dataclass creation."""
        result = UploadResult(
            local_path=Path("/test/file.html"),
            gcs_uri="gs://bucket/file.html",
            file_size=1024,
            upload_time_seconds=1.5,
            success=True,
        )

        assert result.local_path == Path("/test/file.html")
        assert result.gcs_uri == "gs://bucket/file.html"
        assert result.file_size == 1024
        assert result.upload_time_seconds == 1.5
        assert result.success is True
        assert result.error_message is None

    def test_batch_upload_result_dataclass(self) -> None:
        """Test BatchUploadResult dataclass creation."""
        result = BatchUploadResult(
            total_files=10,
            successful_uploads=8,
            failed_uploads=2,
            uploaded_uris=["gs://bucket/file1.html", "gs://bucket/file2.html"],
            failed_files=["/path/file3.html", "/path/file4.html"],
            total_upload_time_seconds=30.5,
            total_size_bytes=8192,
        )

        assert result.total_files == 10
        assert result.successful_uploads == 8
        assert result.failed_uploads == 2
        assert len(result.uploaded_uris) == 2
        assert len(result.failed_files) == 2
        assert result.total_upload_time_seconds == 30.5
        assert result.total_size_bytes == 8192

    def test_get_upload_progress_initial(self) -> None:
        """Test initial progress state."""
        progress = self.uploader.get_upload_progress()

        assert isinstance(progress, dict)
        assert progress["total_files"] == 0
        assert progress["completed_files"] == 0
        assert progress["bytes_uploaded"] == 0
        assert progress["upload_rate_bytes_per_sec"] == 0.0

    def test_upload_file_not_found(self) -> None:
        """Test upload with non-existent file."""
        non_existent_path = Path("/non/existent/file.html")
        result = self.uploader.upload_file(non_existent_path)

        assert isinstance(result, UploadResult)
        assert result.success is False
        assert result.error_message is not None
        assert "not found" in result.error_message.lower()
        assert result.local_path == non_existent_path
        assert result.gcs_uri == ""
        assert result.file_size == 0
        assert result.upload_time_seconds == 0.0

    def test_upload_file_success_no_credentials(self) -> None:
        """Test successful upload when no credentials available (simulation mode)."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write("<html><body>Test content</body></html>")
            temp_path = Path(f.name)

        try:
            result = self.uploader.upload_file(temp_path)

            assert isinstance(result, UploadResult)
            assert result.success is True
            assert result.error_message is None
            assert result.local_path == temp_path
            assert result.gcs_uri == f"gs://{self.bucket_name}/{temp_path.name}"
            assert result.file_size > 0
            assert result.upload_time_seconds > 0
        finally:
            temp_path.unlink()

    def test_upload_file_with_custom_key(self) -> None:
        """Test upload with custom GCS key."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write("<html><body>Custom key test</body></html>")
            temp_path = Path(f.name)

        custom_key = "custom/path/document.html"

        try:
            result = self.uploader.upload_file(temp_path, gcs_key=custom_key)

            assert result.success is True
            assert result.gcs_uri == f"gs://{self.bucket_name}/{custom_key}"
        finally:
            temp_path.unlink()

    def test_upload_directory_no_credentials(self) -> None:
        """Test directory upload when no credentials available."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test HTML files
            for i in range(3):
                file_path = temp_path / f"document_{i}.html"
                file_path.write_text(f"<html><body>Content {i}</body></html>")

            result = self.uploader.upload_directory(temp_path, gcs_prefix="test/")

            assert isinstance(result, BatchUploadResult)
            assert result.total_files == 3
            assert result.successful_uploads == 3
            assert result.failed_uploads == 0
            assert len(result.uploaded_uris) == 3
            assert len(result.failed_files) == 0
            assert result.total_upload_time_seconds > 0
            assert result.total_size_bytes > 0

            # Verify URIs have correct prefix
            for uri in result.uploaded_uris:
                assert uri.startswith(f"gs://{self.bucket_name}/test/")

    def test_upload_directory_empty(self) -> None:
        """Test directory upload with no HTML files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create non-HTML files that should be ignored
            (temp_path / "readme.txt").write_text("Not an HTML file")

            result = self.uploader.upload_directory(temp_path)

            assert result.total_files == 0
            assert result.successful_uploads == 0
            assert result.failed_uploads == 0
            assert len(result.uploaded_uris) == 0
            assert len(result.failed_files) == 0

    def test_validate_upload_no_credentials(self) -> None:
        """Test upload validation when no credentials available."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write("<html><body>Validation test</body></html>")
            temp_path = Path(f.name)

        try:
            gcs_uri = f"gs://{self.bucket_name}/{temp_path.name}"
            is_valid = self.uploader.validate_upload(temp_path, gcs_uri)
            # Should return True in test mode (no credentials)
            assert is_valid is True
        finally:
            temp_path.unlink()

    def test_validate_upload_file_not_found(self) -> None:
        """Test validation with non-existent local file."""
        non_existent_path = Path("/non/existent/file.html")
        gcs_uri = f"gs://{self.bucket_name}/file.html"

        is_valid = self.uploader.validate_upload(non_existent_path, gcs_uri)
        assert is_valid is False

    @patch("document_uploader.uploader.storage")
    def test_init_with_credentials(self, mock_storage: Mock) -> None:
        """Test initialization when credentials are available."""
        mock_client = Mock()
        mock_bucket = Mock()
        mock_storage.Client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket

        uploader = DocumentUploader("test-bucket", "test-project")

        assert uploader.client == mock_client
        assert uploader.bucket == mock_bucket
        mock_storage.Client.assert_called_once_with(project="test-project")
        mock_client.bucket.assert_called_once_with("test-bucket")

    @patch("document_uploader.uploader.storage")
    def test_upload_file_with_credentials_success(self, mock_storage: Mock) -> None:
        """Test successful upload with actual GCS credentials."""
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()

        mock_storage.Client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        uploader = DocumentUploader("test-bucket", "test-project")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write("<html><body>Test content</body></html>")
            temp_path = Path(f.name)

        try:
            result = uploader.upload_file(temp_path)

            assert result.success is True
            mock_bucket.blob.assert_called_once_with(temp_path.name)
            mock_blob.upload_from_filename.assert_called_once_with(str(temp_path))
        finally:
            temp_path.unlink()

    @patch("document_uploader.uploader.storage")
    def test_upload_file_with_credentials_error(self, mock_storage: Mock) -> None:
        """Test upload failure with GCS credentials."""
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()

        mock_storage.Client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.upload_from_filename.side_effect = Exception("Upload failed")

        uploader = DocumentUploader("test-bucket", "test-project")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write("<html><body>Test content</body></html>")
            temp_path = Path(f.name)

        try:
            result = uploader.upload_file(temp_path)

            assert result.success is False
            assert result.error_message == "Upload failed"
        finally:
            temp_path.unlink()

    @patch("document_uploader.uploader.storage")
    def test_validate_upload_with_credentials(self, mock_storage: Mock) -> None:
        """Test validation with actual GCS credentials."""
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()

        mock_storage.Client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.exists.return_value = True
        mock_blob.size = 100

        uploader = DocumentUploader("test-bucket", "test-project")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write("<html><body>Test</body></html>")  # Should be ~30 bytes
            temp_path = Path(f.name)

        try:
            # Mock the file size to match
            mock_blob.size = temp_path.stat().st_size

            gcs_uri = f"gs://test-bucket/{temp_path.name}"
            is_valid = uploader.validate_upload(temp_path, gcs_uri)

            assert is_valid is True
            mock_bucket.blob.assert_called_once_with(temp_path.name)
        finally:
            temp_path.unlink()

    @patch("document_uploader.uploader.storage")
    def test_validate_upload_size_mismatch(self, mock_storage: Mock) -> None:
        """Test validation failure due to size mismatch."""
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()

        mock_storage.Client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.exists.return_value = True
        mock_blob.size = 999  # Different from actual file size

        uploader = DocumentUploader("test-bucket", "test-project")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write("<html><body>Test</body></html>")
            temp_path = Path(f.name)

        try:
            gcs_uri = f"gs://test-bucket/{temp_path.name}"
            is_valid = uploader.validate_upload(temp_path, gcs_uri)

            assert is_valid is False
        finally:
            temp_path.unlink()

    @patch("document_uploader.uploader.storage")
    def test_validate_upload_invalid_uri(self, mock_storage: Mock) -> None:
        """Test validation with invalid GCS URI."""
        mock_client = Mock()
        mock_bucket = Mock()

        mock_storage.Client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket

        uploader = DocumentUploader("test-bucket", "test-project")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write("<html><body>Test</body></html>")
            temp_path = Path(f.name)

        try:
            # Invalid URI (wrong bucket)
            gcs_uri = "gs://wrong-bucket/file.html"
            is_valid = uploader.validate_upload(temp_path, gcs_uri)

            assert is_valid is False
        finally:
            temp_path.unlink()
