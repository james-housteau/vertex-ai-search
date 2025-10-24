# Genesis Aggressive Auto-Organization System

This document describes the implementation of GitHub issue #261: "Implement Aggressive Auto-Organization to Prevent Repository Decay".

## Overview

The auto-organization system prevents repository decay by automatically detecting and moving misplaced files according to Genesis conventions, while maintaining fail-fast principles and AI safety boundaries.

## Components

### 1. Enhanced File Organization Script

**Location**: `.genesis/scripts/check-file-organization.sh`

**Features**:
- **Dry-run mode** (`--dry-run`): Preview changes without making them
- **Auto-move mode** (`--auto-move`): Automatically organize misplaced files
- **Import path updates**: Automatically fixes Python import statements after moves
- **Component boundary respect**: Doesn't move files between Genesis components
- **Fail-fast verification**: Verifies all moves completed successfully

**Auto-move rules**:
- `test_*.py`, `*_test.py`, `conftest.py` → `tests/`
- `*.test.html`, `*.spec.js`, `*.test.ts` → `tests/`
- `*.sh` (non-wrapper scripts) → `scripts/`
- `*.py` (non-test, non-setup) → `src/`
- `*.md` (non-core documentation) → `docs/`

**Usage**:
```bash
# Report mode (default) - show suggestions
.genesis/scripts/check-file-organization.sh

# Preview what would be moved
.genesis/scripts/check-file-organization.sh --dry-run

# Actually move files
.genesis/scripts/check-file-organization.sh --auto-move
```

### 2. Git Hooks Integration

**Hooks directory**: `.genesis/hooks/`

**Implemented hooks**:
- `post-checkout`: Runs after branch switches
- `post-merge`: Runs after pulls/merges
- `post-commit`: Runs after commits
- `pre-push`: Final check before pushes

**Installation**:
```bash
.genesis/scripts/install-organization-hooks.sh
```

The installer:
- Backs up existing hooks before replacement
- Makes hooks executable
- Provides installation summary
- Handles repository root detection

### 3. Import Path Updates

When Python files are moved, the system automatically:
1. Converts file paths to module paths
2. Searches all Python files in the repository
3. Updates `from module import` statements
4. Updates `import module` statements
5. Provides feedback on changes made

### 4. Fail-Fast Principles

The system follows Genesis fail-fast principles:
- **Verification**: All moved files are verified to exist at destination
- **Error handling**: Clear error messages for conflicts (file already exists)
- **Exit codes**: Non-zero exit on verification failures in auto-move mode
- **Logging**: Comprehensive logging of all operations

## Safety Features

### Component Boundary Respect

The system respects Genesis component boundaries and won't move files between:
- `bootstrap/`, `genesis/`, `shared-python/`, `shared-typescript/`
- `smart-commit/`, `terraform/`, `testing/`
- `worktree-tools/`, `templates/`, `worktrees/`

This ensures component integrity while organizing the main repository structure.

### AI Safety Integration

- File count limits are respected during organization
- Component isolation is maintained
- Worktree structures are preserved

### Manual Review Categories

Some files require manual review and won't be auto-moved:
- Configuration files (`*.json`, `*.yml` not in standard locations)
- Hidden configuration files (except standard ones)
- Wrapper scripts (`*wrapper.sh`)
- Files that don't match standard patterns

## Testing

### Manual Testing
```bash
# Create test files
touch test_example.py example_test.js conftest.py example.sh

# Test dry-run
.genesis/scripts/check-file-organization.sh --dry-run

# Test actual moves
.genesis/scripts/check-file-organization.sh --auto-move

# Verify files moved correctly
ls tests/ scripts/
```

### Hook Testing
```bash
# Install hooks
.genesis/scripts/install-organization-hooks.sh

# Test a hook manually (from repository root)
.git/hooks/post-commit
```

## Implementation Details

### Architecture Decisions

1. **Bash over Python**: Chose bash for better integration with git hooks and lower dependency overhead
2. **Modular functions**: Separate functions for each check type enable targeted testing
3. **Progressive enhancement**: Falls back gracefully when tools are unavailable
4. **Component awareness**: Understands Genesis dual-package architecture

### Error Handling

- Missing dependencies are handled gracefully
- File conflicts are reported clearly
- Partial failures don't break the entire process
- All operations are logged for debugging

### Performance Considerations

- Uses efficient `find` commands with exclusions
- Minimizes file system operations
- Batches similar operations
- Provides progress feedback for long operations

## Future Enhancements

Potential future improvements:
1. **Language-specific rules**: Enhanced rules for TypeScript, Go, etc.
2. **Custom patterns**: User-configurable file organization rules
3. **Integration testing**: Automated testing of the organization system
4. **Metrics**: Track organization improvements over time
5. **IDE integration**: VS Code extension for organization suggestions

## Troubleshooting

### Common Issues

**Hook not running**:
- Verify hooks are installed: `ls -la .git/hooks/post-*`
- Check hook permissions: `chmod +x .git/hooks/post-*`

**Script not found**:
- Ensure you're in repository root
- Check script exists: `ls -la .genesis/scripts/check-file-organization.sh`

**Import updates failing**:
- Verify `sed` command availability
- Check Python file syntax after moves
- Review import paths manually if needed

### Debug Mode

Add `set -x` to any script for detailed execution tracing:
```bash
set -x
.genesis/scripts/check-file-organization.sh --dry-run
```

## Contributing

When modifying the auto-organization system:
1. Test in dry-run mode first
2. Verify component boundaries are respected
3. Test import path updates with real Python files
4. Ensure fail-fast behavior is maintained
5. Update this documentation for any new features
