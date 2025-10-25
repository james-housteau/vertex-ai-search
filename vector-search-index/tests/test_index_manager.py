"""Tests for Vector Search Index Manager."""

from unittest.mock import MagicMock, Mock, patch

import pytest
from vector_search_index.config import DistanceMetric, IndexConfig, ShardSize
from vector_search_index.manager import VectorSearchIndexManager


class TestVectorSearchIndexManager:
    """Test suite for VectorSearchIndexManager."""

    @pytest.fixture
    def mock_aiplatform(self) -> Mock:
        """Mock aiplatform initialization."""
        with patch("vector_search_index.manager.aiplatform") as mock:
            yield mock

    @pytest.fixture
    def manager(self, mock_aiplatform: Mock) -> VectorSearchIndexManager:
        """Create a manager instance with mocked dependencies."""
        return VectorSearchIndexManager(
            project_id="test-project", location="us-central1"
        )

    def test_manager_initialization(
        self, mock_aiplatform: Mock, manager: VectorSearchIndexManager
    ) -> None:
        """Test manager initializes with correct project and location."""
        mock_aiplatform.init.assert_called_once_with(
            project="test-project", location="us-central1"
        )
        assert manager.project_id == "test-project"
        assert manager.location == "us-central1"

    def test_create_index_success(
        self, mock_aiplatform: Mock, manager: VectorSearchIndexManager
    ) -> None:
        """Test successful index creation."""
        # Mock the MatchingEngineIndex.create method
        mock_index = MagicMock()
        mock_index.resource_name = (
            "projects/test-project/locations/us-central1/indexes/123"
        )
        mock_index.display_name = "test-index"
        mock_aiplatform.MatchingEngineIndex.create.return_value = mock_index

        # Create index
        config = IndexConfig(
            display_name="test-index",
            dimensions=768,
            distance_metric=DistanceMetric.DOT_PRODUCT_DISTANCE,
            shard_size=ShardSize.SHARD_SIZE_SMALL,
        )
        result = manager.create_index(config)

        # Verify
        assert result == mock_index.resource_name
        assert mock_aiplatform.MatchingEngineIndex.create.called
        call_args = mock_aiplatform.MatchingEngineIndex.create.call_args
        assert call_args[1]["display_name"] == "test-index"

    def test_create_index_with_custom_config(
        self, mock_aiplatform: Mock, manager: VectorSearchIndexManager
    ) -> None:
        """Test index creation with custom ScaNN configuration."""
        mock_index = MagicMock()
        mock_index.resource_name = (
            "projects/test-project/locations/us-central1/indexes/456"
        )
        mock_aiplatform.MatchingEngineIndex.create.return_value = mock_index

        config = IndexConfig(
            display_name="custom-index",
            dimensions=768,
            distance_metric=DistanceMetric.COSINE_DISTANCE,
            shard_size=ShardSize.SHARD_SIZE_MEDIUM,
            approximate_neighbors_count=150,
            leaf_node_embedding_count=1000,
        )
        result = manager.create_index(config)

        assert result == mock_index.resource_name
        call_args = mock_aiplatform.MatchingEngineIndex.create.call_args
        assert call_args[1]["display_name"] == "custom-index"
        metadata = call_args[1]["metadata"]
        assert metadata["config"]["dimensions"] == 768
        assert (
            metadata["config"]["distanceMeasureType"]
            == DistanceMetric.COSINE_DISTANCE.value
        )

    def test_get_index_status_success(
        self, mock_aiplatform: Mock, manager: VectorSearchIndexManager
    ) -> None:
        """Test getting index status."""
        mock_index = MagicMock()
        mock_index.deployed_indexes = []
        mock_index.metadata = {"state": "READY"}
        mock_aiplatform.MatchingEngineIndex.return_value = mock_index

        index_name = "projects/test-project/locations/us-central1/indexes/123"
        status = manager.get_index_status(index_name)

        assert status["state"] == "READY"
        assert "deployed_indexes" in status
        assert isinstance(status["deployed_indexes"], list)

    def test_get_index_status_not_found(
        self, mock_aiplatform: Mock, manager: VectorSearchIndexManager
    ) -> None:
        """Test getting status for non-existent index."""
        mock_aiplatform.MatchingEngineIndex.side_effect = Exception("Index not found")

        index_name = "projects/test-project/locations/us-central1/indexes/999"
        with pytest.raises(Exception, match="Index not found"):
            manager.get_index_status(index_name)

    def test_update_index_success(
        self, mock_aiplatform: Mock, manager: VectorSearchIndexManager
    ) -> None:
        """Test successful index update."""
        mock_index = MagicMock()
        mock_index.resource_name = (
            "projects/test-project/locations/us-central1/indexes/123"
        )
        mock_aiplatform.MatchingEngineIndex.return_value = mock_index

        index_name = "projects/test-project/locations/us-central1/indexes/123"
        config = IndexConfig(
            display_name="updated-index",
            dimensions=768,
            distance_metric=DistanceMetric.DOT_PRODUCT_DISTANCE,
        )

        result = manager.update_index(index_name, config)

        assert result == mock_index.resource_name
        mock_index.update.assert_called_once()

    def test_delete_index_success(
        self, mock_aiplatform: Mock, manager: VectorSearchIndexManager
    ) -> None:
        """Test successful index deletion."""
        mock_index = MagicMock()
        mock_aiplatform.MatchingEngineIndex.return_value = mock_index

        index_name = "projects/test-project/locations/us-central1/indexes/123"
        manager.delete_index(index_name)

        mock_index.delete.assert_called_once()

    def test_delete_index_not_found(
        self, mock_aiplatform: Mock, manager: VectorSearchIndexManager
    ) -> None:
        """Test deleting non-existent index."""
        mock_aiplatform.MatchingEngineIndex.side_effect = Exception("Index not found")

        index_name = "projects/test-project/locations/us-central1/indexes/999"
        with pytest.raises(Exception, match="Index not found"):
            manager.delete_index(index_name)

    def test_list_indexes_success(
        self, mock_aiplatform: Mock, manager: VectorSearchIndexManager
    ) -> None:
        """Test listing all indexes."""
        mock_index1 = MagicMock()
        mock_index1.resource_name = (
            "projects/test-project/locations/us-central1/indexes/1"
        )
        mock_index1.display_name = "index-1"

        mock_index2 = MagicMock()
        mock_index2.resource_name = (
            "projects/test-project/locations/us-central1/indexes/2"
        )
        mock_index2.display_name = "index-2"

        mock_aiplatform.MatchingEngineIndex.list.return_value = [
            mock_index1,
            mock_index2,
        ]

        indexes = manager.list_indexes()

        assert len(indexes) == 2
        assert indexes[0]["name"] == mock_index1.resource_name
        assert indexes[1]["name"] == mock_index2.resource_name


