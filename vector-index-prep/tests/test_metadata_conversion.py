"""Tests for metadata to restricts conversion."""

from vector_index_prep.jsonl_generator import _metadata_to_restricts


class TestMetadataToRestricts:
    """Test metadata to restricts conversion."""

    def test_metadata_to_restricts_empty(self) -> None:
        """Test conversion with empty metadata."""
        # Arrange
        metadata = {}

        # Act
        result = _metadata_to_restricts(metadata)

        # Assert
        assert result == []

    def test_metadata_to_restricts_single_field(self) -> None:
        """Test conversion with single metadata field."""
        # Arrange
        metadata = {"source_file": "test.html"}

        # Act
        result = _metadata_to_restricts(metadata)

        # Assert
        assert len(result) == 1
        assert result[0]["namespace"] == "source_file"
        assert result[0]["allow"] == ["test.html"]

    def test_metadata_to_restricts_multiple_fields(self) -> None:
        """Test conversion with multiple metadata fields."""
        # Arrange
        metadata = {
            "source_file": "test.html",
            "section": "intro",
            "category": "docs",
        }

        # Act
        result = _metadata_to_restricts(metadata)

        # Assert
        assert len(result) == 3
        namespaces = {r["namespace"] for r in result}
        assert namespaces == {"source_file", "section", "category"}

    def test_metadata_to_restricts_numeric_values(self) -> None:
        """Test conversion with numeric metadata values."""
        # Arrange
        metadata = {"page_number": 42, "score": 0.95}

        # Act
        result = _metadata_to_restricts(metadata)

        # Assert
        assert len(result) == 2
        # Values should be converted to strings
        for restrict in result:
            assert isinstance(restrict["allow"][0], str)

    def test_metadata_to_restricts_list_values(self) -> None:
        """Test conversion with list metadata values."""
        # Arrange
        metadata = {"tags": ["tag1", "tag2", "tag3"]}

        # Act
        result = _metadata_to_restricts(metadata)

        # Assert
        assert len(result) == 1
        assert result[0]["namespace"] == "tags"
        assert result[0]["allow"] == ["tag1", "tag2", "tag3"]
