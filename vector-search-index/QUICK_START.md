# Quick Start Guide - vector-search-index

## Installation

```bash
cd /Users/source-code/vertex-ai-search/worktrees/feature-6/vector-search-index
make setup
```

## Running Tests

```bash
# Quick test (fast subset)
make test-quick

# Full test suite
make test

# With coverage report
make test-cov
```

## Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type check
make typecheck

# All quality checks
make quality
```

## Build Package

```bash
make build
```

## Usage Example

```python
from vector_search_index import (
    VectorSearchIndexManager,
    IndexConfig,
    DistanceMetric,
    ShardSize,
)

# Initialize
manager = VectorSearchIndexManager(
    project_id="my-project",
    location="us-central1"
)

# Create index
config = IndexConfig(
    display_name="my-index",
    dimensions=768,
    distance_metric=DistanceMetric.DOT_PRODUCT_DISTANCE,
)
index_name = manager.create_index(config)

# Get status
status = manager.get_index_status(index_name)
print(f"State: {status['state']}")

# List all indexes
indexes = manager.list_indexes()
for idx in indexes:
    print(f"- {idx['display_name']}")

# Delete
manager.delete_index(index_name)
```

## Module Structure

```
vector-search-index/
├── src/vector_search_index/     # Source code
│   ├── __init__.py              # Public API
│   ├── manager.py               # Index manager
│   └── config.py                # Configuration models
├── tests/                       # Test suite
│   ├── test_index_manager.py    # Manager tests
│   └── test_config_validation.py # Config tests
├── Makefile                     # Build targets
├── pyproject.toml               # Dependencies
└── README.md                    # Full documentation
```

## Development Workflow

1. Make changes to code
2. Run `make format` to format
3. Run `make test` to verify
4. Run `make quality` before commit
5. Run `make build` to package

## Documentation

- **README.md** - Full module documentation
- **CLAUDE.md** - AI-specific guidance
- **IMPLEMENTATION_STATUS.md** - Detailed implementation status
- **TDD_IMPLEMENTATION_SUMMARY.md** - TDD process summary

## Support

For detailed information, see README.md or CLAUDE.md.
