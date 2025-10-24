# html-extractor

HTML content extraction module for Vertex AI search functionality


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

- Extract clean text content from HTML files and URLs
- BeautifulSoup for robust HTML parsing
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
cd vertex-ai-search/html-extractor
poetry install
```

### Install as Package

```bash
pip install html-extractor
```

## Usage

After installation, you can use the `html-extractor` command:

```bash
# Show help
html-extractor --help

# Extract text from a URL
html-extractor extract-url https://example.com

# Extract text from a local HTML file
html-extractor extract-file /path/to/file.html

# Save extracted content to a file
html-extractor extract-url https://example.com --output extracted.txt
html-extractor extract-file /path/to/file.html --output extracted.txt
```

## Available Commands

- `extract-url` - Extract text content from a URL
- `extract-file` - Extract text content from an HTML file

## Development

```bash
# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Run the CLI in development
poetry run html-extractor --help

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
