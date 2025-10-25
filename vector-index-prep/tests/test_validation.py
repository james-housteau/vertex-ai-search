"""Tests for input validation."""

import pytest
from shared_contracts import TextChunk, Vector768
from vector_index_prep.jsonl_generator import generate_jsonl


class TestValidation:
    """Test input validation for generate_jsonl."""

    def test_empty_chunks_raises_error(self) -> None:
        """Test that empty chunks list raises ValueError."""
        # Arrange
        chunks = []
        embeddings = [
            Vector768(chunk_id="chunk_001", embedding=[0.1] * 768),
        ]
        output_path = "gs://test-bucket/output.jsonl"

        # Act & Assert
        with pytest.raises(ValueError, match="Chunks and embeddings cannot be empty"):
            generate_jsonl(chunks, embeddings, output_path)

    def test_empty_embeddings_raises_error(self) -> None:
        """Test that empty embeddings list raises ValueError."""
        # Arrange
        chunks = [
            TextChunk(
                chunk_id="chunk_001",
                content="Test",
                metadata={},
                token_count=1,
                source_file="test.html",
            )
        ]
        embeddings = []
        output_path = "gs://test-bucket/output.jsonl"

        # Act & Assert
        with pytest.raises(ValueError, match="Chunks and embeddings cannot be empty"):
            generate_jsonl(chunks, embeddings, output_path)

    def test_both_empty_raises_error(self) -> None:
        """Test that both empty lists raise ValueError."""
        # Arrange
        chunks = []
        embeddings = []
        output_path = "gs://test-bucket/output.jsonl"

        # Act & Assert
        with pytest.raises(ValueError, match="Chunks and embeddings cannot be empty"):
            generate_jsonl(chunks, embeddings, output_path)

    def test_chunk_without_embedding_raises_error(self) -> None:
        """Test that chunk without matching embedding raises ValueError."""
        # Arrange
        chunks = [
            TextChunk(
                chunk_id="chunk_001",
                content="Test",
                metadata={},
                token_count=1,
                source_file="test.html",
            ),
            TextChunk(
                chunk_id="chunk_002",
                content="Test 2",
                metadata={},
                token_count=2,
                source_file="test.html",
            ),
        ]
        embeddings = [
            Vector768(chunk_id="chunk_001", embedding=[0.1] * 768),
            # chunk_002 has no embedding
        ]
        output_path = "gs://test-bucket/output.jsonl"

        # Act & Assert
        with pytest.raises(ValueError, match="No embedding found for chunk: chunk_002"):
            generate_jsonl(chunks, embeddings, output_path)
