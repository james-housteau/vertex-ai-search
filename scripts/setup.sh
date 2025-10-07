#!/bin/bash
# vertex-ai-search Development Setup Script
set -euo pipefail

echo "🚀 Setting up vertex-ai-search development environment..."

# Change to project root directory (parent of scripts/)
cd "$(dirname "$0")/.."

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]]; then
    echo "❌ Error: Not in project root directory (pyproject.toml not found)"
    echo "   Current directory: $(pwd)"
    exit 1
fi

# Install dependencies and development tools
echo "📦 Installing dependencies with Poetry..."

if command -v poetry >/dev/null 2>&1; then
    poetry install

    # Poetry should handle all dependencies including local path dependencies
    # Dependencies are defined in pyproject.toml
else
    echo "❌ Error: Poetry not found. Please install Poetry first."
    echo "   Visit: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Install Genesis CLI for development features
echo "🌟 Installing Genesis CLI for development features..."
if ! poetry run genesis --version >/dev/null 2>&1; then
    echo "   Installing Genesis from GitHub releases..."

    # Check if gh CLI is available and authenticated
    GENESIS_REPO="jhousteau/genesis"
    if command -v gh >/dev/null 2>&1; then
        # Check if authenticated
        if gh auth status >/dev/null 2>&1; then
            echo "   Using GitHub CLI to download packages..."

            # Create temp directory for downloads
            TEMP_DIR=$(mktemp -d)
            PROJECT_DIR=$(pwd)
            cd "$TEMP_DIR"

            # Download wheel files using gh CLI
            echo "   Downloading latest Genesis release..."
            if gh release download --pattern '*.whl' --repo "$GENESIS_REPO" --clobber; then
                # Install the downloaded wheels from project directory
                echo "   Installing Genesis packages..."
                cd "$PROJECT_DIR"
                if poetry run pip install "$TEMP_DIR"/genesis_cli-*.whl "$TEMP_DIR"/genesis_shared_core-*.whl --force-reinstall; then
                    echo "✅ Genesis CLI installed successfully"
                else
                    echo "❌ Failed to install Genesis packages"
                fi
            else
                echo "❌ Failed to download Genesis packages"
                echo "   This might be due to authentication or network issues"
            fi

            # Clean up
            rm -rf "$TEMP_DIR"
        else
            echo "⚠️  GitHub CLI not authenticated"
            echo "   Please authenticate with GitHub:"
            echo "   1. Run: gh auth login"
            echo "   2. Follow the prompts to authenticate"
            echo "   3. Re-run: make setup"
            echo ""
            echo "   Or install manually from: https://github.com/$GENESIS_REPO/releases"
        fi
    else
        echo "⚠️  GitHub CLI (gh) not found"
        echo "   Genesis requires authenticated access to GitHub releases"
        echo "   Please install and authenticate GitHub CLI:"
        echo "   1. Install: brew install gh"
        echo "   2. Authenticate: gh auth login"
        echo "   3. Re-run: make setup"
        echo ""
        echo "   Or install manually from: https://github.com/$GENESIS_REPO/releases"
    fi
else
    echo "✅ Genesis already installed"
fi

# Install pre-commit hooks
if [[ -d ".git" ]]; then
    echo "🔧 Installing pre-commit hooks..."
    if command -v pre-commit >/dev/null 2>&1; then
        pre-commit install
    else
        poetry run pre-commit install
    fi
else
    echo "ℹ️  No git repository found - hooks will be installed when you init git"
fi

# Check if direnv is available
if command -v direnv >/dev/null 2>&1; then
    echo "🌍 direnv detected - environment will auto-load when entering directory"
    direnv allow
else
    echo "⚠️  direnv not found - you can install it for automatic environment loading"
    echo "   Or manually source .envrc: source .envrc"
fi

# Source environment
if [[ -f ".envrc" ]]; then
    echo "🌍 Loading environment variables..."
    source .envrc
fi

# Test the setup
echo "🧪 Testing setup..."

# Test that Python and Poetry work
if poetry run python --version >/dev/null 2>&1; then
    echo "✅ Python environment is working"
else
    echo "❌ Python environment test failed"
fi

# Test that CLI is available (if applicable)
if poetry run vertex-ai-search --version >/dev/null 2>&1; then
    echo "✅ vertex-ai-search CLI is available"
    CLI_VERSION=$(poetry run vertex-ai-search --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
    echo "   Version: $CLI_VERSION"
else
    echo "⚠️  vertex-ai-search CLI not available yet - run 'poetry install' if needed"
fi

# Test that Click imports work
if poetry run python -c "import click; print('✅ Click CLI framework working')" 2>/dev/null; then
    :
else
    echo "⚠️  Click CLI framework not properly installed - check pyproject.toml"
fi

# Test that shared_core imports work (if applicable)
if poetry run python -c "from shared_core import get_logger; print('✅ shared_core imports working')" 2>/dev/null; then
    :
else
    echo "ℹ️  shared_core not available - this is normal for standalone projects"
fi

echo ""
echo "🎉 Setup complete! You can now:"
echo "   • Run tests: make test"
echo "   • Run CLI: make run-dev"
echo "   • Format code: make format"
echo "   • Check quality: make quality"
echo "   • Build packages: make build"
echo "   • See all commands: make help"
echo ""
echo "📝 Remember to source the environment before working:"
echo "   source .envrc"
