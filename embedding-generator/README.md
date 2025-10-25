# Embedding Generator

Generate 768-dimensional embeddings using Vertex AI text-embedding-004 model.

## Overview

This module converts text chunks into 768-dimensional embedding vectors using Google's Vertex AI text-embedding-004 model. It supports batch processing, automatic retry logic, and rate limiting to handle Vertex AI quotas.

## Features

- **768-dimensional vectors**: Using text-embedding-004 model
- **Batch processing**: Configurable batch size (default: 100)
- **Retry logic**: Exponential backoff for API failures
- **Rate limiting**: Respect Vertex AI quotas
- **Type safety**: Pydantic models with validation

## Installation

```bash
cd embedding-generator/
make setup
```

## Usage

```python
from embedding_generator import EmbeddingGenerator
from shared_contracts import TextChunk

# Initialize generator
generator = EmbeddingGenerator(
    project_id="your-gcp-project",
    location="us-central1",
    batch_size=100,
    max_retries=3
)

# Create text chunks
chunks = [
    TextChunk(
        chunk_id="chunk-1",
        content="What is the capital of France?",
        metadata={"source": "test"},
        token_count=10,
        source_file="test.html"
    )
]

# Generate embeddings
vectors = generator.generate(chunks)

# Use the vectors
for vector in vectors:
    print(f"Chunk: {vector.chunk_id}")
    print(f"Dimensions: {len(vector.embedding)}")
    print(f"Model: {vector.model}")
```

## Development

```bash
# Run tests
make test

# Fast test subset
make test-quick

# Coverage report
make test-cov

# Code quality
make quality

# Build package
make build
```

## Dependencies

- Python 3.13+
- google-cloud-aiplatform
- shared-contracts (from ../shared-contracts)
- Pydantic v2

## Configuration

### Batch Size
Control how many chunks are processed per API call (default: 100).

### Max Retries
Number of retry attempts on API failures (default: 3).

### Rate Limiting
Automatically respects Vertex AI quotas with exponential backoff.

## Integration

This module is part of the vector search pipeline:

**Input**: List[TextChunk] from chunker module
**Output**: List[Vector768] for indexer module

## Testing

All tests use mocked Vertex AI API calls - no actual API requests are made during testing.

```bash
# Run all tests
make test

# Run specific test
poetry run pytest tests/test_generator.py::TestEmbeddingGenerator::test_generate_single_embedding -v
```

## Quality Standards

- 80% minimum test coverage
- Black formatting (88 chars)
- Ruff linting
- Mypy strict type checking
- All functions type annotated
