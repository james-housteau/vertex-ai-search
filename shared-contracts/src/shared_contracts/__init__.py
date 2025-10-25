"""Shared data contracts for the vector search pipeline."""

from shared_contracts.models import (
    DEFAULT_EMBEDDING_MODEL,
    EMBEDDING_DIMENSIONS,
    SearchMatch,
    TextChunk,
    Vector768,
)

__version__ = "0.1.0"
__all__ = [
    "TextChunk",
    "Vector768",
    "SearchMatch",
    "EMBEDDING_DIMENSIONS",
    "DEFAULT_EMBEDDING_MODEL",
]
