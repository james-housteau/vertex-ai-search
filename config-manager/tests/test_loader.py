"""Tests for config_manager.loader module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from config_manager.loader import (
    apply_env_overrides,
    load_config,
    load_yaml_file,
    merge_configs,
)
from config_manager.models import AppConfig


class TestLoadYamlFile:
    """Test YAML file loading functionality."""

    def test_load_existing_file(self) -> None:
        """Test loading an existing YAML file."""
        data = {"app_name": "test", "debug": True}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(data, f)
            temp_path = Path(f.name)

        try:
            result = load_yaml_file(temp_path)
            assert result == data
        finally:
            temp_path.unlink()

    def test_load_nonexistent_file(self) -> None:
        """Test loading a file that doesn't exist."""
        nonexistent_path = Path("/nonexistent/file.yaml")

        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            load_yaml_file(nonexistent_path)

    def test_load_empty_file(self) -> None:
        """Test loading an empty YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")  # Empty file
            temp_path = Path(f.name)

        try:
            result = load_yaml_file(temp_path)
            assert result == {}
        finally:
            temp_path.unlink()

    def test_load_invalid_yaml(self) -> None:
        """Test loading invalid YAML content."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")  # Invalid YAML
            temp_path = Path(f.name)

        try:
            with pytest.raises(yaml.YAMLError, match="Invalid YAML"):
                load_yaml_file(temp_path)
        finally:
            temp_path.unlink()


class TestMergeConfigs:
    """Test configuration merging functionality."""

    def test_merge_simple_configs(self) -> None:
        """Test merging simple configuration dictionaries."""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}

        result = merge_configs(base, override)
        expected = {"a": 1, "b": 3, "c": 4}

        assert result == expected

    def test_merge_nested_configs(self) -> None:
        """Test merging nested configuration dictionaries."""
        base = {"server": {"host": "localhost", "port": 8000}, "debug": False}
        override = {
            "server": {"port": 9000, "timeout": 30},
            "logging": {"level": "DEBUG"},
        }

        result = merge_configs(base, override)
        expected = {
            "server": {"host": "localhost", "port": 9000, "timeout": 30},
            "debug": False,
            "logging": {"level": "DEBUG"},
        }

        assert result == expected

    def test_merge_preserves_original(self) -> None:
        """Test that merging preserves original dictionaries."""
        base = {"a": 1}
        override = {"b": 2}

        merge_configs(base, override)

        # Original dictionaries should be unchanged
        assert base == {"a": 1}
        assert override == {"b": 2}


class TestApplyEnvOverrides:
    """Test environment variable override functionality."""

    def test_apply_env_overrides_basic(self) -> None:
        """Test applying basic environment variable overrides."""
        config = {"debug": False, "port": 8000}

        with patch.dict(os.environ, {"CONFIG_DEBUG": "true", "CONFIG_PORT": "9000"}):
            result = apply_env_overrides(config)

        expected = {"debug": True, "port": 9000}
        assert result == expected

    def test_apply_env_overrides_boolean_conversion(self) -> None:
        """Test boolean conversion in environment overrides."""
        config = {"feature1": False, "feature2": True}

        with patch.dict(
            os.environ, {"CONFIG_FEATURE1": "true", "CONFIG_FEATURE2": "false"}
        ):
            result = apply_env_overrides(config)

        expected = {"feature1": True, "feature2": False}
        assert result == expected

    def test_apply_env_overrides_string_values(self) -> None:
        """Test string value handling in environment overrides."""
        config = {"log_level": "INFO", "host": "localhost"}

        with patch.dict(
            os.environ, {"CONFIG_LOG_LEVEL": "DEBUG", "CONFIG_HOST": "0.0.0.0"}
        ):
            result = apply_env_overrides(config)

        expected = {"log_level": "DEBUG", "host": "0.0.0.0"}
        assert result == expected

    def test_apply_env_overrides_custom_prefix(self) -> None:
        """Test environment overrides with custom prefix."""
        config = {"debug": False}

        with patch.dict(os.environ, {"MYAPP_DEBUG": "true"}):
            result = apply_env_overrides(config, prefix="MYAPP_")

        expected = {"debug": True}
        assert result == expected

    def test_apply_env_overrides_no_relevant_vars(self) -> None:
        """Test when no relevant environment variables exist."""
        config = {"debug": False, "port": 8000}

        with patch.dict(os.environ, {"OTHER_VAR": "value"}):
            result = apply_env_overrides(config)

        assert result == config

    def test_apply_env_preserves_original(self) -> None:
        """Test that applying env overrides preserves original config."""
        config = {"debug": False}

        with patch.dict(os.environ, {"CONFIG_DEBUG": "true"}):
            apply_env_overrides(config)

        # Original should be unchanged
        assert config == {"debug": False}


class TestLoadConfig:
    """Test complete configuration loading functionality."""

    def test_load_config_integration(self) -> None:
        """Test complete configuration loading with temporary files."""
        # Create temporary config files
        defaults_data = {
            "app_name": "test-app",
            "debug": False,
            "port": 8000,
            "timeout": 30,
        }

        dev_data = {"debug": True, "port": 8001}

        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # Write config files
            with open(config_dir / "defaults.yaml", "w") as f:
                yaml.dump(defaults_data, f)

            with open(config_dir / "development.yaml", "w") as f:
                yaml.dump(dev_data, f)

            # Test loading
            with patch.dict(os.environ, {"CONFIG_TIMEOUT": "60"}):
                config = load_config("development", config_dir)

            assert isinstance(config, AppConfig)
            assert config.app_name == "test-app"
            assert config.debug is True  # Overridden by environment
            assert config.port == 8001  # Overridden by dev config
            assert config.timeout == 60  # Overridden by env var

    def test_load_config_missing_defaults(self) -> None:
        """Test loading config when defaults file is missing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            with pytest.raises(FileNotFoundError, match="Configuration file not found"):
                load_config("development", config_dir)

    def test_load_config_missing_environment(self) -> None:
        """Test loading config when environment file is missing."""
        defaults_data = {"app_name": "test"}

        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            with open(config_dir / "defaults.yaml", "w") as f:
                yaml.dump(defaults_data, f)

            with pytest.raises(FileNotFoundError, match="Configuration file not found"):
                load_config("development", config_dir)

    def test_load_config_without_env_vars(self) -> None:
        """Test loading config without applying environment variables."""
        defaults_data = {"debug": False}
        dev_data = {"port": 8001}

        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            with open(config_dir / "defaults.yaml", "w") as f:
                yaml.dump(defaults_data, f)

            with open(config_dir / "development.yaml", "w") as f:
                yaml.dump(dev_data, f)

            with patch.dict(os.environ, {"CONFIG_DEBUG": "true"}):
                config = load_config("development", config_dir, apply_env_vars=False)

            # Environment variable should not be applied
            assert config.debug is False
            assert config.port == 8001

    def test_load_config_validation_error(self) -> None:
        """Test loading config with invalid data."""
        defaults_data = {"port": "invalid"}  # Should be int

        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            with open(config_dir / "defaults.yaml", "w") as f:
                yaml.dump(defaults_data, f)

            with open(config_dir / "development.yaml", "w") as f:
                yaml.dump({}, f)

            with pytest.raises(ValueError, match="Configuration validation failed"):
                load_config("development", config_dir)
