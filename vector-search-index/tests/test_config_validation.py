"""Additional tests for IndexConfig validation."""

import pytest
from pydantic import ValidationError
from vector_search_index.config import DistanceMetric, IndexConfig, ShardSize


class TestIndexConfigEdgeCases:
    """Test edge cases and boundary conditions for IndexConfig."""

    def test_index_config_minimum_valid_dimensions(self) -> None:
        """Test index config with minimum valid dimensions (1)."""
        config = IndexConfig(
            display_name="test",
            dimensions=1,
            distance_metric=DistanceMetric.DOT_PRODUCT_DISTANCE,
        )
        assert config.dimensions == 1

    def test_index_config_large_dimensions(self) -> None:
        """Test index config with large dimension values."""
        config = IndexConfig(
            display_name="test",
            dimensions=2048,
            distance_metric=DistanceMetric.DOT_PRODUCT_DISTANCE,
        )
        assert config.dimensions == 2048

    def test_index_config_negative_dimensions(self) -> None:
        """Test that negative dimensions are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            IndexConfig(
                display_name="test",
                dimensions=-1,
                distance_metric=DistanceMetric.DOT_PRODUCT_DISTANCE,
            )
        assert "dimensions" in str(exc_info.value).lower()

    def test_index_config_zero_approximate_neighbors(self) -> None:
        """Test that zero approximate neighbors count is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            IndexConfig(
                display_name="test",
                dimensions=768,
                distance_metric=DistanceMetric.DOT_PRODUCT_DISTANCE,
                approximate_neighbors_count=0,
            )
        assert "approximate_neighbors_count" in str(exc_info.value).lower()

    def test_index_config_zero_leaf_node_count(self) -> None:
        """Test that zero leaf node embedding count is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            IndexConfig(
                display_name="test",
                dimensions=768,
                distance_metric=DistanceMetric.DOT_PRODUCT_DISTANCE,
                leaf_node_embedding_count=0,
            )
        assert "leaf_node_embedding_count" in str(exc_info.value).lower()

    def test_index_config_empty_display_name(self) -> None:
        """Test that empty display name is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            IndexConfig(
                display_name="",
                dimensions=768,
                distance_metric=DistanceMetric.DOT_PRODUCT_DISTANCE,
            )
        assert "display_name" in str(exc_info.value).lower()

    def test_index_config_all_distance_metrics(self) -> None:
        """Test that all distance metrics are accepted."""
        for metric in DistanceMetric:
            config = IndexConfig(
                display_name="test",
                dimensions=768,
                distance_metric=metric,
            )
            assert config.distance_metric == metric

    def test_index_config_all_shard_sizes(self) -> None:
        """Test that all shard sizes are accepted."""
        for shard_size in ShardSize:
            config = IndexConfig(
                display_name="test",
                dimensions=768,
                distance_metric=DistanceMetric.DOT_PRODUCT_DISTANCE,
                shard_size=shard_size,
            )
            assert config.shard_size == shard_size

    def test_index_config_defaults(self) -> None:
        """Test that default values are set correctly."""
        config = IndexConfig(
            display_name="test",
            dimensions=768,
            distance_metric=DistanceMetric.DOT_PRODUCT_DISTANCE,
        )
        assert config.shard_size == ShardSize.SHARD_SIZE_SMALL
        assert config.approximate_neighbors_count == 100
        assert config.leaf_node_embedding_count == 500

    def test_index_config_custom_all_parameters(self) -> None:
        """Test config with all custom parameters."""
        config = IndexConfig(
            display_name="custom-test-index",
            dimensions=1536,
            distance_metric=DistanceMetric.EUCLIDEAN_DISTANCE,
            shard_size=ShardSize.SHARD_SIZE_LARGE,
            approximate_neighbors_count=300,
            leaf_node_embedding_count=3000,
        )
        assert config.display_name == "custom-test-index"
        assert config.dimensions == 1536
        assert config.distance_metric == DistanceMetric.EUCLIDEAN_DISTANCE
        assert config.shard_size == ShardSize.SHARD_SIZE_LARGE
        assert config.approximate_neighbors_count == 300
        assert config.leaf_node_embedding_count == 3000
