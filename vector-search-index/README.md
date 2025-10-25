# vector-search-index

Vector Search Index management for Vertex AI Vector Search operations.

## Overview

This module provides functionality to create, update, delete, and monitor Vector Search indexes in Google Cloud Vertex AI. It supports ScaNN (Scalable Nearest Neighbors) algorithm configuration for approximate nearest neighbor search.

## Features

- Create Vector Search indexes with ScaNN configuration
- Update existing index configurations
- Delete indexes
- Monitor index deployment status
- Support for various distance metrics
- Configurable replication and sharding

## Installation

```bash
cd vector-search-index/
make setup
```

## Usage

```python
from vector_search_index import VectorSearchIndexManager

# Initialize manager
manager = VectorSearchIndexManager(
    project_id="my-project",
    location="us-central1"
)

# Create an index
index = manager.create_index(
    display_name="my-vector-index",
    dimensions=768,
    distance_metric="DOT_PRODUCT_DISTANCE",
    shard_size="SHARD_SIZE_SMALL"
)

# Get index status
status = manager.get_index_status(index_name)

# Delete an index
manager.delete_index(index_name)
```

## Development

```bash
# Run tests
make test

# Run tests with coverage
make test-cov

# Code quality checks
make quality

# Build package
make build
```

## Requirements

- Python 3.13+
- google-cloud-aiplatform >= 1.38.0
- Valid GCP credentials with Vertex AI permissions

## Testing

The module includes comprehensive tests with 80%+ coverage. Tests use mocked Vertex AI API calls to ensure reliability without requiring actual GCP resources.

```bash
# Quick tests
make test-quick

# Full test suite
make test

# Coverage report
make test-cov
```
