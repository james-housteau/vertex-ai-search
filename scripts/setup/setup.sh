#!/bin/bash
# test Development Setup Script
set -euo pipefail

echo "🚀 Setting up test development environment..."

# Change to project root directory (parent of scripts/)
cd "$(dirname "$0")/.."

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]]; then
    echo "❌ Error: Not in project root directory (pyproject.toml not found)"
    echo "   Current directory: $(pwd)"
    exit 1
fi

# Install dependencies and development tools
echo "📦 Installing dependencies with Poetry..."

if command -v poetry >/dev/null 2>&1; then
    poetry install

    # Poetry should handle all dependencies including local path dependencies
    # Dependencies are defined in pyproject.toml
else
    echo "❌ Error: Poetry not found. Please install Poetry first."
    echo "   Visit: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Install pre-commit hooks
if [[ -d ".git" ]]; then
    echo "🔧 Installing pre-commit hooks..."
    if command -v pre-commit >/dev/null 2>&1; then
        pre-commit install
    else
        poetry run pre-commit install
    fi
else
    echo "ℹ️  No git repository found - hooks will be installed when you init git"
fi

# Check if direnv is available
if command -v direnv >/dev/null 2>&1; then
    echo "🌍 direnv detected - environment will auto-load when entering directory"
    direnv allow
else
    echo "⚠️  direnv not found - you can install it for automatic environment loading"
    echo "   Or manually source .envrc: source .envrc"
fi

# Source environment
if [[ -f ".envrc" ]]; then
    echo "🌍 Loading environment variables..."
    source .envrc
fi

# Test the setup
echo "🧪 Testing setup..."

# Test that Python and Poetry work
if poetry run python --version >/dev/null 2>&1; then
    echo "✅ Python environment is working"
else
    echo "❌ Python environment test failed"
fi

# Test that CLI is available (if applicable)
if poetry run  --version >/dev/null 2>&1; then
    echo "✅ test CLI is available"
    CLI_VERSION=$(poetry run  --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
    echo "   Version: $CLI_VERSION"
else
    echo "⚠️  test CLI not available yet - run 'poetry install' if needed"
fi

# Test that shared_core imports work (if applicable)
if poetry run python -c "from shared_core import get_logger; print('✅ shared_core imports working')" 2>/dev/null; then
    :
else
    echo "⚠️  shared_core not properly installed - check pyproject.toml dependencies"
fi

echo ""
echo "🎉 Setup complete! You can now:"
echo "   • Run tests: make test"
echo "   • Format code: make format"
echo "   • Check quality: make quality"
echo "   • Build packages: make build"
echo "   • See all commands: make help"
echo ""
echo "📝 Remember to source the environment before working:"
echo "   source .envrc"
