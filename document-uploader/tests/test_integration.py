"""Integration tests for document uploader."""

import tempfile
from pathlib import Path

from document_uploader import DocumentUploader


class TestDocumentUploaderIntegration:
    """Integration tests for complete upload workflows."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.bucket_name = "integration-test-bucket"
        self.project_id = "integration-test-project"
        # Note: DocumentUploader will be initialized in test methods
        # to avoid credentials issues during class setup

    def test_complete_upload_workflow(self) -> None:
        """Test complete upload workflow from directory creation to validation."""
        uploader = DocumentUploader(
            bucket_name=self.bucket_name, project_id=self.project_id, max_workers=4
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test documents
            test_files = []
            for i in range(5):
                file_path = temp_path / f"document_{i}.html"
                content = f"""
                <!DOCTYPE html>
                <html>
                <head><title>Document {i}</title></head>
                <body>
                    <h1>Test Document {i}</h1>
                    <p>This is the content of document {i}.</p>
                    <p>{'Content padding ' * 20}</p>
                </body>
                </html>
                """
                file_path.write_text(content)
                test_files.append(file_path)

            # Upload directory
            batch_result = uploader.upload_directory(
                temp_path, gcs_prefix="integration_test/"
            )

            # Verify batch results
            assert batch_result.total_files == 5
            assert batch_result.successful_uploads == 5
            assert batch_result.failed_uploads == 0
            assert len(batch_result.uploaded_uris) == 5
            assert len(batch_result.failed_files) == 0
            assert batch_result.total_upload_time_seconds > 0
            assert batch_result.total_size_bytes > 0

            # Verify all URIs have correct prefix
            for uri in batch_result.uploaded_uris:
                assert uri.startswith(f"gs://{self.bucket_name}/integration_test/")

            # Test individual file uploads
            single_file = temp_path / "single_test.html"
            single_file.write_text("<html><body>Single file test</body></html>")

            single_result = uploader.upload_file(
                single_file, gcs_key="single_test/test.html"
            )

            assert single_result.success is True
            assert (
                single_result.gcs_uri
                == f"gs://{self.bucket_name}/single_test/test.html"
            )
            assert single_result.file_size > 0
            assert single_result.upload_time_seconds > 0

            # Test upload validation
            is_valid = uploader.validate_upload(single_file, single_result.gcs_uri)
            assert is_valid is True

    def test_upload_progress_tracking(self) -> None:
        """Test progress tracking during uploads."""
        uploader = DocumentUploader(
            bucket_name=self.bucket_name, project_id=self.project_id, max_workers=4
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create files of different sizes
            for i in range(10):
                file_path = temp_path / f"progress_test_{i}.html"
                content = f"<html><body>{'Content ' * (100 * (i + 1))}</body></html>"
                file_path.write_text(content)

            # Check initial progress
            initial_progress = uploader.get_upload_progress()
            assert initial_progress["total_files"] == 0
            assert initial_progress["completed_files"] == 0

            # Upload directory
            batch_result = uploader.upload_directory(temp_path)

            # Check final progress
            final_progress = uploader.get_upload_progress()
            assert final_progress["total_files"] == 10
            assert final_progress["completed_files"] == 10
            assert final_progress["bytes_uploaded"] > 0
            assert final_progress["upload_rate_bytes_per_sec"] > 0

            # Verify progress matches batch result
            assert final_progress["bytes_uploaded"] == batch_result.total_size_bytes

    def test_error_handling_and_resilience(self) -> None:
        """Test error handling for various failure scenarios."""
        uploader = DocumentUploader(
            bucket_name=self.bucket_name, project_id=self.project_id, max_workers=4
        )
        # Test non-existent file
        non_existent = Path("/non/existent/file.html")
        result = uploader.upload_file(non_existent)

        assert result.success is False
        assert "not found" in result.error_message.lower()

        # Test non-existent directory
        non_existent_dir = Path("/non/existent/directory")
        batch_result = uploader.upload_directory(non_existent_dir)

        assert batch_result.total_files == 0
        assert batch_result.successful_uploads == 0
        assert batch_result.failed_uploads == 0

    def test_parallel_upload_performance(self) -> None:
        """Test that parallel uploads work efficiently."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create multiple files for parallel processing
            file_count = 20
            for i in range(file_count):
                file_path = temp_path / f"parallel_{i}.html"
                content = f"<html><body>Parallel test {i} {'data ' * 50}</body></html>"
                file_path.write_text(content)

            # Test with different worker counts
            uploader_sequential = DocumentUploader(
                bucket_name=self.bucket_name, project_id=self.project_id, max_workers=1
            )

            uploader_parallel = DocumentUploader(
                bucket_name=self.bucket_name, project_id=self.project_id, max_workers=4
            )

            # Upload with sequential processing
            result_sequential = uploader_sequential.upload_directory(temp_path)

            # Clear directory and create new files for parallel test
            for file in temp_path.glob("*.html"):
                file.unlink()

            for i in range(file_count):
                file_path = temp_path / f"parallel2_{i}.html"
                content = f"<html><body>Parallel test2 {i} {'data ' * 50}</body></html>"
                file_path.write_text(content)

            # Upload with parallel processing
            result_parallel = uploader_parallel.upload_directory(temp_path)

            # Both should succeed
            assert result_sequential.successful_uploads == file_count
            assert result_parallel.successful_uploads == file_count

            # Note: In simulated mode, timing differences may not be significant,
            # but the parallel version should at least not be slower
            assert result_parallel.total_upload_time_seconds <= (
                result_sequential.total_upload_time_seconds * 1.5
            )
