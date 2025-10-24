# Search Engine Module

Pure search functionality testing using Vertex AI Agent Builder API.

## Overview

This module provides a clean, isolated implementation for executing search queries against Vertex AI data stores, parsing responses, and handling authentication and API connectivity.

## Features

- Execute search queries against Vertex AI data stores
- Parse and validate search responses with proper error handling
- Handle authentication and API connectivity
- Provide search result analysis with timing metrics
- Support batch operations for efficiency

## API Contract

### SearchResult

```python
@dataclass
class SearchResult:
    query: str
    results: List[Dict[str, Any]]
    result_count: int
    execution_time_ms: float
    relevance_scores: List[float]
    success: bool
    error_message: Optional[str] = None
```

### SearchEngine

```python
class SearchEngine:
    def __init__(self, project_id: str, data_store_id: str) -> None
    def search(self, query: str, max_results: int = 10) -> SearchResult
    def batch_search(self, queries: List[str]) -> List[SearchResult]
    def validate_connection(self) -> bool
```

## Usage

### Python API

```python
from search_engine import SearchEngine

# Initialize engine
engine = SearchEngine(
    project_id="my-project",
    data_store_id="my-datastore"
)

# Single search
result = engine.search("machine learning", max_results=5)
if result.success:
    print(f"Found {result.result_count} results in {result.execution_time_ms}ms")
    for doc in result.results:
        print(f"- {doc.get('title', 'No title')}")

# Batch search
queries = ["AI", "machine learning", "data science"]
results = engine.batch_search(queries)

# Validate connection
if engine.validate_connection():
    print("Connection is valid")
```

### CLI

```bash
# Search with CLI
search-engine search \
    --project-id my-project \
    --data-store-id my-datastore \
    --query "machine learning" \
    --max-results 5

# Validate connection
search-engine validate \
    --project-id my-project \
    --data-store-id my-datastore
```

## Development

### Setup

```bash
make setup
```

### Testing

```bash
make test          # Run all tests
make test-cov      # Run tests with coverage
make test-quick    # Run fast tests only
```

### Code Quality

```bash
make quality       # Run all quality checks
make format        # Format code
make lint          # Lint code
make typecheck     # Type check
```

### Build

```bash
make build         # Build wheel package
```

## Dependencies

### Production Dependencies
- google-cloud-discoveryengine - Google Cloud Discovery Engine client (optional for testing)
- click - CLI framework

### Development Dependencies
- pytest - Testing framework
- pytest-cov - Coverage reporting
- pytest-mock - Mocking utilities
- black - Code formatting
- mypy - Type checking
- ruff - Linting

### Installation

For production use with Google Cloud:
```bash
pip install search-engine[gcp]
```

For development and testing (without Google Cloud):
```bash
pip install search-engine
```

## Testing Strategy

This module uses comprehensive mocking to enable testing without Google Cloud dependencies:

- **Dependency Mocking**: Google Cloud SDK is mocked at the module level
- **Independent Testing**: Tests run without requiring actual Google Cloud credentials
- **80% Coverage**: Maintained through comprehensive unit and integration tests
- **TDD Implementation**: Built using Test-Driven Development principles

### Running Tests Without Google Cloud

```bash
# Tests work without google-cloud-discoveryengine installed
make test

# Demonstrate mocking functionality
python test_mocking_demo.py
```

## Pure Module Isolation

This module follows Pure Module Isolation principles:
- Independent build and test capability
- No ../imports or external module dependencies
- Self-contained with all required functionality
- <60 files total
- 80%+ test coverage requirement
