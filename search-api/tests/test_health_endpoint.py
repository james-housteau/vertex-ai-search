"""Tests for /health endpoint.

TDD RED Phase - These tests define the expected behavior.
They will FAIL until we implement the code.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_client():
    """Create test client."""
    from search_api.api import app

    return TestClient(app)


class TestHealthEndpoint:
    """Tests for GET /health endpoint."""

    def test_health_endpoint_exists(self, test_client):
        """Test that /health endpoint is accessible."""
        response = test_client.get("/health")
        assert response.status_code == 200

    def test_health_returns_status(self, test_client):
        """Test that health endpoint returns status."""
        response = test_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_returns_service_info(self, test_client):
        """Test that health endpoint returns service information."""
        response = test_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert data["service"] == "search-api"
