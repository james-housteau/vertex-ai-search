# Professional-grade Agent Container with Native Docker Isolation
FROM python:3.13-slim-bookworm

# Enable bash strict mode for all RUN commands
SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

# Install development tools in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Core development
    build-essential git curl wget ca-certificates gnupg \
    gcc g++ make cmake pkg-config \
    # Python development
    python3-dev python3-pip python3-venv \
    # Node.js (will be updated with proper version below)
    nodejs npm \
    # Editors and tools
    vim nano tree jq ripgrep fd-find htop \
    # Database clients
    postgresql-client redis-tools sqlite3 \
    # Network tools (for development only)
    iputils-ping dnsutils netcat-openbsd \
    # Shell and automation tools
    direnv gh \
    # Additional utilities
    unzip zip rsync \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && command -v direnv \
    && command -v gh

# Install Node.js properly
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g typescript tsx nodemon @anthropic-ai/claude-code \
    && corepack enable \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry for Python package management
ENV POETRY_HOME=/opt/poetry \
    POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_IN_PROJECT=true
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

# Optional Genesis CLI from GitHub Releases using BuildKit secret
# Usage: docker build --secret id=github_token,env=GITHUB_TOKEN ...
# Avoids caching/leaking token.
RUN --mount=type=secret,id=github_token \
    if [ -f /run/secrets/github_token ]; then \
      echo "Installing Genesis CLI from GitHub Releases..."; \
      export GITHUB_TOKEN="$(cat /run/secrets/github_token)"; \
      \
      # Get asset IDs and names for wheel files
      assets=$(curl -fsSH "Authorization: token ${GITHUB_TOKEN}" \
        https://api.github.com/repos/jhousteau/genesis/releases/latest \
        | jq -r '.assets[] | select(.name|endswith(".whl")) | "\(.id):\(.name)"'); \
      \
      if [ -z "$assets" ]; then \
        echo "No wheel files found in latest release"; \
        exit 0; \
      fi; \
      \
      # Download using asset API
      for asset in $assets; do \
        id="${asset%%:*}"; \
        name="${asset#*:}"; \
        echo "Downloading: $name"; \
        curl -fsSLH "Authorization: token ${GITHUB_TOKEN}" \
          -H "Accept: application/octet-stream" \
          "https://api.github.com/repos/jhousteau/genesis/releases/assets/$id" \
          -o "$name"; \
      done; \
      \
      # Install shared-core first, then cli (dependency order matters)
      if ls genesis_shared_core-*.whl 1> /dev/null 2>&1; then \
        echo "Installing genesis-shared-core..."; \
        python3 -m pip install --no-cache-dir genesis_shared_core-*.whl; \
      fi; \
      \
      if ls genesis_cli-*.whl 1> /dev/null 2>&1; then \
        echo "Installing genesis-cli..."; \
        python3 -m pip install --no-cache-dir genesis_cli-*.whl; \
      fi; \
      \
      # Verify installation
      python3 -c "import genesis; print('Genesis CLI installed successfully')" || \
        echo "Genesis CLI installation failed but continuing..."; \
      \
      rm -f *.whl; \
      echo "Genesis CLI installation completed"; \
    else \
      echo "Skipping Genesis CLI installation (no secret provided)"; \
    fi

# Git configuration defaults
RUN git config --system user.name "Developer" \
    && git config --system user.email "developer@genesis-cli.local" \
    && git config --system init.defaultBranch main

# Create non-root user
RUN groupadd -g 1000 developer \
    && useradd -u 1000 -g developer -s /bin/bash -d /workspace developer

# Pre-create .local directories in workspace for user packages
RUN mkdir -p /workspace/.local/bin /workspace/.local/lib /workspace/.local/share \
    && mkdir -p /workspace/.cache /workspace/.config \
    && mkdir -p /workspace/.npm-global /workspace/.venv \
    && chown -R developer:developer /workspace

# Configure direnv and custom prompt for developer user
RUN echo 'eval "$(direnv hook bash)"' >> /workspace/.bashrc \
    && echo 'PROJECT_SHORT=${PROJECT_NAME%%-*}' >> /workspace/.bashrc \
    && echo 'export PS1="\\u@${PROJECT_SHORT:-container}:\\w\\$ "' >> /workspace/.bashrc \
    && mkdir -p /workspace/.config/direnv \
    && printf '[whitelist]\nprefix = ["/workspace"]\n' > /workspace/.config/direnv/direnv.toml \
    && chown -R developer:developer /workspace/.config /workspace/.bashrc

# CRITICAL: Set workspace as home to prevent any attempts to access /home
ENV HOME=/workspace \
    PATH=/workspace/.local/bin:/workspace/.npm-global/bin:/usr/local/bin:/usr/bin:/bin \
    PYTHONUSERBASE=/workspace/.local \
    PYTHONPATH=/workspace \
    npm_config_prefix=/workspace/.npm-global \
    npm_config_cache=/workspace/.cache/npm \
    POETRY_CACHE_DIR=/workspace/.cache/poetry

# Setup script (mounted path safe)
COPY scripts/container-setup.sh /usr/local/bin/container-setup.sh
RUN chmod +x /usr/local/bin/container-setup.sh || true

# Minimal entry script
RUN install -m 0755 /dev/stdin /usr/local/bin/entrypoint.sh <<'EOF'
#!/bin/bash
set -euo pipefail

# Colors for clean output
GREEN='\033[0;32m'; BLUE='\033[0;34m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo -e "${BLUE}🚀 genesis-cli Agent Development Container${NC}"
echo "🔧 User: $(whoami) | Workspace: ${HOME}"
echo "🐍 $(python --version 2>&1) | 📦 $(node --version 2>&1)"
echo -e "${GREEN}🔒 Agent isolation active${NC}"
echo ""

# Copy setup script to workspace if needed
if [ -f /usr/local/bin/container-setup.sh ] && [ ! -f /workspace/scripts/container-setup.sh ]; then
  mkdir -p /workspace/scripts && cp /usr/local/bin/container-setup.sh /workspace/scripts/container-setup.sh || true
fi

# Auto-setup if requested
if [ "${AUTO_SETUP:-false}" = "true" ] && [ -x /workspace/scripts/container-setup.sh ]; then
  echo -e "${YELLOW}🚀 Running automated setup...${NC}"
  /workspace/scripts/container-setup.sh || true
fi

echo -e "${BLUE}💡 Agent Ready:${NC}"
echo "   ./scripts/container-setup.sh    # Run setup"
echo "   Workspace: $(pwd)"
echo ""

# Set reasonable ulimits
ulimit -c 0 || true
ulimit -n 4096 || true
ulimit -u 1024 || true

# Execute the original command or start interactive shell
exec "$@"
EOF

# Switch to non-root user
USER developer
WORKDIR /workspace

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD test -w /workspace && test -r /usr/bin/python3 || exit 1

# Default command
CMD ["/bin/bash", "-l"]
