"""Vertex AI Agent Builder data store management for unstructured HTML documents."""

from .datastore_manager import VertexDataStoreManager
from .models import DataStoreResult, ImportProgress

__version__ = "0.1.0"
__all__ = [
    "VertexDataStoreManager",
    "DataStoreResult",
    "ImportProgress",
]
