# CLAUDE.md

This file provides guidance to Claude Code when working with this module.

## Module Overview

**shared-contracts** is a foundational module providing type-safe data contracts for the vector search pipeline. It defines three Pydantic v2 dataclasses that serve as the interface between all other modules in the pipeline.

## Purpose

This module exists to:
1. Define shared data structures used across the pipeline
2. Provide validation for data integrity
3. Enable type-safe communication between modules
4. Serve as a dependency for issues #3-7 (chunker, embedder, indexer, query, evaluator)

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
poetry run pytest tests/test_models.py -v

# Run specific test class
poetry run pytest tests/test_models.py::TestTextChunk -v

# Run specific test function
poetry run pytest tests/test_models.py::TestTextChunk::test_text_chunk_creation_valid -v

# Run tests matching pattern
poetry run pytest -k "text_chunk" -v
```

## Code Architecture

### Module Structure
```
shared-contracts/
├── src/shared_contracts/
│   ├── __init__.py      # Public API exports
│   └── models.py        # Data contract definitions
├── tests/
│   └── test_models.py   # Comprehensive validation tests
├── Makefile             # Standard targets
├── pyproject.toml       # Poetry configuration
├── CLAUDE.md            # This file
└── README.md            # Usage documentation
```

### Data Contracts

#### TextChunk
Represents chunked HTML content ready for embedding.
- All fields required except metadata can be empty dict
- `chunk_id` and `content` must be non-empty strings
- `token_count` must be positive integer
- Used by: chunker (#3), embedder (#4), indexer (#5)

#### Vector768
Represents 768-dimensional embedding vectors.
- `embedding` must have exactly 768 float values
- `model` defaults to "text-embedding-004"
- Used by: embedder (#4), indexer (#5), query (#6)

#### SearchMatch
Represents search results with relevance scores.
- `score` must be float between 0.0 and 1.0 inclusive
- `content` can be empty (edge case)
- Used by: query (#6), evaluator (#7)

## Technology Stack

- **Python Version**: 3.13+
- **Package Manager**: Poetry
- **Validation**: Pydantic v2 (BaseModel with validators)
- **Testing**: pytest with 80% coverage requirement
- **Code Quality**: black (88 chars), ruff, mypy strict

## Important Notes

### Pure Module Isolation
- **No `../` imports** - This module is completely independent
- **Only dependency**: pydantic (and dev tools)
- **Can build independently**: `cd shared-contracts && make setup && make test`
- **Must stay under 60 files** (currently at ~8 files)

### Validation Strategy
- Use Pydantic `field_validator` for custom validation
- Use `min_length=1` for non-empty strings
- Use `ge=1` for positive integers
- Use `ge=0.0, le=1.0` for score ranges
- Use custom validator for embedding dimension check

### Dependencies
This module is a **dependency** for:
- chunker (#3) - uses TextChunk
- embedder (#4) - uses TextChunk and Vector768
- indexer (#5) - uses Vector768
- query (#6) - uses Vector768 and SearchMatch
- evaluator (#7) - uses SearchMatch

Other modules will add this as a dependency via:
```toml
[tool.poetry.dependencies]
shared-contracts = {path = "../shared-contracts", develop = true}
```

### Testing Requirements
- 80% minimum coverage (enforced)
- Test all validation rules
- Test required fields
- Test value constraints
- Test default values
- Test edge cases

## Code Quality Requirements

- **Coverage**: Minimum 80% (enforced by pytest)
- **Formatting**: Black with 88 character line length
- **Linting**: Ruff with strict settings
- **Type Safety**: mypy strict mode, all functions typed
- **Testing**: pytest framework, HTML coverage reports

## Development Workflow

1. **Always work within this directory**: `cd shared-contracts/`
2. **Run tests frequently**: `make test` or `make test-quick`
3. **Check coverage**: `make test-cov`
4. **Verify quality**: `make quality` before commits
5. **Keep it simple**: Minimal code to satisfy requirements

## Quick Reference

```bash
# First time setup
cd shared-contracts/
make setup

# Development cycle
make test-quick    # Fast feedback
make format        # Format code
make quality       # Full quality check

# Before commit
make test-cov      # Verify 80% coverage
make quality       # All checks pass
```
