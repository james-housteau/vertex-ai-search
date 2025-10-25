# CLAUDE.md

This file provides guidance to Claude Code when working with this module.

## Module Overview

**vector-index-prep** transforms TextChunk and Vector768 objects into JSONL format compatible with Vertex AI Vector Search index import. Output is written to Google Cloud Storage for subsequent index operations.

## Purpose

This module exists to:
1. Transform chunks + embeddings to JSONL format
2. Validate JSONL schema compliance
3. Write to GCS bucket or local file
4. Enable Vertex AI Vector Search index creation

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
poetry run pytest tests/test_jsonl_generator.py -v

# Run specific test function
poetry run pytest tests/test_jsonl_generator.py::TestJSONLGeneration::test_generate_jsonl_basic -v

# Run tests matching pattern
poetry run pytest -k "jsonl" -v
```

## Code Architecture

### Module Structure
```
vector-index-prep/
├── src/vector_index_prep/
│   ├── __init__.py      # Public API exports
│   └── jsonl_generator.py  # JSONL generation logic
├── tests/
│   └── test_jsonl_generator.py  # Comprehensive tests
├── Makefile             # Standard targets
├── pyproject.toml       # Poetry configuration
├── CLAUDE.md            # This file
└── README.md            # Usage documentation
```

## Technology Stack

- **Python Version**: 3.13+
- **Package Manager**: Poetry
- **Dependencies**: pydantic, google-cloud-storage, shared-contracts
- **Testing**: pytest with 80% coverage requirement
- **Code Quality**: black (88 chars), ruff, mypy strict

## Important Notes

### Pure Module Isolation
- **No `../` imports** - This module is completely independent
- **Dependencies**: pydantic, google-cloud-storage, shared-contracts
- **Can build independently**: `cd vector-index-prep && make setup && make test`
- **Must stay under 60 files** (currently at ~8 files)

### JSONL Format Specification
Each line in the output JSONL file must be a valid JSON object with:
- `id`: string (chunk_id)
- `embedding`: array of exactly 768 floats
- `restricts`: array of objects with `namespace` and `allow` fields (metadata)

Example:
```json
{"id": "chunk_001", "embedding": [0.1, 0.2, ...], "restricts": [{"namespace": "source_file", "allow": ["test.html"]}]}
```

### Validation Requirements
- Chunks and embeddings must not be empty
- Every chunk must have a corresponding embedding (matched by chunk_id)
- Embedding must have exactly 768 dimensions
- Output path can be GCS (gs://) or local file path

### Testing Requirements
- 80% minimum coverage (enforced)
- Test basic JSONL generation
- Test multiple chunks/embeddings
- Test validation errors
- Test metadata conversion to restricts
- Test GCS and local file output
- Mock GCS client for unit tests

## Code Quality Requirements

- **Coverage**: Minimum 80% (enforced by pytest)
- **Formatting**: Black with 88 character line length
- **Linting**: Ruff with strict settings
- **Type Safety**: mypy strict mode, all functions typed
- **Testing**: pytest framework, HTML coverage reports

## Development Workflow

1. **Always work within this directory**: `cd vector-index-prep/`
2. **Run tests frequently**: `make test` or `make test-quick`
3. **Check coverage**: `make test-cov`
4. **Verify quality**: `make quality` before commits
5. **Keep it simple**: Minimal code to satisfy requirements

## Quick Reference

```bash
# First time setup
cd vector-index-prep/
make setup

# Development cycle
make test-quick    # Fast feedback
make format        # Format code
make quality       # Full quality check

# Before commit
make test-cov      # Verify 80% coverage
make quality       # All checks pass
```
