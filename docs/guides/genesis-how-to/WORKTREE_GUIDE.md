# Worktree Management Guide

## Overview

Genesis uses sparse worktrees to enable AI-safe development by limiting the number of files visible in each development context to under 30 files.

## What are Sparse Worktrees?

Sparse worktrees allow you to check out only specific files or directories from a Git repository, creating focused development environments that:

- **Reduce cognitive load** for developers and AI assistants
- **Prevent context overflow** in AI-assisted development
- **Enable parallel development** on different features
- **Maintain repository integrity** while providing isolation

## Genesis Worktree Commands

### Create a Worktree
```bash
# Create worktree for specific component
genesis worktree create auth-system src/auth/

# Create worktree with custom path
genesis worktree create payment-flow src/payment/ --path ../payment-worktree

# Create worktree with file pattern
genesis worktree create api-routes "src/routes/*.py"
```

### List Worktrees
```bash
genesis worktree list
```

Output:
```
📂 Active Worktrees for vertex-ai-search:
  🌟 main (current)     /path/to/vertex-ai-search                [25 files]
  🔧 auth-system       /path/to/vertex-ai-search-auth           [18 files]
  🔧 payment-flow      /path/to/payment-worktree                [12 files]
```

### Remove a Worktree
```bash
genesis worktree remove auth-system
```

### Switch Between Worktrees
```bash
cd ../vertex-ai-search-auth    # Switch to auth worktree
cd ../vertex-ai-search         # Switch back to main
```

## AI Safety Guidelines

### File Limits
- **Maximum 30 files** per worktree for AI safety
- Genesis automatically warns if approaching limit
- Use `genesis worktree validate` to check file counts

### Best Practices
1. **Feature-focused worktrees**: One worktree per feature/component
2. **Minimal scope**: Include only files needed for current task
3. **Regular validation**: Check file counts before major development sessions
4. **Clean removal**: Remove completed worktrees to avoid clutter

## Worktree Organization Patterns

### By Feature
```
main/                    # Core project files
auth-worktree/          # Authentication system
api-worktree/           # API endpoints
ui-worktree/            # User interface components
```

### By Layer
```
main/                    # Project configuration
models-worktree/        # Data models
services-worktree/      # Business logic
controllers-worktree/   # Request handlers
```

### By Module
```
main/                    # Shared utilities
user-module/            # User management
order-module/           # Order processing
payment-module/         # Payment handling
```

## Configuration

### Worktree Settings
Configure worktree behavior in `.genesis/worktree-config.yml`:

```yaml
max_files: 30
auto_validate: true
default_patterns:
  - "**/*.py"
  - "**/*.ts"
  - "**/*.md"
exclude_patterns:
  - "**/__pycache__/**"
  - "**/node_modules/**"
  - "**/.git/**"
```

### Git Configuration
Genesis automatically configures Git settings for worktrees:

```bash
# Enable worktree features
git config extensions.worktreeConfig true

# Set safe directories
git config --global --add safe.directory /path/to/worktree
```

## Advanced Usage

### Custom Sparse Patterns
```bash
# Include specific file types
echo "src/*.py" > .git/info/sparse-checkout
echo "tests/*.py" >> .git/info/sparse-checkout

# Apply sparse checkout
git read-tree -m -u HEAD
```

### Worktree Hooks
Genesis can run custom scripts on worktree creation:

`.genesis/hooks/post-worktree-create.sh`:
```bash
#!/bin/bash
echo "Setting up worktree: $WORKTREE_NAME"
echo "Path: $WORKTREE_PATH"
echo "Files: $FILE_COUNT"
```

### Integration with IDEs

#### VS Code
```json
{
  "files.watcherExclude": {
    "../*-worktree/**": true
  }
}
```

#### PyCharm
Configure project structure to recognize worktree directories.

## Troubleshooting

### "Too many files" Warning
```bash
# Check current file count
genesis worktree validate

# Reduce scope by excluding directories
echo "!tests/fixtures/" >> .git/info/sparse-checkout
git read-tree -m -u HEAD
```

### Worktree Creation Fails
```bash
# Ensure clean working directory
git status

# Check for conflicts
git worktree prune
```

### Missing Files in Worktree
```bash
# Update sparse-checkout patterns
echo "src/missing-file.py" >> .git/info/sparse-checkout
git read-tree -m -u HEAD
```

### Worktree Path Issues
```bash
# Use absolute paths
genesis worktree create feature-name /absolute/path/to/files

# Or use relative patterns
genesis worktree create feature-name "./src/feature/**"
```

## Security Considerations

### File Isolation
- Worktrees share Git history but isolate working files
- Sensitive files can be excluded from specific worktrees
- Use `.gitignore` patterns for security-sensitive paths

### Access Control
```bash
# Restrict worktree creation to specific paths
genesis worktree create --allowed-paths="src/,tests/,docs/"
```

## Performance Optimization

### Large Repositories
- Use shallow clones for worktrees: `--depth 1`
- Configure Git to optimize for many worktrees
- Regular cleanup of unused worktrees

### File System Optimization
```bash
# Enable Git's filesystem optimizations
git config core.preloadindex true
git config core.fscache true
git config gc.auto 256
```

## Related Documentation

- [AI Safety Best Practices](./AI_SAFETY.md)
- [Genesis CLI Reference](./CLI_REFERENCE.md)
- [Troubleshooting Guide](./TROUBLESHOOTING.md)
