"""Test cases for NQ Downloader CLI commands."""

import os
from pathlib import Path
from unittest.mock import Mock, patch

from click.testing import CliRunner
from nq_downloader.downloader import DownloadResult
from nq_downloader.main import cli, main


class TestCLI:
    """Test CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_cli_group_help(self):
        """Test CLI group shows help text."""
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Natural Questions dataset downloader" in result.output

    def test_cli_version_option(self):
        """Test version option displays correctly."""
        result = self.runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_download_command_help(self):
        """Test download command help."""
        result = self.runner.invoke(cli, ["download", "--help"])
        assert result.exit_code == 0
        assert "Download a shard" in result.output

    def test_validate_command_help(self):
        """Test validate command help."""
        result = self.runner.invoke(cli, ["validate", "--help"])
        assert result.exit_code == 0
        assert "Validate a downloaded" in result.output

    def test_status_command_help(self):
        """Test status command help."""
        result = self.runner.invoke(cli, ["status", "--help"])
        assert result.exit_code == 0
        assert "Display application status" in result.output


class TestDownloadCommand:
    """Test download command functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("nq_downloader.main.NQDownloader")
    def test_download_success(self, mock_downloader_class):
        """Test successful download."""
        # Setup mock
        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader

        success_result = DownloadResult(
            local_path=Path("./data/nq-train-00.jsonl.gz"),
            file_size=1024000,
            download_time_seconds=2.5,
            checksum="abcd1234567890ef" * 2,  # 32 char checksum
            success=True,
        )
        mock_downloader.download_shard.return_value = success_result

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                cli, ["download", "--project-id", "test-project", "--shard", "00"]
            )

        assert result.exit_code == 0
        assert "Download completed successfully" in result.output
        assert "Download Summary" in result.output
        mock_downloader.download_shard.assert_called_once_with(
            shard_id="00", show_progress=True
        )

    @patch("nq_downloader.main.NQDownloader")
    def test_download_with_no_progress_flag(self, mock_downloader_class):
        """Test download with no-progress flag."""
        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader

        success_result = DownloadResult(
            local_path=Path("./data/nq-train-01.jsonl.gz"),
            file_size=2048000,
            download_time_seconds=1.5,
            checksum="efgh5678901234ab" * 2,
            success=True,
        )
        mock_downloader.download_shard.return_value = success_result

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                cli,
                [
                    "download",
                    "--project-id",
                    "test-project",
                    "--shard",
                    "01",
                    "--no-progress",
                ],
            )

        assert result.exit_code == 0
        mock_downloader.download_shard.assert_called_once_with(
            shard_id="01", show_progress=False
        )

    @patch("nq_downloader.main.NQDownloader")
    def test_download_failure(self, mock_downloader_class):
        """Test download failure scenario."""
        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader

        failure_result = DownloadResult(
            local_path=Path("./data/nq-train-00.jsonl.gz"),
            file_size=0,
            download_time_seconds=0.1,
            checksum="",
            success=False,
            error_message="Network timeout",
        )
        mock_downloader.download_shard.return_value = failure_result

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                cli, ["download", "--project-id", "test-project"]
            )

        assert result.exit_code == 1
        assert "Download failed: Network timeout" in result.output

    @patch("nq_downloader.main.NQDownloader")
    def test_download_exception(self, mock_downloader_class):
        """Test download command with exception."""
        mock_downloader_class.side_effect = Exception("GCS connection failed")

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                cli, ["download", "--project-id", "test-project"]
            )

        assert result.exit_code == 1
        assert "GCS connection failed" in result.output

    def test_download_missing_project_id(self):
        """Test download without required project ID."""
        result = self.runner.invoke(cli, ["download"])
        assert result.exit_code == 2
        assert "Missing option" in result.output

    @patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "env-project-id"})
    @patch("nq_downloader.main.NQDownloader")
    def test_download_project_id_from_env(self, mock_downloader_class):
        """Test download using project ID from environment."""
        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader

        success_result = DownloadResult(
            local_path=Path("./data/nq-train-00.jsonl.gz"),
            file_size=1024,
            download_time_seconds=1.0,
            checksum="abc123def456" * 2,
            success=True,
        )
        mock_downloader.download_shard.return_value = success_result

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ["download"])

        assert result.exit_code == 0
        mock_downloader_class.assert_called_once()
        args, kwargs = mock_downloader_class.call_args
        assert kwargs["project_id"] == "env-project-id"  # project_id from env

    @patch("nq_downloader.main.NQDownloader")
    def test_download_custom_output_dir(self, mock_downloader_class):
        """Test download with custom output directory."""
        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader

        success_result = DownloadResult(
            local_path=Path("./custom/nq-train-00.jsonl.gz"),
            file_size=1024,
            download_time_seconds=1.0,
            checksum="custom123" * 8,
            success=True,
        )
        mock_downloader.download_shard.return_value = success_result

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                cli,
                [
                    "download",
                    "--project-id",
                    "test-project",
                    "--output-dir",
                    "./custom",
                ],
            )

        assert result.exit_code == 0
        mock_downloader_class.assert_called_once()
        args, kwargs = mock_downloader_class.call_args
        assert kwargs["output_dir"] == Path("./custom")  # output_dir


