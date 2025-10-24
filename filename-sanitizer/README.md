# filename-sanitizer

Cross-platform filename sanitization module for Vertex AI search functionality.

## Overview

The filename-sanitizer module provides robust, cross-platform filename sanitization capabilities for the Vertex AI search system. It ensures that filenames are safe, consistent, and compatible across different operating systems and file systems.

## Features

- Cross-platform filename sanitization
- Configurable sanitization rules
- Unicode normalization
- Length constraints
- Reserved name handling
- CLI interface for batch operations

## Installation

```bash
# Install dependencies
make setup

# Install for development
poetry install
```

## Usage

### CLI Usage

```bash
# Sanitize a single filename
filename-sanitizer sanitize "problematic filename!@#.txt"

# Batch sanitize files
filename-sanitizer batch-sanitize *.txt

# Check if filename is valid
filename-sanitizer validate "filename.txt"
```

### Python API Usage

```python
from filename_sanitizer import sanitize_filename, is_valid_filename

# Sanitize a filename
clean_name = sanitize_filename("problematic filename!@#.txt")
print(clean_name)  # "problematic_filename.txt"

# Check if filename is valid
is_valid = is_valid_filename("test.txt")
print(is_valid)  # True
```

## Development

### Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run quick tests
make test-quick
```

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type check
make typecheck

# Run all quality checks
make quality
```

### Building

```bash
# Build package
make build
```

## Architecture

The module follows a clean architecture with:

- **Core Logic**: Filename sanitization algorithms
- **CLI Interface**: Click-based command-line interface
- **Configuration**: Flexible sanitization rules
- **Validation**: Comprehensive filename validation

## Configuration

The module supports various configuration options:

- Maximum filename length
- Allowed/forbidden characters
- Unicode normalization form
- Platform-specific rules
- Extension handling

## License

This project is part of the Vertex AI search functionality toolkit.
