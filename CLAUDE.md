# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **monorepo** containing a comprehensive testing framework for Google Vertex AI Search and Conversation capabilities. The system follows **Pure Module Isolation** architecture - each module is completely independent and can be built, tested, and deployed in isolation.

The system processes 1600 HTML documents from the Natural Questions dataset to test Vertex AI Agent Builder search and conversation capabilities.

## Critical Architecture Principle: Pure Module Isolation

**Each module exists independently at the root level.** This is NOT a typical monorepo with shared dependencies - it's a constellation of 12 completely isolated modules that can build and test without any knowledge of each other.

### Core Rules
1. **Never use `cd` at the root level for development** - Always work within a specific module directory
2. **Never import from `../`** - Modules cannot import from parent or sibling directories
3. **Each module must be <60 files** - AI-safe development constraint
4. **Each module builds independently** - `cd module && make build` must work in isolation

## Available Modules (12 Total)

Each module has its own `Makefile`, `pyproject.toml`, tests, and dependencies:

### Stream 1: Data Pipeline
- **`nq-downloader/`** - Download Natural Questions dataset (97.10% coverage)
- **`html-extractor/`** - Extract content from HTML documents (93% coverage)
- **`filename-sanitizer/`** - Cross-platform filename handling (94% coverage)

### Stream 2: Infrastructure
- **`config-manager/`** - Configuration management (94.77% coverage)
- **`cli-orchestrator/`** - CLI framework integration (86% coverage)

### Stream 3: Cloud Services
- **`gcs-manager/`** - Google Cloud Storage operations (97.10% coverage)
- **`document-uploader/`** - Parallel file upload with retry (94.15% coverage)
- **`vertex-datastore/`** - Vertex AI data store integration (95.54% coverage)

### Stream 4: Testing & Metrics
- **`search-engine/`** - Vertex AI search functionality testing
- **`answer-service/`** - Conversation and answer generation testing
- **`metrics-collector/`** - Performance metrics collection
- **`load-tester/`** - End-to-end load testing orchestration

## Development Workflow

### Working with Individual Modules (RECOMMENDED)

```bash
# ALWAYS work within a specific module directory
cd nq-downloader/

# All standard commands work in isolation
make setup               # Install dependencies for THIS module only
make test                # Test THIS module only
make test-quick          # Fast subset for rapid feedback
make test-cov            # Coverage report (80% minimum required)
make format              # Format code with black and ruff
make lint                # Lint with ruff
make typecheck           # Type check with mypy
make quality             # All quality checks (format + lint + typecheck)
make build               # Build THIS module only
make clean               # Clean THIS module's artifacts

# Single test execution (within module)
poetry run pytest tests/test_file.py -v
poetry run pytest tests/test_file.py::test_function_name -v
poetry run pytest -k "test_pattern" -v
```

### Multi-Module Convenience Commands (from root)

```bash
# These are convenience wrappers - they just cd into each module
make list-modules        # List all available modules
make setup-all          # Setup all modules (runs setup in each)
make test-all           # Test all modules independently
make build-all          # Build all modules independently
make quality-all        # Quality checks on all modules
```

### Module Independence Validation

```bash
# Verify a module works in complete isolation
cd gcs-manager/
make clean
make setup
make test
make build
# Should work without any reference to other modules
```

## Code Architecture

### Standard Module Structure

Every module follows this pattern:
```
module-name/
├── Makefile              # Standard targets: setup, test, lint, build, clean
├── pyproject.toml        # Independent dependencies and configuration
├── src/module_name/      # Source code
│   ├── __init__.py
│   ├── main.py          # Entry point (if CLI)
│   └── ...
├── tests/               # Independent test suite
│   ├── __init__.py
│   └── test_*.py
├── CLAUDE.md            # Module-specific guidance
└── README.md            # Module documentation
```

### Common Technology Stack (Per Module)

- **Python Version**: 3.13+ (all modules)
- **Package Manager**: Poetry (dependency isolation per module)
- **CLI Framework**: Click with Rich styling (where applicable)
- **Testing**: pytest with 80% coverage requirement
- **Code Quality**: black (88 chars), ruff linting, mypy strict type checking
- **Models**: Pydantic v2 for data validation

### Genesis Framework Integration

All modules use Genesis shared utilities:
- ConfigLoader for YAML/environment configuration
- Structured logging with `get_logger()`
- Comprehensive error handling
- Retry logic with exponential backoff
- Production-ready health checks

## System Integration Flow

Modules connect through well-defined APIs, not compilation dependencies:

1. **Data Preparation**: `nq-downloader` → `html-extractor` → `filename-sanitizer`
2. **Configuration**: `config-manager` provides settings to all services
3. **Cloud Operations**: `gcs-manager` → `document-uploader` → `vertex-datastore`
4. **Testing Pipeline**: `search-engine` + `answer-service` → `metrics-collector` → `load-tester`

## Important Development Notes

### When Working on a Specific Module
1. **Always `cd` into the module directory first**
2. **Read the module's own `CLAUDE.md`** for module-specific details
3. **Never import from `../`** - each module is isolated
4. **Run tests frequently** - 80% coverage is enforced
5. **Keep modules under 60 files** - AI-safe development constraint

### When Working Across Multiple Modules
1. **Use the root-level convenience commands** (`make test-all`, etc.)
2. **Remember modules don't share code** - changes must be made in each module
3. **Test each module independently** before integration testing
4. **Review module dependency declarations** in `pyproject.toml`

### Code Quality Requirements (All Modules)
- **Coverage**: Minimum 80% (enforced by pytest)
- **Formatting**: Black with 88 character line length
- **Linting**: Ruff with strict settings
- **Type Safety**: mypy strict mode, all functions must have type annotations
- **Testing**: pytest framework, HTML coverage reports generated

## Lean TDD Workflow Integration

This project includes a complete Lean TDD workflow system (see `.claude/LEAN-TDD-WORKFLOW.md`):

### Available Slash Commands
- `/tdd [issue-number]` - Resolve GitHub issue using TDD workflow
- `/feature [issue-number]` - Implement feature with TDD
- `/bug [issue-number]` - Debug and resolve bugs systematically
- `/commit` - Create git commit with validation
- `/pr [issue-number]` - Create pull request with lean validation
- `/metrics` - Show lean development metrics
- `/issue [action] [instructions]` - Create GitHub issue from context

### Core Principles
- Write minimal code to pass tests
- No abstractions or patterns unless absolutely necessary
- Each module should remain under 60 files for AI-safe development
- Test critical paths, not edge cases

## Quick Reference

```bash
# New to the project? Start here:
make list-modules        # See all available modules

# Work on a specific module:
cd gcs-manager/          # Enter module directory
make setup               # Install dependencies
make test                # Run tests
make quality             # Check code quality

# Work across all modules:
make setup-all           # Setup everything
make test-all            # Test everything
make quality-all         # Quality check everything
```

## Module Selection Guide

- **Need to download Natural Questions dataset?** → `nq-downloader/`
- **Need to process HTML content?** → `html-extractor/`
- **Need to manage GCS buckets/objects?** → `gcs-manager/`
- **Need to upload documents to GCS?** → `document-uploader/`
- **Need to manage Vertex AI data stores?** → `vertex-datastore/`
- **Need to test search functionality?** → `search-engine/`
- **Need to test conversation/answers?** → `answer-service/`
- **Need to collect performance metrics?** → `metrics-collector/`
- **Need to run load tests?** → `load-tester/`
- **Need configuration management?** → `config-manager/`
- **Need CLI orchestration?** → `cli-orchestrator/`
- **Need filename sanitization?** → `filename-sanitizer/`
