# vertex-ai-search

A vertex-ai-search project created with Genesis


## Genesis Shared Utilities

This project uses `shared-core`, the same battle-tested utilities that power Genesis itself:

- **Configuration Management**: `ConfigLoader` for YAML/env config with validation
- **Logging**: Structured logging with `get_logger()`
- **Error Handling**: Comprehensive error context with `create_error_context()`
- **Resilience**: Retry logic with exponential backoff via `@retry` decorator
- **Health Checks**: Production-ready health monitoring with `HealthCheck`
- **Environment**: Type-safe env vars with `get_required_env()` and `get_optional_env()`

These utilities are proven in production and follow Genesis best practices.

## Features

- Click framework for CLI commands
- Rich library for beautiful terminal output
- Poetry for dependency management
- Pytest with coverage reporting
- Pre-commit hooks for code quality
- Type checking with mypy

## Installation

### Prerequisites

- Python 3.13+
- Poetry

### Install from Source

```bash
# Clone and install
git clone <repository-url>
cd vertex-ai-search
poetry install
```

### Install as Package

```bash
pip install vertex-ai-search
```

## Usage

After installation, you can use the `vertex-ai-search` command:

```bash
# Show help
vertex-ai-search --help

# Say hello
vertex-ai-search hello
vertex-ai-search hello --name Alice --count 3

# Display styled messages
vertex-ai-search display "Welcome to vertex-ai-search!"
vertex-ai-search display "Success!" --style success
vertex-ai-search display "Warning!" --style warning

# Check status
vertex-ai-search status
```

## Available Commands

- `hello` - Say hello to someone
- `display` - Display text with styling options
- `status` - Show application status

## Development

```bash
# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Run the CLI in development
poetry run vertex-ai-search --help

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov

# Format code
poetry run black src/ tests/
poetry run isort src/ tests/

# Type checking
poetry run mypy src/
```

## Building and Distribution

```bash
# Build the package
poetry build

# Publish to PyPI (if configured)
poetry publish
```

## Testing

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run all quality checks
make quality
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the quality checks
6. Submit a pull request
