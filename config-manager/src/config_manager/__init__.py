"""Config Manager - Configuration management for Vertex AI search functionality."""

from .models import AppConfig, ConfigManager
from .loader import load_config

__version__ = "0.1.0"
__all__ = ["AppConfig", "ConfigManager", "load_config"]
