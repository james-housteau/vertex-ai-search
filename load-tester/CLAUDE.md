# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

This is a Python module for end-to-end load testing of Vertex AI Search and conversation systems. The project uses Poetry for dependency management and follows a standard Python package structure with `src/` layout.

## Development Commands

### Essential Commands
```bash
# Initial setup and install dependencies
make setup

# Run the CLI tool in development mode
make run-dev
# or
poetry run load-tester

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
poetry run pytest tests/test_load_tester.py -v

# Run specific test function
poetry run pytest tests/test_load_tester.py::test_function_name -v

# Run tests matching pattern
poetry run pytest -k "test_pattern" -v
```

## Code Architecture

### Project Structure
- **Entry Point**: `src/load_tester/main.py` - CLI entry point with Click commands
- **Core Module**: `src/load_tester/load_tester.py` - Main LoadTester class implementation
- **Data Models**: `src/load_tester/models.py` - API contract dataclasses and mock services
- **Package Layout**: Standard `src/` layout with `load_tester` as the main package
- **Testing**: Comprehensive tests in `tests/` directory using pytest framework

### API Contract
The module implements the exact API contract specified in Stream 4:

#### Configuration and Results
```python
@dataclass
class LoadTestConfig:
    concurrent_users: int
    test_duration_seconds: int
    search_queries: List[str]
    conversation_queries: List[str]
    ramp_up_time_seconds: int

@dataclass
class LoadTestResult:
    config: LoadTestConfig
    total_operations: int
    search_metrics: PerformanceMetrics
    conversation_metrics: PerformanceMetrics
    error_rate: float
    success: bool
```

#### LoadTester Class
```python
class LoadTester:
    def __init__(self, search_engine: SearchEngine, answer_service: AnswerService, metrics_collector: MetricsCollector) -> None
    def run_load_test(self, config: LoadTestConfig) -> LoadTestResult
    def run_search_load_test(self, queries: List[str], concurrent_users: int, duration_seconds: int) -> LoadTestResult
    def run_conversation_load_test(self, queries: List[str], concurrent_users: int, duration_seconds: int) -> LoadTestResult
    def generate_comprehensive_report(self, result: LoadTestResult) -> str
```

### CLI Commands
The application provides a Click-based CLI with the following commands:
- `run-load-test` - Execute comprehensive load test with mixed operations
- `search-load-test` - Execute search-only load test
- `conversation-load-test` - Execute conversation-only load test
- `validate` - Validate connection to all required services

### Load Testing Capabilities
- **Concurrent Execution**: Uses ThreadPoolExecutor for realistic concurrent user simulation
- **Ramp-up Timing**: Gradual user load increase with configurable timing
- **Mixed Operations**: Simultaneous search and conversation operations
- **Performance Metrics**: Comprehensive response time and throughput analysis
- **Error Handling**: Graceful handling of service failures and timeouts

### Mock Services for Independent Testing
The module includes complete mock implementations:
- **MockSearchEngine**: Simulates search operations with realistic response times
- **MockAnswerService**: Simulates conversation operations
- **MockMetricsCollector**: Collects and calculates performance metrics

This enables full module testing without external dependencies.

### Configuration
- **Poetry**: All dependencies managed via `pyproject.toml`
- **Code Style**: Black formatting (88 char line length), isort for imports
- **Type Checking**: mypy with strict settings (`disallow_untyped_defs`)
- **Testing**: pytest with 80% coverage requirement, HTML coverage reports, asyncio support
- **Environment**: direnv configuration in `.envrc` with project-specific settings

### Pure Module Isolation
This module follows Pure Module Isolation principles:
- Independent build and test capability (`make test`, `make build`)
- No ../imports or external module dependencies
- Self-contained with all required functionality through mock services
- <60 files total
- 80%+ test coverage requirement

## Important Notes

- **Python Version**: Requires Python 3.13+
- **Coverage Requirement**: Tests must maintain 80% coverage (enforced by pytest configuration)
- **Code Style**: Strictly enforced via black (88 chars) and ruff linting
- **Type Safety**: All functions must have type annotations (mypy strict mode)
- **Environment**: Uses direnv for automatic environment setup when entering the directory
- **Concurrency**: Uses asyncio and concurrent.futures for realistic load simulation
- **Testing**: Comprehensive mocking ensures independent testing without external services

## Dependencies

### Production Dependencies
- **pydantic**: Data validation and settings management
- **click**: CLI framework for command-line interface
- **python-dotenv**: Environment variable management

### Development Dependencies
- **pytest**: Testing framework with coverage reporting
- **pytest-cov**: Coverage plugin for pytest
- **pytest-mock**: Mocking utilities for pytest
- **pytest-asyncio**: Async testing support
- **black**: Code formatting
- **isort**: Import sorting
- **mypy**: Static type checking
- **ruff**: Fast Python linter

## Test Strategy

### TDD Implementation
The module was implemented using Test-Driven Development (TDD):
1. **RED Phase**: Comprehensive acceptance tests defining API contract
2. **GREEN Phase**: Minimal implementation to pass tests with mock services
3. **REFACTOR Phase**: Code quality improvements while maintaining test coverage

### Test Categories
- **test_acceptance.py**: API contract validation and comprehensive scenarios
- **test_models.py**: Data models and mock service testing
- **test_load_tester.py**: Core LoadTester functionality and concurrent execution
- **test_cli.py**: CLI command testing with mocking
- **test_integration.py**: End-to-end integration workflows

### Test Coverage
- Target: 80%+ coverage
- All critical paths covered including error scenarios
- Comprehensive mocking for all external dependencies
- Independent test execution without external services
- Concurrent execution testing with realistic scenarios

## Load Testing Patterns

### Supported Scenarios
1. **Comprehensive Mixed Testing**: Search + conversation operations simultaneously
2. **Search-Only Testing**: Pure search functionality validation
3. **Conversation-Only Testing**: Answer generation performance testing
4. **High Concurrency Testing**: Stress testing with multiple concurrent users
5. **Ramp-up Testing**: Gradual load increase simulation

### Performance Metrics
- Response time distribution (min, max, avg, percentiles)
- Throughput measurement (requests per second)
- Success/failure rates and error analysis
- Concurrent user handling capabilities

### Integration Strategy
The module uses composition to integrate with other Stream 4 modules:
- Accepts SearchEngine, AnswerService, and MetricsCollector instances
- Provides factory function with mock implementations for testing
- Supports different load testing patterns through configuration
- Generates comprehensive reports combining all module metrics

This completes Stream 4 and provides the complete testing framework for the Vertex AI Search system.
