# Genesis Shared Core Reference

`genesis-shared-core` provides battle-tested utilities for Python applications following Genesis principles.

## Installation

Genesis projects automatically include `genesis-shared-core` as a dependency. For manual installation:

```bash
pip install genesis-shared-core
```

## Core Modules

### 1. Logging Framework

Professional logging with structured output and context awareness.

```python
from shared_core.logger import get_logger

logger = get_logger(__name__)

# Basic usage
logger.info("Processing request", request_id="123", user="alice")
logger.error("Failed to connect", error=str(e), retry_count=3)

# Structured logging (automatically enabled in production)
# Output: {"level": "INFO", "message": "Processing request", "request_id": "123", "user": "alice"}
```

**Features:**
- Automatic JSON formatting in production (`LOG_JSON=true`)
- Context preservation across function calls
- Performance metrics included
- File/line number tracking in debug mode

### 2. Configuration Management

Fail-fast configuration with type safety and validation.

```python
import os
from shared_core.env import get_required_env
from shared_core.config import ConfigLoader

# Required variables (fails fast if missing)
api_key = get_required_env("API_KEY")
database_url = get_required_env("DATABASE_URL")

# Optional with defaults
port = os.getenv("PORT", "8000")
workers = os.getenv("WORKERS", "4")

# Structured configuration using ConfigLoader
loader = ConfigLoader("APP_")
config = loader.load(defaults={
    "api_key": get_required_env("API_KEY"),
    "port": int(os.getenv("PORT", "8000")),
    "debug": os.getenv("DEBUG", "false").lower() == "true"
})
```

**Principles:**
- No silent defaults for critical configuration
- Clear error messages when configuration is missing
- Type conversion helpers for common cases

### 3. Health Monitoring

Application health checks with detailed diagnostics.

```python
from shared_core.health import HealthCheck, HealthStatus

checker = HealthCheck()

# Add component checks
checker.add_check("database", check_database_connection)
checker.add_check("cache", check_redis_connection)
checker.add_check("api", check_external_api)

# Get health status
status = checker.check_health()
# Returns: {
#   "status": "healthy",
#   "components": {
#     "database": {"status": "healthy", "latency": 0.023},
#     "cache": {"status": "healthy", "latency": 0.001},
#     "api": {"status": "degraded", "latency": 1.5, "error": "High latency"}
#   }
# }

# FastAPI integration
@app.get("/health")
async def health():
    return checker.check_health()
```

### 4. Error Handling

Consistent error handling with proper logging and recovery.

```python
from shared_core.errors import handle_error, ValidationError, ValidationError

# Custom error types
class PaymentError(ValidationError):
    """Payment processing failed"""
    pass

# Error handling decorator
@handle_error(default_return=None, log_errors=True)
def process_payment(amount: float):
    if amount <= 0:
        raise ValidationError("Amount must be positive")
    # Process payment...

# Manual error handling
try:
    result = risky_operation()
except Exception as e:
    handle_error(e, context={"operation": "risky", "user": user_id})
    raise
```

### 5. Retry Logic with Circuit Breaker

Resilient external service calls with automatic recovery.

```python
# from shared_core.retry import CircuitBreaker  # Note: retry module is empty, with_retry

# Circuit breaker for external services
# breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=RequestException
)

# @breaker
def call_external_api(endpoint: str):
    response = requests.get(endpoint)
    response.raise_for_status()
    return response.json()

# Exponential backoff retry
@with_retry(max_attempts=3, backoff_factor=2)
def upload_file(file_path: str):
    # Upload with automatic retry on failure
    pass
```

**Configuration:**
- `CB_FAILURE_THRESHOLD`: Failures before circuit opens (default: 5)
- `CB_TIMEOUT`: Recovery timeout in seconds (default: 60)
- `RETRY_MAX_ATTEMPTS`: Maximum retry attempts (default: 3)

### 6. Performance Monitoring

Track and optimize application performance.

```python
# from shared_core.monitoring import track_performance  # Module not available, get_metrics

# @track_performance("database_query")
def fetch_users(filter_params):
    # Database operation
    return users

# Get performance metrics
# metrics = get_metrics()
# Returns: {
#   "database_query": {
#     "count": 1523,
#     "avg_duration": 0.045,
#     "p95_duration": 0.120,
#     "p99_duration": 0.250
#   }
# }
```

## Environment Variables

Genesis shared-core respects these environment variables:

