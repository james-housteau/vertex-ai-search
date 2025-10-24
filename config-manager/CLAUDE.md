# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

This is a Python CLI tool created with the Genesis framework for Vertex AI search functionality. The project uses Poetry for dependency management and follows a standard Python package structure with `src/` layout.

## Development Commands

### Essential Commands
```bash
# Initial setup and install dependencies
make setup

# Run the CLI tool in development mode
make run-dev
# or
poetry run vertex-ai-search

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
poetry run pytest tests/test_cli.py -v

# Run specific test function
poetry run pytest tests/test_cli.py::test_function_name -v

# Run tests matching pattern
poetry run pytest -k "test_pattern" -v
```

## Code Architecture

### Project Structure
- **Entry Point**: `src/vertex_ai_search/main.py` - Simple entry point that delegates to CLI
- **CLI Framework**: `src/vertex_ai_search/cli.py` - Click-based command structure with Rich styling
- **Package Layout**: Standard `src/` layout with `vertex_ai_search` as the main package
- **Testing**: Tests in `tests/` directory using pytest framework

### CLI Commands
The application provides a Click-based CLI with the following commands:
- `hello` - Greeting command with name and count options
- `display` - Text display with styling options (info, success, warning, error)
- `status` - Application status and version info

### Configuration
- **Poetry**: All dependencies managed via `pyproject.toml`
- **Code Style**: Black formatting (88 char line length), isort for imports
- **Type Checking**: mypy with strict settings (`disallow_untyped_defs`)
- **Testing**: pytest with 80% coverage requirement, HTML coverage reports
- **Environment**: direnv configuration in `.envrc` with project-specific settings

### Genesis Framework Integration
This project is scaffolded with Genesis and includes:
- Shared utilities for configuration, logging, error handling, and resilience patterns
- Standard development toolchain (Poetry, pytest, black, mypy, ruff)
- Pre-commit hooks for code quality
- Makefile with standardized development commands

## Important Notes

- **Python Version**: Requires Python 3.13+
- **Coverage Requirement**: Tests must maintain 80% coverage (enforced by pytest configuration)
- **Code Style**: Strictly enforced via black (88 chars) and ruff linting
- **Type Safety**: All functions must have type annotations (mypy strict mode)
- **Environment**: Uses direnv for automatic environment setup when entering the directory
