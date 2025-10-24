#!/bin/bash
# Genesis Container Rebuild Script - Simplified
# Clean, sync, rebuild, and enter shell
set -euo pipefail

echo "🔄 Starting container rebuild..."

# Change to project root
cd "$(dirname "$0")/../.."

# Simple lock mechanism
LOCKFILE=".container-rebuild.lock"
if [[ -f "$LOCKFILE" ]]; then
    echo "❌ Container rebuild already in progress"
    exit 1
fi

echo "$$" > "$LOCKFILE"
trap 'rm -f "$LOCKFILE"' EXIT

# Check project root
if [[ ! -f "Dockerfile" ]] && [[ ! -f "docker-compose.yml" ]]; then
    echo "❌ Error: No Dockerfile or docker-compose.yml found"
    exit 1
fi

# Find Genesis command
GENESIS_CMD=""
if command -v genesis >/dev/null 2>&1; then
    GENESIS_CMD="genesis"
elif command -v poetry >/dev/null 2>&1 && poetry run genesis --version >/dev/null 2>&1; then
    GENESIS_CMD="poetry run genesis"
else
    echo "⚠️ Warning: Genesis CLI not found, skipping sync step"
fi

# Step 1: Clean Docker resources
echo "🧹 Cleaning Docker resources..."
if [[ -f "scripts/docker/docker-cleanup.sh" ]]; then
    bash scripts/docker/docker-cleanup.sh
else
    docker container prune -f
    docker image prune -f
fi

# Step 2: Sync project files
if [[ -n "$GENESIS_CMD" ]]; then
    echo "🔄 Syncing project files..."
    $GENESIS_CMD sync || echo "⚠️ Sync failed, continuing..."
fi

# Step 3: Rebuild container
echo "🏗️ Building container..."
if [[ -f "docker-compose.yml" ]]; then
    docker compose build --no-cache
else
    docker build --no-cache -t "test:latest" .
fi

# Step 4: Start container
echo "🚀 Starting container..."
if [[ -f "docker-compose.yml" ]]; then
    docker compose up -d
else
    docker run -d --name "test" "test:latest"
fi

echo "✅ Container rebuild complete!"
echo "💡 Use 'docker compose exec <service> bash' to enter the container"
