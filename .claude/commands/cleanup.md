---
allowed-tools: Task, Bash, Read, Write, Edit, Grep, Glob
argument-hint: "[issue-number]"
description: "Clean up code and remove dead code with Genesis"
model: claude-sonnet-4-20250514
---

# Cleanup Workflow for Issue #$1

Remove dead code, unused dependencies, and technical debt using Genesis integration and specialized agents.

## STEP 1-7: Standard Genesis Worktree Setup

```bash
# Standard setup (see /bug command for full details)
genesis status
source .envrc
gh issue view $1 || exit 1
genesis clean
genesis worktree create cleanup-$1 --max-files 30 \
  --include .genesis/ --include .claude/ --include scripts/ \
  --include shared-python/ --include Makefile --include pyproject.toml \
  --include pytest.ini --include .pre-commit-config.yaml --include .envrc
cd worktrees/cleanup-$1/
source .envrc
genesis status
```

## STEP 8: Cleanup Agent Workflow

### Agent 1: issue-analyst
Validate cleanup scope is atomic and well-defined.

### Agent 2: bloat-detector
Identify removal targets:
- Dead code and unused functions
- Orphaned dependencies
- Redundant files and duplications
- Over-engineered abstractions

### Agent 3: dependency-tracker
Verify removal safety:
- Check usage patterns
- Identify downstream impacts
- Validate no breaking changes

### Agent 4: scope-guardian
Prevent scope creep:
- Ensure only targeted removals
- No new features or improvements
- Maintain minimal change principle

### Agent 5: build-validator
Verify system integrity:
- All tests pass after cleanup
- No functionality broken
- Genesis quality gates satisfied

## STEP 9-11: Quality Gates, Commit, and Return

```bash
# Quality validation
genesis autofix
make test

# Commit and PR
git add .
genesis commit -m "cleanup: remove dead code from issue #$1"
gh pr create --title "cleanup: issue #$1" \
  --body "Removed dead code and unused dependencies per issue #$1"

# Return to main
cd ../../
genesis status
echo "✅ SUCCESS: Cleanup completed for issue #$1"
```
