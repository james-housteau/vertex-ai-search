# CLAUDE.md

This file provides guidance to Claude Code when working with this module.

## Module Overview

**embedding-generator** converts text chunks into 768-dimensional embedding vectors using Google Vertex AI's text-embedding-004 model. It provides batch processing, retry logic, and rate limiting.

## Purpose

This module exists to:
1. Generate embeddings for text chunks using Vertex AI
2. Handle batch processing efficiently (default: 100 chunks per batch)
3. Provide retry logic with exponential backoff for API failures
4. Manage rate limiting to respect Vertex AI quotas
5. Convert TextChunk → Vector768 with type safety

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
poetry run pytest tests/test_generator.py -v

# Run specific test class
poetry run pytest tests/test_generator.py::TestEmbeddingGenerator -v

# Run specific test function
poetry run pytest tests/test_generator.py::TestEmbeddingGenerator::test_generate_single_embedding -v

# Run tests matching pattern
poetry run pytest -k "batch" -v
```

## Code Architecture

### Module Structure
```
embedding-generator/
├── src/embedding_generator/
│   ├── __init__.py      # Public API exports
│   └── generator.py     # Core embedding generation logic
├── tests/
│   └── test_generator.py # Comprehensive tests with mocked API
├── Makefile             # Standard targets
├── pyproject.toml       # Poetry configuration
├── CLAUDE.md            # This file
└── README.md            # Usage documentation
```

### Core Components

#### EmbeddingGenerator
Main class for generating embeddings.
- Initializes Vertex AI client
- Manages batch processing
- Handles retry logic with exponential backoff
- Converts TextChunk list to Vector768 list

## Technology Stack

- **Python Version**: 3.13+
- **Package Manager**: Poetry
- **Vertex AI SDK**: google-cloud-aiplatform
- **Validation**: Pydantic v2 (via shared-contracts)
- **Testing**: pytest with mocked API calls
- **Code Quality**: black (88 chars), ruff, mypy strict

## Important Notes

### Pure Module Isolation
- **No `../` imports** - This module is completely independent
- **Dependencies**: google-cloud-aiplatform, pydantic, shared-contracts
- **Can build independently**: `cd embedding-generator && make setup && make test`
- **Must stay under 60 files** (currently at ~8 files)

### API Integration
- Uses Vertex AI TextEmbeddingModel
- Model: text-embedding-004 (768 dimensions)
- All tests mock API calls - no real requests during testing
- Batch processing to optimize API usage

### Retry Strategy
- Default: 3 retries with exponential backoff
- Handles transient API failures
- Configurable max_retries parameter

### Batch Processing
- Default batch size: 100 chunks
- Configurable via batch_size parameter
- Processes chunks in batches to respect API limits

## Dependencies

### Upstream
- **shared-contracts** - Uses TextChunk and Vector768 models

### Downstream
This module provides embeddings to:
- **indexer** (#5) - Indexes vectors in Vertex AI

## Testing Requirements

- 80% minimum coverage (enforced)
- Mock all Vertex AI API calls
- Test single and batch processing
- Test retry logic
- Test error handling
- Test edge cases (empty list, API failures)

## Code Quality Requirements

- **Coverage**: Minimum 80% (enforced by pytest)
- **Formatting**: Black with 88 character line length
- **Linting**: Ruff with strict settings
- **Type Safety**: mypy strict mode, all functions typed
- **Testing**: pytest framework, HTML coverage reports

## Development Workflow

1. **Always work within this directory**: `cd embedding-generator/`
2. **Run tests frequently**: `make test` or `make test-quick`
3. **Check coverage**: `make test-cov`
4. **Verify quality**: `make quality` before commits
5. **Keep it simple**: Minimal code to satisfy requirements

## Implementation Notes

### Lean TDD Approach
- Write minimal code to pass tests
- No premature abstractions
- Direct implementation over design patterns
- Inline code before extracting functions

### Key Simplifications
- Single class (EmbeddingGenerator)
- No factory patterns
- No abstract base classes
- No unnecessary interfaces
- Direct Vertex AI SDK usage

## Quick Reference

```bash
# First time setup
cd embedding-generator/
make setup

# Development cycle
make test-quick    # Fast feedback
make format        # Format code
make quality       # Full quality check

# Before commit
make test-cov      # Verify 80% coverage
make quality       # All checks pass
```

## Configuration Parameters

### project_id (required)
GCP project ID for Vertex AI

### location (required)
GCP location (e.g., "us-central1")

### batch_size (optional)
Number of chunks per API batch (default: 100)

### max_retries (optional)
Maximum retry attempts on failures (default: 3)
