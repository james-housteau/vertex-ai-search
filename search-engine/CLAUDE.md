# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

This is a Python module for pure search functionality testing using Vertex AI Agent Builder API. The project uses Poetry for dependency management and follows a standard Python package structure with `src/` layout.

## Development Commands

### Essential Commands
```bash
# Initial setup and install dependencies
make setup

# Run the CLI tool in development mode
make run-dev
# or
poetry run search-engine

# Run tests
make test                 # All tests with verbose output
make test-quick          # Fast subset for rapid feedback
make test-cov            # Tests with coverage report (80% minimum required)

# Code quality checks
make format              # Format with black and ruff
make lint                # Lint with ruff
make typecheck           # Type check with mypy
make quality             # Run all quality checks (format + lint + typecheck)

# Build and distribution
make build               # Build wheel packages
make clean               # Clean all artifacts and caches
```

### Single Test Execution
```bash
# Run specific test file
poetry run pytest tests/test_search_engine.py -v

# Run specific test function
poetry run pytest tests/test_search_engine.py::test_function_name -v

# Run tests matching pattern
poetry run pytest -k "test_pattern" -v
```

## Code Architecture

### Project Structure
- **Entry Point**: `src/search_engine/main.py` - CLI entry point
- **Core Module**: `src/search_engine/search_engine.py` - Main SearchEngine class
- **Data Models**: `src/search_engine/models.py` - SearchResult dataclass
- **Package Layout**: Standard `src/` layout with `search_engine` as the main package
- **Testing**: Tests in `tests/` directory using pytest framework

### API Contract
The module implements the exact API contract specified in Stream 4:

#### SearchResult Dataclass
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

#### SearchEngine Class
```python
class SearchEngine:
    def __init__(self, project_id: str, data_store_id: str) -> None
    def search(self, query: str, max_results: int = 10) -> SearchResult
    def batch_search(self, queries: List[str]) -> List[SearchResult]
    def validate_connection(self) -> bool
```

### CLI Commands
The application provides a Click-based CLI with the following commands:
- `search` - Execute search queries with project-id, data-store-id, query, and max-results options
- `validate` - Validate connection to Vertex AI search service

### Configuration
- **Poetry**: All dependencies managed via `pyproject.toml`
- **Code Style**: Black formatting (88 char line length), isort for imports
- **Type Checking**: mypy with strict settings (`disallow_untyped_defs`)
- **Testing**: pytest with 80% coverage requirement, HTML coverage reports
- **Environment**: direnv configuration in `.envrc` with project-specific settings

### Pure Module Isolation
This module follows Pure Module Isolation principles:
- Independent build and test capability (`make test`, `make build`)
- No ../imports or external module dependencies
- Self-contained with all required functionality
- <60 files total
- 80%+ test coverage requirement

## Important Notes

- **Python Version**: Requires Python 3.13+
- **Coverage Requirement**: Tests must maintain 80% coverage (enforced by pytest configuration)
- **Code Style**: Strictly enforced via black (88 chars) and ruff linting
- **Type Safety**: All functions must have type annotations (mypy strict mode)
- **Environment**: Uses direnv for automatic environment setup when entering the directory
- **Google Cloud**: Requires google-cloud-discoveryengine dependency for API access
- **Testing**: Comprehensive mocking for Google Cloud APIs to ensure independent testing

## Dependencies

### Production Dependencies
- **google-cloud-discoveryengine**: Google Cloud Discovery Engine client for Vertex AI search
- **pydantic**: Data validation and settings management
- **click**: CLI framework for command-line interface
- **python-dotenv**: Environment variable management

### Development Dependencies
- **pytest**: Testing framework with coverage reporting
- **pytest-cov**: Coverage plugin for pytest
- **pytest-mock**: Mocking utilities for pytest
- **black**: Code formatting
- **isort**: Import sorting
- **mypy**: Static type checking
- **ruff**: Fast Python linter

## Test Strategy

### TDD Implementation
The module was implemented using Test-Driven Development (TDD):
1. **RED Phase**: Comprehensive acceptance tests defining API contract
2. **GREEN Phase**: Minimal implementation to pass tests
3. **REFACTOR Phase**: Code quality improvements while maintaining tests

### Test Categories
- **test_acceptance.py**: API contract validation and acceptance tests
- **test_models.py**: SearchResult dataclass testing
- **test_search_engine.py**: Core SearchEngine functionality
- **test_cli.py**: CLI command testing
- **test_integration.py**: End-to-end integration workflows

### Test Coverage
- Target: 80%+ coverage
- All critical paths covered including error scenarios
- Comprehensive mocking for Google Cloud APIs
- Independent test execution without external dependencies
