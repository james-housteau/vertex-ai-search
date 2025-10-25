"""Configuration models for Vector Search Index."""

from enum import Enum

from pydantic import BaseModel, Field


class DistanceMetric(str, Enum):
    """Supported distance metrics for vector search."""

    DOT_PRODUCT_DISTANCE = "DOT_PRODUCT_DISTANCE"
    COSINE_DISTANCE = "COSINE_DISTANCE"
    EUCLIDEAN_DISTANCE = "EUCLIDEAN_DISTANCE"


class ShardSize(str, Enum):
    """Supported shard sizes for index."""

    SHARD_SIZE_SMALL = "SHARD_SIZE_SMALL"
    SHARD_SIZE_MEDIUM = "SHARD_SIZE_MEDIUM"
    SHARD_SIZE_LARGE = "SHARD_SIZE_LARGE"


class IndexConfig(BaseModel):
    """Configuration for Vector Search Index.

    Attributes:
        display_name: Human-readable name for the index.
        dimensions: Number of dimensions in vectors (e.g., 768 for text-embedding-004).
        distance_metric: Distance metric to use for similarity search.
        shard_size: Size of index shards for performance tuning.
        approximate_neighbors_count: Number of approximate neighbors for ScaNN.
        leaf_node_embedding_count: Number of embeddings per leaf node.
    """

    display_name: str = Field(..., min_length=1)
    dimensions: int = Field(..., gt=0)
    distance_metric: DistanceMetric
    shard_size: ShardSize = ShardSize.SHARD_SIZE_SMALL
    approximate_neighbors_count: int = Field(default=100, gt=0)
    leaf_node_embedding_count: int = Field(default=500, gt=0)
