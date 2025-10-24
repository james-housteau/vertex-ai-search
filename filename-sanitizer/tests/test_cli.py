"""Tests for the CLI module."""

from click.testing import CliRunner
from filename_sanitizer.cli import cli


class TestCLI:
    """Test the CLI interface."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_cli_help(self):
        """Test CLI help message."""
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Cross-platform filename sanitization tool" in result.output

    def test_version(self):
        """Test version command."""
        result = self.runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "filename-sanitizer" in result.output

    def test_sanitize_command(self):
        """Test sanitize command."""
        result = self.runner.invoke(cli, ["sanitize", "file<name>.txt"])
        assert result.exit_code == 0
        assert "Original:" in result.output
        assert "Sanitized:" in result.output
        assert "file_name_.txt" in result.output

    def test_sanitize_with_options(self):
        """Test sanitize command with options."""
        result = self.runner.invoke(
            cli,
            ["sanitize", "file<name>.txt", "--replacement", "-", "--max-length", "20"],
        )
        assert result.exit_code == 0
        assert "file-name-.txt" in result.output

    def test_validate_command_valid(self):
        """Test validate command with valid filename."""
        result = self.runner.invoke(cli, ["validate", "valid_file.txt"])
        assert result.exit_code == 0
        assert " Valid filename" in result.output

    def test_validate_command_invalid(self):
        """Test validate command with invalid filename."""
        result = self.runner.invoke(cli, ["validate", "invalid<file>.txt"])
        assert result.exit_code == 0
        assert " Invalid filename" in result.output
        assert "Issues found:" in result.output

    def test_status_command(self):
        """Test status command."""
        result = self.runner.invoke(cli, ["status"])
        assert result.exit_code == 0
        assert "Filename Sanitizer" in result.output
        assert "Version:" in result.output
        assert "Configuration" in result.output


class TestBatchSanitize:
    """Test batch sanitize functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_batch_sanitize_no_files(self):
        """Test batch sanitize with no matching files."""
        result = self.runner.invoke(cli, ["batch-sanitize", "nonexistent*.txt"])
        assert result.exit_code == 0
        assert "No files found" in result.output

    def test_batch_sanitize_dry_run(self):
        """Test batch sanitize with dry run."""
        with self.runner.isolated_filesystem():
            # Create test files with problematic names
            with open("test<file>.txt", "w") as f:
                f.write("test content")

            result = self.runner.invoke(cli, ["batch-sanitize", "*.txt", "--dry-run"])
            assert result.exit_code == 0
            assert "Dry run:" in result.output

    def test_batch_sanitize_actual_rename(self):
        """Test batch sanitize with actual file renaming."""
        with self.runner.isolated_filesystem():
            # Create test files with problematic names
            with open("test<file>.txt", "w") as f:
                f.write("test content")

            result = self.runner.invoke(cli, ["batch-sanitize", "*.txt"])
            assert result.exit_code == 0

            # Check that the problematic file was renamed
            import os

            files = os.listdir(".")
            assert "test<file>.txt" not in files
            assert any("test_file" in f for f in files)


class TestValidateCommand:
    """Test validate command variations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_validate_empty_filename(self):
        """Test validate with empty filename."""
        result = self.runner.invoke(cli, ["validate", ""])
        assert result.exit_code == 0
        assert " Invalid filename" in result.output
        assert "Empty filename" in result.output

    def test_validate_reserved_name(self):
        """Test validate with Windows reserved name."""
        result = self.runner.invoke(cli, ["validate", "CON.txt"])
        assert result.exit_code == 0
        assert " Invalid filename" in result.output
        assert "reserved name" in result.output

    def test_validate_long_filename(self):
        """Test validate with long filename."""
        long_name = "a" * 300 + ".txt"
        result = self.runner.invoke(cli, ["validate", long_name])
        assert result.exit_code == 0
        assert " Invalid filename" in result.output
        assert "Too long" in result.output

    def test_validate_no_length_check(self):
        """Test validate without length checking."""
        long_name = "a" * 300 + ".txt"
        result = self.runner.invoke(cli, ["validate", long_name, "--no-check-length"])
        # This should still fail due to length, but we're testing the option exists
        assert result.exit_code == 0


class TestSanitizeEdgeCases:
    """Test sanitize command edge cases."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_sanitize_already_valid(self):
        """Test sanitize with already valid filename."""
        result = self.runner.invoke(cli, ["sanitize", "valid_file.txt"])
        assert result.exit_code == 0
        assert "already safe" in result.output

    def test_sanitize_unicode(self):
        """Test sanitize with Unicode characters."""
        result = self.runner.invoke(cli, ["sanitize", "cafe.txt"])
        assert result.exit_code == 0
        assert "cafe.txt" in result.output

    def test_sanitize_no_unicode_normalize(self):
        """Test sanitize with Unicode normalization disabled."""
        result = self.runner.invoke(
            cli, ["sanitize", "cafe.txt", "--no-unicode-normalize"]
        )
        assert result.exit_code == 0
