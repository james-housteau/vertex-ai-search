# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

This is a Python CLI tool created with the Genesis framework for Vertex AI conversation and answer testing functionality. The project uses Poetry for dependency management and follows a standard Python package structure with `src/` layout.

## Development Commands

### Essential Commands
```bash
# Initial setup and install dependencies
make setup

# Run the CLI tool in development mode
make run-dev
# or
poetry run answer-service

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
poetry run pytest tests/test_service.py -v

# Run specific test function
poetry run pytest tests/test_service.py::test_function_name -v

# Run tests matching pattern
poetry run pytest -k "test_pattern" -v
```

## Code Architecture

### Project Structure
- **Entry Point**: `src/answer_service/main.py` - Simple entry point that delegates to CLI
- **Core Service**: `src/answer_service/service.py` - AnswerService implementation with Vertex AI integration
- **Data Models**: `src/answer_service/models.py` - ConversationResult and related data classes
- **Package Layout**: Standard `src/` layout with `answer_service` as the main package
- **Testing**: Tests in `tests/` directory using pytest framework

### Core Components
- **AnswerService**: Main service class for conversation management and Vertex AI integration
- **ConversationResult**: Data model for conversation results with metrics and metadata
- **Conversation API**: Methods for starting, managing, and ending conversation sessions

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
- **Pure Module Isolation**: No ../imports allowed, module must be independently buildable
- **Google Cloud**: Requires proper GCP credentials and project configuration for Vertex AI services
