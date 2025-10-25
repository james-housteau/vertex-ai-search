"""Configuration loader with YAML support and environment variable overrides."""

import os
from pathlib import Path
from typing import Any

import yaml

from .models import AppConfig, ConfigManager


def load_yaml_file(file_path: Path) -> dict[str, Any]:
    """Load YAML configuration file.

    Args:
        file_path: Path to YAML file

    Returns:
        Dict[str, Any]: Parsed YAML content

    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML is invalid
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    try:
        with open(file_path, encoding="utf-8") as f:
            content = yaml.safe_load(f)
            return content if content is not None else {}
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid YAML in {file_path}: {e}") from e


def merge_configs(
    base_config: dict[str, Any], override_config: dict[str, Any]
) -> dict[str, Any]:
    """Merge two configuration dictionaries.

    Args:
        base_config: Base configuration
        override_config: Configuration to overlay

    Returns:
        Dict[str, Any]: Merged configuration
    """
    merged = base_config.copy()

    for key, value in override_config.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value

    return merged


def apply_env_overrides(
    config: dict[str, Any], prefix: str = "CONFIG_"
) -> dict[str, Any]:
    """Apply environment variable overrides to configuration.

    Args:
        config: Base configuration
        prefix: Environment variable prefix

    Returns:
        Dict[str, Any]: Configuration with environment overrides
    """
    result = config.copy()

    for env_key, env_value in os.environ.items():
        if env_key.startswith(prefix):
            # Convert CONFIG_LOG_LEVEL to log_level
            config_key = env_key[len(prefix) :].lower()

            # Convert string values to appropriate types
            if env_value.lower() in ("true", "false"):
                result[config_key] = env_value.lower() == "true"
            elif env_value.isdigit():
                result[config_key] = int(env_value)
            else:
                result[config_key] = env_value

    return result


def load_config(
    environment: str = "development",
    config_dir: Path | None = None,
    apply_env_vars: bool = True,
) -> AppConfig:
    """Load configuration for the specified environment.

    Args:
        environment: Environment name
        config_dir: Configuration directory path
        apply_env_vars: Whether to apply environment variable overrides

    Returns:
        AppConfig: Loaded and validated configuration

    Raises:
        FileNotFoundError: If configuration files are not found
        ValueError: If configuration is invalid
    """
    config_manager = ConfigManager(config_dir)

    # Load defaults
    defaults_path = config_manager.config_dir / "defaults.yaml"
    base_config = load_yaml_file(defaults_path)

    # Load environment-specific config
    env_path = config_manager.config_dir / f"{environment}.yaml"
    env_config = load_yaml_file(env_path)

    # Merge configurations
    merged_config = merge_configs(base_config, env_config)

    # Apply environment variable overrides
    if apply_env_vars:
        merged_config = apply_env_overrides(merged_config)

    # Validate and return
    return config_manager.validate_config(merged_config)
