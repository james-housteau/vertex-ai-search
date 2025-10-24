#!/bin/bash
# Common setup functions for test projects
# This file provides shared functionality across all project types

# Initialize basic setup and validation
init_setup() {
    local project_name="$1"

    # Change to project root directory (parent of scripts/utils/)
    cd "$(dirname "$0")/../.."

    # Check if we're in the right directory
    if [[ ! -f "pyproject.toml" ]]; then
        echo "❌ Error: Not in project root directory (pyproject.toml not found)"
        echo "   Current directory: $(pwd)"
        exit 1
    fi
}

# Setup development tools (pre-commit, direnv, environment)
setup_development_tools() {
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
}

# Test that Python environment is working
test_python_environment() {
    echo "🧪 Testing setup..."

    if poetry run python --version >/dev/null 2>&1; then
        echo "✅ Python environment is working"
    else
        echo "❌ Python environment test failed"
    fi
}

# Test CLI availability (if applicable)
test_cli_availability() {
    local command_name="$1"
    local project_name="$2"

    if poetry run "$command_name" --version >/dev/null 2>&1; then
        echo "✅ $project_name CLI is available"
        CLI_VERSION=$(poetry run "$command_name" --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown")
        echo "   Version: $CLI_VERSION"
    else
        echo "⚠️  $project_name CLI not available yet - run 'poetry install' if needed"
    fi
}

# Test shared_core imports (if applicable)
test_shared_core_imports() {
    if poetry run python -c "from shared_core import get_logger; print('✅ shared_core imports working')" 2>/dev/null; then
        :
    else
        echo "ℹ️  shared_core not available - this is normal for standalone projects"
    fi
}

# Show final completion message
show_completion_message() {
    echo ""
    echo "🎉 Setup complete! You can now:"
    echo "   • Run tests: make test"
    echo "   • Format code: make format"
    echo "   • Check quality: make quality"
    echo "   • Build packages: make build"
    echo "   • See all commands: make help"
    echo ""
    echo "📝 Remember to source the environment before working:"
    echo "   source .envrc"
}
