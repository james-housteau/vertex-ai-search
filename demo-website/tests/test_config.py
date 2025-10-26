"""Tests for configuration management."""

import pytest

from demo_website.config import Settings, get_settings


def test_default_settings() -> None:
    """Test default settings are loaded correctly."""
    settings = Settings()
    assert settings.api_url.startswith("https://")
    assert settings.host == "0.0.0.0"
    assert settings.port == 8080


def test_get_settings() -> None:
    """Test get_settings factory function."""
    settings = get_settings()
    assert isinstance(settings, Settings)
    assert settings.api_url.startswith("https://")


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test settings can be loaded from environment."""
    monkeypatch.setenv("API_URL", "https://custom-api.example.com")
    monkeypatch.setenv("PORT", "9000")

    settings = Settings()
    assert settings.api_url == "https://custom-api.example.com"
    assert settings.port == 9000
