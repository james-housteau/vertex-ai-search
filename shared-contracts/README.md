# shared-contracts

Shared data contracts for the vector search pipeline. This module provides type-safe dataclasses using Pydantic v2 for data validation across the entire pipeline.

## Overview

This is a foundational module that defines three core data contracts:

1. **TextChunk** - Represents chunked HTML content ready for embedding
2. **Vector768** - Represents 768-dimensional embedding vectors
3. **SearchMatch** - Represents search results with relevance scores

## Installation

```bash
cd shared-contracts/
make setup
```

## Usage

```python
from shared_contracts import TextChunk, Vector768, SearchMatch

# Create a text chunk
chunk = TextChunk(
    chunk_id="chunk_001",
    content="This is test content",
    metadata={"source": "test.html", "section": "intro"},
    token_count=5,
    source_file="test.html"
)

# Create an embedding vector (768 dimensions)
vector = Vector768(
    chunk_id="chunk_001",
    embedding=[0.1] * 768,
    model="text-embedding-004"  # Optional, has default
)

# Create a search result
match = SearchMatch(
    chunk_id="chunk_001",
    score=0.95,  # Must be between 0.0 and 1.0
    content="Relevant content",
    metadata={"source": "test.html"}
)
```

## Data Contracts

### TextChunk

Represents a chunk of text extracted from HTML documents.

**Fields:**
- `chunk_id` (str): Unique identifier, required, non-empty
- `content` (str): Text content, required, non-empty
- `metadata` (Dict[str, Any]): Metadata dictionary, required (can be empty)
- `token_count` (int): Number of tokens, required, must be > 0
- `source_file` (str): Source filename, required, non-empty

### Vector768

Represents a 768-dimensional embedding vector from text-embedding-004 model.

**Fields:**
- `chunk_id` (str): Unique identifier, required, non-empty
- `embedding` (List[float]): Vector, required, must have exactly 768 dimensions
- `model` (str): Model name, default="text-embedding-004"

### SearchMatch

Represents a search result with relevance score.

**Fields:**
- `chunk_id` (str): Unique identifier, required, non-empty
- `score` (float): Relevance score, required, must be between 0.0 and 1.0
- `content` (str): Matched content, required
- `metadata` (Dict[str, Any]): Metadata dictionary, required (can be empty)

## Development

```bash
# Run tests
make test

# Run tests with coverage
make test-cov

# Format code
make format

# Lint code
make lint

# Type check
make typecheck

# Run all quality checks
make quality

# Build package
make build

# Clean artifacts
make clean
```

## Testing

The module has comprehensive test coverage (80%+) validating:

- Required field enforcement
- Non-empty string validation
- Type constraints (e.g., exactly 768 dimensions)
- Value constraints (e.g., score between 0-1)
- Default values
- Edge cases

## Pure Module Isolation

This module follows Pure Module Isolation principles:

- No imports from `../` (parent directories)
- Only depends on pydantic and stdlib
- Can be built/tested independently: `cd shared-contracts && make test`
- Under 60 files total

## Dependencies

- Python 3.13+
- pydantic ^2.5.0

## License

Proprietary
