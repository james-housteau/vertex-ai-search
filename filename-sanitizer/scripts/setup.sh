#!/bin/bash
set -euo pipefail

# filename-sanitizer setup script

echo "=€ Setting up filename-sanitizer development environment..."

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "L Poetry is not installed. Please install Poetry first:"
    echo "   curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Install dependencies
echo "=æ Installing dependencies with Poetry..."
poetry install

# Verify installation
echo " Verifying installation..."
poetry run python -c "import filename_sanitizer; print(f'filename-sanitizer {filename_sanitizer.__version__} installed successfully')"

echo "<‰ Setup complete! You can now run:"
echo "   make test        # Run tests"
echo "   make run-dev     # Run CLI in development mode"
echo "   make quality     # Check code quality"
