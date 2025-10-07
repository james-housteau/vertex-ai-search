#!/bin/bash
# Simple Docker cleanup for Genesis projects
# Removes stopped containers, dangling images, and unused volumes
set -euo pipefail

echo "🐳 Cleaning Docker resources..."

# Stop and remove containers for current project
PROJECT_NAME="${PROJECT_NAME:-vertex-ai-search}"
if [ -n "$PROJECT_NAME" ]; then
    docker ps -aq --filter "label=com.docker.compose.project=$PROJECT_NAME" | xargs -r docker stop
    docker ps -aq --filter "label=com.docker.compose.project=$PROJECT_NAME" | xargs -r docker rm
fi

# Remove dangling images and volumes
docker image prune -f
docker volume prune -f

# Remove stopped containers
docker container prune -f

echo "✅ Docker cleanup complete"
