#!/usr/bin/env bash
set -euo pipefail

echo "Setting up shared-contracts module..."

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry not found. Please install Poetry first."
    exit 1
fi

# Install dependencies
echo "Installing dependencies with Poetry..."
poetry install

echo "Setup complete!"
