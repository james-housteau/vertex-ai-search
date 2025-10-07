# Troubleshooting Guide

## Overview

Common issues and solutions for Genesis development workflows.

## Installation Issues

### Genesis CLI Not Found
**Symptoms:**
```
bash: genesis: command not found
```

**Solutions:**
```bash
# Install globally
pip install genesis-cli

# Or install in project virtual environment
poetry add genesis-cli
poetry shell

# Verify installation
genesis --version
```

### Poetry Installation Issues
**Symptoms:**
```
Command 'poetry' not found
```

**Solutions:**
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify installation
poetry --version
```

## Bootstrap Issues

### Bootstrap Fails with "Template not found"
**Symptoms:**
```
❌ Bootstrap failed: Template 'python-api' not found or Genesis not detected
```

**Solutions:**
```bash
# Ensure you're in Genesis project directory
cd /path/to/genesis

# Verify templates directory exists
ls templates/

# Check available templates
ls templates/
# Should show: cli-tool, python-api, typescript-service, etc.
```

### Permission Denied on Scripts
**Symptoms:**
```
Permission denied: ./scripts/setup.sh
```

**Solutions:**
```bash
# Fix script permissions
chmod +x scripts/*.sh
find . -name "*.sh" -exec chmod +x {} \;

# Or use Genesis sync to fix permissions
genesis sync --force
```

### Git Initialization Fails
**Symptoms:**
```
fatal: not a git repository
```

**Solutions:**
```bash
# Initialize Git in project directory
cd project-name
git init
git add .
git commit -m "Initial commit"

# Or bootstrap with Git initialization
genesis bootstrap project-name --type python-api
```

## Container Issues

### Docker Build Failures

#### GITHUB_TOKEN Not Set
**Symptoms:**
```
❌ GITHUB_TOKEN not found in environment
```

**Solutions:**
```bash
# Set GITHUB_TOKEN
export GITHUB_TOKEN="your-token-here"

# Or add to .envrc
echo 'export GITHUB_TOKEN="your-token-here"' >> .envrc
direnv allow

# Verify
echo $GITHUB_TOKEN
```

#### Build Context Issues
**Symptoms:**
```
COPY failed: file not found in build context
```

**Solutions:**
```bash
# Ensure you're in project root
pwd  # Should be project directory

# Check Dockerfile exists
ls Dockerfile

# Rebuild with no cache
docker compose build --no-cache
```

### Container Runtime Issues

#### Container Name Already in Use
**Symptoms:**
```
Error response from daemon: Conflict. The container name "/vertex-ai-search-agent" is already in use
```

**Solutions:**
```bash
# Use Genesis container remove (handles standalone containers)
genesis container remove

# Or manually remove the conflicting container
docker ps -a | grep vertex-ai-search
docker rm -f <container-id>

# Then rebuild
./scripts/container-rebuild.sh
```

#### Container Exits Immediately
**Symptoms:**
```
Container vertex-ai-search-dev exits with code 0
```

**Solutions:**
```bash
# Check container logs
docker compose logs dev

# Use interactive mode
docker compose run --rm dev bash

# Check for script errors
docker compose run --rm dev cat /usr/local/bin/entrypoint.sh
```

#### Agent Container Security Issues
**Symptoms:**
```
Agent can write outside workspace
```

**Solutions:**
```bash
# Verify agent isolation
scripts/audit-agent.sh

# Check read-only filesystem
docker inspect vertex-ai-search-agent --format='{{.HostConfig.ReadonlyRootfs}}'

# Should return: true
```

## Sync Issues

### Files Not Updating
**Symptoms:**
```
Files remain unchanged after sync
```

**Solutions:**
```bash
# Force sync all files
genesis sync --force

# Check if files are locally modified
git status

# If modified, either commit or reset
git add . && git commit -m "Save changes before sync"
# OR
git reset --hard HEAD
```

### Manifest Parse Errors
**Symptoms:**
```
❌ Failed to load manifest: Invalid YAML
```

**Solutions:**
```bash
# Check manifest syntax
python -c "import yaml; yaml.safe_load(open('templates/shared/manifest.yml'))"

# Fix YAML indentation
# Ensure consistent spacing (use spaces, not tabs)
```

### Permission Issues on Sync
**Symptoms:**
```
Permission denied writing to .claude/hooks/
```

**Solutions:**
```bash
# Fix directory permissions
chmod -R 755 .claude/

# Ensure you own the files
sudo chown -R $(whoami) .

# Run sync again
genesis sync
```

## Worktree Issues

### Worktree Creation Fails
**Symptoms:**
```
fatal: 'path' is already checked out
```

**Solutions:**
```bash
# Remove existing worktree
git worktree remove path-name

# Or use different path
genesis worktree create feature-name ./different-path

# Clean up stale worktrees
git worktree prune
```

### Too Many Files Warning
**Symptoms:**
```
⚠️  Worktree has 35 files (exceeds 30 file AI safety limit)
```

**Solutions:**
```bash
# Reduce scope with sparse checkout
echo "src/specific-module/" > .git/info/sparse-checkout
git read-tree -m -u HEAD

# Or create more focused worktree
genesis worktree create narrow-scope "src/module/specific-file.py"

# Validate file count
genesis worktree validate
```

## Quality Gate Failures

### Pre-commit Hook Failures
**Symptoms:**
```
black.............Failed
ruff..............Failed
```

**Solutions:**
```bash
# Run formatters manually
poetry run black .
poetry run ruff check --fix .

# Or use Genesis autofix
genesis autofix

# Commit formatted code
git add . && git commit -m "Apply formatting fixes"
```

### Test Failures
**Symptoms:**
```
FAILED tests/test_feature.py::test_function
```

**Solutions:**
```bash
# Run specific test for debugging
poetry run pytest tests/test_feature.py::test_function -v

# Run with debugger
poetry run pytest --pdb tests/test_feature.py::test_function

# Check test environment
poetry run python -m pytest --version
```

### Security Scan Failures
**Symptoms:**
```
Safety check failed: Found 3 vulnerabilities
```

**Solutions:**
```bash
# View detailed vulnerability report
poetry run safety check --full-report

# Update vulnerable packages
poetry update

# If vulnerability can't be fixed, document exception
echo "# Known vulnerability - tracked in issue #123" > .safety-exceptions
```

## Environment Issues

### Direnv Not Loading
**Symptoms:**
```
Environment variables not set
```

**Solutions:**
```bash
# Install direnv
brew install direnv  # macOS
# or
apt install direnv   # Ubuntu

# Add to shell
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc
source ~/.bashrc

# Allow .envrc
direnv allow .
```

### Python Version Issues
**Symptoms:**
```
The currently activated Python version 3.8 is not supported
```

**Solutions:**
```bash
# Install correct Python version
pyenv install 3.11.0
pyenv local 3.11.0

# Update Poetry to use correct Python
poetry env use python3.11

# Verify Python version
python --version
```

### Package Installation Issues
**Symptoms:**
```
ERROR: Could not build wheels for package
```

**Solutions:**
```bash
# Update build tools
poetry run pip install --upgrade pip setuptools wheel

# Install system dependencies (Ubuntu)
sudo apt-get install build-essential python3-dev

# Install system dependencies (macOS)
xcode-select --install
```

## Network and Connectivity Issues

### GitHub Access Issues
**Symptoms:**
```
Permission denied (publickey)
fatal: Could not read from remote repository
```

**Solutions:**
```bash
# Check SSH key
ssh -T git@github.com

# Generate new SSH key if needed
ssh-keygen -t ed25519 -C "your-email@example.com"

# Add to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Add to GitHub account
cat ~/.ssh/id_ed25519.pub
# Copy and paste to GitHub > Settings > SSH Keys
```

### Package Download Failures
**Symptoms:**
```
WARNING: Retrying download: Connection timeout
```

**Solutions:**
```bash
# Check network connectivity
ping pypi.org
curl -I https://pypi.org/

# Use different package index
poetry source add --priority=primary pypi-mirror https://pypi.org/simple/

# Configure timeout
poetry config installer.max-workers 10
```

## Performance Issues

### Slow Container Builds
**Symptoms:**
Build takes >5 minutes consistently

**Solutions:**
```bash
# Use BuildKit cache
export DOCKER_BUILDKIT=1

# Clean build cache periodically
docker builder prune

# Use multi-stage builds
# (Already implemented in Genesis Dockerfile)

# Consider using container registry cache
docker buildx build --cache-from=type=registry,ref=your-registry/cache
```

### Large Git Repository
**Symptoms:**
Operations take very long time

**Solutions:**
```bash
# Use shallow clone
git clone --depth 1 https://github.com/user/repo.git

# Enable Git optimizations
git config core.preloadindex true
git config core.fscache true

# Prune unnecessary objects
git gc --aggressive
```

## Diagnostic Commands

### System Information
```bash
# Genesis version
genesis --version

# Python environment
python --version
poetry --version

# Docker environment
docker --version
docker compose version

# Git configuration
git config --list --show-origin
```

### Project Health Check
```bash
# Validate project structure
make validate-bootstrap

# Check file organization
make check-org

# Verify quality gates
make quality-report

# Container health
docker compose ps
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=debug

# Run commands with verbose output
genesis sync --dry-run 2>&1 | tee debug.log

# Check specific component
LOG_LEVEL=debug python -m genesis.cli container build
```

## Getting Help

### Community Support
- GitHub Issues: https://github.com/jhousteau/genesis/issues
- Discussion Forum: https://github.com/jhousteau/genesis/discussions
- Documentation: See related docs in this directory

### Bug Reports
When reporting bugs, include:
```bash
# System information
genesis --version
python --version
docker --version
uname -a

# Error logs
LOG_LEVEL=debug genesis command 2>&1 | tee error.log

# Project state
git status
ls -la .genesis/
```

### Feature Requests
- Use GitHub Issues with "enhancement" label
- Include use case and expected behavior
- Reference related documentation

## Related Documentation

- [Genesis CLI Reference](./CLI_REFERENCE.md)
- [Worktree Management Guide](./WORKTREE_GUIDE.md)
- [AI Safety Best Practices](./AI_SAFETY.md)
- [Genesis Standards Guild](./GENESIS_STANDARDS_GUILD.md)
