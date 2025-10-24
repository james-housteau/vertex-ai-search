# Version Management Guide for vertex-ai-search

This  project uses Genesis's professional version management system for consistent, automated version handling across all project files.

## Quick Start

```bash
# Show current version
python .genesis/scripts/build/version.py show

# Bump version types
./.genesis/scripts/build/bump-version.sh patch  # 1.0.0 → 1.0.1
./.genesis/scripts/build/bump-version.sh minor  # 1.0.0 → 1.1.0
./.genesis/scripts/build/bump-version.sh major  # 1.0.0 → 2.0.0

# Manual version operations
python .genesis/scripts/build/version.py bump patch
python .genesis/scripts/build/version.py sync
```

## System Overview

Genesis provides a **single source of truth** version management system that automatically synchronizes versions across:



- `README.md` - Documentation version references
- Any other files with `__version__` declarations

## Version Files in This Project





### Automated Scripts

**`.genesis/scripts/build/bump-version.sh`** - Intelligent version bumping
- Detects project type (Python/Node.js)
- Uses appropriate tooling (Poetry/NPM)
- Validates git repository state
- Syncs across all project files
- Provides commit instructions

**`.genesis/scripts/build/version.py`** - Python-based utilities
- Cross-platform version operations
- Semantic versioning support
- File synchronization capabilities
- Fail-fast error handling

## Version Management Workflows

### Recommended: Automated Bumping

```bash
# Make your changes and commit them
git add -A && git commit -m "feat: add new feature"

# Bump version automatically
./.genesis/scripts/build/bump-version.sh minor

# Follow the provided instructions:
git diff                                          # Review changes
git add -A && git commit -m "bump: version 1.1.0" # Commit version bump
git tag v1.1.0                                   # Tag release
git push && git push --tags                      # Push everything
```

### Manual Version Control

```bash
# Check current version
python .genesis/scripts/build/version.py show

# Bump specific version types
python .genesis/scripts/build/version.py bump patch
python .genesis/scripts/build/version.py bump minor --sync

# Sync version across files (without bumping)
python .genesis/scripts/build/version.py sync
```

### Project-Specific Commands





## Semantic Versioning Support

Genesis follows [Semantic Versioning](https://semver.org/) principles:

### Standard Versions
- **patch**: Bug fixes and small improvements (`1.0.0` → `1.0.1`)
- **minor**: New features, backward compatible (`1.0.0` → `1.1.0`)
- **major**: Breaking changes (`1.0.0` → `2.0.0`)

### Prerelease Versions
- **alpha**: Early development releases (`1.0.0` → `1.0.0-alpha`)
- **beta**: Feature-complete but untested (`1.0.0` → `1.0.0-beta`)
- **rc**: Release candidates (`1.0.0` → `1.0.0-rc`)

### Example Progression
```
1.0.0-alpha → 1.0.0-alpha.2 → 1.0.0-beta → 1.0.0-rc → 1.0.0 → 1.0.1
```

## File Synchronization

Genesis automatically syncs versions to these file patterns:

### Automatic Sync Targets
- `package.json` - NPM/Node.js projects
- `**/__init__.py` - Python packages with `__version__` declarations
- `README.md` - Version references in documentation

### Exclusions
The system skips these directories to avoid modifying dependencies:
- `.venv`, `venv`, `env` - Python virtual environments
- `node_modules` - NPM dependencies
- `site-packages` - Python packages
- `.git` - Git metadata

### Custom Sync Behavior

You can customize which files get version updates by modifying the sync patterns in `.genesis/scripts/build/version.py`.

## Integration with Development Tools

### Pre-commit Hooks
Add version validation to your pre-commit configuration:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: version-consistency
        name: Version Consistency Check
        entry: python .genesis/scripts/build/version.py show
        language: system
        pass_filenames: false
```

### CI/CD Integration
Use in continuous integration:

```yaml
# Example GitHub Actions
- name: Check Version Consistency
  run: python .genesis/scripts/build/version.py show

- name: Validate Semantic Version
  run: |
    VERSION=$(python .genesis/scripts/build/version.py show)
    if [[ ! $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
      echo "Invalid semantic version: $VERSION"
      exit 1
    fi
```

### Development Scripts Integration





## Troubleshooting

### Common Issues

**Issue:** `FileNotFoundError: No version file found`
**Solution:** Ensure your project has `pyproject.toml` or `package.json` with version field

**Issue:** Version sync fails for some files
**Solution:** Check file permissions and ensure files aren't in excluded directories

**Issue:** Git validation fails during bump
**Solution:** Commit or stash uncommitted changes before version bumping

### Debugging Commands

```bash
# Verbose version detection
python .genesis/scripts/build/version.py show --help

# Test version bumping without changes
python .genesis/scripts/build/version.py bump patch --dry-run

# Manual file sync with error details
python .genesis/scripts/build/version.py sync --verbose
```

### Recovery from Version Issues

```bash
# Reset to known version



# Sync to all other files
python .genesis/scripts/build/version.py sync --version 1.0.0

# Verify consistency
python .genesis/scripts/build/version.py show
```

## Customization

### Project-Specific Modifications

The Genesis version management system is designed to be customizable:

1. **Modify `.genesis/scripts/build/version.py`** for custom version file formats
2. **Update `.genesis/scripts/build/bump-version.sh`** for project-specific workflows
3. **Add version validation** in your project's pre-commit hooks

### Version File Patterns

To add support for additional version files:

```python
# In .genesis/scripts/build/version.py, modify sync_version_to_files()

# Add custom version file patterns
custom_version_files = project_path.glob("**/version.")
for version_file in custom_version_files:
    # Add your sync logic here
    pass
```

## Best Practices

### Development Workflow

1. ✅ **Always commit changes before version bumping**
2. ✅ **Use semantic versioning principles**
3. ✅ **Tag releases with `git tag v{VERSION}`**
4. ✅ **Keep version references in sync**
5. ❌ **Never manually edit multiple version files**

### Release Management

1. **Feature development**: Use `minor` bumps
2. **Bug fixes**: Use `patch` bumps
3. **Breaking changes**: Use `major` bumps
4. **Experimental features**: Use `alpha` or `beta` prereleases

### Automation

```bash
# Create release script
cat > scripts/release.sh << 'EOF'
#!/bin/bash
set -euo pipefail

BUMP_TYPE=${1:-patch}

# Run tests
make test

# Bump version
./.genesis/scripts/build/bump-version.sh $BUMP_TYPE

# Follow bump instructions automatically
git add -A
NEW_VERSION=$(python .genesis/scripts/build/version.py show)
git commit -m "bump: version $NEW_VERSION"
git tag "v$NEW_VERSION"
git push && git push --tags

echo "✅ Released version $NEW_VERSION"
EOF

chmod +x scripts/release.sh
```

## Resources

- [Semantic Versioning Specification](https://semver.org/)
- [Genesis Documentation](./README.md)
- [Project Setup Guide](./docs/getting-started.md)

---

*This version management system is provided by Genesis - consistent tooling for professional development workflows.*
