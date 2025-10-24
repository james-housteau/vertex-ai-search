"""Tests for main CLI module."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from click.testing import CliRunner

from document_uploader.main import main, upload_file, upload_directory
from document_uploader.uploader import UploadResult, BatchUploadResult


class TestCLIMain:
    """Test cases for CLI main functions."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_main_group_help(self) -> None:
        """Test main group shows help."""
        result = self.runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Document uploader for Vertex AI search functionality" in result.output

    @patch("document_uploader.main.DocumentUploader")
    def test_upload_file_success(self, mock_uploader_class: Mock) -> None:
        """Test successful single file upload."""
        # Mock the uploader instance
        mock_uploader = Mock()
        mock_uploader_class.return_value = mock_uploader

        # Mock successful upload result
        mock_result = UploadResult(
            local_path=Path("test.html"),
            gcs_uri="gs://test-bucket/test.html",
            file_size=100,
            upload_time_seconds=1.0,
            success=True,
        )
        mock_uploader.upload_file.return_value = mock_result

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write("<html><body>Test</body></html>")
            temp_path = Path(f.name)

        try:
            result = self.runner.invoke(
                upload_file,
                [
                    str(temp_path),
                    "--bucket",
                    "test-bucket",
                    "--project",
                    "test-project",
                ],
            )

            assert result.exit_code == 0
            assert "Uploaded" in result.output
            assert "gs://test-bucket/test.html" in result.output

            # Verify uploader was called correctly
            mock_uploader_class.assert_called_once_with(
                bucket_name="test-bucket", project_id="test-project"
            )
            mock_uploader.upload_file.assert_called_once_with(temp_path, gcs_key=None)
        finally:
            temp_path.unlink()

    @patch("document_uploader.main.DocumentUploader")
    def test_upload_file_with_custom_key(self, mock_uploader_class: Mock) -> None:
        """Test single file upload with custom GCS key."""
        mock_uploader = Mock()
        mock_uploader_class.return_value = mock_uploader

        mock_result = UploadResult(
            local_path=Path("test.html"),
            gcs_uri="gs://test-bucket/custom/path/test.html",
            file_size=100,
            upload_time_seconds=1.0,
            success=True,
        )
        mock_uploader.upload_file.return_value = mock_result

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write("<html><body>Test</body></html>")
            temp_path = Path(f.name)

        try:
            result = self.runner.invoke(
                upload_file,
                [
                    str(temp_path),
                    "--bucket",
                    "test-bucket",
                    "--project",
                    "test-project",
                    "--gcs-key",
                    "custom/path/test.html",
                ],
            )

            assert result.exit_code == 0
            mock_uploader.upload_file.assert_called_once_with(
                temp_path, gcs_key="custom/path/test.html"
            )
        finally:
            temp_path.unlink()

    @patch("document_uploader.main.DocumentUploader")
    def test_upload_file_failure(self, mock_uploader_class: Mock) -> None:
        """Test failed single file upload."""
        mock_uploader = Mock()
        mock_uploader_class.return_value = mock_uploader

        mock_result = UploadResult(
            local_path=Path("test.html"),
            gcs_uri="gs://test-bucket/test.html",
            file_size=100,
            upload_time_seconds=1.0,
            success=False,
            error_message="Upload failed: Network error",
        )
        mock_uploader.upload_file.return_value = mock_result

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write("<html><body>Test</body></html>")
            temp_path = Path(f.name)

        try:
            result = self.runner.invoke(
                upload_file,
                [
                    str(temp_path),
                    "--bucket",
                    "test-bucket",
                    "--project",
                    "test-project",
                ],
            )

            assert result.exit_code == 0  # CLI doesn't exit with error code
            assert "Failed to upload" in result.output
            assert "Network error" in result.output
        finally:
            temp_path.unlink()

    @patch("document_uploader.main.DocumentUploader")
    def test_upload_directory_success(self, mock_uploader_class: Mock) -> None:
        """Test successful directory upload."""
        mock_uploader = Mock()
        mock_uploader_class.return_value = mock_uploader

        mock_result = BatchUploadResult(
            total_files=3,
            successful_uploads=3,
            failed_uploads=0,
            uploaded_uris=[
                "gs://test-bucket/file1.html",
                "gs://test-bucket/file2.html",
            ],
            failed_files=[],
            total_upload_time_seconds=2.0,
            total_size_bytes=300,
        )
        mock_uploader.upload_directory.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            result = self.runner.invoke(
                upload_directory,
                [
                    str(temp_path),
                    "--bucket",
                    "test-bucket",
                    "--project",
                    "test-project",
                ],
            )

            assert result.exit_code == 0
            assert "Uploaded 3/3 files" in result.output

            mock_uploader_class.assert_called_once_with(
                bucket_name="test-bucket", project_id="test-project", max_workers=4
            )
            mock_uploader.upload_directory.assert_called_once_with(
                temp_path, gcs_prefix=""
            )

    @patch("document_uploader.main.DocumentUploader")
    def test_upload_directory_with_options(self, mock_uploader_class: Mock) -> None:
        """Test directory upload with prefix and custom workers."""
        mock_uploader = Mock()
        mock_uploader_class.return_value = mock_uploader

        mock_result = BatchUploadResult(
            total_files=2,
            successful_uploads=2,
            failed_uploads=0,
            uploaded_uris=["gs://test-bucket/docs/file1.html"],
            failed_files=[],
            total_upload_time_seconds=1.0,
            total_size_bytes=200,
        )
        mock_uploader.upload_directory.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            result = self.runner.invoke(
                upload_directory,
                [
                    str(temp_path),
                    "--bucket",
                    "test-bucket",
                    "--project",
                    "test-project",
                    "--prefix",
                    "docs/",
                    "--workers",
                    "8",
                ],
            )

            assert result.exit_code == 0
            mock_uploader_class.assert_called_once_with(
                bucket_name="test-bucket", project_id="test-project", max_workers=8
            )
            mock_uploader.upload_directory.assert_called_once_with(
                temp_path, gcs_prefix="docs/"
            )

    @patch("document_uploader.main.DocumentUploader")
    def test_upload_directory_with_failures(self, mock_uploader_class: Mock) -> None:
        """Test directory upload with some failures."""
        mock_uploader = Mock()
        mock_uploader_class.return_value = mock_uploader

        mock_result = BatchUploadResult(
            total_files=5,
            successful_uploads=3,
            failed_uploads=2,
            uploaded_uris=[
                "gs://test-bucket/file1.html",
                "gs://test-bucket/file2.html",
            ],
            failed_files=["/path/to/failed1.html", "/path/to/failed2.html"],
            total_upload_time_seconds=3.0,
            total_size_bytes=300,
        )
        mock_uploader.upload_directory.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            result = self.runner.invoke(
                upload_directory,
                [
                    str(temp_path),
                    "--bucket",
                    "test-bucket",
                    "--project",
                    "test-project",
                ],
            )

            assert result.exit_code == 0
            assert "Uploaded 3/5 files" in result.output
            assert "Failed uploads:" in result.output
            assert "failed1.html" in result.output
            assert "failed2.html" in result.output

    def test_upload_file_missing_args(self) -> None:
        """Test upload file command with missing required arguments."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write("<html><body>Test</body></html>")
            temp_path = Path(f.name)

        try:
            result = self.runner.invoke(upload_file, [str(temp_path)])
            assert result.exit_code != 0
            assert "Missing option '--bucket'" in result.output
        finally:
            temp_path.unlink()

    def test_upload_directory_missing_args(self) -> None:
        """Test upload directory command with missing required arguments."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(upload_directory, [temp_dir])
            assert result.exit_code != 0
            assert "Missing option '--bucket'" in result.output
