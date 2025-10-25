"""HTML chunker implementation."""

from pathlib import Path

from bs4 import BeautifulSoup
from shared_contracts.models import TextChunk


class HTMLChunker:
    """Chunk HTML content into fixed-size token segments."""

    def __init__(self, chunk_size: int = 450, overlap: int = 80) -> None:
        """Initialize chunker with configuration.

        Args:
            chunk_size: Target tokens per chunk (default: 450)
            overlap: Token overlap between chunks (default: 80)
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        # Approximate: 1 word ≈ 1.3 tokens (reasonable for English text)
        self.words_per_token = 1.0 / 1.3

    def chunk_file(self, file_path: str | Path) -> list[TextChunk]:
        """Chunk HTML file into token-based segments.

        Args:
            file_path: Path to HTML file

        Returns:
            List of TextChunk objects with metadata

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is empty or invalid HTML
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        html_content = path.read_text(encoding="utf-8")
        return self.chunk_html(html_content, path.name)

    def chunk_html(self, html_content: str, source_file: str) -> list[TextChunk]:
        """Chunk HTML content into token-based segments.

        Args:
            html_content: Raw HTML content
            source_file: Source file name for metadata

        Returns:
            List of TextChunk objects with metadata

        Raises:
            ValueError: If content is empty
        """
        if not html_content or not html_content.strip():
            raise ValueError("Content cannot be empty")

        # Extract clean text from HTML
        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text(separator=" ", strip=True)

        # Split into words for approximate token-based chunking
        words = text.split()

        # Calculate target words per chunk (approximation)
        words_per_chunk = int(self.chunk_size * self.words_per_token)
        words_overlap = int(self.overlap * self.words_per_token)

        # Create chunks with overlap
        chunks = []
        start_idx = 0
        chunk_index = 0

        while start_idx < len(words):
            # Get chunk words
            end_idx = start_idx + words_per_chunk
            chunk_words = words[start_idx:end_idx]
            chunk_text = " ".join(chunk_words)

            # Approximate token count (words * 1.3)
            token_count = int(len(chunk_words) * 1.3)

            # Create TextChunk
            chunk_id = f"{source_file}#chunk-{chunk_index}"
            chunk = TextChunk(
                chunk_id=chunk_id,
                content=chunk_text,
                token_count=token_count,
                source_file=source_file,
                metadata={
                    "chunk_index": chunk_index,
                    "start_word": start_idx,
                    "end_word": end_idx,
                    "overlap_words": words_overlap,
                },
            )
            chunks.append(chunk)

            # Move to next chunk with overlap
            start_idx += words_per_chunk - words_overlap
            chunk_index += 1

        return chunks
