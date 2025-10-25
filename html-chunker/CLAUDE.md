# CLAUDE.md

This file provides guidance to Claude Code when working with this module.

## Module Overview

**html-chunker** processes HTML files into fixed-size token chunks with overlap for optimal vector search performance. Uses tiktoken for accurate token counting and BeautifulSoup for HTML parsing.

## Purpose

This module exists to:
1. Convert HTML documents into 450-token chunks with 80-token overlap
2. Extract clean text from HTML while preserving order
3. Generate TextChunk objects with metadata
4. Enable efficient vector search with optimal chunk sizes

## Development Commands

### Essential Commands
```bash
# Initial setup
make setup

# Run tests
make test                 # All tests with verbose output
make test-quick          # Fast subset for rapid feedback
make test-cov            # Tests with coverage report (80% minimum)

# Code quality
make format              # Format with black and ruff
make lint                # Lint with ruff
make typecheck           # Type check with mypy
make quality             # All quality checks

# Build
make build               # Build wheel packages
make clean               # Clean artifacts
```

### Single Test Execution
```bash
# Run specific test file
poetry run pytest tests/test_chunker.py -v

# Run specific test class
poetry run pytest tests/test_chunker.py::TestHTMLChunker -v

# Run specific test function
poetry run pytest tests/test_chunker.py::TestHTMLChunker::test_chunk_html_simple_content -v

# Run tests matching pattern
poetry run pytest -k "chunk_html" -v
```

## Code Architecture

### Module Structure
```
html-chunker/
├── src/html_chunker/
│   ├── __init__.py      # Public API exports
│   └── chunker.py       # Main chunker implementation
├── tests/
│   ├── __init__.py
│   └── test_chunker.py  # Comprehensive tests
├── Makefile             # Standard targets
├── pyproject.toml       # Poetry configuration
├── CLAUDE.md            # This file
└── README.md            # Usage documentation
```

### Key Components

#### HTMLChunker
Main class for chunking HTML content.
- **chunk_size**: 450 tokens (default)
- **overlap**: 80 tokens (default)
- **encoding**: cl100k_base (OpenAI's tiktoken encoding)

Public methods:
- `chunk_file(file_path)` - Chunk from file path
- `chunk_html(html_content, source_file)` - Chunk from HTML string

## Technology Stack

- **Python Version**: 3.13+
- **Package Manager**: Poetry
- **HTML Parsing**: BeautifulSoup4 with lxml
- **Token Counting**: tiktoken (cl100k_base encoding)
- **Data Models**: Pydantic v2 via shared-contracts
- **Testing**: pytest with 80% coverage requirement
- **Code Quality**: black (88 chars), ruff, mypy strict

## Important Notes

### Pure Module Isolation
- **No `../` imports** - This module is completely independent
- **Dependencies**: pydantic, tiktoken, beautifulsoup4, lxml, shared-contracts
- **Can build independently**: `cd html-chunker && make setup && make test`
- **Must stay under 60 files** (currently at ~8 files)

### Chunking Algorithm
1. Extract clean text from HTML using BeautifulSoup
2. Tokenize using tiktoken's cl100k_base encoding
3. Create chunks of 450 tokens with 80-token overlap
4. Generate unique chunk IDs: `{source_file}#chunk-{index}`
5. Calculate accurate token counts per chunk
6. Include metadata: chunk index, total chunks, overlap info

### TextChunk Requirements
Each chunk must satisfy shared-contracts validation:
- `chunk_id`: Non-empty string (format: filename#chunk-N)
- `content`: Non-empty string (clean text, no HTML tags)
- `metadata`: Dict with chunk info (index, total, overlap)
- `token_count`: Positive integer (accurate tiktoken count)
- `source_file`: Non-empty string (original filename)

### Testing Requirements
- 80% minimum coverage (enforced)
- Test chunking with various content sizes
- Test overlap between consecutive chunks
- Test file I/O operations
- Test error handling (missing files, empty content)
- Test metadata generation
- Test text order preservation
- Test HTML tag stripping

## Code Quality Requirements

- **Coverage**: Minimum 80% (enforced by pytest)
- **Formatting**: Black with 88 character line length
- **Linting**: Ruff with strict settings
- **Type Safety**: mypy strict mode, all functions typed
- **Testing**: pytest framework, HTML coverage reports

## Development Workflow

1. **Always work within this directory**: `cd html-chunker/`
2. **Run tests frequently**: `make test` or `make test-quick`
3. **Check coverage**: `make test-cov`
4. **Verify quality**: `make quality` before commits
5. **Keep it simple**: Minimal code to satisfy requirements

## Quick Reference

```bash
# First time setup
cd html-chunker/
make setup

# Development cycle
make test-quick    # Fast feedback
make format        # Format code
make quality       # Full quality check

# Before commit
make test-cov      # Verify 80% coverage
make quality       # All checks pass
```

## Usage Example

```python
from html_chunker import HTMLChunker

# Initialize with defaults (450 tokens, 80 overlap)
chunker = HTMLChunker()

# Chunk from file
chunks = chunker.chunk_file("document.html")

# Chunk from HTML string
html = "<html><body><p>Content</p></body></html>"
chunks = chunker.chunk_html(html, "source.html")

# Access chunk data
for chunk in chunks:
    print(f"ID: {chunk.chunk_id}")
    print(f"Tokens: {chunk.token_count}")
    print(f"Content: {chunk.content[:100]}...")
```
