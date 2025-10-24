# vertex-datastore

Vertex AI Agent Builder data store management for unstructured HTML documents with layout-aware parsing.


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

- **Data Store Creation**: Create unstructured data stores with layout-aware HTML parsing
- **Document Import**: Import HTML documents from GCS with progress monitoring
- **Progress Tracking**: Real-time import progress with status updates
- **Serving Config**: Generate serving config paths for search integration
- **CLI Interface**: Complete command-line interface for all operations
- **Error Handling**: Robust error handling and validation
- **Type Safety**: Full type annotations with mypy checking

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
pip install vertex-datastore
```

## Usage

### CLI Interface

After installation, you can use the `vertex-datastore` command:

```bash
# Show help
vertex-datastore --help

# Create a data store
vertex-datastore --project-id my-project create "My Data Store" "gs://my-bucket/documents/"

# Import documents
vertex-datastore --project-id my-project import-docs my-datastore-id "gs://my-bucket/html-files/"

# Check import status
vertex-datastore --project-id my-project status "projects/my-project/operations/import-123"

# Get serving config for search integration
vertex-datastore --project-id my-project serving-config my-datastore-id

# Delete a data store
vertex-datastore --project-id my-project delete --force my-datastore-id
```

### Python API

```python
from vertex_datastore import VertexDataStoreManager

# Initialize manager
manager = VertexDataStoreManager(project_id="my-project", location="global")

# Create data store
result = manager.create_data_store("My HTML Store", "gs://my-bucket/html-docs/")
print(f"Created: {result.data_store_id}")

# Import documents
operation_id = manager.import_documents(result.data_store_id, "gs://my-bucket/html-docs/")

# Monitor progress
progress = manager.get_import_progress(operation_id)
print(f"Status: {progress.status}, Progress: {progress.progress_percent}%")

# Wait for completion
success = manager.wait_for_import_completion(operation_id, timeout_minutes=60)

# Get serving config for search
serving_config = manager.get_serving_config(result.data_store_id)
print(f"Serving config: {serving_config}")
```

## Available Commands

- `create` - Create a new unstructured data store
- `import-docs` - Import documents from GCS
- `status` - Check import operation status
- `serving-config` - Get serving config path for search integration
- `delete` - Delete a data store

## Development

```bash
# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Run the CLI in development
poetry run vertex-datastore --help

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
