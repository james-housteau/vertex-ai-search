"""Tests for config_manager.models module."""

from pathlib import Path

import pytest
from config_manager.models import AppConfig, ConfigManager, EnvironmentConfig
from pydantic import ValidationError


class TestAppConfig:
    """Test AppConfig Pydantic model."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = AppConfig()

        assert config.app_name == "vertex-ai-search"
        assert config.version == "1.0.0"
        assert config.log_level == "INFO"
        assert config.debug is False
        assert config.timeout == 30
        assert config.host == "0.0.0.0"
        assert config.port == 8000

    def test_custom_values(self) -> None:
        """Test configuration with custom values."""
        config = AppConfig(
            app_name="test-app",
            version="2.0.0",
            debug=True,
            port=9000,
        )

        assert config.app_name == "test-app"
        assert config.version == "2.0.0"
        assert config.port == 9000

    def test_port_validation(self) -> None:
        """Test port number validation."""
        # Valid port
        config = AppConfig(port=8080)
        assert config.port == 8080

        # Invalid port - too low
        with pytest.raises(ValidationError):
            AppConfig(port=1023)

        # Invalid port - too high
        with pytest.raises(ValidationError):
            AppConfig(port=65536)

    def test_timeout_validation(self) -> None:
        """Test timeout validation."""
        # Valid timeout
        config = AppConfig(timeout=60)
        assert config.timeout == 60

        # Invalid timeout - too low
        with pytest.raises(ValidationError):
            AppConfig(timeout=0)

        # Invalid timeout - too high
        with pytest.raises(ValidationError):
            AppConfig(timeout=301)

    def test_config_immutable(self) -> None:
        """Test that configuration is immutable."""
        config = AppConfig()

        # Attempting to set immutable field raises ValidationError
        with pytest.raises(ValidationError):
            config.debug = True

    def test_extra_fields_forbidden(self) -> None:
        """Test that extra fields are not allowed."""
        # Creating AppConfig with invalid field should raise ValidationError
        with pytest.raises(ValidationError):
            AppConfig(invalid_field="value")


class TestEnvironmentConfig:
    """Test EnvironmentConfig model."""

    def test_default_values(self) -> None:
        """Test default environment configuration."""
        config = EnvironmentConfig()

        assert config.environment == "development"
        assert config.config_overrides == {}

    def test_custom_values(self) -> None:
        """Test custom environment configuration."""
        overrides = {"debug": True, "port": 9000}
        config = EnvironmentConfig(environment="production", config_overrides=overrides)

        assert config.environment == "production"
        assert config.config_overrides == overrides

    def test_extra_fields_allowed(self) -> None:
        """Test that extra fields are allowed in EnvironmentConfig."""
        # EnvironmentConfig allows arbitrary extra fields
        config = EnvironmentConfig(custom_field="value")
        assert hasattr(config, "custom_field")


class TestConfigManager:
    """Test ConfigManager class."""

    def test_init_default_config_dir(self) -> None:
        """Test initialization with default config directory."""
        manager = ConfigManager()
        assert manager.config_dir == Path("config")

    def test_init_custom_config_dir(self) -> None:
        """Test initialization with custom config directory."""
        custom_path = Path("/custom/config")
        manager = ConfigManager(custom_path)
        assert manager.config_dir == custom_path

    def test_get_available_environments_no_dir(self) -> None:
        """Test getting environments when config directory doesn't exist."""
        manager = ConfigManager(Path("/nonexistent"))
        environments = manager.get_available_environments()
        assert environments == []

    def test_validate_config_valid(self) -> None:
        """Test validating valid configuration data."""
        manager = ConfigManager()
        config_data = {"app_name": "test-app", "debug": True, "port": 9000}

        config = manager.validate_config(config_data)
        assert isinstance(config, AppConfig)
        assert config.app_name == "test-app"
        assert config.debug is True
        assert config.port == 9000

    def test_validate_config_invalid(self) -> None:
        """Test validating invalid configuration data."""
        manager = ConfigManager()
        config_data = {"port": "invalid"}  # Should be int

        with pytest.raises(ValueError, match="Configuration validation failed"):
            manager.validate_config(config_data)

    def test_clear_cache(self) -> None:
        """Test clearing configuration cache."""
        manager = ConfigManager()
        # Add something to cache
        manager._cache["test"] = AppConfig()
        assert len(manager._cache) == 1

        manager.clear_cache()
        assert len(manager._cache) == 0

    def test_load_config_file_not_found(self) -> None:
        """Test loading config when files don't exist."""
        manager = ConfigManager(Path("/nonexistent"))

        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            manager.load_config("development")

    def test_caching(self) -> None:
        """Test that configurations are cached."""
        manager = ConfigManager()

        # Mock the load to avoid file system dependency
        config = AppConfig(app_name="cached-test")
        manager._cache["test"] = config

        # Should return cached version
        result = manager.load_config("test")
        assert result is config
