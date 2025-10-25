"""Tests for embedding generator functionality."""

from unittest.mock import MagicMock, Mock, patch

from embedding_generator import EmbeddingGenerator
from shared_contracts import TextChunk, Vector768


class TestEmbeddingGenerator:
    """Test cases for EmbeddingGenerator."""

    def test_generate_single_embedding(self) -> None:
        """Test generating embedding for a single text chunk."""
        # Given
        chunk = TextChunk(
            chunk_id="chunk-1",
            content="What is the capital of France?",
            metadata={"source": "test"},
            token_count=10,
            source_file="test.html",
        )

        # Mock Vertex AI response
        mock_embedding = [0.1] * 768
        mock_response = Mock()
        mock_response.values = mock_embedding

        with (
            patch("vertexai.init"),
            patch(
                "vertexai.language_models.TextEmbeddingModel.from_pretrained"
            ) as mock_model,
        ):
            mock_instance = MagicMock()
            mock_instance.get_embeddings.return_value = [mock_response]
            mock_model.return_value = mock_instance

            generator = EmbeddingGenerator(
                project_id="test-project", location="us-central1"
            )

            # When
            result = generator.generate([chunk])

            # Then
            assert len(result) == 1
            assert isinstance(result[0], Vector768)
            assert result[0].chunk_id == "chunk-1"
            assert len(result[0].embedding) == 768
            assert result[0].model == "text-embedding-004"

    def test_generate_batch_embeddings(self) -> None:
        """Test generating embeddings for multiple chunks in batch."""
        # Given
        chunks = [
            TextChunk(
                chunk_id=f"chunk-{i}",
                content=f"Test content {i}",
                metadata={},
                token_count=5,
                source_file="test.html",
            )
            for i in range(3)
        ]

        # Mock Vertex AI responses
        mock_embeddings = [[0.1 * i] * 768 for i in range(3)]
        mock_responses = [Mock(values=emb) for emb in mock_embeddings]

        with (
            patch("vertexai.init"),
            patch(
                "vertexai.language_models.TextEmbeddingModel.from_pretrained"
            ) as mock_model,
        ):
            mock_instance = MagicMock()
            mock_instance.get_embeddings.return_value = mock_responses
            mock_model.return_value = mock_instance

            generator = EmbeddingGenerator(
                project_id="test-project", location="us-central1"
            )

            # When
            result = generator.generate(chunks)

            # Then
            assert len(result) == 3
            for i, vector in enumerate(result):
                assert vector.chunk_id == f"chunk-{i}"
                assert len(vector.embedding) == 768

    def test_generate_with_batch_processing(self) -> None:
        """Test batch processing with configurable batch size."""
        # Given
        chunks = [
            TextChunk(
                chunk_id=f"chunk-{i}",
                content=f"Test content {i}",
                metadata={},
                token_count=5,
                source_file="test.html",
            )
            for i in range(5)
        ]

        # Mock Vertex AI responses - need to return multiple responses for batches
        mock_embedding = [0.1] * 768

        def mock_get_embeddings(texts):
            # Return one mock response per input text
            return [Mock(values=mock_embedding) for _ in texts]

        with (
            patch("vertexai.init"),
            patch(
                "vertexai.language_models.TextEmbeddingModel.from_pretrained"
            ) as mock_model,
        ):
            mock_instance = MagicMock()
            mock_instance.get_embeddings.side_effect = mock_get_embeddings
            mock_model.return_value = mock_instance

            generator = EmbeddingGenerator(
                project_id="test-project", location="us-central1", batch_size=2
            )

            # When
            result = generator.generate(chunks)

            # Then
            assert len(result) == 5
            # Should have called API multiple times due to batch size
            assert mock_instance.get_embeddings.call_count >= 2

    def test_generate_with_retry_on_failure(self) -> None:
        """Test retry logic on API failures."""
        # Given
        chunk = TextChunk(
            chunk_id="chunk-1",
            content="Test content",
            metadata={},
            token_count=5,
            source_file="test.html",
        )

        mock_embedding = [0.1] * 768
        mock_response = Mock()
        mock_response.values = mock_embedding

        with (
            patch("vertexai.init"),
            patch(
                "vertexai.language_models.TextEmbeddingModel.from_pretrained"
            ) as mock_model,
        ):
            mock_instance = MagicMock()
            # Fail once, then succeed
            mock_instance.get_embeddings.side_effect = [
                Exception("API Error"),
                [mock_response],
            ]
            mock_model.return_value = mock_instance

            generator = EmbeddingGenerator(
                project_id="test-project", location="us-central1", max_retries=2
            )

            # When
            result = generator.generate([chunk])

            # Then
            assert len(result) == 1
            assert mock_instance.get_embeddings.call_count == 2

    def test_generate_empty_list(self) -> None:
        """Test handling of empty input list."""
        # Given
        with (
            patch("vertexai.init"),
            patch("vertexai.language_models.TextEmbeddingModel.from_pretrained"),
        ):
            generator = EmbeddingGenerator(
                project_id="test-project", location="us-central1"
            )

            # When
            result = generator.generate([])

            # Then
            assert result == []

    def test_initialization_defaults(self) -> None:
        """Test generator initialization with default parameters."""
        # Given/When
        with (
            patch("vertexai.init") as mock_init,
            patch("vertexai.language_models.TextEmbeddingModel.from_pretrained"),
        ):
            generator = EmbeddingGenerator(
                project_id="test-project", location="us-central1"
            )

            # Then
            mock_init.assert_called_once_with(
                project="test-project", location="us-central1"
            )
            assert generator.batch_size == 100
            assert generator.max_retries == 3
