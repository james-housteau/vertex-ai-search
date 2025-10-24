"""Pydantic models for configuration management."""

from typing import Optional, Dict, Any, List
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict


class AppConfig(BaseModel):
    """Main application configuration model."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    # Application metadata
    app_name: str = Field(default="vertex-ai-search")
    version: str = Field(default="1.0.0")
    description: str = Field(default="A vertex-ai-search project created with Genesis")

    # Core settings
    log_level: str = Field(default="INFO")
    debug: bool = Field(default=False)
    timeout: int = Field(default=30, ge=1, le=300)

    # Service configuration
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1024, le=65535)


class EnvironmentConfig(BaseModel):
    """Environment-specific configuration."""

    model_config = ConfigDict(frozen=True, extra="allow")

    environment: str = Field(default="development")
    config_overrides: Dict[str, Any] = Field(default_factory=dict)


class ConfigManager:
    """Configuration manager for loading and merging configuration files."""

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        """Initialize the configuration manager.

        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = config_dir or Path("config")
        self._cache: Dict[str, AppConfig] = {}

    def load_config(self, environment: str = "development") -> AppConfig:
        """Load configuration for the specified environment.

        Args:
            environment: Environment name (development, staging, production, test)

        Returns:
            AppConfig: Loaded and validated configuration

        Raises:
            FileNotFoundError: If configuration files are not found
            ValueError: If configuration is invalid
        """
        if environment in self._cache:
            return self._cache[environment]

        # Import here to avoid circular imports
        from .loader import load_config as loader_load_config

        try:
            config = loader_load_config(environment, self.config_dir)
            self._cache[environment] = config
            return config
        except Exception:
            # If loading fails, we'll let the exception bubble up
            raise

    def get_available_environments(self) -> List[str]:
        """Get list of available environment configurations.

        Returns:
            List[str]: Available environment names
        """
        if not self.config_dir.exists():
            return []

        env_files = []
        for file_path in self.config_dir.glob("*.yaml"):
            if file_path.name != "defaults.yaml":
                env_files.append(file_path.stem)

        return sorted(env_files)

    def validate_config(self, config_data: Dict[str, Any]) -> AppConfig:
        """Validate configuration data against the schema.

        Args:
            config_data: Raw configuration dictionary

        Returns:
            AppConfig: Validated configuration

        Raises:
            ValueError: If configuration is invalid
        """
        try:
            return AppConfig(**config_data)
        except Exception as e:
            raise ValueError(f"Configuration validation failed: {e}") from e

    def clear_cache(self) -> None:
        """Clear the configuration cache."""
        self._cache.clear()
