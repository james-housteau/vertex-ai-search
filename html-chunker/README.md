# html-chunker

HTML content chunker with token-based segmentation for vector search pipeline.

## Purpose

Process HTML files into fixed-size token chunks with overlap for optimal vector search performance.

## Features

- 450-token chunks with 80-token overlap
- Clean text extraction from HTML
- Metadata preservation
- TextChunk output format (shared-contracts)

## Installation

```bash
make setup
```

## Usage

```python
from html_chunker import HTMLChunker

chunker = HTMLChunker()
chunks = chunker.chunk_file("document.html")
```

## Development

```bash
make test           # Run all tests
make test-quick     # Fast subset
make test-cov       # Coverage report
make quality        # All quality checks
make build          # Build wheel
```

## Requirements

- Python 3.13+
- tiktoken for token counting
- BeautifulSoup4 for HTML parsing
- shared-contracts for TextChunk type
