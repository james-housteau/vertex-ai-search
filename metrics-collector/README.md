# Metrics Collector

Performance metrics collection and analysis for Vertex AI search and conversation operations.

## Overview

The metrics-collector module provides comprehensive performance metrics collection, aggregation, and analysis capabilities for search and conversation operations. It supports real-time metric recording, statistical calculations, and export functionality.

## Features

- Thread-safe metrics collection from search and conversation operations
- Statistical calculations (average, median, p95) using proper algorithms
- Real-time metric recording and batch analysis
- JSON and CSV export with pandas integration
- Comprehensive performance reports with timestamps

## Installation

```bash
make setup
```

## Usage

### CLI Interface

```bash
# Run metrics collector
make run-dev

# Or directly
poetry run metrics-collector
```

### API Usage

```python
from metrics_collector import MetricsCollector, PerformanceMetrics
from pathlib import Path

# Initialize collector
collector = MetricsCollector(output_dir=Path("./metrics"))

# Record metrics (examples with mock data)
search_result = SearchResult(...)
conversation_result = ConversationResult(...)

collector.record_search_metric(search_result)
collector.record_conversation_metric(conversation_result)

# Generate reports
metrics = collector.generate_report()
print(f"Success rate: {metrics.success_rate}")

# Export data
collector.export_to_json(Path("metrics.json"))
collector.export_to_csv(Path("metrics.csv"))
```

## API Reference

### PerformanceMetrics

```python
@dataclass
class PerformanceMetrics:
    operation_type: str          # 'search' or 'conversation'
    total_operations: int        # Total number of operations
    success_rate: float          # Percentage of successful operations
    avg_response_time_ms: float  # Average response time
    median_response_time_ms: float # Median response time
    p95_response_time_ms: float  # 95th percentile response time
    error_count: int             # Number of failed operations
    timestamp: datetime          # Report generation time
```

### MetricsCollector

```python
class MetricsCollector:
    def __init__(self, output_dir: Path = Path("./metrics")) -> None
    def record_search_metric(self, search_result: SearchResult) -> None
    def record_conversation_metric(self, conversation_result: ConversationResult) -> None
    def generate_report(self) -> PerformanceMetrics
    def export_to_json(self, file_path: Path) -> bool
    def export_to_csv(self, file_path: Path) -> bool
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
- pandas for statistical operations
- Thread-safe operations for concurrent usage

## Architecture

The module follows Pure Module Isolation principles:
- Independent build and test capability
- No external module dependencies
- Self-contained with all required functionality
- 80%+ test coverage requirement
