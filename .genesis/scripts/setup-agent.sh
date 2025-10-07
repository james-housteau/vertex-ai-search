#!/bin/bash
# setup-agent.sh - Initialize professional agent environment

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔒 vertex-ai-search - Professional Agent Setup${NC}"

# Create workspace structure
echo "Creating workspace structure..."
mkdir -p workspace/{projects,data,logs,tmp,.local,.cache,.config}

# Set permissions
echo "Setting permissions..."
chmod 755 workspace
chmod 644 .genesis/agent-seccomp.json

# Build image
echo -e "${BLUE}Building agent image...${NC}"
docker compose --profile agent build

# Test jail
echo -e "${BLUE}Testing jail security...${NC}"
docker compose --profile agent run --rm agent bash -c '
  echo "=== Security Test ==="
  echo "1. Current user: $(whoami)"
  echo "2. Current directory: $(pwd)"
  echo "3. Home directory: $HOME"
  echo -n "4. Can write to workspace: "
  touch /workspace/test 2>/dev/null && echo "✓ Yes" && rm /workspace/test || echo "✗ No"
  echo -n "5. Can write to /tmp: "
  touch /tmp/test 2>/dev/null && echo "✓ Yes" && rm /tmp/test || echo "✗ No"
  echo -n "6. Can write to /etc: "
  touch /etc/test 2>/dev/null && echo "⚠️  WARNING: Root FS is writable!" || echo "✓ No (good!)"
  echo -n "7. Can see host /etc/passwd: "
  [ -f /etc/passwd ] && grep -q "root:x:0:0:root:/root" /etc/passwd && echo "✓ Container passwd" || echo "✗ No passwd"
  echo -n "8. Can escape to host: "
  ls /host 2>/dev/null && echo "⚠️  WARNING: Host accessible!" || echo "✓ No (secured!)"
  echo "=== Test Complete ==="
'

echo -e "${GREEN}✅ Agent environment ready!${NC}"
echo -e "${BLUE}Usage:${NC}"
echo "  Start agent:  docker compose --profile agent up -d"
echo "  Enter shell:  docker compose --profile agent exec agent bash"
echo "  Stop agent:   docker compose --profile agent down"
