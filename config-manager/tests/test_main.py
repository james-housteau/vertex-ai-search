"""Tests for config_manager.main CLI module."""

import tempfile
from pathlib import Path

import yaml
from click.testing import CliRunner
from config_manager.main import cli


class TestCLI:
    """Test CLI commands."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    def test_cli_help(self) -> None:
        """Test CLI help command."""
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert (
            "Configuration management for Vertex AI search functionality"
            in result.output
        )

    def test_version_option(self) -> None:
        """Test version option."""
        result = self.runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output


class TestLoadCommand:
    """Test the 'load' command."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    def test_load_with_valid_config(self) -> None:
        """Test loading a valid configuration."""
        defaults_data = {
            "app_name": "test-app",
            "version": "2.0.0",
            "debug": False,
            "log_level": "INFO",
            "host": "localhost",
            "port": 8000,
            "timeout": 30,
        }

        dev_data = {
            "debug": True,
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # Write config files
            with open(config_dir / "defaults.yaml", "w") as f:
                yaml.dump(defaults_data, f)

            with open(config_dir / "development.yaml", "w") as f:
                yaml.dump(dev_data, f)

            result = self.runner.invoke(
                cli,
                [
                    "load",
                    "--environment",
                    "development",
                    "--config-dir",
                    str(config_dir),
                ],
            )

            assert result.exit_code == 0
            assert "Configuration for environment 'development'" in result.output
            assert "App Name: test-app" in result.output
            assert "Version: 2.0.0" in result.output
            assert "Debug: True" in result.output
            assert "Log Level: INFO" in result.output
            assert "Host: localhost" in result.output
            assert "Port: 8000" in result.output

    def test_load_default_environment(self) -> None:
        """Test loading with default environment."""
        defaults_data = {"app_name": "test"}
        dev_data = {}

        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            with open(config_dir / "defaults.yaml", "w") as f:
                yaml.dump(defaults_data, f)

            with open(config_dir / "development.yaml", "w") as f:
                yaml.dump(dev_data, f)

            result = self.runner.invoke(cli, ["load", "--config-dir", str(config_dir)])

            assert result.exit_code == 0
            assert "development" in result.output

    def test_load_missing_config_file(self) -> None:
        """Test loading when config files are missing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            result = self.runner.invoke(cli, ["load", "--config-dir", str(config_dir)])

            assert result.exit_code == 1
            assert "Error:" in result.output

    def test_load_invalid_config(self) -> None:
        """Test loading with invalid configuration."""
        defaults_data = {"port": "invalid"}  # Should be int
        dev_data = {}

        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            with open(config_dir / "defaults.yaml", "w") as f:
                yaml.dump(defaults_data, f)

            with open(config_dir / "development.yaml", "w") as f:
                yaml.dump(dev_data, f)

            result = self.runner.invoke(cli, ["load", "--config-dir", str(config_dir)])

            assert result.exit_code == 1
            assert "Configuration validation error:" in result.output


class TestListEnvironmentsCommand:
    """Test the 'list-environments' command."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    def test_list_environments_with_configs(self) -> None:
        """Test listing environments when config files exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # Create config files
            (config_dir / "defaults.yaml").touch()
            (config_dir / "development.yaml").touch()
            (config_dir / "production.yaml").touch()
            (config_dir / "staging.yaml").touch()

            result = self.runner.invoke(
                cli, ["list-environments", "--config-dir", str(config_dir)]
            )

            assert result.exit_code == 0
            assert "Available environments:" in result.output
            assert "development" in result.output
            assert "production" in result.output
            assert "staging" in result.output
            assert "defaults" not in result.output  # Should exclude defaults

    def test_list_environments_no_configs(self) -> None:
        """Test listing environments when no config files exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            result = self.runner.invoke(
                cli, ["list-environments", "--config-dir", str(config_dir)]
            )

            assert result.exit_code == 0
            assert "No environment configurations found." in result.output

    def test_list_environments_nonexistent_dir(self) -> None:
        """Test listing environments for non-existent directory."""
        result = self.runner.invoke(
            cli, ["list-environments", "--config-dir", "/nonexistent/path"]
        )

        # Click will fail with exit code 2 if the path doesn't exist
        assert result.exit_code == 2


class TestValidateCommand:
    """Test the 'validate' command."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    def test_validate_valid_config(self) -> None:
        """Test validating a valid configuration."""
        defaults_data = {
            "app_name": "test-app",
            "version": "1.0.0",
            "host": "localhost",
            "port": 8000,
        }
        dev_data = {}

        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            with open(config_dir / "defaults.yaml", "w") as f:
                yaml.dump(defaults_data, f)

            with open(config_dir / "development.yaml", "w") as f:
                yaml.dump(dev_data, f)

            result = self.runner.invoke(
                cli,
                [
                    "validate",
                    "--environment",
                    "development",
                    "--config-dir",
                    str(config_dir),
                ],
            )

            assert result.exit_code == 0
            assert " Configuration for 'development' is valid" in result.output
            assert "App: test-app v1.0.0" in result.output
            assert "Host: localhost:8000" in result.output

    def test_validate_invalid_config(self) -> None:
        """Test validating an invalid configuration."""
        defaults_data = {"port": "invalid"}  # Should be int
        dev_data = {}

        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            with open(config_dir / "defaults.yaml", "w") as f:
                yaml.dump(defaults_data, f)

            with open(config_dir / "development.yaml", "w") as f:
                yaml.dump(dev_data, f)

            result = self.runner.invoke(
                cli, ["validate", "--config-dir", str(config_dir)]
            )

            assert result.exit_code == 1
            assert " Validation failed:" in result.output

    def test_validate_missing_config(self) -> None:
        """Test validating when config files are missing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            result = self.runner.invoke(
                cli, ["validate", "--config-dir", str(config_dir)]
            )

            assert result.exit_code == 1
            assert " Error:" in result.output

    def test_validate_default_environment(self) -> None:
        """Test validate with default environment."""
        defaults_data = {"app_name": "test"}
        dev_data = {}

        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            with open(config_dir / "defaults.yaml", "w") as f:
                yaml.dump(defaults_data, f)

            with open(config_dir / "development.yaml", "w") as f:
                yaml.dump(dev_data, f)

            result = self.runner.invoke(
                cli, ["validate", "--config-dir", str(config_dir)]
            )

            assert result.exit_code == 0
            assert "development" in result.output


class TestMainFunction:
    """Test the main entry point."""

    def test_main_function_exists(self) -> None:
        """Test that main function exists and is callable."""
        from config_manager.main import main

        # Just test that it exists and can be imported
        assert callable(main)
