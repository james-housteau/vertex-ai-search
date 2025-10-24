#!/bin/bash
set -e

echo "🚀 Setting up document-uploader development environment..."

# Install Poetry if not available
if ! command -v poetry &> /dev/null; then
    echo "📦 Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Install dependencies
echo "📦 Installing dependencies..."
poetry install

echo "✅ Setup complete! You can now run:"
echo "  make test       # Run tests"
echo "  make run-dev    # Run CLI tool"
echo "  make quality    # Check code quality"
