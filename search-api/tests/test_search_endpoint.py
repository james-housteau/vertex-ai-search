"""Tests for /search endpoint.

TDD RED Phase - These tests define the expected behavior.
They will FAIL until we implement the code.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_vector_client(mocker):
    """Mock VectorQueryClient."""
    mock_client = mocker.Mock()
    mock_client.last_query_latency_ms = 85.5
    return mock_client


@pytest.fixture
def test_client(mocker, mock_vector_client):
    """Create test client with mocked dependencies."""
    # Mock the get_vector_client function to return our mock
    mocker.patch("search_api.api.get_vector_client", return_value=mock_vector_client)

    # Clear the cache between tests
    from search_api.api import app, search_cache

    search_cache.clear()

    return TestClient(app)


class TestSearchEndpoint:
    """Tests for GET /search endpoint."""

    def test_search_endpoint_exists(self, test_client):
        """Test that /search endpoint is accessible."""
        response = test_client.get("/search", params={"q": "test query"})
        assert response.status_code in [200, 422]  # 422 if validation fails

    def test_search_returns_results(self, test_client, mock_vector_client, mocker):
        """Test that search returns SearchMatch results."""
        # Import SearchMatch to create mock response
        from shared_contracts import SearchMatch

        # Mock query results
        mock_results = [
            SearchMatch(
                chunk_id="chunk-1",
                score=0.95,
                content="Sample content 1",
                metadata={"source": "doc1.html"},
            ),
            SearchMatch(
                chunk_id="chunk-2",
                score=0.87,
                content="Sample content 2",
                metadata={"source": "doc2.html"},
            ),
        ]
        mock_vector_client.query.return_value = mock_results

        response = test_client.get("/search", params={"q": "test query"})

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 2
        assert data["results"][0]["chunk_id"] == "chunk-1"
        assert data["results"][0]["score"] == 0.95

    def test_search_requires_query_parameter(self, test_client):
        """Test that search requires 'q' query parameter."""
        response = test_client.get("/search")
        assert response.status_code == 422  # Validation error

    def test_search_accepts_top_k_parameter(self, test_client, mock_vector_client):
        """Test that search accepts optional top_k parameter."""
        from shared_contracts import SearchMatch

        mock_vector_client.query.return_value = [
            SearchMatch(chunk_id="chunk-1", score=0.95, content="test", metadata={})
        ]

        response = test_client.get("/search", params={"q": "test", "top_k": 5})

        assert response.status_code == 200
        mock_vector_client.query.assert_called_with("test", top_k=5)

    def test_search_tracks_latency(self, test_client, mock_vector_client):
        """Test that search response includes latency tracking."""
        from shared_contracts import SearchMatch

        mock_vector_client.query.return_value = [
            SearchMatch(chunk_id="chunk-1", score=0.95, content="test", metadata={})
        ]
        mock_vector_client.last_query_latency_ms = 42.5

        response = test_client.get("/search", params={"q": "test"})

        assert response.status_code == 200
        data = response.json()
        assert "latency_ms" in data
        # Latency should include query time plus any caching overhead
        assert data["latency_ms"] >= 0

    def test_search_handles_empty_results(self, test_client, mock_vector_client):
        """Test that search handles empty result sets."""
        mock_vector_client.query.return_value = []

        response = test_client.get("/search", params={"q": "nonexistent"})

        assert response.status_code == 200
        data = response.json()
        assert data["results"] == []
        assert "latency_ms" in data


class TestSearchCaching:
    """Tests for in-memory caching behavior."""

    def test_cache_hit_faster_than_miss(self, mocker):
        """Test that cached queries are faster than uncached."""
        from shared_contracts import SearchMatch

        from search_api.api import app, search_cache

        # Clear cache
        search_cache.clear()

        # Mock vector client
        mock_vector_client = mocker.Mock()
        mock_result = [
            SearchMatch(chunk_id="chunk-1", score=0.95, content="test", metadata={})
        ]
        mock_vector_client.query.return_value = mock_result

        mocker.patch(
            "search_api.api.get_vector_client", return_value=mock_vector_client
        )

        test_client = TestClient(app)

        # First request - cache miss
        response1 = test_client.get("/search", params={"q": "cache test"})
        latency1 = response1.json()["latency_ms"]

        # Second request - cache hit
        response2 = test_client.get("/search", params={"q": "cache test"})
        latency2 = response2.json()["latency_ms"]

        assert response1.status_code == 200
        assert response2.status_code == 200
        # Cache hit should be significantly faster
        assert latency2 < latency1 or latency2 < 10  # <10ms for cache hit

    def test_cache_respects_top_k_parameter(self, mocker):
        """Test that cache keys include top_k parameter."""
        from shared_contracts import SearchMatch

        from search_api.api import app, search_cache

        # Clear cache
        search_cache.clear()

        # Mock vector client
        mock_vector_client = mocker.Mock()
        mock_result = [
            SearchMatch(chunk_id="chunk-1", score=0.95, content="test", metadata={})
        ]
        mock_vector_client.query.return_value = mock_result

        mocker.patch(
            "search_api.api.get_vector_client", return_value=mock_vector_client
        )

        test_client = TestClient(app)

        # Same query, different top_k - should hit vector client twice
        test_client.get("/search", params={"q": "test", "top_k": 5})
        test_client.get("/search", params={"q": "test", "top_k": 10})

        assert mock_vector_client.query.call_count == 2

    def test_cache_stores_results(self, mocker):
        """Test that cache stores and retrieves results correctly."""
        from shared_contracts import SearchMatch

        from search_api.api import app, search_cache

        # Clear cache
        search_cache.clear()

        # Mock vector client
        mock_vector_client = mocker.Mock()
        mock_result = [
            SearchMatch(chunk_id="chunk-1", score=0.95, content="test", metadata={})
        ]
        mock_vector_client.query.return_value = mock_result

        mocker.patch(
            "search_api.api.get_vector_client", return_value=mock_vector_client
        )

        test_client = TestClient(app)

        # First request
        response1 = test_client.get("/search", params={"q": "cacheable"})

        # Second request - should use cache
        response2 = test_client.get("/search", params={"q": "cacheable"})

        # Vector client should only be called once
        assert mock_vector_client.query.call_count == 1

        # Results should be identical
        assert response1.json()["results"] == response2.json()["results"]
