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
        # Mock Vertex AI to avoid actual API calls
        mocker.patch("search_api.api.vertexai.init")

        mock_model = mocker.Mock()
        mock_response = mocker.Mock()
        mock_response.__iter__ = mocker.Mock(
            return_value=iter([mocker.Mock(text="Summary")])
        )
        mock_model.generate_content.return_value = mock_response

        mocker.patch("search_api.api.GenerativeModel", return_value=mock_model)

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
        # Mock Vertex AI
        mocker.patch("search_api.api.vertexai.init")

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

        mocker.patch("search_api.api.GenerativeModel", return_value=mock_model)

        response = test_client.post(
            "/summarize", json={"content": "Long content to summarize"}
        )

        assert response.status_code == 200
        # Should be SSE stream
        assert "text/event-stream" in response.headers.get("content-type", "")

    def test_summarize_streams_tokens(self, test_client, mocker):
        """Test that summarize streams tokens as SSE."""
        # Mock Vertex AI streaming response
        mocker.patch("search_api.api.vertexai.init")

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

        mocker.patch("search_api.api.GenerativeModel", return_value=mock_model)

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
        # Mock Vertex AI
        mocker.patch("search_api.api.vertexai.init")

        mock_model = mocker.Mock()
        mock_response = mocker.Mock()
        mock_response.__iter__ = mocker.Mock(
            return_value=iter([mocker.Mock(text="Summary")])
        )
        mock_model.generate_content.return_value = mock_response

        mocker.patch("search_api.api.GenerativeModel", return_value=mock_model)

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


class TestSummarizeCaching:
    """Tests for /summarize endpoint caching behavior."""

    def test_summarize_metadata_includes_cache_hit_on_miss(self, mocker):
        """Test that summarize metadata includes cache_hit=false on cache miss."""
        from shared_contracts import SearchMatch

        from search_api.api import app, search_cache

        # Clear cache
        search_cache.clear()

        # Mock vector client
        mock_vector_client = mocker.Mock()
        mock_result = [
            SearchMatch(
                chunk_id="chunk-1", score=0.95, content="test content", metadata={}
            )
        ]
        mock_vector_client.query.return_value = mock_result
        mocker.patch(
            "search_api.api.get_vector_client", return_value=mock_vector_client
        )

        # Mock Vertex AI
        mocker.patch("search_api.api.vertexai.init")
        mock_model = mocker.Mock()
        mock_response = mocker.Mock()
        mock_response.__iter__ = mocker.Mock(
            return_value=iter([mocker.Mock(text="Summary")])
        )
        mock_model.generate_content.return_value = mock_response
        mocker.patch("search_api.api.GenerativeModel", return_value=mock_model)

        test_client = TestClient(app)

        # Make request - cache miss
        response = test_client.post(
            "/summarize", json={"query": "test query", "top_k": 5}
        )

        assert response.status_code == 200

        # Parse SSE stream
        import json

        content = response.text
        lines = content.strip().split("\n")

        # Find the first metadata event
        metadata_found = False
        for line in lines:
            if line.startswith("data: "):
                data = json.loads(line[6:])  # Skip "data: " prefix
                if "metadata" in data:
                    metadata = data["metadata"]
                    assert (
                        "cache_hit" in metadata
                    ), "cache_hit field missing from metadata"
                    assert (
                        metadata["cache_hit"] is False
                    ), "cache_hit should be False on cache miss"
                    metadata_found = True
                    break

        assert metadata_found, "No metadata event found in SSE stream"

    def test_summarize_metadata_includes_cache_hit_on_hit(self, mocker):
        """Test that summarize metadata includes cache_hit=true on cache hit."""
        import hashlib
        import re

        from shared_contracts import SearchMatch

        from search_api.api import app, search_cache

        # Clear cache
        search_cache.clear()

        # Mock vector client
        mock_vector_client = mocker.Mock()
        mock_result = [
            SearchMatch(
                chunk_id="chunk-1", score=0.95, content="test content", metadata={}
            )
        ]
        mock_vector_client.query.return_value = mock_result
        mocker.patch(
            "search_api.api.get_vector_client", return_value=mock_vector_client
        )

        # Pre-populate cache with normalized query
        query = "test query"
        top_k = 5
        normalized_q = re.sub(r"\s+", " ", query.lower().strip())
        cache_key = hashlib.md5(f"{normalized_q}:{top_k}".encode()).hexdigest()
        import time

        search_cache[cache_key] = (mock_result, time.time())

        # Mock Vertex AI
        mocker.patch("search_api.api.vertexai.init")
        mock_model = mocker.Mock()
        mock_response = mocker.Mock()
        mock_response.__iter__ = mocker.Mock(
            return_value=iter([mocker.Mock(text="Summary")])
        )
        mock_model.generate_content.return_value = mock_response
        mocker.patch("search_api.api.GenerativeModel", return_value=mock_model)

        test_client = TestClient(app)

        # Make request - cache hit
        response = test_client.post(
            "/summarize", json={"query": "test query", "top_k": 5}
        )

        assert response.status_code == 200

        # Parse SSE stream
        import json

        content = response.text
        lines = content.strip().split("\n")

        # Find the first metadata event
        metadata_found = False
        for line in lines:
            if line.startswith("data: "):
                data = json.loads(line[6:])  # Skip "data: " prefix
                if "metadata" in data:
                    metadata = data["metadata"]
                    assert (
                        "cache_hit" in metadata
                    ), "cache_hit field missing from metadata"
                    assert (
                        metadata["cache_hit"] is True
                    ), "cache_hit should be True on cache hit"
                    metadata_found = True
                    break

        assert metadata_found, "No metadata event found in SSE stream"


