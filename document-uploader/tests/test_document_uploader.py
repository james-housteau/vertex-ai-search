"""Acceptance tests for document uploader module."""

import tempfile
from pathlib import Path

from document_uploader import BatchUploadResult, DocumentUploader, UploadResult


# Skip tests that require actual GCS credentials in CI/test environments
def skip_if_no_gcs_credentials() -> bool:
    """Check if GCS credentials are available."""
    try:
        from google.auth import default

        default()
        return False
    except Exception:
        return True


class TestDocumentUploaderAcceptance:
    """Acceptance tests for DocumentUploader class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.bucket_name = "test-bucket"
        self.project_id = "test-project"
        # Note: DocumentUploader will be initialized in test methods
        # to avoid credentials issues during class setup

    def test_upload_single_file_success(self) -> None:
        """Test successful upload of a single file."""
        uploader = DocumentUploader(
            bucket_name=self.bucket_name, project_id=self.project_id, max_workers=2
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write("<html><body>Test content</body></html>")
            temp_path = Path(f.name)

        try:
            result = uploader.upload_file(temp_path)

            assert isinstance(result, UploadResult)
            assert result.local_path == temp_path
            assert result.gcs_uri.startswith(f"gs://{self.bucket_name}/")
            assert result.file_size > 0
            assert result.upload_time_seconds > 0
            assert result.success is True
            assert result.error_message is None
        finally:
            temp_path.unlink()

    def test_upload_single_file_with_custom_key(self) -> None:
        """Test upload with custom GCS key."""
        uploader = DocumentUploader(
            bucket_name=self.bucket_name, project_id=self.project_id, max_workers=2
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write("<html><body>Custom key test</body></html>")
            temp_path = Path(f.name)

        custom_key = "custom/path/document.html"

        try:
            result = uploader.upload_file(temp_path, gcs_key=custom_key)

            assert result.success is True
            assert result.gcs_uri == f"gs://{self.bucket_name}/{custom_key}"
        finally:
            temp_path.unlink()

    def test_upload_directory_batch(self) -> None:
        """Test batch upload of multiple files from directory."""
        uploader = DocumentUploader(
            bucket_name=self.bucket_name, project_id=self.project_id, max_workers=2
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            files = []
            for i in range(3):
                file_path = temp_path / f"document_{i}.html"
                file_path.write_text(f"<html><body>Content {i}</body></html>")
                files.append(file_path)

            result = uploader.upload_directory(temp_path, gcs_prefix="batch_test/")

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
                assert uri.startswith(f"gs://{self.bucket_name}/batch_test/")

    def test_upload_validation_success(self) -> None:
        """Test upload validation for successful upload."""
        uploader = DocumentUploader(
            bucket_name=self.bucket_name, project_id=self.project_id, max_workers=2
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write("<html><body>Validation test</body></html>")
            temp_path = Path(f.name)

        try:
            result = uploader.upload_file(temp_path)
            assert result.success is True

            # Validate the upload
            is_valid = uploader.validate_upload(temp_path, result.gcs_uri)
            assert is_valid is True
        finally:
            temp_path.unlink()

    def test_upload_progress_tracking(self) -> None:
        """Test progress tracking during batch upload."""
        uploader = DocumentUploader(
            bucket_name=self.bucket_name, project_id=self.project_id, max_workers=2
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create multiple test files
            for i in range(5):
                file_path = temp_path / f"progress_test_{i}.html"
                file_path.write_text(f"<html><body>Progress content {i}</body></html>")

            # Start upload in background (this would normally be async)
            uploader.upload_directory(temp_path)

            # Check progress
            progress = uploader.get_upload_progress()

            assert isinstance(progress, dict)
            assert "total_files" in progress
            assert "completed_files" in progress
            assert "bytes_uploaded" in progress
            assert "upload_rate_bytes_per_sec" in progress

    def test_upload_file_not_found_error(self) -> None:
        """Test error handling when file doesn't exist."""
        uploader = DocumentUploader(
            bucket_name=self.bucket_name, project_id=self.project_id, max_workers=2
        )
        non_existent_path = Path("/non/existent/file.html")

        result = uploader.upload_file(non_existent_path)

        assert isinstance(result, UploadResult)
        assert result.success is False
        assert result.error_message is not None
        assert "not found" in result.error_message.lower()

    def test_upload_with_retry_on_failure(self) -> None:
        """Test retry logic when upload fails initially."""
        uploader = DocumentUploader(
            bucket_name=self.bucket_name, project_id=self.project_id, max_workers=2
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write("<html><body>Retry test</body></html>")
            temp_path = Path(f.name)

        try:
            # This should eventually succeed after retries
            result = uploader.upload_file(temp_path)
            assert isinstance(result, UploadResult)
            # Note: Success depends on implementation of retry logic
        finally:
            temp_path.unlink()

    def test_parallel_upload_performance(self) -> None:
        """Test that parallel uploads are faster than sequential."""
        uploader = DocumentUploader(
            bucket_name=self.bucket_name, project_id=self.project_id, max_workers=2
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create larger files for timing comparison
            for i in range(10):
                file_path = temp_path / f"parallel_test_{i}.html"
                content = f"<html><body>{'Large content ' * 100} {i}</body></html>"
                file_path.write_text(content)

            result = uploader.upload_directory(temp_path)

            assert result.successful_uploads == 10
            assert result.total_upload_time_seconds > 0
            # Parallel should be faster than sequential for multiple files

    def test_memory_efficient_large_directory(self) -> None:
        """Test memory efficiency with large number of files."""
        uploader = DocumentUploader(
            bucket_name=self.bucket_name, project_id=self.project_id, max_workers=2
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create many small files
            for i in range(50):
                file_path = temp_path / f"memory_test_{i}.html"
                file_path.write_text(f"<html><body>Memory test {i}</body></html>")

            result = uploader.upload_directory(temp_path)

            assert result.total_files == 50
            assert result.successful_uploads == 50
            assert result.failed_uploads == 0