class TestValidateCommand:
    """Test validate command functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_validate_existing_file(self):
        """Test validate command with existing file."""
        with self.runner.isolated_filesystem():
            # Create a test file
            test_file = Path("test.gz")
            test_file.write_bytes(b"test content")

            with patch("nq_downloader.main.NQDownloader") as mock_class:
                mock_downloader = Mock()
                mock_class.return_value = mock_downloader
                mock_downloader._calculate_checksum.return_value = "abc123def456"

                result = self.runner.invoke(cli, ["validate", str(test_file)])

        assert result.exit_code == 0
        assert "File exists" in result.output
        assert "Checksum: abc123def456" in result.output

    def test_validate_nonexistent_file(self):
        """Test validate command with non-existent file."""
        result = self.runner.invoke(cli, ["validate", "nonexistent.gz"])
        assert result.exit_code == 2
        assert "does not exist" in result.output

    def test_validate_wrong_extension_warning(self):
        """Test validate command shows warning for wrong file extension."""
        with self.runner.isolated_filesystem():
            # Create a test file with wrong extension
            test_file = Path("test.txt")
            test_file.write_text("test content")

            with patch("nq_downloader.main.NQDownloader") as mock_class:
                mock_downloader = Mock()
                mock_class.return_value = mock_downloader
                mock_downloader._calculate_checksum.return_value = "checksum123"

                result = self.runner.invoke(cli, ["validate", str(test_file)])

        assert result.exit_code == 0
        assert "Warning: Expected .gz file" in result.output

    def test_validate_checksum_calculation_error(self):
        """Test validate command when checksum calculation fails."""
        with self.runner.isolated_filesystem():
            test_file = Path("test.gz")
            test_file.write_bytes(b"test content")

            with patch("nq_downloader.main.NQDownloader") as mock_class:
                mock_downloader = Mock()
                mock_class.return_value = mock_downloader
                mock_downloader._calculate_checksum.side_effect = Exception("IO error")

                result = self.runner.invoke(cli, ["validate", str(test_file)])

        assert result.exit_code == 1
        assert "Checksum calculation failed" in result.output


class TestStatusCommand:
    """Test status command functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_status_basic_output(self):
        """Test status command shows basic information."""
        result = self.runner.invoke(cli, ["status"])

        assert result.exit_code == 0
        assert "NQ Downloader Status" in result.output
        assert "Environment Information" in result.output
        assert "Version" in result.output
        assert "0.1.0" in result.output
        assert "Python Path" in result.output

    @patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "status-test-project"})
    def test_status_with_project_env_var(self):
        """Test status command shows project ID from environment."""
        result = self.runner.invoke(cli, ["status"])

        assert result.exit_code == 0
        assert "GOOGLE_CLOUD_PROJECT" in result.output
        assert "status-test-project" in result.output

    @patch.dict(os.environ, {}, clear=True)
    def test_status_without_project_env_var(self):
        """Test status command when project ID not set."""
        result = self.runner.invoke(cli, ["status"])

        assert result.exit_code == 0
        assert "GOOGLE_CLOUD_PROJECT" in result.output
        assert "Not set" in result.output

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/path/to/creds.json"})
    def test_status_with_credentials_path(self):
        """Test status command shows credentials path."""
        result = self.runner.invoke(cli, ["status"])

        assert result.exit_code == 0
        assert "GOOGLE_APPLICATION_CREDENTIALS" in result.output
        assert "/path/to/creds.json" in result.output

    @patch.dict(os.environ, {}, clear=True)
    def test_status_without_credentials_path(self):
        """Test status command when credentials not explicitly set."""
        result = self.runner.invoke(cli, ["status"])

        assert result.exit_code == 0
        assert "GOOGLE_APPLICATION_CREDENTIALS" in result.output
        assert "Using default credentials" in result.output


class TestMainEntryPoint:
    """Test main entry point."""

    @patch("nq_downloader.main.cli")
    def test_main_calls_cli(self, mock_cli):
        """Test main function calls CLI."""
        main()
        mock_cli.assert_called_once()
