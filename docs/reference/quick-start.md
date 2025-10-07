# Genesis Quick Start Guide

## Project Setup

### 1. Create New Project
```bash
# Bootstrap a new project
genesis bootstrap my-project --template python-api

# Or initialize Genesis in existing project
cd existing-project
genesis init --template cli-tool
```

### 2. Environment Setup
```bash
# Load environment (required for all work)
source .envrc

# Install dependencies
make setup

# Verify installation
genesis status
```

## Daily Development Workflow

### Starting Work
```bash
# Always start with environment
source .envrc

# Update from latest templates
genesis sync

# Check project health
genesis status
```

### Writing Code
```bash
# Create feature branch
git checkout -b feature/new-feature

# Run tests continuously
make test-watch

# Format and lint as you go
make format
make lint
```

### Committing Changes
```bash
# ALWAYS use genesis commit (not git commit)
genesis commit -m "feat: add user authentication"

# Genesis automatically:
# - Formats code
# - Runs linters
# - Checks types
# - Runs tests
# - Scans security
```

### Creating Pull Requests
```bash
# Push branch
git push -u origin feature/new-feature

# Create PR with Genesis
genesis pr create --title "Add user authentication"
```

## Common Tasks

### Running Tests
```bash
make test              # Run all tests
make test-unit         # Unit tests only
make test-integration  # Integration tests
make test-cov         # With coverage report
```

### Code Quality
```bash
make format           # Auto-format code
make lint            # Check code quality
make typecheck       # Type checking
make quality         # All quality checks
```

### Building & Deployment
```bash
make build           # Build project
make docker-build    # Build container
make deploy          # Deploy to environment
```

## Using Genesis Shared Core

### Basic Setup
```python
from shared_core.logger import get_logger
from shared_core.env import get_required_env
from shared_core.health import HealthCheck

# Logging
logger = get_logger(__name__)
logger.info("Application started")

# Configuration
api_key = get_required_env("API_KEY")

# Health checks
health = HealthCheck()
```

### Error Handling
```python
from shared_core.errors import handle_error

@handle_error(default_return=None)
def risky_operation():
    # Code that might fail
    pass
```

### External Services
```python
# from shared_core.retry import CircuitBreaker  # Note: retry module is empty

# breaker = CircuitBreaker()

# @breaker
def call_api():
    # API call with automatic circuit breaking
    pass
```

## Project Structure

```
my-project/
├── .genesis/           # Genesis configuration
│   ├── config.yml     # Project settings
│   └── scripts/       # Quality scripts
├── src/               # Source code
│   └── my_project/    # Python package
├── tests/             # Test files
│   ├── unit/
│   └── integration/
├── Makefile          # Build commands
├── pyproject.toml    # Python config
└── .envrc            # Environment setup
```

## Environment Variables

### Required
```bash
ENV=development       # Environment name
LOG_LEVEL=info       # Logging level
```

### Optional
```bash
LOG_JSON=false       # JSON logs (true in production)
DEBUG=true           # Debug mode
```

## Troubleshooting

### Environment Not Loaded
```
Error: Required environment variable 'LOG_LEVEL' is not set
```
**Fix:** Run `source .envrc`

### Genesis Command Not Found
```
Command 'genesis' not found
```
**Fix:** Run `make setup` to install Genesis

### Quality Gates Failed
```
❌ Linting failed
```
**Fix:** Run `make autofix` to fix automatically

### Too Many Files
```
Module has 73 files (exceeds 60 file limit)
```
**Fix:** Split module or use worktrees

## Getting Help

### Documentation
```bash
# View Genesis documentation
genesis docs

# View project README
cat README.md
```

### Commands
```bash
# List all Genesis commands
genesis --help

# Get help for specific command
genesis commit --help
```

### Status Checks
```bash
# Check project health
genesis status

# Validate configuration
genesis validate
```

## Best Practices

### ✅ DO
- Run `source .envrc` before starting work
- Use `genesis commit` for all commits
- Keep modules under 60 files
- Write tests first (TDD)
- Use structured logging

### ❌ DON'T
- Use `git commit` directly
- Add silent defaults
- Ignore quality gate failures
- Store secrets in code
- Over-engineer solutions

## Quick Command Reference

| Task | Command |
|------|---------|
| Start work | `source .envrc` |
| Run tests | `make test` |
| Format code | `make format` |
| Commit changes | `genesis commit -m "message"` |
| Check health | `genesis status` |
| Update templates | `genesis sync` |
| Build project | `make build` |
| View logs | `make logs` |
| Clean workspace | `make clean` |

## Next Steps

1. Read [Genesis Principles](./genesis-principles.md)
2. Review [Shared Core Reference](./genesis-shared-core.md)
3. Set up your IDE with Genesis support
4. Join the Genesis community
