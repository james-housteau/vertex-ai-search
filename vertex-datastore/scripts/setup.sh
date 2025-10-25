#!/bin/bash
# Setup script for vertex-datastore development environment

set -e

echo "🚀 Setting up vertex-datastore development environment..."

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry not found. Please install Poetry first:"
    echo "   curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

echo "📦 Installing dependencies with Poetry..."
poetry install

echo "🔧 Installing pre-commit hooks..."
poetry run pre-commit install || echo "⚠️  Pre-commit hooks installation failed (this is optional)"

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  make test        # Run tests"
echo "  make run-dev     # Run the CLI tool"
echo "  make quality     # Check code quality"
