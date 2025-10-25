"""Tests for vector query client functionality.

TDD RED Phase - Write failing tests first to define expected behavior.
"""

import time
from unittest.mock import MagicMock, Mock, patch

from shared_contracts import SearchMatch
from vector_query_client import VectorQueryClient


class TestVectorQueryClient:
    """Test cases for VectorQueryClient.

    Following TDD RED phase - these tests define the expected API:
    - Input: query text string
    - Output: List[SearchMatch] with scores
    - Latency tracking per query
    """

    def test_query_single_result(self) -> None:
        """Test executing a query that returns a single match."""
        # Given - a query string
        query_text = "What is the capital of France?"

        # Mock Vertex AI Vector Search response
        mock_neighbor = Mock()
        mock_neighbor.id = "chunk-123"
        mock_neighbor.distance = 0.15  # Lower distance = higher similarity

        mock_datapoint = Mock()
        mock_datapoint.datapoint_id = "chunk-123"
        mock_datapoint.restricts = []

        mock_response = Mock()
        mock_response.nearest_neighbors = [[mock_neighbor]]

        with (
            patch("vertexai.init"),
            patch(
                "google.cloud.aiplatform.MatchingEngineIndexEndpoint"
            ) as mock_endpoint_class,
            patch(
                "vertexai.language_models.TextEmbeddingModel.from_pretrained"
            ) as mock_embedding_model,
        ):
            # Mock endpoint
            mock_endpoint = MagicMock()
            mock_endpoint.find_neighbors.return_value = [mock_response]
            mock_endpoint_class.return_value = mock_endpoint

            # Mock embedding generation
            mock_emb_instance = MagicMock()
            mock_emb_response = Mock()
            mock_emb_response.values = [0.1] * 768
            mock_emb_instance.get_embeddings.return_value = [mock_emb_response]
            mock_embedding_model.return_value = mock_emb_instance

            client = VectorQueryClient(
                project_id="test-project",
                location="us-central1",
                index_endpoint_id="test-endpoint",
                deployed_index_id="test-index",
            )

            # When - executing the query
            results = client.query(query_text)

            # Then - should return SearchMatch list
            assert len(results) == 1
            assert isinstance(results[0], SearchMatch)
            assert results[0].chunk_id == "chunk-123"
            assert 0.0 <= results[0].score <= 1.0
            assert results[0].content == ""  # Content fetched separately
            assert isinstance(results[0].metadata, dict)

    def test_query_multiple_results(self) -> None:
        """Test executing a query that returns multiple matches."""
        # Given - a query string
        query_text = "Machine learning fundamentals"

        # Mock multiple neighbors with different distances
        mock_neighbors = []
        for i in range(3):
            mock_neighbor = Mock()
            mock_neighbor.id = f"chunk-{i}"
            mock_neighbor.distance = 0.1 * (i + 1)  # Increasing distances
            mock_neighbors.append(mock_neighbor)

        mock_response = Mock()
        mock_response.nearest_neighbors = [mock_neighbors]

        with (
            patch("vertexai.init"),
            patch(
                "google.cloud.aiplatform.MatchingEngineIndexEndpoint"
            ) as mock_endpoint_class,
            patch(
                "vertexai.language_models.TextEmbeddingModel.from_pretrained"
            ) as mock_embedding_model,
        ):
            # Mock endpoint
            mock_endpoint = MagicMock()
            mock_endpoint.find_neighbors.return_value = [mock_response]
            mock_endpoint_class.return_value = mock_endpoint

            # Mock embedding generation
            mock_emb_instance = MagicMock()
            mock_emb_response = Mock()
            mock_emb_response.values = [0.1] * 768
            mock_emb_instance.get_embeddings.return_value = [mock_emb_response]
            mock_embedding_model.return_value = mock_emb_instance

            client = VectorQueryClient(
                project_id="test-project",
                location="us-central1",
                index_endpoint_id="test-endpoint",
                deployed_index_id="test-index",
            )

            # When
            results = client.query(query_text, top_k=3)

            # Then - should return 3 results in similarity order
            assert len(results) == 3
            for i, result in enumerate(results):
                assert isinstance(result, SearchMatch)
                assert result.chunk_id == f"chunk-{i}"
                # Higher scores should come first (converted from distances)
                if i > 0:
                    assert results[i - 1].score >= result.score

    def test_query_tracks_latency(self) -> None:
        """Test that query latency is tracked for SLO monitoring."""
        # Given
        query_text = "Test query"

        mock_neighbor = Mock()
        mock_neighbor.id = "chunk-1"
        mock_neighbor.distance = 0.2

        mock_response = Mock()
        mock_response.nearest_neighbors = [[mock_neighbor]]

        with (
            patch("vertexai.init"),
            patch(
                "google.cloud.aiplatform.MatchingEngineIndexEndpoint"
            ) as mock_endpoint_class,
            patch(
                "vertexai.language_models.TextEmbeddingModel.from_pretrained"
            ) as mock_embedding_model,
        ):
            mock_endpoint = MagicMock()
            mock_endpoint.find_neighbors.return_value = [mock_response]
            mock_endpoint_class.return_value = mock_endpoint

            mock_emb_instance = MagicMock()
            mock_emb_response = Mock()
            mock_emb_response.values = [0.1] * 768
            mock_emb_instance.get_embeddings.return_value = [mock_emb_response]
            mock_embedding_model.return_value = mock_emb_instance

            client = VectorQueryClient(
                project_id="test-project",
                location="us-central1",
                index_endpoint_id="test-endpoint",
                deployed_index_id="test-index",
            )

            # When
            start = time.time()
            _ = client.query(query_text)
            elapsed = time.time() - start

            # Then - should have latency tracking
            assert hasattr(client, "last_query_latency_ms")
            assert client.last_query_latency_ms > 0
            assert client.last_query_latency_ms < elapsed * 1000 + 100  # Allow margin

    def test_query_empty_results(self) -> None:
        """Test handling query with no matches."""
        # Given
        query_text = "Nonexistent content"

        mock_response = Mock()
        mock_response.nearest_neighbors = [[]]  # Empty results

        with (
            patch("vertexai.init"),
            patch(
                "google.cloud.aiplatform.MatchingEngineIndexEndpoint"
            ) as mock_endpoint_class,
            patch(
                "vertexai.language_models.TextEmbeddingModel.from_pretrained"
            ) as mock_embedding_model,
        ):
            mock_endpoint = MagicMock()
            mock_endpoint.find_neighbors.return_value = [mock_response]
            mock_endpoint_class.return_value = mock_endpoint

            mock_emb_instance = MagicMock()
            mock_emb_response = Mock()
            mock_emb_response.values = [0.1] * 768
            mock_emb_instance.get_embeddings.return_value = [mock_emb_response]
            mock_embedding_model.return_value = mock_emb_instance

            client = VectorQueryClient(
                project_id="test-project",
                location="us-central1",
                index_endpoint_id="test-endpoint",
                deployed_index_id="test-index",
            )

            # When
            results = client.query(query_text)

            # Then
            assert results == []
            assert isinstance(results, list)

    def test_query_with_custom_top_k(self) -> None:
        """Test querying with custom number of results."""
        # Given
        query_text = "Custom top_k test"
        custom_top_k = 5

        # Mock 5 neighbors
        mock_neighbors = []
        for i in range(5):
            mock_neighbor = Mock()
            mock_neighbor.id = f"chunk-{i}"
            mock_neighbor.distance = 0.1 * (i + 1)
            mock_neighbors.append(mock_neighbor)

        mock_response = Mock()
        mock_response.nearest_neighbors = [mock_neighbors]

        with (
            patch("vertexai.init"),
            patch(
                "google.cloud.aiplatform.MatchingEngineIndexEndpoint"
            ) as mock_endpoint_class,
            patch(
                "vertexai.language_models.TextEmbeddingModel.from_pretrained"
            ) as mock_embedding_model,
        ):
            mock_endpoint = MagicMock()
            mock_endpoint.find_neighbors.return_value = [mock_response]
            mock_endpoint_class.return_value = mock_endpoint

            mock_emb_instance = MagicMock()
            mock_emb_response = Mock()
            mock_emb_response.values = [0.1] * 768
            mock_emb_instance.get_embeddings.return_value = [mock_emb_response]
            mock_embedding_model.return_value = mock_emb_instance

            client = VectorQueryClient(
                project_id="test-project",
                location="us-central1",
                index_endpoint_id="test-endpoint",
                deployed_index_id="test-index",
            )

            # When
            results = client.query(query_text, top_k=custom_top_k)

            # Then
            assert len(results) == 5
            # Verify find_neighbors was called with correct top_k
            mock_endpoint.find_neighbors.assert_called_once()
            call_args = mock_endpoint.find_neighbors.call_args
            assert call_args[1]["num_neighbors"] == custom_top_k

    def test_distance_to_score_conversion(self) -> None:
        """Test that distances are properly converted to similarity scores.

        Lower distance = higher similarity.
        Distance of 0 should give score of 1.0.
        """
        # Given
        query_text = "Test query"

        # Mock neighbor with distance 0 (perfect match)
        mock_neighbor = Mock()
        mock_neighbor.id = "chunk-perfect"
        mock_neighbor.distance = 0.0

        mock_response = Mock()
        mock_response.nearest_neighbors = [[mock_neighbor]]

        with (
            patch("vertexai.init"),
            patch(
                "google.cloud.aiplatform.MatchingEngineIndexEndpoint"
            ) as mock_endpoint_class,
            patch(
                "vertexai.language_models.TextEmbeddingModel.from_pretrained"
            ) as mock_embedding_model,
        ):
            mock_endpoint = MagicMock()
            mock_endpoint.find_neighbors.return_value = [mock_response]
            mock_endpoint_class.return_value = mock_endpoint

            mock_emb_instance = MagicMock()
            mock_emb_response = Mock()
            mock_emb_response.values = [0.1] * 768
            mock_emb_instance.get_embeddings.return_value = [mock_emb_response]
            mock_embedding_model.return_value = mock_emb_instance

            client = VectorQueryClient(
                project_id="test-project",
                location="us-central1",
                index_endpoint_id="test-endpoint",
                deployed_index_id="test-index",
            )

            # When
            results = client.query(query_text)

            # Then - distance 0 should convert to score 1.0
            assert results[0].score == 1.0

    def test_query_initialization_parameters(self) -> None:
        """Test client initialization with required parameters."""
        # Given/When
        with (
            patch("vertexai.init"),
            patch("google.cloud.aiplatform.MatchingEngineIndexEndpoint"),
            patch("vertexai.language_models.TextEmbeddingModel.from_pretrained"),
        ):
            client = VectorQueryClient(
                project_id="my-project",
                location="us-west1",
                index_endpoint_id="endpoint-123",
                deployed_index_id="deployed-456",
            )

            # Then
            assert client.project_id == "my-project"
            assert client.location == "us-west1"
            assert client.index_endpoint_id == "endpoint-123"
            assert client.deployed_index_id == "deployed-456"

    def test_query_latency_target_tracking(self) -> None:
        """Test that latency can be checked against p95 target of 120ms."""
        # Given
        query_text = "Latency test"

        mock_neighbor = Mock()
        mock_neighbor.id = "chunk-1"
        mock_neighbor.distance = 0.1

        mock_response = Mock()
        mock_response.nearest_neighbors = [[mock_neighbor]]

        with (
            patch("vertexai.init"),
            patch(
                "google.cloud.aiplatform.MatchingEngineIndexEndpoint"
            ) as mock_endpoint_class,
            patch(
                "vertexai.language_models.TextEmbeddingModel.from_pretrained"
            ) as mock_embedding_model,
        ):
            mock_endpoint = MagicMock()
            mock_endpoint.find_neighbors.return_value = [mock_response]
            mock_endpoint_class.return_value = mock_endpoint

            mock_emb_instance = MagicMock()
            mock_emb_response = Mock()
            mock_emb_response.values = [0.1] * 768
            mock_emb_instance.get_embeddings.return_value = [mock_emb_response]
            mock_embedding_model.return_value = mock_emb_instance

            client = VectorQueryClient(
                project_id="test-project",
                location="us-central1",
                index_endpoint_id="test-endpoint",
                deployed_index_id="test-index",
            )

            # When
            _ = client.query(query_text)

            # Then - latency should be trackable
            assert hasattr(client, "last_query_latency_ms")
            # In tests, latency should be very low (mocked)
            # In production, we'd check against 120ms p95 target
            assert client.last_query_latency_ms >= 0
