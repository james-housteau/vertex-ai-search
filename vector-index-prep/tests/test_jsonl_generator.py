"""Tests for JSONL generator functionality."""

import json
from unittest.mock import MagicMock, mock_open, patch

import pytest
from shared_contracts import TextChunk, Vector768
from vector_index_prep.jsonl_generator import generate_jsonl


class TestJSONLGeneration:
    """Test JSONL generation from chunks and embeddings."""

    def test_generate_jsonl_basic(self) -> None:
        """Test basic JSONL generation with single chunk and embedding."""
        # Arrange
        chunks = [
            TextChunk(
                chunk_id="chunk_001",
                content="Test content",
                metadata={"source": "test.html"},
                token_count=5,
                source_file="test.html",
            )
        ]
        embeddings = [
            Vector768(
                chunk_id="chunk_001",
                embedding=[0.1] * 768,
                model="text-embedding-004",
            )
        ]
        output_path = "gs://test-bucket/output.jsonl"

        # Mock GCS client
        with patch("vector_index_prep.jsonl_generator.storage.Client") as mock_client:
            mock_bucket = MagicMock()
            mock_blob = MagicMock()
            mock_client.return_value.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob

            # Act
            generate_jsonl(chunks, embeddings, output_path)

            # Assert - verify GCS interaction
            mock_client.assert_called_once()
            mock_client.return_value.bucket.assert_called_once_with("test-bucket")
            mock_bucket.blob.assert_called_once_with("output.jsonl")
            mock_blob.upload_from_string.assert_called_once()

            # Verify JSONL content structure
            uploaded_content = mock_blob.upload_from_string.call_args[0][0]
            lines = uploaded_content.strip().split("\n")
            assert len(lines) == 1

            # Parse and validate JSONL format
            jsonl_obj = json.loads(lines[0])
            assert jsonl_obj["id"] == "chunk_001"
            assert len(jsonl_obj["embedding"]) == 768
            assert jsonl_obj["embedding"][0] == 0.1
            assert "restricts" in jsonl_obj

    def test_generate_jsonl_multiple_chunks(self) -> None:
        """Test JSONL generation with multiple chunks and embeddings."""
        # Arrange
        chunks = [
            TextChunk(
                chunk_id=f"chunk_{i:03d}",
                content=f"Content {i}",
                metadata={"source": f"test{i}.html"},
                token_count=10,
                source_file=f"test{i}.html",
            )
            for i in range(3)
        ]
        embeddings = [
            Vector768(
                chunk_id=f"chunk_{i:03d}",
                embedding=[float(i)] * 768,
                model="text-embedding-004",
            )
            for i in range(3)
        ]
        output_path = "gs://test-bucket/output.jsonl"

        # Mock GCS client
        with patch("vector_index_prep.jsonl_generator.storage.Client") as mock_client:
            mock_bucket = MagicMock()
            mock_blob = MagicMock()
            mock_client.return_value.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob

            # Act
            generate_jsonl(chunks, embeddings, output_path)

            # Assert
            uploaded_content = mock_blob.upload_from_string.call_args[0][0]
            lines = uploaded_content.strip().split("\n")
            assert len(lines) == 3

            # Verify each line
            for i, line in enumerate(lines):
                jsonl_obj = json.loads(line)
                assert jsonl_obj["id"] == f"chunk_{i:03d}"
                assert jsonl_obj["embedding"][0] == float(i)

    def test_generate_jsonl_mismatched_ids_raises_error(self) -> None:
        """Test that mismatched chunk_ids raise ValueError."""
        # Arrange
        chunks = [
            TextChunk(
                chunk_id="chunk_001",
                content="Test content",
                metadata={},
                token_count=5,
                source_file="test.html",
            )
        ]
        embeddings = [
            Vector768(
                chunk_id="chunk_999",  # Mismatched ID
                embedding=[0.1] * 768,
            )
        ]
        output_path = "gs://test-bucket/output.jsonl"

        # Act & Assert
        with pytest.raises(ValueError, match="No embedding found for chunk"):
            generate_jsonl(chunks, embeddings, output_path)

    def test_generate_jsonl_missing_embedding_raises_error(self) -> None:
        """Test that missing embedding for chunk raises ValueError."""
        # Arrange
        chunks = [
            TextChunk(
                chunk_id="chunk_001",
                content="Test content",
                metadata={},
                token_count=5,
                source_file="test.html",
            ),
            TextChunk(
                chunk_id="chunk_002",
                content="More content",
                metadata={},
                token_count=5,
                source_file="test.html",
            ),
        ]
        embeddings = [
            Vector768(
                chunk_id="chunk_001",
                embedding=[0.1] * 768,
            )
            # Missing embedding for chunk_002
        ]
        output_path = "gs://test-bucket/output.jsonl"

        # Act & Assert
        with pytest.raises(ValueError, match="No embedding found for chunk"):
            generate_jsonl(chunks, embeddings, output_path)

    def test_generate_jsonl_empty_lists_raises_error(self) -> None:
        """Test that empty chunk/embedding lists raise ValueError."""
        # Arrange
        chunks = []
        embeddings = []
        output_path = "gs://test-bucket/output.jsonl"

        # Act & Assert
        with pytest.raises(ValueError, match="Chunks and embeddings cannot be empty"):
            generate_jsonl(chunks, embeddings, output_path)

    def test_generate_jsonl_metadata_in_restricts(self) -> None:
        """Test that chunk metadata is converted to restricts format."""
        # Arrange
        chunks = [
            TextChunk(
                chunk_id="chunk_001",
                content="Test content",
                metadata={
                    "source_file": "test.html",
                    "section": "intro",
                },
                token_count=5,
                source_file="test.html",
            )
        ]
        embeddings = [
            Vector768(
                chunk_id="chunk_001",
                embedding=[0.1] * 768,
            )
        ]
        output_path = "gs://test-bucket/output.jsonl"

        # Mock GCS client
        with patch("vector_index_prep.jsonl_generator.storage.Client") as mock_client:
            mock_bucket = MagicMock()
            mock_blob = MagicMock()
            mock_client.return_value.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob

            # Act
            generate_jsonl(chunks, embeddings, output_path)

            # Assert
            uploaded_content = mock_blob.upload_from_string.call_args[0][0]
            jsonl_obj = json.loads(uploaded_content.strip())

            # Verify restricts format
            assert "restricts" in jsonl_obj
            assert isinstance(jsonl_obj["restricts"], list)
            # Should have restricts for each metadata key
            assert len(jsonl_obj["restricts"]) >= 1

    def test_generate_jsonl_local_file_path(self) -> None:
        """Test generation with local file path (no GCS upload)."""
        # Arrange
        chunks = [
            TextChunk(
                chunk_id="chunk_001",
                content="Test content",
                metadata={},
                token_count=5,
                source_file="test.html",
            )
        ]
        embeddings = [
            Vector768(
                chunk_id="chunk_001",
                embedding=[0.1] * 768,
            )
        ]
        output_path = "/tmp/output.jsonl"

        # Mock file open
        m = mock_open()
        with patch("builtins.open", m):
            # Act
            generate_jsonl(chunks, embeddings, output_path)

            # Assert
            m.assert_called_once_with(output_path, "w")
            # Verify write was called
            handle = m()
            assert handle.write.called

            # Reconstruct written content
            written_content = "".join(
                call.args[0] for call in handle.write.call_args_list
            )
            jsonl_obj = json.loads(written_content.strip())
            assert jsonl_obj["id"] == "chunk_001"
