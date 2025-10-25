"""Vector Search Index module for Vertex AI Vector Search operations."""

from vector_search_index.config import DistanceMetric, IndexConfig, ShardSize
from vector_search_index.manager import VectorSearchIndexManager

__version__ = "0.1.0"

__all__ = [
    "VectorSearchIndexManager",
    "IndexConfig",
    "DistanceMetric",
    "ShardSize",
]
