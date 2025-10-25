"""Tests for API module structure and imports."""

import pytest


class TestModuleStructure:
    """Tests for module structure and imports."""

    def test_api_module_imports(self):
        """Test that api module can be imported."""
        from search_api import api

        assert api is not None
        assert hasattr(api, "app")

    def test_fastapi_app_exists(self):
        """Test that FastAPI app is created."""
        from search_api.api import app

        assert app is not None
        assert app.title == "Search API"

    def test_health_endpoint_registered(self):
        """Test that health endpoint is registered."""
        from search_api.api import app

        routes = [route.path for route in app.routes]
        assert "/health" in routes

    def test_search_endpoint_registered(self):
        """Test that search endpoint is registered."""
        from search_api.api import app

        routes = [route.path for route in app.routes]
        assert "/search" in routes

    def test_summarize_endpoint_registered(self):
        """Test that summarize endpoint is registered."""
        from search_api.api import app

        routes = [route.path for route in app.routes]
        assert "/summarize" in routes
