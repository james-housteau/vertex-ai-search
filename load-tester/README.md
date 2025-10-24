# Load Tester

End-to-End Load Testing for Vertex AI Search system. This module provides comprehensive load testing capabilities for validating search and conversation operations under concurrent user loads.

## Features

- **Comprehensive Load Testing**: Mixed search and conversation operations
- **Concurrent User Simulation**: Realistic multi-user load patterns
- **Performance Metrics Collection**: Detailed response time and throughput analysis
- **Ramp-up Timing**: Gradual user load increase simulation
- **Independent Testing**: Mock services for development and testing
- **CLI Interface**: Easy-to-use command-line tools

## Installation

```bash
# Install dependencies
make setup

# Run tests
make test

# Build package
make build
```

## Quick Start

### CLI Usage

```bash
# Run comprehensive load test
load-tester run-load-test --concurrent-users 10 --duration 30 \
  --search-queries "AI basics" --search-queries "ML concepts" \
  --conversation-queries "Explain AI" --conversation-queries "What is ML?"

# Run search-only load test
load-tester search-load-test --concurrent-users 5 --duration 15 \
  --queries "search query 1" --queries "search query 2"

# Run conversation-only load test
load-tester conversation-load-test --concurrent-users 3 --duration 20 \
  --queries "conversation 1" --queries "conversation 2"

# Validate service connections
load-tester validate --project-id my-project --data-store-id my-datastore
```

### Python API

```python
from load_tester.load_tester import create_load_tester_with_mocks
from load_tester.models import LoadTestConfig

# Create load tester (with mock services for development)
load_tester = create_load_tester_with_mocks("project-id", "datastore-id")

# Configure load test
config = LoadTestConfig(
    concurrent_users=10,
    test_duration_seconds=30,
    search_queries=["AI basics", "ML concepts"],
    conversation_queries=["Explain AI", "What is ML?"],
    ramp_up_time_seconds=5
)

# Execute comprehensive load test
result = load_tester.run_load_test(config)

# Generate comprehensive report
report = load_tester.generate_comprehensive_report(result)
print(report)
```

## API Contract

### LoadTestConfig

```python
@dataclass
class LoadTestConfig:
    concurrent_users: int
    test_duration_seconds: int
    search_queries: List[str]
    conversation_queries: List[str]
    ramp_up_time_seconds: int
```

### LoadTestResult

```python
@dataclass
class LoadTestResult:
    config: LoadTestConfig
    total_operations: int
    search_metrics: PerformanceMetrics
    conversation_metrics: PerformanceMetrics
    error_rate: float
    success: bool
```

### LoadTester Class

```python
class LoadTester:
    def __init__(self, search_engine: SearchEngine, answer_service: AnswerService, metrics_collector: MetricsCollector) -> None
    def run_load_test(self, config: LoadTestConfig) -> LoadTestResult
    def run_search_load_test(self, queries: List[str], concurrent_users: int, duration_seconds: int) -> LoadTestResult
    def run_conversation_load_test(self, queries: List[str], concurrent_users: int, duration_seconds: int) -> LoadTestResult
    def generate_comprehensive_report(self, result: LoadTestResult) -> str
```

## Load Testing Scenarios

### Comprehensive Mixed Testing
- Simultaneous search and conversation operations
- Realistic user behavior simulation
- Full system stress testing

### Search-Only Testing
- Pure search functionality validation
- Search engine performance analysis
- Query response time measurement

### Conversation-Only Testing
- Answer generation performance
- Conversation service validation
- Complex query handling

### High Concurrency Testing
- Stress testing with multiple concurrent users
- System capacity validation
- Performance under load

## Performance Metrics

- **Response Times**: Min, Max, Average, P50, P95, P99
- **Throughput**: Requests per second
- **Success Rates**: Successful vs failed operations
- **Error Analysis**: Error rate calculation and reporting
- **Concurrency**: Concurrent user handling performance

## Testing with Mock Services

The module includes comprehensive mock implementations for independent testing:

- **MockSearchEngine**: Simulates search operations with realistic response times
- **MockAnswerService**: Simulates conversation operations
- **MockMetricsCollector**: Collects and calculates performance metrics

This enables full module testing without external dependencies.

## Development

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run specific test file
poetry run pytest tests/test_load_tester.py -v

# Format code
make format

# Type checking
make typecheck

# Quality checks
make quality
```

## Integration

This module integrates with other Stream 4 modules:

- **search-engine**: For search functionality testing
- **answer-service**: For conversation testing
- **metrics-collector**: For performance metrics collection

The module follows Pure Module Isolation principles and can be developed, tested, and deployed independently.

## Requirements

- Python 3.13+
- Poetry for dependency management
- 80%+ test coverage
- Type annotations for all functions
- Independent build and test capabilities
