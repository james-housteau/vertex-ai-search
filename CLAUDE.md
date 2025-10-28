# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **monorepo** containing a comprehensive testing framework for Google Vertex AI Search and Conversation capabilities. The system follows **Pure Module Isolation** architecture - each module is completely independent and can be built, tested, and deployed in isolation.

The system processes 1600 HTML documents from the Natural Questions dataset to test Vertex AI Agent Builder search and conversation capabilities.

## Critical Architecture Principle: Pure Module Isolation

**Each module exists independently at the root level.** This is NOT a typical monorepo with shared dependencies - it's a constellation of 20 completely isolated modules that can build and test without any knowledge of each other.

### Core Rules
1. **Never use `cd` at the root level for development** - Always work within a specific module directory
2. **Never import from `../`** - Modules cannot import from parent or sibling directories
3. **Each module must be <60 files** - AI-safe development constraint
4. **Each module builds independently** - `cd module && make build` must work in isolation

## Available Modules (20 Production Modules)

Each module has its own `Makefile`, `pyproject.toml`, tests, and dependencies.
Note: The `archive/` directory contains deprecated code and is not counted as an active module.

### Stream 1: Data Pipeline
- **`nq-downloader/`** - Download Natural Questions dataset (97% coverage)
- **`html-extractor/`** - Extract content from HTML documents (92% coverage)
- **`filename-sanitizer/`** - Cross-platform filename handling (95% coverage)

### Stream 2: Infrastructure
- **`config-manager/`** - Configuration management (97% coverage)
- **`cli-orchestrator/`** - CLI framework integration (80% coverage)

### Stream 3: Cloud Services
- **`gcs-manager/`** - Google Cloud Storage operations (97% coverage)
- **`document-uploader/`** - Parallel file upload with retry (94% coverage)
- **`vertex-datastore/`** - Vertex AI data store integration (88% coverage)

### Stream 4: Testing & Metrics
- **`search-engine/`** - Vertex AI search functionality testing (86% coverage)
- **`answer-service/`** - Conversation and answer generation testing (98% coverage)
- **`metrics-collector/`** - Performance metrics collection (98% coverage)
- **`load-tester/`** - End-to-end load testing orchestration (97% coverage)

### Stream 5: Vector Search Pipeline
- **`shared-contracts/`** - Shared Pydantic models (TextChunk, Vector768, SearchMatch) (100% coverage)
- **`html-chunker/`** - Chunk HTML into 450-token segments with 80-token overlap (100% coverage)
- **`embedding-generator/`** - Generate text-embedding-004 vectors from chunks (94% coverage)
- **`vector-index-prep/`** - Prepare JSONL for Vertex AI Vector Search index (100% coverage)
- **`vector-search-index/`** - Manage Vertex AI Vector Search indexes (100% coverage)
- **`vector-query-client/`** - Execute fast ANN queries (<120ms p95) (100% coverage)

### Stream 6: Production API
- **`search-api/`** - FastAPI service with /search, /summarize, /health endpoints (88% coverage)
- **`demo-website/`** - Web UI for search and streaming summarization (TBD coverage)

## Development Workflow

### Working with Individual Modules (RECOMMENDED)

```bash
# ALWAYS work within a specific module directory
cd nq-downloader/

# All standard commands work in isolation
make setup               # Install dependencies for THIS module only
make test                # Test THIS module only
make test-quick          # Fast subset for rapid feedback
make test-all            # All tests including slow/integration
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
make test                # Fast tests across all modules (excludes slow/integration markers)
make test-all            # All tests including slow/integration (no coverage)
make test-cov            # All tests with coverage reports (includes slow/integration)
make build-all          # Build all modules independently
make quality-all        # Quality checks on all modules
make format              # Format all code with black and ruff
make clean               # Clean all build artifacts
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
5. **Vector Search Pipeline**: `html-chunker` → `embedding-generator` → `vector-index-prep` → `vector-search-index` → `vector-query-client`
6. **Production API**: `search-api` (uses `vector-query-client` + `shared-contracts`)
7. **Demo UI**: `demo-website` (uses `search-api` via HTTP)

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

### Known Type Issues (Non-Blocking)
Some modules have type warnings from third-party libraries without stubs:
- `html-chunker`: shared-contracts missing stubs
- `nq-downloader`: google.cloud.storage missing stubs
- `search-api`: shared-contracts, vector-query-client, google.generativeai type issues
- `vector-index-prep`: google.cloud, shared-contracts missing stubs
- `vector-query-client`: distance calculation type narrowing
- `vector-search-index`: MatchingEngineIndex dynamic attributes

These are non-blocking since they come from external dependencies. Focus on ensuring your module code has proper type annotations.

## Local Development for Production APIs

### Running the Search API Locally

```bash
cd search-api/

# Setup environment
make setup

# Run with uvicorn (development mode with auto-reload)
poetry run uvicorn search_api.api:app --reload --host 0.0.0.0 --port 8080

# Access API at http://localhost:8080
# API docs at http://localhost:8080/docs
```

### Running the Demo Website Locally

```bash
cd demo-website/

# Setup environment
make setup

# Configure API URL (point to local or deployed search-api)
export API_URL="http://localhost:8080"  # or production URL

# Run with uvicorn (development mode with auto-reload)
poetry run uvicorn demo_website.main:app --reload --host 0.0.0.0 --port 8000

# Access demo at http://localhost:8000
```

### Docker Development

```bash
# Build search-api Docker image
cd search-api/
docker build -t search-api:latest .
docker run -p 8080:8080 search-api:latest