```bash
# Logging
LOG_LEVEL=info|debug|warning|error|critical
LOG_JSON=true|false              # JSON output for production
LOG_CONTEXT=true|false           # Include context in logs

# Circuit Breaker
CB_FAILURE_THRESHOLD=5           # Failures before opening
CB_TIMEOUT=60.0                  # Recovery timeout (seconds)
CB_EXPECTED_EXCEPTIONS=RequestException,TimeoutError

# Retry Policy
RETRY_MAX_ATTEMPTS=3            # Maximum retry attempts
RETRY_BACKOFF_FACTOR=2          # Exponential backoff multiplier
RETRY_MAX_DELAY=30              # Maximum delay between retries

# Health Checks
HEALTH_CHECK_TIMEOUT=5          # Health check timeout (seconds)
HEALTH_INCLUDE_DETAILS=true     # Include component details

# Performance
PERF_TRACKING_ENABLED=true      # Enable performance tracking
PERF_SAMPLING_RATE=1.0          # Sampling rate (0.0-1.0)
```

## Integration Examples

### FastAPI Application

```python
from fastapi import FastAPI
from shared_core.logger import get_logger
from shared_core.health import HealthCheck
from shared_core.env import get_required_env

app = FastAPI()
logger = get_logger(__name__)
health = HealthCheck()

# Configuration
API_KEY = get_required_env("API_KEY")
DATABASE_URL = get_required_env("DATABASE_URL")

@app.on_event("startup")
async def startup():
    logger.info("Starting application")
    health.add_check("database", check_database)

@app.get("/health")
async def health_check():
    return health.check_health()
```

### CLI Application

```python
import click
from shared_core.logger import get_logger
from shared_core.errors import handle_error

logger = get_logger(__name__)

@click.command()
@click.option("--config", required=True)
@handle_error(log_errors=True)
def main(config):
    logger.info("Starting CLI", config_file=config)
    # Application logic

if __name__ == "__main__":
    main()
```

### Background Worker

```python
from shared_core.logger import get_logger
# from shared_core.retry import CircuitBreaker  # Note: retry module is empty
# from shared_core.monitoring import track_performance  # Module not available

logger = get_logger(__name__)
# breaker = CircuitBreaker()

# @track_performance("job_processing")
# @breaker
def process_job(job_id):
    logger.info("Processing job", job_id=job_id)
    # Job processing logic

def worker_loop():
    while True:
        job = queue.get()
        try:
            process_job(job.id)
        except Exception as e:
            logger.error("Job failed", job_id=job.id, error=str(e))
```

## Best Practices

### 1. Fail-Fast Configuration
```python
# ❌ Bad: Silent defaults hide configuration issues
port = os.getenv("PORT", "8000")  # Might work in dev, fail in prod

# ✅ Good: Explicit requirement
port = get_required_env("PORT")  # Fails immediately if not set
```

### 2. Structured Logging
```python
# ❌ Bad: String concatenation loses structure
logger.info(f"User {user_id} performed {action}")

# ✅ Good: Structured fields for querying
logger.info("User action", user_id=user_id, action=action)
```

### 3. Error Context
```python
# ❌ Bad: Lost error context
except Exception:
    logger.error("Operation failed")

# ✅ Good: Preserve context for debugging
except Exception as e:
    logger.error("Operation failed",
                error=str(e),
                operation="data_sync",
                user_id=user_id)
```

### 4. Health Checks
```python
# ❌ Bad: Binary health status
@app.get("/health")
def health():
    return {"status": "ok"}

# ✅ Good: Detailed component health
@app.get("/health")
def health():
    return health_checker.check_health()
```

## Migration Guide

### From Python logging

```python
# Before: Standard logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Processing: %s", item_id)

# After: Genesis shared-core
from shared_core.logger import get_logger
logger = get_logger(__name__)
logger.info("Processing item", item_id=item_id)
```

### From os.environ

```python
# Before: Direct environment access
import os
api_key = os.environ.get("API_KEY", "default-key")

# After: Fail-fast configuration
from shared_core.env import get_required_env
api_key = get_required_env("API_KEY")
```

### From try/except blocks

```python
# Before: Manual error handling
try:
    result = process_data()
except Exception as e:
    print(f"Error: {e}")
    return None

# After: Consistent error handling
from shared_core.errors import handle_error

@handle_error(default_return=None)
def process_data():
    # Processing logic
    pass
```

## Troubleshooting

### Missing Environment Variables
```
ValueError: Required environment variable 'DATABASE_URL' is not set
```
**Solution:** Set all required variables or use `.env` file in development.

### Circuit Breaker Open
```
CircuitBreakerOpenError: Circuit breaker is open
```
**Solution:** Wait for recovery timeout or check external service health.

### JSON Logging in Development
```bash
# Disable JSON logging for local development
export LOG_JSON=false
export LOG_LEVEL=debug
```

### Performance Tracking Overhead
```bash
# Disable in development if needed
export PERF_TRACKING_ENABLED=false
```

## Support

- **Issues:** Report bugs at [Genesis GitHub](https://github.com/your-org/genesis)
- **Documentation:** Full docs at [Genesis Docs](https://docs.genesis.dev)
- **Version:** Check version with `pip show genesis-shared-core`
