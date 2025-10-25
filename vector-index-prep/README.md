# vector-index-prep

Transform chunks + embeddings to JSONL format for Vertex AI Vector Search index.

## Overview

This module takes TextChunk and Vector768 objects and generates JSONL files compatible with Vertex AI Vector Search index import. Output is written to Google Cloud Storage for subsequent index operations.

## Features

- Transform TextChunk + Vector768 to JSONL format
- Validate JSONL schema compliance
- Write to GCS bucket
- 80%+ test coverage
- Pure module isolation

## Installation

```bash
make setup
```

## Usage

```python
from vector_index_prep import generate_jsonl
from shared_contracts import TextChunk, Vector768

chunks = [...]  # List of TextChunk objects
embeddings = [...]  # List of Vector768 objects

# Generate JSONL and upload to GCS
generate_jsonl(chunks, embeddings, "gs://bucket/path/output.jsonl")
```

## Development

```bash
make test          # Run all tests
make test-cov      # Run tests with coverage
make quality       # Run all quality checks
make build         # Build packages
```

## JSONL Format

Each line is a JSON object with:
- `id`: string (chunk_id)
- `embedding`: array of 768 floats
- `restricts`: array of objects with namespace and allow fields (metadata)

Example:
```json
{"id": "chunk_001", "embedding": [0.1, 0.2, ...], "restricts": [{"namespace": "source_file", "allow": ["doc1.html"]}]}
```
