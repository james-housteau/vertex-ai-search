# Genesis Packaging System

The Genesis packaging system provides a robust, multi-layered approach to building, distributing, and installing Genesis components. This comprehensive guide covers the complete packaging ecosystem.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Package Structure](#package-structure)
- [Build System](#build-system)
- [Distribution Strategy](#distribution-strategy)
- [Installation Methods](#installation-methods)
- [Dynamic Dependency Resolution](#dynamic-dependency-resolution)
- [Development Workflow](#development-workflow)
- [Template Integration](#template-integration)
- [Common Operations](#common-operations)
- [Troubleshooting](#troubleshooting)

## Architecture Overview

Genesis uses a **dual-package architecture** with intelligent dependency resolution:

```
┌─────────────────────┐    ┌──────────────────────┐
│   genesis-cli       │    │ genesis-shared-core  │
│                     │    │                      │
│ • CLI commands      │───▶│ • Utilities          │
│ • Templates         │    │ • Logging            │
│ • Orchestration     │    │ • Config management  │
│ • Component tools   │    │ • Health checks      │
└─────────────────────┘    └──────────────────────┘
```

### Key Design Principles

1. **Modular Architecture**: Core utilities separated from CLI interface
2. **Dynamic Resolution**: Multiple fallback strategies for dependency installation
3. **Private Repository Support**: Works with GitHub private repositories
4. **Development Mode**: Local development paths for faster iteration
5. **Fail-Safe Installation**: Embedded manifests ensure installation always works

## Package Structure

### 1. Genesis CLI (`genesis-cli`)

**Location**: `/Users/jameshousteau/source_code/genesis/`
**Configuration**: `pyproject.toml`
**Package Name**: `genesis-cli`
**Version**: `0.12.0`

```toml
[tool.poetry]
name = "genesis-cli"
packages = [{include = "genesis"}, {include = "solve"}]
include = [
    "templates/**/*",
    "smart-commit/**/*",
    "worktree-tools/**/*",
    "scripts/**/*",
    "solve/**/*",
]
```

**Key Components**:
- **CLI Interface**: `genesis.cli` module with Click-based commands
- **Templates**: Complete project templates for Python, TypeScript, Terraform
- **Component Tools**: Worktree management, smart commit, bootstrap system
- **Solve System**: AI-safe development orchestration

**Entry Points**:
```toml
[tool.poetry.scripts]
genesis = "genesis.cli:cli"
```

### 2. Genesis Shared Core (`genesis-shared-core`)

**Location**: `/Users/jameshousteau/source_code/genesis/shared-python/`
**Configuration**: `shared-python/pyproject.toml`
**Package Name**: `genesis-shared-core`
**Version**: `0.1.0`

```toml
[tool.poetry]
name = "genesis-shared-core"
packages = [{include = "shared_core", from = "src"}]
```

**Key Modules**:
- **Logging**: Structured logging with JSON output support
- **Configuration**: Environment-driven configuration management
- **Health Checks**: Service health monitoring utilities
- **Retry Logic**: Circuit breaker and exponential backoff
- **Error Handling**: Structured error management framework

## Build System

### Poetry-Based Build Pipeline

Genesis uses **Poetry** as the primary build system with coordinated builds across packages:

```bash
# Build shared-core first
cd shared-python
poetry build

# Build CLI (depends on shared-core)
cd ..
poetry build
```

### Build Configuration

**Build Backend**: `poetry.core.masonry.api`
**Python Requirement**: `>=3.13` (CLI), `>=3.11` (shared-core)
**Build Output**: Both `.whl` (wheel) and `.tar.gz` (source) distributions

### Automated Build Script

The `scripts/publish-packages.sh` script coordinates the complete build process:

```bash
#!/bin/bash
# Publish Genesis packages to GitHub Release
echo "📦 Building genesis-shared-core..."
cd shared-python && poetry build && cd ..

echo "📦 Building genesis-cli..."
poetry build

echo "📤 Uploading packages to release: $RELEASE_TAG"
gh release upload $RELEASE_TAG shared-python/dist/* --clobber
gh release upload $RELEASE_TAG dist/* --clobber
```

## Distribution Strategy

### Multi-Channel Distribution

Genesis supports multiple distribution channels with automatic fallback:

#### 1. **GitHub Releases** (Primary)
- **URL Pattern**: `https://github.com/jhousteau/genesis/releases/download/{version}/{filename}`
- **Package Types**: `.whl` and `.tar.gz` for both packages
- **Authentication**: GitHub token for private repositories
- **Manifest**: `releases.json` uploaded as release asset

#### 2. **Local Development** (Development Mode)
- **Location**: Local `../genesis` directory detection
- **Installation**: `pip install -e` for editable installs
- **Shared Core**: `pip install -e ../genesis/shared-python`
- **CLI**: `pip install -e ../genesis`

#### 3. **Git Installation** (Fallback)
- **Format**: `pip install "genesis-cli @ git+https://github.com/jhousteau/genesis.git@main"`
- **Requirements**: GitHub token for private repositories
- **Use Case**: When GitHub releases aren't available

### Release Manifest System

The `releases.json` manifest provides version metadata and download URLs:

```json
{
  "latest": "v0.12.0",
  "versions": {
    "v0.12.0": {
      "cli": "genesis_cli-0.12.0-py3-none-any.whl",
      "shared_core": "genesis_shared_core-0.1.0-py3-none-any.whl",
      "cli_source": "genesis_cli-0.12.0.tar.gz",
      "shared_core_source": "genesis_shared_core-0.1.0.tar.gz"
    }
  }
}
```

## Installation Methods

### For Users

#### Simple Installation
```bash
pip install genesis-cli
```

#### From GitHub (Private Repository)
```bash
# Requires GITHUB_TOKEN environment variable
pip install "genesis-cli @ git+https://github.com/jhousteau/genesis.git@main"
```

#### Specific Version
```bash
pip install genesis-cli==0.12.0
```

### For Developers

#### Development Setup
```bash
# Clone repository
git clone https://github.com/jhousteau/genesis.git
cd genesis

# Install in development mode
poetry install

# Install shared-core in development mode
poetry run pip install -e shared-python/
```

#### Template Installation (Generated Projects)

Genesis templates automatically include installation logic:

```bash
# Local development (if genesis directory exists)
if [[ -d "../genesis" ]]; then
    poetry run pip install -e "../genesis/shared-python" 2>/dev/null || true
    poetry run pip install -e "../genesis"
    echo "✅ Genesis CLI installed from local development version"

# GitHub installation (with token)
elif [[ -n "${GITHUB_TOKEN}" ]]; then
    poetry run pip install --force-reinstall \
      "genesis-cli @ git+https://github.com/jhousteau/genesis.git@main"
    echo "✅ Genesis CLI installed from GitHub"
fi
```

## Dynamic Dependency Resolution

### Hybrid Resolution System

Genesis implements a sophisticated three-tier dependency resolution system in `genesis/core/dependencies.py`:

```python
class DependencyResolver:
    def get_manifest(self) -> dict:
        """Get manifest using hybrid approach: local → authenticated → embedded."""
        # Strategy 1: Local file (development)
        if manifest := self._try_local_manifest():
            return manifest

        # Strategy 2: Authenticated GitHub fetch
        if manifest := self._try_authenticated_fetch():
            return manifest

        # Strategy 3: Embedded fallback (always works)
        return get_embedded_manifest()
```

#### Resolution Strategies

1. **Local Development** (`_try_local_manifest`)
   - Looks for `releases.json` in Genesis repository
   - Used during Genesis development
   - Fastest resolution path

2. **Authenticated GitHub** (`_try_authenticated_fetch`)
   - Uses `GITHUB_TOKEN` to access private releases
   - Fetches `releases.json` from latest release assets
   - Supports private repository deployments

3. **Embedded Manifest** (`get_embedded_manifest`)
   - Hard-coded manifest in source code
   - Always available, no network required
   - Updated during each release

### Auto-Installation System

The `genesis.install` module provides automatic dependency installation:

```python
def ensure_dependencies():
    """Ensure all Genesis dependencies are available."""
    if not is_shared_core_available():
        logger.info("genesis-shared-core not found, installing dynamically...")
        url = get_shared_core_url()  # Uses DependencyResolver
        subprocess.run([sys.executable, "-m", "pip", "install", url])
```

**Triggered**: Automatically when Genesis CLI starts
**Fallback**: Local path injection if installation fails

## Development Workflow

### Local Development Setup

```bash
# 1. Clone and setup
git clone https://github.com/jhousteau/genesis.git
cd genesis
make setup

# 2. Install in development mode
poetry install
poetry run pip install -e shared-python/

# 3. Verify installation
poetry run genesis --version
```

### Package Development Cycle

```bash
# 1. Make changes to code
edit genesis/commands/sync.py

# 2. Test changes locally
poetry run genesis sync --dry-run

# 3. Run quality checks
make test
make lint
make typecheck

# 4. Build packages
poetry build
cd shared-python && poetry build && cd ..

# 5. Test installation
pip install dist/genesis_cli-*.whl --force-reinstall
```

### Release Process

```bash
# 1. Bump version
make version-bump-minor  # or patch/major

# 2. Update dependencies and build
./scripts/publish-packages.sh v0.12.1

# 3. Create GitHub release
gh release create v0.12.1 \
  dist/*.whl dist/*.tar.gz \
  shared-python/dist/*.whl shared-python/dist/*.tar.gz \
  releases.json
```

## Template Integration

### Template Package Installation

Genesis templates include comprehensive package installation logic:

#### Container Installation (`Dockerfile.template`)
```dockerfile
# Download packages from GitHub releases
RUN wget https://github.com/jhousteau/genesis/releases/download/v0.12.0/genesis_cli-0.12.0-py3-none-any.whl
RUN pip install genesis_shared_core-*.whl genesis_cli-*.whl
```

#### Development Installation (`setup.sh.template`)
```bash
# Multi-mode installation with fallbacks
if [[ -d "../genesis" ]]; then
    # Local development mode
    poetry run pip install -e "../genesis/shared-python" 2>/dev/null || true
    poetry run pip install -e "../genesis"
elif [[ -n "${GITHUB_TOKEN" ]]; then
    # Authenticated GitHub installation
    poetry run pip install --force-reinstall \
      "genesis-cli @ git+https://github.com/jhousteau/genesis.git@main"
else
    echo "⚠️  Could not install Genesis CLI - GITHUB_TOKEN not set"
fi
```

#### Makefile Integration (`Makefile.template`)
```makefile
genesis-commit: ## Smart commit with quality gates
	@if command -v genesis >/dev/null 2>&1; then \
		genesis commit; \
	else \
		echo "❌ Error: Genesis CLI not found. Install with: pip install genesis-cli"; \
	fi
```

## Common Operations

### Check Package Versions

```bash
# CLI version
genesis --version

# Installed packages
pip show genesis-cli genesis-shared-core

# Available versions
genesis version show
```

### Update Genesis

```bash
# Update to latest
pip install --upgrade genesis-cli

# Force reinstall from GitHub
pip install --force-reinstall \
  "genesis-cli @ git+https://github.com/jhousteau/genesis.git@main"

# Development mode update
cd genesis && git pull && poetry install
```

### Build Local Packages

```bash
# Build both packages
make build-packages

# Or manually
cd shared-python && poetry build && cd ..
poetry build
```

### Test Installation

```bash
# Create test environment
python -m venv test-env
source test-env/bin/activate

# Install from local builds
pip install dist/genesis_cli-*.whl

# Test functionality
genesis --help
genesis bootstrap test-project
```

## Troubleshooting

### Common Issues

#### 1. **"genesis-shared-core not found"**

**Cause**: Dependency resolution failed
**Solution**:
```bash
# Manual installation
pip install genesis-shared-core

# Or from GitHub
pip install "genesis-shared-core @ git+https://github.com/jhousteau/genesis.git@main#subdirectory=shared-python"
```

#### 2. **"Permission denied" during installation**

**Cause**: System-wide installation restrictions
**Solution**:
```bash
# Use user installation
pip install --user genesis-cli

# Or virtual environment
python -m venv genesis-env
source genesis-env/bin/activate
pip install genesis-cli
```

#### 3. **"Package not found" from private repository**

**Cause**: Missing GitHub authentication
**Solution**:
```bash
# Set GitHub token
export GITHUB_TOKEN="your_token_here"

# Or create .env file
echo "GITHUB_TOKEN=your_token_here" > .env
```

#### 4. **Version conflicts**

**Cause**: Multiple Genesis installations
**Solution**:
```bash
# Remove all versions
pip uninstall genesis-cli genesis-shared-core -y

# Clean install
pip install genesis-cli
```

#### 5. **Development mode issues**

**Cause**: Path or virtual environment problems
**Solution**:
```bash
# Verify paths
poetry run python -c "import genesis; print(genesis.__file__)"

# Reinstall in development mode
poetry run pip install -e . --force-reinstall
poetry run pip install -e shared-python/ --force-reinstall
```

### Debug Installation

```bash
# Check resolver sources
python -c "
from genesis.core.dependencies import _resolver
print('Manifest sources:')
manifest = _resolver.get_manifest()
print(f'Latest: {manifest[\"latest\"]}')
print(f'Versions: {list(manifest[\"versions\"].keys())}')
"

# Check installation paths
python -c "
import genesis
import shared_core
print(f'Genesis: {genesis.__file__}')
print(f'Shared Core: {shared_core.__file__}')
"

# Verify dependency resolution
python -c "
from genesis.core.dependencies import get_shared_core_url
print(f'Shared Core URL: {get_shared_core_url()}')
"
```

### Logs and Monitoring

Genesis provides detailed logging for package resolution:

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
genesis --verbose bootstrap test-project
```

Log messages include:
- `📄 Using local releases.json with N versions`
- `🔐 Using authenticated GitHub manifest`
- `📦 Using embedded manifest`
- `Resolved package_name version -> URL`

## Advanced Configuration

### Custom Package Sources

For enterprise deployments, you can customize package sources:

```python
# Custom resolver configuration
from genesis.core.dependencies import DependencyResolver

resolver = DependencyResolver()
resolver._github_base = "https://your-enterprise-github.com/api/v3"
resolver._releases_base = "https://your-enterprise-github.com/releases/download"
```

### Container Optimization

For containerized deployments:

```dockerfile
# Multi-stage build for smaller images
FROM python:3.13-slim as builder
WORKDIR /build
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.13-slim
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --find-links /wheels genesis-cli
```

---

## Summary

The Genesis packaging system provides:

- **Dual-package architecture** with clear separation of concerns
- **Multi-channel distribution** supporting private repositories
- **Dynamic dependency resolution** with multiple fallback strategies
- **Template integration** for consistent project setup
- **Development-friendly** workflows with editable installations
- **Enterprise-ready** features for private deployments

This robust packaging system ensures Genesis can be reliably installed and updated across diverse environments while maintaining the flexibility needed for active development.
