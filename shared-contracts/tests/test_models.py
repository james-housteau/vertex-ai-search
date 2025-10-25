"""Comprehensive tests for shared data contracts."""

import pytest
from pydantic import ValidationError
from shared_contracts.models import SearchMatch, TextChunk, Vector768


class TestTextChunk:
    """Test suite for TextChunk dataclass."""

    def test_text_chunk_creation_valid(self) -> None:
        """Test creating a valid TextChunk."""
        chunk = TextChunk(
            chunk_id="chunk_001",
            content="This is test content",
            metadata={"source": "test.html", "section": "intro"},
            token_count=5,
            source_file="test.html",
        )
        assert chunk.chunk_id == "chunk_001"
        assert chunk.content == "This is test content"
        assert chunk.metadata == {"source": "test.html", "section": "intro"}
        assert chunk.token_count == 5
        assert chunk.source_file == "test.html"

    def test_text_chunk_chunk_id_required(self) -> None:
        """Test that chunk_id is required."""
        with pytest.raises(ValidationError) as exc_info:
            TextChunk(
                content="Test",
                metadata={},
                token_count=1,
                source_file="test.html",
            )
        assert "chunk_id" in str(exc_info.value)

    def test_text_chunk_chunk_id_non_empty(self) -> None:
        """Test that chunk_id cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            TextChunk(
                chunk_id="",
                content="Test",
                metadata={},
                token_count=1,
                source_file="test.html",
            )
        assert "chunk_id" in str(exc_info.value).lower()

    def test_text_chunk_content_required(self) -> None:
        """Test that content is required."""
        with pytest.raises(ValidationError) as exc_info:
            TextChunk(
                chunk_id="chunk_001",
                metadata={},
                token_count=1,
                source_file="test.html",
            )
        assert "content" in str(exc_info.value)

    def test_text_chunk_content_non_empty(self) -> None:
        """Test that content cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            TextChunk(
                chunk_id="chunk_001",
                content="",
                metadata={},
                token_count=1,
                source_file="test.html",
            )
        assert "content" in str(exc_info.value).lower()

    def test_text_chunk_metadata_required(self) -> None:
        """Test that metadata is required."""
        with pytest.raises(ValidationError) as exc_info:
            TextChunk(
                chunk_id="chunk_001",
                content="Test",
                token_count=1,
                source_file="test.html",
            )
        assert "metadata" in str(exc_info.value)

    def test_text_chunk_token_count_required(self) -> None:
        """Test that token_count is required."""
        with pytest.raises(ValidationError) as exc_info:
            TextChunk(
                chunk_id="chunk_001",
                content="Test",
                metadata={},
                source_file="test.html",
            )
        assert "token_count" in str(exc_info.value)

    def test_text_chunk_token_count_positive(self) -> None:
        """Test that token_count must be positive."""
        with pytest.raises(ValidationError) as exc_info:
            TextChunk(
                chunk_id="chunk_001",
                content="Test",
                metadata={},
                token_count=0,
                source_file="test.html",
            )
        assert "token_count" in str(exc_info.value).lower()

        with pytest.raises(ValidationError) as exc_info:
            TextChunk(
                chunk_id="chunk_001",
                content="Test",
                metadata={},
                token_count=-1,
                source_file="test.html",
            )
        assert "token_count" in str(exc_info.value).lower()

    def test_text_chunk_source_file_required(self) -> None:
        """Test that source_file is required."""
        with pytest.raises(ValidationError) as exc_info:
            TextChunk(
                chunk_id="chunk_001",
                content="Test",
                metadata={},
                token_count=1,
            )
        assert "source_file" in str(exc_info.value)

    def test_text_chunk_source_file_non_empty(self) -> None:
        """Test that source_file cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            TextChunk(
                chunk_id="chunk_001",
                content="Test",
                metadata={},
                token_count=1,
                source_file="",
            )
        assert "source_file" in str(exc_info.value).lower()

    def test_text_chunk_metadata_can_be_empty_dict(self) -> None:
        """Test that metadata can be an empty dict."""
        chunk = TextChunk(
            chunk_id="chunk_001",
            content="Test",
            metadata={},
            token_count=1,
            source_file="test.html",
        )
        assert chunk.metadata == {}


class TestVector768:
    """Test suite for Vector768 dataclass."""

    def test_vector768_creation_valid(self) -> None:
        """Test creating a valid Vector768."""
        embedding = [0.1] * 768
        vector = Vector768(
            chunk_id="chunk_001",
            embedding=embedding,
            model="text-embedding-004",
        )
        assert vector.chunk_id == "chunk_001"
        assert len(vector.embedding) == 768
        assert vector.model == "text-embedding-004"

    def test_vector768_default_model(self) -> None:
        """Test that model has a default value."""
        embedding = [0.1] * 768
        vector = Vector768(
            chunk_id="chunk_001",
            embedding=embedding,
        )
        assert vector.model == "text-embedding-004"

    def test_vector768_chunk_id_required(self) -> None:
        """Test that chunk_id is required."""
        embedding = [0.1] * 768
        with pytest.raises(ValidationError) as exc_info:
            Vector768(embedding=embedding)
        assert "chunk_id" in str(exc_info.value)

    def test_vector768_chunk_id_non_empty(self) -> None:
        """Test that chunk_id cannot be empty."""
        embedding = [0.1] * 768
        with pytest.raises(ValidationError) as exc_info:
            Vector768(chunk_id="", embedding=embedding)
        assert "chunk_id" in str(exc_info.value).lower()

    def test_vector768_embedding_required(self) -> None:
        """Test that embedding is required."""
        with pytest.raises(ValidationError) as exc_info:
            Vector768(chunk_id="chunk_001")
        assert "embedding" in str(exc_info.value)

    def test_vector768_embedding_exactly_768_dimensions(self) -> None:
        """Test that embedding must have exactly 768 dimensions."""
        # Test with 767 dimensions
        with pytest.raises(ValidationError) as exc_info:
            Vector768(
                chunk_id="chunk_001",
                embedding=[0.1] * 767,
            )
        assert (
            "768" in str(exc_info.value) or "embedding" in str(exc_info.value).lower()
        )

        # Test with 769 dimensions
        with pytest.raises(ValidationError) as exc_info:
            Vector768(
                chunk_id="chunk_001",
                embedding=[0.1] * 769,
            )
        assert (
            "768" in str(exc_info.value) or "embedding" in str(exc_info.value).lower()
        )

    def test_vector768_embedding_empty_list(self) -> None:
        """Test that embedding cannot be an empty list."""
        with pytest.raises(ValidationError) as exc_info:
            Vector768(
                chunk_id="chunk_001",
                embedding=[],
            )
        assert (
            "768" in str(exc_info.value) or "embedding" in str(exc_info.value).lower()
        )

    def test_vector768_model_required(self) -> None:
        """Test that model is required (has default)."""
        embedding = [0.1] * 768
        vector = Vector768(chunk_id="chunk_001", embedding=embedding)
        assert vector.model == "text-embedding-004"

    def test_vector768_custom_model(self) -> None:
        """Test that model can be customized."""
        embedding = [0.1] * 768
        vector = Vector768(
            chunk_id="chunk_001",
            embedding=embedding,
            model="custom-model",
        )
        assert vector.model == "custom-model"


class TestSearchMatch:
    """Test suite for SearchMatch dataclass."""

    def test_search_match_creation_valid(self) -> None:
        """Test creating a valid SearchMatch."""
        match = SearchMatch(
            chunk_id="chunk_001",
            score=0.95,
            content="Relevant content",
            metadata={"source": "test.html"},
        )
        assert match.chunk_id == "chunk_001"
        assert match.score == 0.95
        assert match.content == "Relevant content"
        assert match.metadata == {"source": "test.html"}

    def test_search_match_chunk_id_required(self) -> None:
        """Test that chunk_id is required."""
        with pytest.raises(ValidationError) as exc_info:
            SearchMatch(
                score=0.95,
                content="Test",
                metadata={},
            )
        assert "chunk_id" in str(exc_info.value)

    def test_search_match_chunk_id_non_empty(self) -> None:
        """Test that chunk_id cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            SearchMatch(
                chunk_id="",
                score=0.95,
                content="Test",
                metadata={},
            )
        assert "chunk_id" in str(exc_info.value).lower()

    def test_search_match_score_required(self) -> None:
        """Test that score is required."""
        with pytest.raises(ValidationError) as exc_info:
            SearchMatch(
                chunk_id="chunk_001",
                content="Test",
                metadata={},
            )
        assert "score" in str(exc_info.value)

    def test_search_match_score_range_valid(self) -> None:
        """Test that score accepts values in 0.0-1.0 range."""
        # Test lower bound
        match = SearchMatch(
            chunk_id="chunk_001",
            score=0.0,
            content="Test",
            metadata={},
        )
        assert match.score == 0.0

        # Test upper bound
        match = SearchMatch(
            chunk_id="chunk_001",
            score=1.0,
            content="Test",
            metadata={},
        )
        assert match.score == 1.0

        # Test middle value
        match = SearchMatch(
            chunk_id="chunk_001",
            score=0.5,
            content="Test",
            metadata={},
        )
        assert match.score == 0.5

    def test_search_match_score_below_range(self) -> None:
        """Test that score cannot be below 0.0."""
        with pytest.raises(ValidationError) as exc_info:
            SearchMatch(
                chunk_id="chunk_001",
                score=-0.1,
                content="Test",
                metadata={},
            )
        assert "score" in str(exc_info.value).lower()

    def test_search_match_score_above_range(self) -> None:
        """Test that score cannot be above 1.0."""
        with pytest.raises(ValidationError) as exc_info:
            SearchMatch(
                chunk_id="chunk_001",
                score=1.1,
                content="Test",
                metadata={},
            )
        assert "score" in str(exc_info.value).lower()

    def test_search_match_content_required(self) -> None:
        """Test that content is required."""
        with pytest.raises(ValidationError) as exc_info:
            SearchMatch(
                chunk_id="chunk_001",
                score=0.95,
                metadata={},
            )
        assert "content" in str(exc_info.value)

    def test_search_match_content_can_be_empty(self) -> None:
        """Test that content can be empty string (edge case)."""
        # While unusual, search results might have empty content
        match = SearchMatch(
            chunk_id="chunk_001",
            score=0.95,
            content="",
            metadata={},
        )
        assert match.content == ""

    def test_search_match_metadata_required(self) -> None:
        """Test that metadata is required."""
        with pytest.raises(ValidationError) as exc_info:
            SearchMatch(
                chunk_id="chunk_001",
                score=0.95,
                content="Test",
            )
        assert "metadata" in str(exc_info.value)

    def test_search_match_metadata_can_be_empty_dict(self) -> None:
        """Test that metadata can be an empty dict."""
        match = SearchMatch(
            chunk_id="chunk_001",
            score=0.95,
            content="Test",
            metadata={},
        )
        assert match.metadata == {}