class TestSummarizeMetrics:
    """Tests for /summarize endpoint streaming metrics."""

    def test_summarize_includes_time_to_last_token_ms(self, mocker):
        """Test that final metadata includes time_to_last_token_ms.

        This metric tracks when the last content token was sent,
        distinguishing actual streaming duration from total overhead.
        """
        from shared_contracts import SearchMatch

        from search_api.api import app, search_cache

        # Clear cache
        search_cache.clear()

        # Mock vector client
        mock_vector_client = mocker.Mock()
        mock_result = [
            SearchMatch(
                chunk_id="chunk-1", score=0.95, content="test content", metadata={}
            )
        ]
        mock_vector_client.query.return_value = mock_result
        mocker.patch(
            "search_api.api.get_vector_client", return_value=mock_vector_client
        )

        # Mock Vertex AI with multiple tokens
        mocker.patch("search_api.api.vertexai.init")
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
        mocker.patch("search_api.api.GenerativeModel", return_value=mock_model)

        test_client = TestClient(app)

        # Make request
        response = test_client.post(
            "/summarize", json={"query": "test query", "top_k": 5}
        )

        assert response.status_code == 200

        # Parse SSE stream
        import json

        content = response.text
        lines = content.strip().split("\n")

        # Find the final metadata event (with "done": true)
        final_metadata_found = False
        for line in lines:
            if line.startswith("data: "):
                data = json.loads(line[6:])  # Skip "data: " prefix
                if "done" in data and data["done"] is True:
                    # This is the final metadata event
                    assert (
                        "time_to_last_token_ms" in data
                    ), "time_to_last_token_ms field missing from final metadata"

                    # Should be a positive number
                    time_to_last_token = data["time_to_last_token_ms"]
                    assert isinstance(
                        time_to_last_token, (int, float)
                    ), "time_to_last_token_ms should be a number"
                    assert time_to_last_token > 0, "time_to_last_token_ms should be positive"

                    # Should be less than total_time_ms (content finishes before final metadata)
                    assert "total_time_ms" in data, "total_time_ms should also be present"
                    assert (
                        time_to_last_token <= data["total_time_ms"]
                    ), "time_to_last_token_ms should be <= total_time_ms"

                    final_metadata_found = True
                    break

        assert final_metadata_found, "No final metadata event (done=true) found in SSE stream"
