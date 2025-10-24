#!/bin/bash
# Setup GitHub authentication in containers
set -euo pipefail

# Configure Git user if not already configured
if [[ -z "$(git config --global user.name 2>/dev/null || true)" ]]; then
    git config --global user.name "Genesis Developer"
    git config --global user.email "developer@genesis.local"
    echo "✅ Git user configured"
fi

# Setup GitHub authentication if token is available
if [[ -f /run/secrets/github_token ]]; then
    echo "🔐 Setting up GitHub authentication..."

    # Read the token from the Docker secret
    GITHUB_TOKEN=$(cat /run/secrets/github_token)
    export GITHUB_TOKEN

    # Configure git credential helper
    git config --global credential.helper store
    echo "https://jhousteau:${GITHUB_TOKEN}@github.com" > ~/.git-credentials
    chmod 600 ~/.git-credentials

    # Configure GitHub CLI if available
    if command -v gh >/dev/null 2>&1; then
        echo "${GITHUB_TOKEN}" | gh auth login --with-token 2>/dev/null || true
        if gh auth status >/dev/null 2>&1; then
            echo "✅ GitHub CLI authenticated"
        fi
    fi

    echo "✅ Git authentication configured"
else
    echo "⚠️  GitHub token not found at /run/secrets/github_token - git operations may require manual authentication"
fi

# Trust the workspace directory for Git operations
git config --global --add safe.directory /workspace 2>/dev/null || true

echo "✅ Git authentication setup complete"
