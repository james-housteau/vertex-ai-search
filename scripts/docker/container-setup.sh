#!/bin/bash
# Universal Genesis Container Setup Script
# Configures development environment inside containers
set -euo pipefail

echo "🐳 Setting up test container environment..."

# Change to project root directory (parent of scripts/)
cd "$(dirname "$0")/.."

# Check if we're in the right directory




# Container-specific setup
echo "🔧 Configuring container environment..."

# Set up Git configuration for container
if [[ -z "$(git config --global user.name 2>/dev/null)" ]]; then
    git config --global user.name "Developer"
    git config --global user.email "developer@example.com"
    echo "✅ Git user configured"
fi

# Configure Git to trust the workspace directory (security for containers)
if [[ -n "$(pwd)" ]]; then
    git config --global --add safe.directory "$(pwd)" 2>/dev/null || true
    echo "✅ Workspace directory trusted by Git"
fi

# Set up GitHub CLI authentication if token is available
if [[ -n "${GITHUB_TOKEN}" ]] && command -v gh >/dev/null 2>&1; then
    echo "🔐 Setting up GitHub CLI authentication..."
    echo "${GITHUB_TOKEN}" | gh auth login --with-token 2>/dev/null || true
    if gh auth status >/dev/null 2>&1; then
        echo "✅ GitHub CLI authenticated"
    else
        echo "⚠️  GitHub CLI authentication failed - continuing without it"
    fi
fi

# Install dependencies if not already done
echo "📦 Installing project dependencies..."




# Install or update Genesis CLI
echo "🛠️  Installing Genesis CLI..."
if [[ -n "${GITHUB_TOKEN}" ]]; then
    # Install from GitHub with token


else
    echo "⚠️  GITHUB_TOKEN not set - cannot install Genesis CLI"
fi

# Install pre-commit hooks
if [[ -d ".git" ]] && [[ -f ".pre-commit-config.yaml" ]]; then
    echo "🔧 Installing pre-commit hooks..."


fi

# Configure direnv if available
if command -v direnv >/dev/null 2>&1 && [[ -f ".envrc" ]]; then
    echo "🌍 Enabling direnv configuration..."
    direnv allow 2>/dev/null || true
fi

# Test the container setup
echo "🧪 Testing container setup..."




# Create container ready marker
touch .container_ready 2>/dev/null || true

echo ""
echo "🎉 Container setup complete! Development environment ready."
echo ""
echo "🚀 Quick Start:"



echo "   • Open shell: docker exec -it test_dev_1 bash"
echo ""