# Build demo-website Docker image
cd demo-website/
docker build -t demo-website:latest .
docker run -p 8000:8080 -e API_URL="http://localhost:8080" demo-website:latest
```

## Secret Management

**IMPORTANT**: Never commit secrets to version control.

- **`.secrets/` directory**: Use this directory (already in .gitignore) for local credential files
  - Service account keys (`.json`)
  - Environment files with API keys (`.env`)
  - OAuth tokens
- **Environment variables**: Set via `.envrc` (direnv), `.env` files, or shell exports
- **Service account keys**: Store in `.secrets/` and reference via `GOOGLE_APPLICATION_CREDENTIALS`

Example:
```bash
# Store service account key
mkdir -p .secrets/
mv ~/Downloads/service-account-key.json .secrets/

# Reference in environment
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/.secrets/service-account-key.json"
```

## Lean TDD Workflow Integration

This project includes a complete Lean TDD workflow system (see `.claude/LEAN-TDD-WORKFLOW.md`):

### Available Slash Commands
- `/tdd [issue-number]` - Resolve GitHub issue using TDD workflow
- `/feature [issue-number]` - Implement feature with TDD
- `/bug [issue-number]` - Debug and resolve bugs systematically
- `/refactor [issue-number]` - Refactor code to improve structure without changing behavior
- `/optimize [issue-number]` - Optimize performance based on measured bottlenecks
- `/deprecate [issue-number]` - Deprecate old code and provide migration path
- `/commit` - Create git commit with validation (uses genesis commit)
- `/pr [issue-number]` - Create pull request with lean validation
- `/close [issue-number]` - Clean up after PR merge
- `/metrics` - Show lean development metrics
- `/audit [issue-number]` - Audit changes against lean principles
- `/issue [action] [instructions]` - Create GitHub issue from context
- `/research [query]` - Research best practices and solutions
- `/cleanup [issue-number]` - Clean up code and remove dead code with Genesis
- `/update-docs [issue-number]` - Update project documentation
- `/test-fix [test-path-or-pattern]` - Fix failing tests by treating tests as source of truth

### Core Principles
- Write minimal code to pass tests
- No abstractions or patterns unless absolutely necessary
- Each module should remain under 60 files for AI-safe development
- Test critical paths, not edge cases

## Quick Reference

```bash
# New to the project? Start here:
make list-modules        # See all available modules

# Work on a specific module (RECOMMENDED):
cd gcs-manager/          # Enter module directory
make setup               # Install dependencies
make test                # Run fast tests (excludes slow/integration)
make test-quick          # Even faster subset (if available)
make test-all            # Run ALL tests including slow/integration
make test-cov            # Run all tests with coverage report
make quality             # Check code quality (format + lint + typecheck)

# Work across all modules (from root):
make setup-all           # Setup everything
make test                # Fast tests across all modules (no slow/integration)
make test-all            # All tests including slow/integration (no coverage)
make test-cov            # All tests with coverage reports (includes slow/integration)
make quality-all         # Quality check everything
make format              # Format all code with black and ruff
make clean               # Clean all build artifacts

# Run production APIs locally:
cd search-api/ && poetry run uvicorn search_api.api:app --reload
cd demo-website/ && poetry run uvicorn demo_website.main:app --reload
```

## Module Selection Guide

### Data & Processing
- **Need to download Natural Questions dataset?** → `nq-downloader/`
- **Need to process HTML content?** → `html-extractor/`
- **Need to chunk HTML into tokens?** → `html-chunker/`
- **Need to generate embeddings?** → `embedding-generator/`
- **Need filename sanitization?** → `filename-sanitizer/`

### Cloud & Storage
- **Need to manage GCS buckets/objects?** → `gcs-manager/`
- **Need to upload documents to GCS?** → `document-uploader/`
- **Need to manage Vertex AI data stores?** → `vertex-datastore/`

### Vector Search
- **Need shared type contracts?** → `shared-contracts/`
- **Need to prepare vector index data?** → `vector-index-prep/`
- **Need to manage vector search indexes?** → `vector-search-index/`
- **Need to query vector search?** → `vector-query-client/`

### Testing & Metrics
- **Need to test search functionality?** → `search-engine/`
- **Need to test conversation/answers?** → `answer-service/`
- **Need to collect performance metrics?** → `metrics-collector/`
- **Need to run load tests?** → `load-tester/`

### Infrastructure
- **Need configuration management?** → `config-manager/`
- **Need CLI orchestration?** → `cli-orchestrator/`

### Production API
- **Need fast vector search API?** → `search-api/`
- **Need streaming summarization?** → `search-api/`
- **Need production health checks?** → `search-api/`
- **Need in-memory caching for queries?** → `search-api/`

**search-api** provides:
- **GET /search**: Vector similarity search with <120ms p95 latency
- **POST /summarize**: Streaming Gemini Flash summaries via SSE
- **GET /health**: Production health check endpoint
- **In-memory caching**: Sub-10ms cache hits with TTLCache (300s TTL, 1000 entries)
- **FastAPI/Uvicorn**: Production-ready ASGI server
- **Cloud Run ready**: Dockerfile and deployment configuration included

### Demo & UI
- **Need web interface for search?** → `demo-website/`
- **Need to test search-api visually?** → `demo-website/`
- **Need streaming SSE demo?** → `demo-website/`
- **Need to demo vector search to stakeholders?** → `demo-website/`

**demo-website** provides:
- Tab-based UI for search and summarization
- Real-time latency metrics display
- Cache hit/miss indicators
- Server-Sent Events (SSE) streaming for summaries
- Responsive mobile-friendly design
- Configurable API endpoint
- Cloud Run deployment ready
