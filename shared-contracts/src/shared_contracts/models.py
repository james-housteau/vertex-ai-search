"""Data models for vector search pipeline."""

from typing import Any

from pydantic import BaseModel, Field, field_validator

# Constants
EMBEDDING_DIMENSIONS = 768
DEFAULT_EMBEDDING_MODEL = "text-embedding-004"


class TextChunk(BaseModel):
    """Represents a chunk of text extracted from HTML documents.

    Attributes:
        chunk_id: Unique identifier for the chunk.
        content: The actual text content.
        metadata: Metadata about the chunk.
        token_count: Number of tokens in the chunk.
        source_file: Original source file name.
    """

    chunk_id: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    metadata: dict[str, Any]
    token_count: int = Field(..., ge=1)
    source_file: str = Field(..., min_length=1)


class Vector768(BaseModel):
    """Represents a 768-dimensional embedding vector.

    Attributes:
        chunk_id: Unique identifier for the chunk.
        embedding: 768-dimensional vector.
        model: Model used to generate the embedding.
    """

    chunk_id: str = Field(..., min_length=1)
    embedding: list[float]
    model: str = DEFAULT_EMBEDDING_MODEL

    @field_validator("embedding")
    @classmethod
    def validate_embedding_dimensions(cls, v: list[float]) -> list[float]:
        """Validate that embedding has exactly 768 dimensions."""
        if len(v) != EMBEDDING_DIMENSIONS:
            raise ValueError(
                f"Embedding must have exactly {EMBEDDING_DIMENSIONS} dimensions, "
                f"got {len(v)}"
            )
        return v


class SearchMatch(BaseModel):
    """Represents a search result with relevance score.

    Attributes:
        chunk_id: Unique identifier for the matched chunk.
        score: Relevance score between 0.0 and 1.0.
        content: Matched content.
        metadata: Metadata about the match.
    """

    chunk_id: str = Field(..., min_length=1)
    score: float = Field(..., ge=0.0, le=1.0)
    content: str
    metadata: dict[str, Any]