class TestIndexConfig:
    """Test suite for IndexConfig."""

    def test_index_config_valid(self) -> None:
        """Test creating valid index configuration."""
        config = IndexConfig(
            display_name="test-index",
            dimensions=768,
            distance_metric=DistanceMetric.DOT_PRODUCT_DISTANCE,
        )

        assert config.display_name == "test-index"
        assert config.dimensions == 768
        assert config.distance_metric == DistanceMetric.DOT_PRODUCT_DISTANCE
        assert config.shard_size == ShardSize.SHARD_SIZE_SMALL  # default

    def test_index_config_invalid_dimensions(self) -> None:
        """Test index config with invalid dimensions."""
        with pytest.raises(ValueError):
            IndexConfig(
                display_name="test-index",
                dimensions=0,
                distance_metric=DistanceMetric.DOT_PRODUCT_DISTANCE,
            )

    def test_index_config_custom_scann_params(self) -> None:
        """Test index config with custom ScaNN parameters."""
        config = IndexConfig(
            display_name="test-index",
            dimensions=768,
            distance_metric=DistanceMetric.COSINE_DISTANCE,
            shard_size=ShardSize.SHARD_SIZE_LARGE,
            approximate_neighbors_count=200,
            leaf_node_embedding_count=2000,
        )

        assert config.shard_size == ShardSize.SHARD_SIZE_LARGE
        assert config.approximate_neighbors_count == 200
        assert config.leaf_node_embedding_count == 2000

    def test_distance_metric_values(self) -> None:
        """Test all distance metric values are valid."""
        assert DistanceMetric.DOT_PRODUCT_DISTANCE == "DOT_PRODUCT_DISTANCE"
        assert DistanceMetric.COSINE_DISTANCE == "COSINE_DISTANCE"
        assert DistanceMetric.EUCLIDEAN_DISTANCE == "EUCLIDEAN_DISTANCE"

    def test_shard_size_values(self) -> None:
        """Test all shard size values are valid."""
        assert ShardSize.SHARD_SIZE_SMALL == "SHARD_SIZE_SMALL"
        assert ShardSize.SHARD_SIZE_MEDIUM == "SHARD_SIZE_MEDIUM"
        assert ShardSize.SHARD_SIZE_LARGE == "SHARD_SIZE_LARGE"
