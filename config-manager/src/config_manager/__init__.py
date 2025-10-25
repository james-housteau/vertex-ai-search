"""Config Manager - Configuration management for Vertex AI search functionality."""

from .loader import load_config
from .models import AppConfig, ConfigManager

__version__ = "0.1.0"
__all__ = ["AppConfig", "ConfigManager", "load_config"]
