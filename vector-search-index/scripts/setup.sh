#!/bin/bash
# Setup script for vector-search-index module

set -e

echo "Setting up vector-search-index module..."

# Install dependencies with Poetry
poetry install

echo "Setup complete!"
