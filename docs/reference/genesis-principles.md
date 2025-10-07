# Genesis Development Principles

Core principles that guide Genesis-based development.

## 1. Pure Module Isolation

Every module should be independently buildable and testable with <60 files.

### Implementation
```bash
# Each module has its own:
module/
├── Makefile           # Independent build system
├── pyproject.toml     # Or package.json for TypeScript
├── src/               # Source code (<30 files)
├── tests/             # Test files (<30 files)
└── README.md          # Module documentation
```

### Benefits
- AI tools can understand entire module context
- Faster CI/CD builds through parallel execution
- Clear ownership and boundaries
- Reduced cognitive load

### Enforcement
```bash
# Genesis validates module isolation
genesis validate --check-isolation

# Pre-commit hook prevents violations
.genesis/scripts/check-file-organization.sh
```

## 2. Fail-Fast Configuration

Never use silent defaults for critical configuration.

### ❌ Anti-Pattern: Silent Defaults
```python
# Dangerous: Hides configuration problems
api_url = os.getenv("API_URL", "http://localhost:8080")
timeout = int(os.getenv("TIMEOUT", "30"))
```

### ✅ Pattern: Explicit Requirements
```python
from shared_core.env import get_required_env

# Fails immediately if not configured
api_url = get_required_env("API_URL")
timeout = int(get_required_env("TIMEOUT"))
```

### Benefits
- Configuration issues discovered immediately
- No production surprises
- Clear deployment requirements
- Self-documenting configuration

## 3. Quality Gates

Every commit must pass automated quality checks.

### Standard Gates
1. **Format Check** - Consistent code style
2. **Lint Check** - Code quality standards
3. **Type Check** - Type safety validation
4. **Test Check** - All tests passing
5. **Security Check** - No vulnerabilities

### Implementation
```bash
# Use Genesis commit instead of git commit
genesis commit -m "feat: add new feature"

# Automatic quality gate execution:
# 1. Format code (black, prettier, gofmt)
# 2. Run linters (flake8, eslint, golint)
# 3. Type check (mypy, tsc)
# 4. Run tests (pytest, jest, go test)
# 5. Security scan (bandit, gitleaks)
```

### Custom Gates
```yaml
# .genesis/quality-gates.yml
gates:
  - name: no-hardcoded-values
    script: .genesis/scripts/find-hardcoded-values.sh
  - name: api-documentation
    script: .genesis/scripts/validate-api-docs.sh
```

## 4. Explicit Over Implicit

Make intentions clear in code and configuration.

### ❌ Anti-Pattern: Implicit Behavior
```python
def process(data, options=None):
    options = options or {}  # Hidden defaults
    timeout = options.get("timeout", 30)  # Magic number
```

### ✅ Pattern: Explicit Contracts
```python
from dataclasses import dataclass

@dataclass
class ProcessOptions:
    timeout: int = 30  # Visible default
    retries: int = 3

def process(data: dict, options: ProcessOptions):
    # Clear contract
```

## 5. Observability First

Build observability into the foundation, not as an afterthought.

### Standard Observability
```python
from shared_core.logger import get_logger
# from shared_core.monitoring import track_performance  # Module not available

logger = get_logger(__name__)

# @track_performance("api_call")
def fetch_data(endpoint: str):
    logger.info("Fetching data", endpoint=endpoint)
    # Implementation
```

### Metrics Collection
- Request latency
- Error rates
- Resource usage
- Business metrics

## 6. Progressive Enhancement

Start simple, enhance based on measured needs.

### Evolution Path
1. **Simple Script** → Working solution
2. **Add Tests** → Reliability
3. **Add Types** → Maintainability
4. **Add Monitoring** → Observability
5. **Add Caching** → Performance (if needed)
6. **Add Queue** → Scalability (if needed)

### ❌ Anti-Pattern: Premature Optimization
```python
# Over-engineered from start
class AbstractDataProcessorFactory:
    def create_processor(self, strategy: ProcessingStrategy):
        # Complex abstraction for simple problem
```

### ✅ Pattern: Progressive Complexity
```python
# Start simple
def process_data(data):
    return transform(data)

# Add complexity only when measured need exists
```

