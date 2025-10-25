# CLAUDE.md

This file provides guidance to Claude Code when working with this module.

## Module Overview

**vector-search-index** manages Vector Search indexes in Google Cloud Vertex AI. It provides create, update, delete, and status monitoring operations for ScaNN-based approximate nearest neighbor search indexes.

## Purpose

This module exists to:
1. Manage Vector Search index lifecycle (create, update, delete)
2. Configure ScaNN algorithm parameters
3. Monitor index deployment status
4. Provide type-safe index configuration

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
poetry run pytest tests/test_index_manager.py -v

# Run specific test function
poetry run pytest tests/test_index_manager.py::test_create_index -v

# Run tests matching pattern
poetry run pytest -k "create" -v
```

## Code Architecture

### Module Structure
```
vector-search-index/
├── src/vector_search_index/
│   ├── __init__.py      # Public API exports
│   ├── manager.py       # Index manager implementation
│   └── config.py        # Index configuration models
├── tests/
│   ├── __init__.py
│   └── test_index_manager.py  # Manager tests
├── Makefile             # Standard targets
├── pyproject.toml       # Poetry configuration
├── CLAUDE.md            # This file
└── README.md            # Usage documentation
```

### Key Components

#### VectorSearchIndexManager
Main class for index operations:
- `create_index()` - Create new Vector Search index
- `update_index()` - Update index configuration
- `delete_index()` - Delete an index
- `get_index_status()` - Check deployment status

#### IndexConfig
Pydantic model for index configuration:
- Dimensions (768 for text-embedding-004)
- Distance metric (DOT_PRODUCT, COSINE, EUCLIDEAN)
- ScaNN parameters (number of leaves, replication)
- Shard size configuration

## Technology Stack

- **Python Version**: 3.13+
- **Package Manager**: Poetry
- **Cloud SDK**: google-cloud-aiplatform
- **Validation**: Pydantic v2
- **Testing**: pytest with 80% coverage requirement
- **Code Quality**: black (88 chars), ruff, mypy strict

## Important Notes

### Pure Module Isolation
- **No `../` imports** - This module is completely independent
- **Dependencies**: google-cloud-aiplatform, pydantic
- **Can build independently**: `cd vector-search-index && make setup && make test`
- **Must stay under 60 files** (AI-safe development constraint)

### Vertex AI Vector Search
- Uses Vertex AI Vector Search API
- ScaNN algorithm for approximate nearest neighbor search
- Supports various distance metrics
- Asynchronous index creation (requires monitoring)

### Testing Strategy
- Mock Vertex AI API calls using unittest.mock
- Test all CRUD operations
- Test configuration validation
- Test error handling
- No actual GCP resources required

## Code Quality Requirements

- **Coverage**: Minimum 80% (enforced by pytest)
- **Formatting**: Black with 88 character line length
- **Linting**: Ruff with strict settings
- **Type Safety**: mypy strict mode, all functions typed
- **Testing**: pytest framework, HTML coverage reports

## Development Workflow

1. **Always work within this directory**: `cd vector-search-index/`
2. **Run tests frequently**: `make test` or `make test-quick`
3. **Check coverage**: `make test-cov`
4. **Verify quality**: `make quality` before commits
5. **Keep it simple**: Minimal code to satisfy requirements

## Quick Reference

```bash
# First time setup
cd vector-search-index/
make setup

# Development cycle
make test-quick    # Fast feedback
make format        # Format code
make quality       # Full quality check

# Before commit
make test-cov      # Verify 80% coverage
make quality       # All checks pass
```
