"""Tests for /summarize endpoint.

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


class TestSummarizeEndpoint:
    """Tests for POST /summarize endpoint."""

    def test_summarize_endpoint_exists(self, test_client, mocker):
        """Test that /summarize endpoint is accessible."""
        # Mock Gemini to avoid actual API calls
        mock_model = mocker.Mock()
        mock_response = mocker.Mock()
        mock_response.__iter__ = mocker.Mock(
            return_value=iter([mocker.Mock(text="Summary")])
        )
        mock_model.generate_content.return_value = mock_response

        mocker.patch("search_api.api.genai.GenerativeModel", return_value=mock_model)

        response = test_client.post(
            "/summarize", json={"content": "Test content to summarize"}
        )
        # Should return 200 for successful stream
        assert response.status_code == 200

    def test_summarize_requires_content(self, test_client):
        """Test that summarize requires content parameter."""
        response = test_client.post("/summarize", json={})
        assert response.status_code == 422  # Validation error

    def test_summarize_returns_sse_stream(self, test_client, mocker):
        """Test that summarize returns Server-Sent Events stream."""
        # Mock Gemini client
        mock_model = mocker.Mock()
        mock_response = mocker.Mock()
        mock_response.__iter__ = mocker.Mock(
            return_value=iter(
                [
                    mocker.Mock(text="This is "),
                    mocker.Mock(text="a test "),
                    mocker.Mock(text="summary."),
                ]
            )
        )
        mock_model.generate_content.return_value = mock_response

        mocker.patch("search_api.api.genai.GenerativeModel", return_value=mock_model)

        response = test_client.post(
            "/summarize", json={"content": "Long content to summarize"}
        )

        assert response.status_code == 200
        # Should be SSE stream
        assert "text/event-stream" in response.headers.get("content-type", "")

    def test_summarize_streams_tokens(self, test_client, mocker):
        """Test that summarize streams tokens as SSE."""
        # Mock Gemini streaming response
        mock_model = mocker.Mock()
        mock_response = mocker.Mock()
        mock_response.__iter__ = mocker.Mock(
            return_value=iter(
                [
                    mocker.Mock(text="Token1 "),
                    mocker.Mock(text="Token2 "),
                    mocker.Mock(text="Token3"),
                ]
            )
        )
        mock_model.generate_content.return_value = mock_response

        mocker.patch("search_api.api.genai.GenerativeModel", return_value=mock_model)

        response = test_client.post(
            "/summarize", json={"content": "Content to summarize"}
        )

        assert response.status_code == 200

        # Parse SSE stream
        content = response.text
        # SSE format: "data: <message>\n\n"
        assert "data:" in content

    def test_summarize_accepts_max_tokens(self, test_client, mocker):
        """Test that summarize accepts optional max_tokens parameter."""
        mock_model = mocker.Mock()
        mock_response = mocker.Mock()
        mock_response.__iter__ = mocker.Mock(
            return_value=iter([mocker.Mock(text="Summary")])
        )
        mock_model.generate_content.return_value = mock_response

        mocker.patch("search_api.api.genai.GenerativeModel", return_value=mock_model)

        response = test_client.post(
            "/summarize", json={"content": "Content", "max_tokens": 100}
        )

        assert response.status_code == 200


class TestSummarizeValidation:
    """Tests for summarize endpoint validation."""

    def test_summarize_validates_content_not_empty(self, test_client):
        """Test that summarize validates content is not empty."""
        response = test_client.post("/summarize", json={"content": ""})
        assert response.status_code == 422

    def test_summarize_validates_max_tokens_positive(self, test_client):
        """Test that summarize validates max_tokens is positive."""
        response = test_client.post(
            "/summarize", json={"content": "Test content", "max_tokens": -1}
        )
        assert response.status_code == 422
