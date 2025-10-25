# Vertex AI Search and Conversation Testing System

A comprehensive testing framework for Google Vertex AI Search and Conversation capabilities using 1600 HTML documents from the Natural Questions dataset.

## Pure Module Isolation Architecture

This system follows **Pure Module Isolation** principles. Each module exists independently at the root level and can be built, tested, and deployed in complete isolation.

### Available Modules

Each module is self-contained with its own `pyproject.toml`, `Makefile`, tests, and dependencies:

#### Stream 1: Data Pipeline
- **`nq-downloader/`** - Download Natural Questions dataset (97.10% coverage)
- **`html-extractor/`** - Extract content from HTML documents (93% coverage)
- **`filename-sanitizer/`** - Cross-platform filename handling (94% coverage)

#### Stream 2: Infrastructure
- **`config-manager/`** - Configuration management (94.77% coverage)
- **`cli-orchestrator/`** - CLI framework integration (86% coverage)

#### Stream 3: Cloud Services
- **`gcs-manager/`** - Google Cloud Storage operations (97.10% coverage)
- **`document-uploader/`** - Parallel file upload with retry (94.15% coverage)
- **`vertex-datastore/`** - Vertex AI data store integration (95.54% coverage)

#### Stream 4: Testing & Metrics
- **`search-engine/`** - Vertex AI search functionality testing
- **`answer-service/`** - Conversation and answer generation testing
- **`metrics-collector/`** - Performance metrics collection
- **`load-tester/`** - End-to-end load testing orchestration

#### Stream 5: Vector Search Pipeline
- **`shared-contracts/`** - Shared Pydantic models (TextChunk, Vector768, SearchMatch) (100% coverage)
- **`html-chunker/`** - Chunk HTML into 450-token segments with 80-token overlap (100% coverage)
- **`embedding-generator/`** - Generate text-embedding-004 vectors (768D) (94% coverage)
- **`vector-index-prep/`** - Prepare JSONL for Vertex AI Vector Search (100% coverage)
- **`vector-search-index/`** - Manage Vertex AI Vector Search indexes (ScaNN) (100% coverage)
- **`vector-query-client/`** - Execute fast ANN queries (<120ms p95 target) (100% coverage)

#### Stream 6: Production API
- **`search-api/`** - FastAPI service with /search, /summarize, /health endpoints (88% coverage)

## Module Development (Pure Module Isolation)

### Working with Individual Modules

Each module is completely independent:

```bash
# Work with any module in isolation
cd nq-downloader
make test        # Test only this module
make build       # Build only this module
make clean       # Clean only this module

# No knowledge of other modules required
# No ../imports allowed
# <60 files per module for AI-safe development
```

### Module Requirements

Each module MUST:
- Build independently: `cd module && make build`
- Test independently: `cd module && make test`
- Have <60 files total
- Import only from declared dependencies
- Never import from `../` (parent directories)
- Be comprehensible without broader codebase knowledge

### Development Workflow

```bash
# Clone and work on any single module
git clone <repo>
cd <module-name>
make setup
make test
make build

# Develop in isolation - AI-safe worktrees
genesis worktree create <module-name>
cd <module-name>
# < 60 files, focused development
```

## System Integration

Modules connect through well-defined APIs, not compilation:

1. **Data Preparation**: `nq-downloader` → `html-extractor` → `filename-sanitizer`
2. **Configuration**: `config-manager` provides settings
3. **Cloud Operations**: `gcs-manager` → `document-uploader` → `vertex-datastore`
4. **Testing**: `search-engine` + `answer-service` → `metrics-collector` → `load-tester`
5. **Vector Search Pipeline**: `html-chunker` → `embedding-generator` → `vector-index-prep` → `vector-search-index`
6. **Production API**: `search-api` (uses `vector-query-client` + `shared-contracts`)

## Convenience Commands (Optional)

```bash
# List all available modules
make list-modules

# Test all modules independently (convenience only)
make test-all

# Build all modules independently (convenience only)
make build-all

# Quality checks on all modules (convenience only)
make quality-all

# Setup all modules (convenience only)
make setup-all
```

## Pure Module Isolation Benefits

- **Cognitive Load**: Work on <60 files at a time
- **AI-Safe Development**: Focused, efficient development
- **True Parallel Development**: No conflicts between teams
- **Failure Isolation**: One broken module doesn't affect others
- **Deployment Flexibility**: Install/deploy only what you need

> "Each module should be like a space station module - fully self-contained with its own life support (tests, build, dependencies), connecting to others through well-defined airlocks (APIs), and capable of being jettisoned without destroying the station."

## Quick Start

```bash
# List all available modules
make list-modules

# Work with individual modules
cd nq-downloader
make setup
make test
make build

# Or use convenience commands for all modules
make setup-all
make test-all
make build-all
```

## Module Independence Validation

```bash
# Verify each module builds in isolation
for module in */; do
    if [ -f "$module/pyproject.toml" ]; then
        echo "Testing $module independence..."
        cd "$module"
        make test && make build
        cd ..
    fi
done
```

## System Capabilities

The complete system provides:
- **1600 HTML document processing** with Natural Questions dataset
- **Google Cloud Storage integration** with lifecycle management
- **Vertex AI Agent Builder** search and conversation testing
- **Vector Search Pipeline** for sub-120ms p95 latency queries
- **Production Search API** with in-memory caching and SSE streaming
- **Performance metrics collection** with statistical analysis
- **Load testing** with concurrent user simulation
- **End-to-end testing framework** for production validation

All modules maintain 80%+ test coverage and pass all quality gates independently.

### Low-Latency Vector Search (Phase 3 Complete)

The search-api module provides a production-ready FastAPI service:
- **GET /search**: Vector similarity search with <120ms p95 latency
- **POST /summarize**: Streaming Gemini Flash summaries via SSE
- **In-memory caching**: Sub-10ms cache hits with TTLCache
- **Cloud Run ready**: Dockerfile and deployment configuration included

See `docs/guides/VECTOR_SEARCH_QUICKSTART.md` for detailed usage examples.

## Genesis Framework Integration

This project uses Genesis shared utilities for battle-tested functionality:
- **Configuration Management**: `ConfigLoader` for YAML/env config
- **Logging**: Structured logging with `get_logger()`
- **Error Handling**: Comprehensive error context
- **Resilience**: Retry logic with exponential backoff
- **Health Checks**: Production-ready monitoring
