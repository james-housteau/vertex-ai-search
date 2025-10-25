"""Vector query client implementation.

TDD GREEN Phase - Minimal implementation to make tests pass.
"""

import time

import vertexai
from google.cloud import aiplatform
from shared_contracts import SearchMatch  # type: ignore[import-untyped]
from vertexai.language_models import TextEmbeddingModel


class VectorQueryClient:
    """Execute vector similarity search queries against Vertex AI Vector Search.

    Converts query text to embeddings and executes ANN search.
    Tracks latency for SLO monitoring (target: <120ms p95).
    """

    def __init__(
        self,
        project_id: str,
        location: str,
        index_endpoint_id: str,
        deployed_index_id: str,
    ) -> None:
        """Initialize the vector query client.

        Args:
            project_id: GCP project ID
            location: GCP location (e.g., 'us-central1')
            index_endpoint_id: Vertex AI index endpoint ID
            deployed_index_id: Deployed index ID
        """
        self.project_id = project_id
        self.location = location
        self.index_endpoint_id = index_endpoint_id
        self.deployed_index_id = deployed_index_id
        self.last_query_latency_ms: float = 0.0

        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)

        # Initialize embedding model
        self.embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")

        # Initialize index endpoint
        self.index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=index_endpoint_id
        )

    def query(self, query_text: str, top_k: int = 10) -> list[SearchMatch]:
        """Execute a vector similarity search query.

        Args:
            query_text: Text query to search for
            top_k: Number of results to return (default: 10)

        Returns:
            List of SearchMatch objects sorted by similarity score (highest first)
        """
        start_time = time.time()

        # Generate query embedding
        embedding_response = self.embedding_model.get_embeddings([query_text])
        query_embedding = embedding_response[0].values

        # Execute vector search
        response = self.index_endpoint.find_neighbors(
            deployed_index_id=self.deployed_index_id,
            queries=[query_embedding],
            num_neighbors=top_k,
        )

        # Track latency
        self.last_query_latency_ms = (time.time() - start_time) * 1000

        # Convert results to SearchMatch
        results: list[SearchMatch] = []
        if response and response[0].nearest_neighbors:  # type: ignore[attr-defined]
            # nearest_neighbors is a list of neighbor lists (one per query)
            for neighbor in response[0].nearest_neighbors[0]:  # type: ignore[attr-defined]
                # Convert distance to similarity score
                # Distance of 0 = perfect match (score 1.0)
                # Higher distance = lower similarity
                score = self._distance_to_score(neighbor.distance)

                match = SearchMatch(
                    chunk_id=neighbor.id,
                    score=score,
                    content="",  # Content fetched separately if needed
                    metadata={},  # Metadata would come from separate lookup
                )
                results.append(match)

        return results

    def _distance_to_score(self, distance: float) -> float:
        """Convert distance to similarity score.

        Args:
            distance: Distance from vector search (lower = more similar)

        Returns:
            Similarity score between 0.0 and 1.0 (higher = more similar)
        """
        # Simple conversion: score = 1 / (1 + distance)
        # Distance 0 -> score 1.0
        # Distance increases -> score decreases toward 0
        score = 1.0 / (1.0 + distance)
        return min(1.0, max(0.0, score))  # Clamp to [0, 1]
