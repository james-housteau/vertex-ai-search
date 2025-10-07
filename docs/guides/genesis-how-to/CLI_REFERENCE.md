# Genesis CLI Reference

## Overview

The Genesis CLI provides commands for project management, development workflows, and AI-safe practices.

## Installation

```bash
pip install genesis-cli
```

## Global Commands

### `genesis bootstrap <name>`
Create a new project with Genesis patterns and tooling.

**Usage:**
```bash
genesis bootstrap my-project --type python-api
genesis bootstrap my-cli-tool --type cli-tool
genesis bootstrap my-service --type typescript-service
```

**Options:**
- `--type`: Project template type (required)
  - `python-api`: FastAPI-based web service
  - `cli-tool`: Command-line application
  - `typescript-service`: Node.js/TypeScript service
- `--path TEXT`: Directory to create project in
- `--skip-git`: Skip Git initialization

### `genesis sync`
Update project support files from Genesis templates.

**Usage:**
```bash
genesis sync                    # Update support files
genesis sync --dry-run          # Preview changes
genesis sync --force            # Force update all files
genesis sync --path /project    # Sync specific project
```

**Options:**
- `--force`: Force update even if files are modified
- `--dry-run`: Show what would be updated without making changes
- `--path PATH`: Path to project (default: current directory)

### `genesis commit`
Smart commit with quality gates and validation.

**Usage:**
```bash
genesis commit -m "Add new feature"
genesis commit                  # Interactive mode
```

**Features:**
- Automatic code formatting (black, ruff, prettier)
- Pre-commit hook validation
- Test execution
- Security scanning
- Documentation updates

### `genesis container`
Manage Docker containers for development.

**Usage:**
```bash
genesis container build         # Build development container
genesis container run          # Start container
genesis container shell        # Interactive shell
genesis container stop         # Stop container
```

**Profiles:**
- `cli`: Command-line development
- `api`: Web service development
- `ts`: TypeScript development
- `agent`: AI agent development (isolated)

### `genesis worktree`
Manage sparse worktrees for AI-safe development.

**Usage:**
```bash
genesis worktree create feature-auth src/auth/
genesis worktree list
genesis worktree remove feature-auth
```

## Project-Specific Commands

These commands are available when run from within a vertex-ai-search project:

### Development Workflow
```bash
make setup                    # Initial project setup
make test                     # Run tests
make format                   # Format code
make lint                     # Run linters
make run                      # Start development server
```

### Quality Gates
```bash
make security                 # Security scans
make validate-bootstrap       # Validate project setup
make check-org               # Check file organization
```

### Container Development
```bash
make container-build         # Build container
make container-run           # Run container
make container-shell         # Container shell
```

## Environment Variables

### Required
- `GITHUB_TOKEN`: For accessing Genesis packages and releases

### Optional
- `LOG_LEVEL`: Logging level (debug, info, warning, error)
- `GENESIS_UNIX_SHELLS`: Custom shell paths for Unix systems
- `GENESIS_CONTAINER_CONFIG`: Container configuration file

## Configuration Files

### `.envrc`
Environment variable configuration for direnv.

### `pyproject.toml`
Python project configuration including Genesis CLI dependencies.

### `docker-compose.yml`
Container orchestration with development profiles.

### `.claude/settings.json`
Claude Code AI assistant configuration.

## Troubleshooting

Common issues and solutions:

### "Command not found: genesis"
```bash
# Ensure Genesis CLI is installed
pip install genesis-cli

# Or install in project
poetry add genesis-cli
```

### "Permission denied" on scripts
```bash
# Fix script permissions
chmod +x scripts/*.sh
```

### Container build failures
```bash
# Check GITHUB_TOKEN is set
echo $GITHUB_TOKEN

# Rebuild from scratch
genesis container build --no-cache
```

For more troubleshooting, see [TROUBLESHOOTING.md](./TROUBLESHOOTING.md).

## Related Documentation

- [Worktree Management Guide](./WORKTREE_GUIDE.md)
- [AI Safety Best Practices](./AI_SAFETY.md)
- [Genesis Standards Guild](./GENESIS_STANDARDS_GUILD.md)
