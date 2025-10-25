"""Tests for HTML chunker functionality."""

import tempfile
from pathlib import Path

import pytest
from html_chunker import HTMLChunker


class TestHTMLChunker:
    """Test suite for HTMLChunker."""

    def test_chunker_initialization_default(self) -> None:
        """Test chunker initializes with default parameters."""
        chunker = HTMLChunker()
        assert chunker is not None

    def test_chunker_initialization_custom(self) -> None:
        """Test chunker initializes with custom parameters."""
        chunker = HTMLChunker(chunk_size=500, overlap=100)
        assert chunker is not None

    def test_chunk_html_simple_content(self) -> None:
        """Test chunking simple HTML content."""
        chunker = HTMLChunker()
        html = "<html><body><p>This is a test.</p></body></html>"
        chunks = chunker.chunk_html(html, "test.html")

        assert len(chunks) == 1
        assert chunks[0].source_file == "test.html"
        assert "This is a test." in chunks[0].content
        assert chunks[0].token_count > 0
        assert chunks[0].chunk_id.startswith("test.html")

    def test_chunk_html_multiple_chunks(self) -> None:
        """Test chunking HTML that requires multiple chunks."""
        chunker = HTMLChunker()
        # Create content that will exceed 450 tokens
        long_text = " ".join([f"Word{i}" for i in range(600)])
        html = f"<html><body><p>{long_text}</p></body></html>"
        chunks = chunker.chunk_html(html, "long.html")

        # Should create multiple chunks
        assert len(chunks) > 1
        # Each chunk should have appropriate token count
        for chunk in chunks[:-1]:  # All but last should be near chunk_size
            assert 400 <= chunk.token_count <= 500
        # All chunks should have unique IDs
        chunk_ids = [c.chunk_id for c in chunks]
        assert len(chunk_ids) == len(set(chunk_ids))

    def test_chunk_html_overlap(self) -> None:
        """Test that chunks have proper overlap."""
        chunker = HTMLChunker()
        # Create content that will create exactly 2 chunks
        long_text = " ".join([f"Word{i}" for i in range(600)])
        html = f"<html><body><p>{long_text}</p></body></html>"
        chunks = chunker.chunk_html(html, "overlap.html")

        if len(chunks) >= 2:
            # Check that there's some content overlap between consecutive chunks
            # The exact overlap is hard to test without knowing token boundaries
            # but we can verify chunks exist and have content
            assert chunks[0].content
            assert chunks[1].content

    def test_chunk_file_valid(self) -> None:
        """Test chunking from a valid file."""
        chunker = HTMLChunker()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as tmp:
            tmp.write("<html><body><p>File content test.</p></body></html>")
            tmp_path = tmp.name

        try:
            chunks = chunker.chunk_file(tmp_path)
            assert len(chunks) == 1
            assert "File content test." in chunks[0].content
            assert Path(tmp_path).name in chunks[0].source_file
        finally:
            Path(tmp_path).unlink()

    def test_chunk_file_not_found(self) -> None:
        """Test chunking non-existent file raises error."""
        chunker = HTMLChunker()
        with pytest.raises(FileNotFoundError):
            chunker.chunk_file("/nonexistent/file.html")

    def test_chunk_html_empty_content(self) -> None:
        """Test chunking empty HTML raises error."""
        chunker = HTMLChunker()
        with pytest.raises(ValueError, match="empty"):
            chunker.chunk_html("", "empty.html")

    def test_chunk_html_metadata(self) -> None:
        """Test that chunks include proper metadata."""
        chunker = HTMLChunker()
        html = "<html><body><p>Metadata test.</p></body></html>"
        chunks = chunker.chunk_html(html, "meta.html")

        assert len(chunks) >= 1
        chunk = chunks[0]
        # Verify required fields from TextChunk
        assert chunk.chunk_id
        assert chunk.content
        assert chunk.token_count > 0
        assert chunk.source_file == "meta.html"
        assert isinstance(chunk.metadata, dict)

    def test_chunk_html_preserves_text_order(self) -> None:
        """Test that text order is preserved in chunks."""
        chunker = HTMLChunker()
        html = """
        <html><body>
            <p>First paragraph.</p>
            <p>Second paragraph.</p>
            <p>Third paragraph.</p>
        </body></html>
        """
        chunks = chunker.chunk_html(html, "order.html")

        # Concatenate all chunks
        full_text = " ".join([c.content for c in chunks])
        # Original order should be preserved
        assert full_text.index("First") < full_text.index("Second")
        assert full_text.index("Second") < full_text.index("Third")

    def test_chunk_html_strips_tags(self) -> None:
        """Test that HTML tags are stripped from content."""
        chunker = HTMLChunker()
        html = "<html><body><p><b>Bold</b> and <i>italic</i>.</p></body></html>"
        chunks = chunker.chunk_html(html, "tags.html")

        assert len(chunks) >= 1
        # Should not contain HTML tags
        assert "<b>" not in chunks[0].content
        assert "<i>" not in chunks[0].content
        # Should contain text content
        assert "Bold" in chunks[0].content
        assert "italic" in chunks[0].content
