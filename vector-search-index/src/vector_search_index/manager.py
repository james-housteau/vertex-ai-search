"""Vector Search Index Manager for Vertex AI."""

from typing import Any

from google.cloud import aiplatform

from vector_search_index.config import IndexConfig


class VectorSearchIndexManager:
    """Manager for Vertex AI Vector Search Index operations.

    Handles creation, update, deletion, and status monitoring of
    Vector Search indexes using the ScaNN algorithm.
    """

    def __init__(self, project_id: str, location: str) -> None:
        """Initialize the Vector Search Index Manager.

        Args:
            project_id: GCP project ID.
            location: GCP location (e.g., 'us-central1').
        """
        self.project_id = project_id
        self.location = location
        aiplatform.init(project=project_id, location=location)

    def create_index(self, config: IndexConfig) -> str:
        """Create a new Vector Search index.

        Args:
            config: Index configuration.

        Returns:
            Resource name of the created index.
        """
        # Build metadata dict for index creation
        metadata = {
            "config": {
                "dimensions": config.dimensions,
                "algorithmConfig": {
                    "treeAhConfig": {
                        "leafNodeEmbeddingCount": config.leaf_node_embedding_count,
                    }
                },
                "distanceMeasureType": config.distance_metric.value,
                "approximateNeighborsCount": config.approximate_neighbors_count,
                "shardSize": config.shard_size.value,
            }
        }

        # Create the index
        create_fn = aiplatform.MatchingEngineIndex.create
        index = create_fn(
            display_name=config.display_name,
            metadata=metadata,
        )
        return str(index.resource_name)

    def get_index_status(self, index_name: str) -> dict[str, Any]:
        """Get the status of a Vector Search index.

        Args:
            index_name: Full resource name of the index.

        Returns:
            Dictionary containing index status information.
        """
        index_class = aiplatform.MatchingEngineIndex
        index = index_class(index_name)
        return {
            "state": index.metadata.get("state", "UNKNOWN"),
            "deployed_indexes": [
                {"id": dep.deployed_index_id} for dep in index.deployed_indexes
            ],
        }

    def update_index(self, index_name: str, config: IndexConfig) -> str:
        """Update an existing Vector Search index.

        Args:
            index_name: Full resource name of the index.
            config: Updated index configuration.

        Returns:
            Resource name of the updated index.
        """
        index_class = aiplatform.MatchingEngineIndex
        index = index_class(index_name)
        index.update(
            display_name=config.display_name,
        )
        return str(index.resource_name)

    def delete_index(self, index_name: str) -> None:
        """Delete a Vector Search index.

        Args:
            index_name: Full resource name of the index.
        """
        index_class = aiplatform.MatchingEngineIndex
        index = index_class(index_name)
        index.delete()

    def list_indexes(self) -> list[dict[str, str]]:
        """List all Vector Search indexes in the project.

        Returns:
            List of dictionaries containing index information.
        """
        index_class = aiplatform.MatchingEngineIndex
        list_fn = index_class.list
        indexes = list_fn()
        return [
            {"name": index.resource_name, "display_name": index.display_name}
            for index in indexes
        ]
