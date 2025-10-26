#!/bin/bash
# Simple test runner for demo-website module

set -e

echo "=========================================="
echo "Demo Website - TDD Test Runner"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: Must be run from demo-website/ directory"
    exit 1
fi

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is not installed"
    exit 1
fi

echo "Step 1: Installing dependencies..."
poetry install --quiet

echo ""
echo "Step 2: Running tests with coverage..."
poetry run pytest -v --cov=src/demo_website --cov-report=term-missing

echo ""
echo "Step 3: Type checking..."
poetry run mypy src/ tests/

echo ""
echo "Step 4: Linting..."
poetry run ruff check src/ tests/

echo ""
echo "=========================================="
echo "All tests passed! Module is ready."
echo "=========================================="
