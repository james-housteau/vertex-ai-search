# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

This is a Python module for performance metrics collection and analysis for Vertex AI search and conversation operations. The project uses Poetry for dependency management and follows a standard Python package structure with `src/` layout.

## Development Commands

### Essential Commands
```bash
# Initial setup and install dependencies
make setup

# Run the CLI tool in development mode
make run-dev
# or
poetry run metrics-collector

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
poetry run pytest tests/test_metrics_collector.py -v

# Run specific test function
poetry run pytest tests/test_metrics_collector.py::test_function_name -v

# Run tests matching pattern
poetry run pytest -k "test_pattern" -v
```

## Code Architecture

### Project Structure
- **Entry Point**: `src/metrics_collector/main.py` - CLI entry point
- **Core Module**: `src/metrics_collector/metrics_collector.py` - Main MetricsCollector class
- **Data Models**: `src/metrics_collector/models.py` - PerformanceMetrics and related dataclasses
- **Package Layout**: Standard `src/` layout with `metrics_collector` as the main package
- **Testing**: Tests in `tests/` directory using pytest framework

### API Contract
The module implements the exact API contract specified in Stream 4:

#### PerformanceMetrics Dataclass
```python
@dataclass
class PerformanceMetrics:
    operation_type: str          # 'search' or 'conversation'
    total_operations: int        # Total number of operations
    success_rate: float          # Percentage of successful operations
    avg_response_time_ms: float  # Average response time
    median_response_time_ms: float # Median response time
    p95_response_time_ms: float  # 95th percentile response time
    error_count: int             # Number of failed operations
    timestamp: datetime          # Report generation time
```

#### MetricsCollector Class
```python
class MetricsCollector:
    def __init__(self, output_dir: Path = Path("./metrics")) -> None
    def record_search_metric(self, search_result: SearchResult) -> None
    def record_conversation_metric(self, conversation_result: ConversationResult) -> None
    def generate_report(self) -> PerformanceMetrics
    def export_to_json(self, file_path: Path) -> bool
    def export_to_csv(self, file_path: Path) -> bool
```

### Core Functionality
- **Thread-safe metrics collection** from search and conversation operations
- **Statistical calculations** (avg, median, p95) using proper algorithms
- **Real-time metric recording** and batch analysis
- **JSON and CSV export** with pandas integration
- **Comprehensive performance reports** with timestamps

### Configuration
- **Poetry**: All dependencies managed via `pyproject.toml`
- **Code Style**: Black formatting (88 char line length), isort for imports
- **Type Checking**: mypy with strict settings (`disallow_untyped_defs`)
- **Testing**: pytest with 80% coverage requirement, HTML coverage reports
- **Dependencies**: pandas for statistical operations and CSV export

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
- **Thread Safety**: All operations are thread-safe for concurrent usage
- **Statistical Accuracy**: Uses proper statistical algorithms for metrics calculations

## Dependencies

### Production Dependencies
- **pandas**: Statistical operations and CSV export functionality

### Development Dependencies
- **pytest**: Testing framework with coverage reporting
- **pytest-cov**: Coverage plugin for pytest
- **pytest-mock**: Mocking utilities for pytest
- **black**: Code formatting
- **isort**: Import sorting
- **mypy**: Static type checking
- **ruff**: Fast Python linter
- **types-pandas-stubs**: Type stubs for pandas

## Test Strategy

### TDD Implementation
The module was implemented using Test-Driven Development (TDD):
1. **RED Phase**: Comprehensive acceptance tests defining API contract
2. **GREEN Phase**: Minimal implementation to pass tests
3. **REFACTOR Phase**: Code quality improvements while maintaining tests

### Test Categories
- **test_acceptance.py**: API contract validation and acceptance tests
- **test_models.py**: PerformanceMetrics dataclass testing
- **test_metrics_collector.py**: Core MetricsCollector functionality
- **test_main.py**: CLI command testing

### Test Coverage
- Target: 80%+ coverage
- All critical paths covered including error scenarios
- Thread safety testing for concurrent operations
- Statistical calculation validation
- Export functionality testing
