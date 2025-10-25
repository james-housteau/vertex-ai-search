"""Tests for Natural Questions dataset processing functionality."""

import gzip
import json
import tempfile
from pathlib import Path

import pytest
from html_extractor.extractor import NaturalQuestionsExtractor


@pytest.fixture
def temp_jsonl_gz():
    """Create temporary JSONL.gz file with sample data."""
    data = [
        {
            "example_id": "1",
            "document_title": "Title 1",
            "document_html": "<html>Content 1</html>",
            "document_url": "http://example1.com",
        },
        {
            "example_id": "2",
            "document_title": "Title 2",
            "document_html": "<html>Content 2</html>",
            "document_url": "http://example2.com",
        },
        {
            "example_id": "3",
            "document_title": "Title 1",
            "document_html": "<html>Different content</html>",
            "document_url": "http://example3.com",
        },
    ]

    with tempfile.NamedTemporaryFile(mode="wb", suffix=".jsonl.gz", delete=False) as f:
        with gzip.open(f.name, "wt", encoding="utf-8") as gz_file:
            for entry in data:
                gz_file.write(json.dumps(entry) + "\n")
        return Path(f.name)


class TestNaturalQuestionsExtractor:
    """Test Natural Questions dataset processing."""

    def test_extract_html_documents_success(self, temp_jsonl_gz):
        """Test successful extraction of HTML documents."""
        extractor = NaturalQuestionsExtractor()
        result = extractor.extract_html_documents(temp_jsonl_gz)

        assert result.success is True
        assert len(result.documents) == 2
        assert result.stats.total_entries == 3
        assert result.stats.unique_documents == 2
        assert result.stats.duplicates_removed == 1

    def test_extract_html_documents_file_not_found(self):
        """Test extraction with non-existent file."""
        extractor = NaturalQuestionsExtractor()
        result = extractor.extract_html_documents(Path("/nonexistent/file.jsonl.gz"))

        assert result.success is False
        assert "Failed to process JSONL.gz file" in result.error_message

    def test_deduplicate_by_title(self):
        """Test deduplication by document title."""
        extractor = NaturalQuestionsExtractor()
        documents = [
            {"title": "Title A", "content": "Content 1"},
            {"title": "Title B", "content": "Content 2"},
            {"title": "Title A", "content": "Content 3"},
        ]

        unique_docs = extractor.deduplicate_by_title(documents)

        assert len(unique_docs) == 2
        assert unique_docs[0]["title"] == "Title A"
        assert unique_docs[1]["title"] == "Title B"

    def test_generate_statistics(self):
        """Test statistics generation."""
        extractor = NaturalQuestionsExtractor()
        all_docs = [{"title": "A"}, {"title": "B"}, {"title": "A"}]
        unique_docs = [{"title": "A"}, {"title": "B"}]

        stats = extractor.generate_statistics(all_docs, unique_docs, 5)

        assert stats.total_entries == 5
        assert stats.unique_documents == 2
        assert stats.duplicates_removed == 1

    def test_empty_file_handling(self):
        """Test handling of empty JSONL.gz file."""
        with tempfile.NamedTemporaryFile(
            mode="wb", suffix=".jsonl.gz", delete=False
        ) as f:
            with gzip.open(f.name, "wt", encoding="utf-8") as _:
                pass

            extractor = NaturalQuestionsExtractor()
            result = extractor.extract_html_documents(Path(f.name))

            assert result.success is True
            assert len(result.documents) == 0
            assert result.stats.total_entries == 0
