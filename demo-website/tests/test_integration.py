"""Integration tests for demo website."""

import pytest
from fastapi.testclient import TestClient

from demo_website.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


def test_full_page_load(client: TestClient) -> None:
    """Test complete page load with all resources."""
    # Load main page
    response = client.get("/")
    assert response.status_code == 200

    # Load CSS
    response = client.get("/static/style.css")
    assert response.status_code == 200

    # Load JS
    response = client.get("/static/app.js")
    assert response.status_code == 200


def test_health_check_for_cloud_run(client: TestClient) -> None:
    """Test health check works for Cloud Run readiness probe."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


def test_config_provides_api_url(client: TestClient) -> None:
    """Test config endpoint provides API URL for frontend."""
    response = client.get("/config")
    assert response.status_code == 200
    data = response.json()
    assert "api_url" in data
    assert isinstance(data["api_url"], str)
    assert len(data["api_url"]) > 0


def test_static_files_have_correct_content_type(client: TestClient) -> None:
    """Test static files are served with correct MIME types."""
    # CSS should be text/css
    response = client.get("/static/style.css")
    assert "text/css" in response.headers["content-type"]

    # HTML should be text/html
    response = client.get("/")
    assert "text/html" in response.headers["content-type"]
