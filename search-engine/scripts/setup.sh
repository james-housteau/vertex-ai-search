#!/bin/bash

# Setup script for search-engine module
set -euo pipefail

echo "🚀 Setting up search-engine module..."

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Please install Poetry first."
    echo "   Visit: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2)
required_version="3.13"

if [[ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]]; then
    echo "❌ Python $required_version or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Install dependencies
echo "📦 Installing dependencies..."
poetry install

# Setup pre-commit hooks if .pre-commit-config.yaml exists
if [ -f ".pre-commit-config.yaml" ]; then
    echo "🔧 Setting up pre-commit hooks..."
    poetry run pre-commit install
fi

echo "🎉 Setup complete! You can now run:"
echo "   make test      # Run tests"
echo "   make run-dev   # Run CLI tool"
echo "   make quality   # Check code quality"
