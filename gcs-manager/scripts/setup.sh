#!/bin/bash
set -euo pipefail

# GCS Manager Setup Script

echo "🚀 Setting up gcs-manager development environment..."

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Please install poetry first:"
    echo "   curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Check Python version
REQUIRED_PYTHON="3.13"
PYTHON_VERSION=$(python3 --version 2>&1 | grep -o "3\.[0-9]*" | head -1)

if [[ $(echo "$PYTHON_VERSION < $REQUIRED_PYTHON" | bc -l) -eq 1 ]]; then
    echo "❌ Python $REQUIRED_PYTHON or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python version $PYTHON_VERSION detected"

# Install dependencies
echo "📦 Installing dependencies..."
poetry install

# Verify installation
echo "🔍 Verifying installation..."
if poetry run python -c "import gcs_manager; print('✅ gcs_manager module imports successfully')"; then
    echo "✅ Setup completed successfully!"
else
    echo "❌ Setup failed - module import error"
    exit 1
fi

echo ""
echo "🎉 gcs-manager is ready for development!"
echo ""
echo "Quick commands:"
echo "  make test          # Run tests"
echo "  make test-cov      # Run tests with coverage"
echo "  make run-dev       # Run CLI tool"
echo "  make quality       # Check code quality"
echo ""
