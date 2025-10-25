"""Shared test fixtures for search-api tests."""

import pytest


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("GCP_PROJECT_ID", "test-project")
    monkeypatch.setenv("GCP_LOCATION", "us-central1")
    monkeypatch.setenv("INDEX_ENDPOINT_ID", "test-endpoint")
    monkeypatch.setenv("DEPLOYED_INDEX_ID", "test-index")
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")
