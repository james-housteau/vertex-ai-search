# Document Uploader Module

A high-performance document uploader module for Vertex AI search functionality that efficiently transfers HTML files to Google Cloud Storage with parallel processing and comprehensive error handling.

## Features

- **Parallel Uploads**: Configurable concurrent uploads (default: 4 workers) for optimal performance
- **Progress Tracking**: Real-time upload progress with file count and data transfer metrics
- **Error Handling**: Retry logic with exponential backoff for failed uploads
- **File Validation**: Verify uploaded files match local versions (size/checksum)
- **Performance Optimized**: Efficient chunked uploads for large files with memory management
- **Comprehensive Testing**: 80%+ test coverage with unit, integration, and acceptance tests

## API Overview

### Core Classes

```python
from document_uploader import DocumentUploader, UploadResult, BatchUploadResult

# Initialize uploader
uploader = DocumentUploader(
    bucket_name="my-bucket",
    project_id="my-project",
    max_workers=4
)

# Upload single file
result = uploader.upload_file(Path("document.html"))

# Batch upload directory
batch_result = uploader.upload_directory(Path("./documents/"), gcs_prefix="uploads/")

# Validate upload
is_valid = uploader.validate_upload(Path("document.html"), "gs://bucket/document.html")

# Track progress
progress = uploader.get_upload_progress()
```

### Data Classes

```python
@dataclass
class UploadResult:
    local_path: Path
    gcs_uri: str
    file_size: int
    upload_time_seconds: float
    success: bool
    error_message: Optional[str] = None

@dataclass
class BatchUploadResult:
    total_files: int
    successful_uploads: int
    failed_uploads: int
    uploaded_uris: List[str]
    failed_files: List[str]
    total_upload_time_seconds: float
    total_size_bytes: int
```

## Development

This project follows TDD methodology and is scaffolded with Genesis for quick development setup.

### Quick Start

```bash
# Setup the development environment
make setup

# Run the application
make run-dev

# Run tests (with coverage)
make test-cov

# Check code quality
make quality

# Quick test runner (no dependencies required)
python test_runner.py
```

### CLI Usage

```bash
# Upload single file
document-uploader upload-file document.html --bucket my-bucket --project my-project

# Upload directory
document-uploader upload-directory ./documents/ --bucket my-bucket --project my-project --prefix uploads/
```

### Testing

The module includes comprehensive test coverage:

- **Unit Tests**: Test individual components and methods
- **Integration Tests**: Test complete workflows and error scenarios
- **Acceptance Tests**: Test user-facing functionality and requirements
- **Retry Logic Tests**: Test exponential backoff and failure handling

```bash
# Run all tests
make test

# Run specific test file
poetry run pytest tests/test_document_uploader.py -v

# Run tests with coverage
make test-cov
```

## Architecture

### TDD Implementation

The module was developed following Test-Driven Development:

1. **RED Phase**: Created failing acceptance tests for all requirements
2. **GREEN Phase**: Implemented minimal functionality to pass tests
3. **REFACTOR Phase**: Added optimizations, retry logic, and performance improvements

### Key Components

- **DocumentUploader**: Main class handling GCS operations
- **Retry Logic**: Exponential backoff for transient failures
- **Progress Tracking**: Real-time upload statistics
- **Parallel Processing**: ThreadPoolExecutor for concurrent uploads

### Performance Optimizations

- **Parallel Uploads**: Multiple concurrent workers for batch operations
- **Memory Efficient**: Streaming uploads for large files
- **Retry Strategy**: Smart retry with exponential backoff for transient failures
- **Progress Monitoring**: Real-time statistics without performance impact

## Dependencies

- **google-cloud-storage**: GCS client library
- **google-auth**: Authentication for Google Cloud services
- **concurrent.futures**: Parallel processing
- **pytest**: Testing framework
- **black/ruff**: Code formatting and linting

## Integration

This module is designed to integrate with other Vertex AI search components:

- **gcs-manager**: For bucket operations and management
- **filename-sanitizer**: For clean, consistent filenames
- **config-manager**: For upload settings and configuration
- **vertex-datastore**: Exports upload services for data ingestion

## Genesis Shared Utilities

This project uses `shared-core`, the same battle-tested utilities that power Genesis itself:

- **Configuration Management**: `ConfigLoader` for YAML/env config with validation
- **Logging**: Structured logging with `get_logger()`
- **Error Handling**: Comprehensive error context with `create_error_context()`
- **Resilience**: Retry logic with exponential backoff via `@retry` decorator
- **Health Checks**: Production-ready health monitoring with `HealthCheck`
- **Environment**: Type-safe env vars with `get_required_env()` and `get_optional_env()`

These utilities are proven in production and follow Genesis best practices.

## License

This project is created with Genesis and follows the MIT license.
