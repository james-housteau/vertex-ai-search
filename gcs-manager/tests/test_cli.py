"""Tests for GCS Manager CLI."""

from click.testing import CliRunner
from unittest.mock import patch, Mock

from gcs_manager.main import main
from gcs_manager.models import BucketResult


class TestCLI:
    """Test CLI commands."""

    def test_main_command_help(self):
        """Test main command shows help."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "GCS Manager" in result.output
        assert "create" in result.output
        assert "info" in result.output
        assert "delete" in result.output

    @patch("gcs_manager.main.GCSManager")
    def test_create_command_success(self, mock_manager_class):
        """Test create command with successful bucket creation."""
        # Mock successful bucket creation
        mock_manager = Mock()
        mock_result = BucketResult(
            bucket_name="test-bucket",
            bucket_uri="gs://test-bucket",
            region="US",
            created=True,
        )
        mock_manager.create_bucket.return_value = mock_result
        mock_manager_class.return_value = mock_manager

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "create",
                "test-bucket",
                "--project-id",
                "test-project",
                "--region",
                "us",
                "--lifecycle-days",
                "30",
            ],
        )

        assert result.exit_code == 0
        assert "Bucket created successfully" in result.output
        assert "gs://test-bucket" in result.output

    @patch("gcs_manager.main.GCSManager")
    def test_create_command_failure(self, mock_manager_class):
        """Test create command with failed bucket creation."""
        # Mock failed bucket creation
        mock_manager = Mock()
        mock_result = BucketResult(
            bucket_name="test-bucket",
            bucket_uri="",
            region="US",
            created=False,
            error_message="Access denied",
        )
        mock_manager.create_bucket.return_value = mock_result
        mock_manager_class.return_value = mock_manager

        runner = CliRunner()
        result = runner.invoke(
            main, ["create", "test-bucket", "--project-id", "test-project"]
        )

        assert result.exit_code == 0
        assert "Failed to create bucket" in result.output
        assert "Access denied" in result.output

    @patch("gcs_manager.main.GCSManager")
    def test_info_command_success(self, mock_manager_class):
        """Test info command with existing bucket."""
        # Mock bucket info retrieval
        mock_manager = Mock()
        mock_result = BucketResult(
            bucket_name="existing-bucket",
            bucket_uri="gs://existing-bucket",
            region="US-CENTRAL1",
            created=False,
        )
        mock_manager.get_bucket_info.return_value = mock_result
        mock_manager_class.return_value = mock_manager

        runner = CliRunner()
        result = runner.invoke(
            main, ["info", "existing-bucket", "--project-id", "test-project"]
        )

        assert result.exit_code == 0
        assert "existing-bucket" in result.output
        assert "gs://existing-bucket" in result.output
        assert "US-CENTRAL1" in result.output

    @patch("gcs_manager.main.GCSManager")
    def test_info_command_not_found(self, mock_manager_class):
        """Test info command with non-existent bucket."""
        # Mock bucket not found
        mock_manager = Mock()
        mock_manager.get_bucket_info.return_value = None
        mock_manager_class.return_value = mock_manager

        runner = CliRunner()
        result = runner.invoke(
            main, ["info", "nonexistent-bucket", "--project-id", "test-project"]
        )

        assert result.exit_code == 0
        assert "Bucket not found" in result.output

    @patch("gcs_manager.main.GCSManager")
    def test_delete_command_success(self, mock_manager_class):
        """Test delete command with successful deletion."""
        # Mock successful deletion
        mock_manager = Mock()
        mock_manager.delete_bucket.return_value = True
        mock_manager_class.return_value = mock_manager

        runner = CliRunner()
        result = runner.invoke(
            main, ["delete", "test-bucket", "--project-id", "test-project", "--force"]
        )

        assert result.exit_code == 0
        assert "Bucket deleted successfully" in result.output

    @patch("gcs_manager.main.GCSManager")
    def test_delete_command_failure(self, mock_manager_class):
        """Test delete command with failed deletion."""
        # Mock failed deletion
        mock_manager = Mock()
        mock_manager.delete_bucket.return_value = False
        mock_manager_class.return_value = mock_manager

        runner = CliRunner()
        result = runner.invoke(
            main, ["delete", "test-bucket", "--project-id", "test-project", "--force"]
        )

        assert result.exit_code == 0
        assert "Failed to delete bucket" in result.output

    def test_create_command_missing_project_id(self):
        """Test create command requires project-id."""
        runner = CliRunner()
        result = runner.invoke(main, ["create", "test-bucket"])

        assert result.exit_code != 0
        assert "project-id" in result.output or "Missing option" in result.output

    def test_version_option(self):
        """Test version option works."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output
