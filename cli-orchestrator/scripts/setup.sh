#!/bin/bash
set -e

echo "🚀 Setting up CLI Orchestrator development environment..."

# Check if poetry is available
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Please install Poetry first."
    echo "   Visit: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
poetry install

echo "✅ CLI Orchestrator setup complete!"
echo ""
echo "Next steps:"
echo "  make test     # Run tests"
echo "  make run-dev  # Run CLI tool"
echo "  make build    # Build package"