## 7. Test-Driven Development

Write tests first to drive design.

### TDD Workflow
```bash
# 1. Write failing test
# 2. Implement minimum code to pass
# 3. Refactor while keeping tests green

# Genesis TDD command
genesis tdd --feature "user authentication"
```

### Test Organization
```
tests/
├── unit/           # Fast, isolated tests
├── integration/    # Component interaction tests
└── e2e/           # End-to-end workflows
```

## 8. Documentation as Code

Documentation lives with code and is validated automatically.

### Documentation Requirements
- API documentation from code
- README for each module
- Architecture Decision Records (ADRs)
- Runbooks for operations

### Validation
```bash
# Genesis validates documentation
genesis validate --check-docs

# Pre-commit ensures docs updated
.genesis/scripts/validate-documentation.sh
```

## 9. Security by Design

Security is not optional or an afterthought.

### Security Practices
- No secrets in code
- Input validation
- Output encoding
- Dependency scanning
- Security headers

### Enforcement
```bash
# Automatic security scanning
genesis commit  # Runs gitleaks, bandit, etc.

# Pre-commit security checks
.genesis/scripts/security-scan.sh
```

## 10. Continuous Validation

Validate assumptions continuously, not just at release.

### Validation Layers
1. **Local Development** - Pre-commit hooks
2. **CI Pipeline** - Automated testing
3. **Staging** - Integration testing
4. **Production** - Health monitoring
5. **Post-Deploy** - Smoke tests

### Implementation
```yaml
# .github/workflows/validate.yml
on: [push, pull_request]
jobs:
  validate:
    steps:
      - run: genesis validate --all
```

## Anti-Patterns to Avoid

### 1. Silent Failures
```python
# ❌ Bad
try:
    result = risky_operation()
except:
    pass  # Silent failure

# ✅ Good
try:
    result = risky_operation()
except SpecificError as e:
    logger.error("Operation failed", error=str(e))
    raise
```

### 2. Magic Numbers/Strings
```python
# ❌ Bad
if retries > 3:  # What is 3?
    time.sleep(30)  # What is 30?

# ✅ Good
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 30

if retries > MAX_RETRIES:
    time.sleep(RETRY_DELAY_SECONDS)
```

### 3. Implicit Dependencies
```python
# ❌ Bad
import os
api_key = os.environ["API_KEY"]  # Crashes if missing

# ✅ Good
from shared_core.env import get_required_env
api_key = get_required_env("API_KEY")  # Clear requirement
```

### 4. Over-Engineering
```python
# ❌ Bad: Abstract factory for 2 types
class AbstractStrategyFactoryBuilder:
    # 200 lines of abstraction

# ✅ Good: Simple and direct
def create_processor(type: str):
    if type == "json":
        return JsonProcessor()
    return XmlProcessor()
```

## Measuring Success

### Module Health Metrics
- File count <60 per module
- Test coverage >80%
- Build time <2 minutes
- Zero security vulnerabilities
- All quality gates passing

### Project Health Metrics
- Mean time to recovery <1 hour
- Deployment frequency >1/day
- Lead time <1 day
- Change failure rate <5%

## Quick Reference

### Commands
```bash
genesis validate              # Run all validations
genesis commit               # Commit with quality gates
genesis autofix              # Fix formatting/linting
genesis status               # Check project health
genesis sync                 # Update from templates
```

### Environment Variables
```bash
# Required for all projects
ENV=development|staging|production
LOG_LEVEL=debug|info|warning|error
LOG_JSON=true|false

# Module isolation
AI_MAX_FILES=60
MAX_MODULE_SIZE=60

# Quality gates
QUALITY_GATES_ENABLED=true
FAIL_FAST=true
```

### File Structure
```
project/
├── .genesis/              # Genesis configuration
│   ├── config.yml        # Project configuration
│   ├── scripts/          # Quality gate scripts
│   └── templates/        # Custom templates
├── src/                  # Source code
├── tests/                # Test files
├── docs/                 # Documentation
└── Makefile             # Build automation
```
