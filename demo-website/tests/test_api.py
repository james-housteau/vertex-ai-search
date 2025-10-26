"""Tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient

from demo_website.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


def test_health_check(client: TestClient) -> None:
    """Test health check endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_config_endpoint(client: TestClient) -> None:
    """Test config endpoint returns API URL."""
    response = client.get("/config")
    assert response.status_code == 200
    data = response.json()
    assert "api_url" in data
    assert data["api_url"].startswith("https://")


def test_root_serves_index_html(client: TestClient) -> None:
    """Test root endpoint serves index.html."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"


def test_static_css_accessible(client: TestClient) -> None:
    """Test CSS file is accessible."""
    response = client.get("/static/style.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]


def test_static_js_accessible(client: TestClient) -> None:
    """Test JavaScript file is accessible."""
    response = client.get("/static/app.js")
    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"] or "text/plain" in response.headers["content-type"]
