#!/bin/bash
# Genesis CLI Installation Script for Client Projects
# Installs Genesis CLI from GitHub releases with automatic version detection
set -euo pipefail

VERSION=${1:-latest}
REPO_OWNER="jhousteau"
REPO_NAME="genesis"
TEMP_DIR=$(mktemp -d)

echo "🚀 Installing Genesis CLI..."

# Check for gh CLI availability
if command -v gh >/dev/null 2>&1; then
    echo "✅ GitHub CLI detected - will use for better authentication handling"
else
    echo "ℹ️  GitHub CLI not found - will use direct download (may fail for private repos)"
    echo "   Install gh for better results: https://cli.github.com"
fi

# Cleanup function
cleanup() {
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# Function to get latest version from GitHub API
get_latest_version() {
    if command -v curl >/dev/null 2>&1; then
        curl -s "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/releases/latest" | \
            grep '"tag_name":' | \
            sed -E 's/.*"([^"]+)".*/\1/'
    elif command -v wget >/dev/null 2>&1; then
        wget -qO- "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/releases/latest" | \
            grep '"tag_name":' | \
            sed -E 's/.*"([^"]+)".*/\1/'
    else
        echo "❌ Error: Neither curl nor wget found. Cannot fetch latest version."
        exit 1
    fi
}

# Function to get releases.json manifest
get_releases_manifest() {
    local version=$1
    local manifest_url="https://github.com/$REPO_OWNER/$REPO_NAME/releases/download/$version/releases.json"

    echo "📋 Fetching release manifest for $version..."

    if command -v curl >/dev/null 2>&1; then
        curl -L -s "$manifest_url" -o "$TEMP_DIR/releases.json" || {
            echo "⚠️  Could not fetch releases.json, using direct download"
            return 1
        }
    elif command -v wget >/dev/null 2>&1; then
        wget -q "$manifest_url" -O "$TEMP_DIR/releases.json" || {
            echo "⚠️  Could not fetch releases.json, using direct download"
            return 1
        }
    else
        echo "❌ Error: Neither curl nor wget found"
        exit 1
    fi

    return 0
}

# Function to extract version number from tag
extract_version() {
    echo "$1" | sed 's/^v//'
}

# Function to download and install packages
install_packages() {
    local version=$1
    local clean_version
    clean_version=$(extract_version "$version")

    echo "📦 Installing Genesis CLI version $version..."

    # First try using gh CLI if available (handles auth better)
    if command -v gh >/dev/null 2>&1; then
        echo "🔧 Using GitHub CLI for installation (best for private repos)..."

        # Download wheel files using gh
        cd "$TEMP_DIR"
        if gh release download "$version" --pattern '*.whl' --repo "$REPO_OWNER/$REPO_NAME" --clobber; then
            # Find and install the downloaded wheels dynamically
            local cli_wheel=$(ls genesis_cli-*.whl 2>/dev/null | head -1)
            local shared_core_wheel=$(ls genesis_shared_core-*.whl 2>/dev/null | head -1)

            if [[ -n "$cli_wheel" && -n "$shared_core_wheel" ]]; then
                echo "📦 Found packages:"
                echo "   CLI: $cli_wheel"
                echo "   Shared Core: $shared_core_wheel"

                pip install "$shared_core_wheel" "$cli_wheel" --force-reinstall

                if [[ $? -eq 0 ]]; then
                    echo "✅ Successfully installed using GitHub CLI"
                    return 0
                fi
            fi
        fi

        echo "⚠️  GitHub CLI installation failed, falling back to direct download"
    fi

    # Fallback: Try to get exact filenames from releases.json
    if [[ -f "$TEMP_DIR/releases.json" ]]; then
        local cli_wheel
        local shared_core_wheel

        cli_wheel=$(python3 -c "
import json
with open('$TEMP_DIR/releases.json') as f:
    data = json.load(f)
    print(data['versions']['$version']['cli'])
" 2>/dev/null || echo "")

        shared_core_wheel=$(python3 -c "
import json
with open('$TEMP_DIR/releases.json') as f:
    data = json.load(f)
    print(data['versions']['$version']['shared_core'])
" 2>/dev/null || echo "")

        if [[ -n "$cli_wheel" && -n "$shared_core_wheel" ]]; then
            echo "📋 Using manifest-specified filenames:"
            echo "   CLI: $cli_wheel"
            echo "   Shared Core: $shared_core_wheel"

            # Download packages
            local cli_url="https://github.com/$REPO_OWNER/$REPO_NAME/releases/download/$version/$cli_wheel"
            local shared_core_url="https://github.com/$REPO_OWNER/$REPO_NAME/releases/download/$version/$shared_core_wheel"

            if command -v curl >/dev/null 2>&1; then
                curl -L "$shared_core_url" -o "$TEMP_DIR/$shared_core_wheel"
                curl -L "$cli_url" -o "$TEMP_DIR/$cli_wheel"
            elif command -v wget >/dev/null 2>&1; then
                wget "$shared_core_url" -O "$TEMP_DIR/$shared_core_wheel"
                wget "$cli_url" -O "$TEMP_DIR/$cli_wheel"
            fi

            # Install packages
            echo "🔧 Uninstalling existing Genesis packages..."
            pip uninstall -y genesis-cli genesis-shared-core 2>/dev/null || true

            echo "📦 Installing shared-core..."
            pip install "$TEMP_DIR/$shared_core_wheel"

            echo "📦 Installing CLI..."
            pip install "$TEMP_DIR/$cli_wheel"

            return 0
        fi
    fi

    # Fallback: construct filenames based on version
    echo "📋 Using fallback filename construction for version $clean_version"

    # Try to detect shared_core version from available files
    local cli_wheel="genesis_cli-${clean_version}-py3-none-any.whl"
    local shared_core_wheel=""

    # Download release assets list to find shared_core version
    if command -v gh >/dev/null 2>&1; then
        shared_core_wheel=$(gh release view "$version" --repo "$REPO_OWNER/$REPO_NAME" --json assets --jq '.assets[].name' | grep "genesis_shared_core.*\.whl" | head -1)
    fi

    # If we couldn't detect it, use a wildcard pattern
    if [[ -z "$shared_core_wheel" ]]; then
        shared_core_wheel="genesis_shared_core-*.whl"
        echo "⚠️  Could not detect shared_core version, will use pattern matching"
    fi

    echo "📋 Fallback filenames:"
    echo "   CLI: $cli_wheel"
    echo "   Shared Core: $shared_core_wheel"

    # Download packages
    local cli_url="https://github.com/$REPO_OWNER/$REPO_NAME/releases/download/$version/$cli_wheel"
    local shared_core_url="https://github.com/$REPO_OWNER/$REPO_NAME/releases/download/$version/$shared_core_wheel"

    if command -v curl >/dev/null 2>&1; then
        curl -L "$shared_core_url" -o "$TEMP_DIR/$shared_core_wheel"
        curl -L "$cli_url" -o "$TEMP_DIR/$cli_wheel"
    elif command -v wget >/dev/null 2>&1; then
        wget "$shared_core_url" -O "$TEMP_DIR/$shared_core_wheel"
        wget "$cli_url" -O "$TEMP_DIR/$cli_wheel"
    fi

    # Install packages
    echo "🔧 Uninstalling existing Genesis packages..."
    pip uninstall -y genesis-cli genesis-shared-core 2>/dev/null || true

    echo "📦 Installing shared-core..."
    pip install "$TEMP_DIR/$shared_core_wheel"

    echo "📦 Installing CLI..."
    pip install "$TEMP_DIR/$cli_wheel"
}

# Main installation logic
main() {
    # Resolve version
    if [[ "$VERSION" == "latest" ]]; then
        echo "🔍 Fetching latest version..."
        VERSION=$(get_latest_version)
        if [[ -z "$VERSION" ]]; then
            echo "❌ Error: Could not determine latest version"
            exit 1
        fi
        echo "📋 Latest version: $VERSION"
    fi

    # Validate version format
    if [[ ! "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "❌ Error: Invalid version format: $VERSION"
        echo "   Expected format: vX.Y.Z (e.g., v1.5.0)"
        exit 1
    fi

    # Get release manifest (optional, fallback available)
    get_releases_manifest "$VERSION" || true

    # Install packages
    install_packages "$VERSION"

    # Verify installation
    echo "✅ Verifying installation..."
    if command -v genesis >/dev/null 2>&1; then
        local installed_version
        installed_version=$(genesis --version 2>/dev/null | head -n1 || echo "unknown")
        echo "✅ Genesis CLI installed successfully!"
        echo "📋 Installed version: $installed_version"
        echo ""
        echo "🚀 Try it out:"
        echo "   genesis --help"
        echo "   genesis status"
    else
        echo "⚠️  Installation completed but 'genesis' command not found in PATH"
        echo "   You may need to restart your shell or update your PATH"
    fi
}

# Run main function
main "$@"
