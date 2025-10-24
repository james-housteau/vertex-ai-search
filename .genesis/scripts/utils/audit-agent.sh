#!/bin/bash
# audit-agent.sh - Security audit for agent container

set -euo pipefail

echo "🔍 Agent Security Audit"
echo "========================"

CONTAINER="genesis-cli-agent"

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    echo "❌ Container not running. Start with: docker compose --profile agent up -d"
    exit 1
fi

echo "✅ Container is running"

# Security checks
echo -e "\n📋 Security Configuration:"

# 1. User check
USER_ID=$(docker exec $CONTAINER id -u)
echo -n "1. Running as non-root: "
[ "$USER_ID" != "0" ] && echo "✅ Yes (UID: $USER_ID)" || echo "❌ No (ROOT!)"

# 2. Read-only filesystem
echo -n "2. Read-only root filesystem: "
docker inspect $CONTAINER --format='{{.HostConfig.ReadonlyRootfs}}' | grep -q true && echo "✅ Yes" || echo "❌ No"

# 3. Capabilities
echo "3. Capabilities:"
CAPS_DROP=$(docker inspect $CONTAINER --format='{{json .HostConfig.CapDrop}}' | jq -r '.[]' 2>/dev/null | tr '\n' ' ')
CAPS_ADD=$(docker inspect $CONTAINER --format='{{json .HostConfig.CapAdd}}' | jq -r '.[]' 2>/dev/null | tr '\n' ' ')
echo "   Dropped: $CAPS_DROP"
echo "   Added: $CAPS_ADD"

# 4. Security options
echo "4. Security options:"
docker inspect $CONTAINER --format='{{json .HostConfig.SecurityOpt}}' | jq -r '.[]' 2>/dev/null | sed 's/^/   - /'

# 5. Resource limits
echo -e "\n📊 Resource Limits:"
docker stats --no-stream --format "   CPU: {{.CPUPerc}}\n   Memory: {{.MemUsage}}\n   PIDs: {{.PIDs}}" $CONTAINER

# 6. Mount points
echo -e "\n📁 Mount Points:"
docker exec $CONTAINER mount | grep -E "(workspace|tmp)" | sed 's/^/   /'

# 7. Network isolation
echo -e "\n🌐 Network Configuration:"
NETWORK=$(docker inspect $CONTAINER --format='{{.HostConfig.NetworkMode}}')
echo "   Network mode: $NETWORK"

# 8. Escape attempt test
echo -e "\n🔒 Escape Attempt Tests:"
echo -n "   Can chroot: "
docker exec $CONTAINER bash -c 'chroot / /bin/true 2>/dev/null' && echo "❌ Yes (BAD!)" || echo "✅ No"
echo -n "   Can mount: "
docker exec $CONTAINER bash -c 'mount -t tmpfs tmpfs /mnt 2>/dev/null' && echo "❌ Yes (BAD!)" || echo "✅ No"
echo -n "   Can access Docker socket: "
docker exec $CONTAINER bash -c 'ls /var/run/docker.sock 2>/dev/null' && echo "❌ Yes (BAD!)" || echo "✅ No"
echo -n "   Can write outside workspace: "
docker exec $CONTAINER bash -c 'touch /usr/test 2>/dev/null' && echo "❌ Yes (BAD!)" || echo "✅ No"
echo -n "   Can access /proc/sys: "
docker exec $CONTAINER bash -c 'ls /proc/sys 2>/dev/null' && echo "⚠️  Limited access" || echo "✅ No access"

echo -e "\n✅ Audit complete!"
