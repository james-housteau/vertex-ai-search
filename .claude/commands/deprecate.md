---
allowed-tools: Task, Bash, Read, Write, Edit, Grep, Glob
argument-hint: "[issue-number]"
description: "Deprecate old code and provide migration path"
model: claude-sonnet-4-20250514
---

# Deprecation Workflow for Issue #$1

Deprecate old code with clear migration path using Genesis and specialized agents.

## STEP 1-7: Standard Genesis Worktree Setup

```bash
# Standard setup (see /bug command for full details)
genesis status
source .envrc
gh issue view $1 || exit 1
genesis clean
genesis worktree create deprecate-$1 --max-files 30 \
  --include .genesis/ --include .claude/ --include scripts/ \
  --include shared-python/ --include Makefile --include pyproject.toml \
  --include pytest.ini --include .pre-commit-config.yaml --include .envrc
cd worktrees/deprecate-$1/
source .envrc
genesis status
```

## STEP 8: Deprecation Agent Workflow

### Agent 1: issue-analyst
Validate deprecation scope:
- Identify what needs deprecation
- Confirm migration requirements
- Ensure atomic deprecation approach

### Agent 2: dependency-tracker
Analyze usage and dependencies:
- Find all usage points
- Identify downstream dependencies
- Map migration requirements
- Document impact analysis

### Agent 3: lean-implementer
Implement migration path:
- Add deprecation warnings
- Create migration utilities if needed
- Update documentation
- Provide clear upgrade path

### Agent 4: scope-guardian
Ensure surgical removal:
- Only deprecate specified components
- No additional changes
- Maintain backward compatibility where required

### Agent 5: build-validator
Verify system integrity:
- All tests pass with deprecations
- Migration path works
- Warnings displayed correctly
- Genesis quality gates satisfied

## STEP 9-11: Quality Gates, Commit, and Return

```bash
# Quality validation
genesis autofix
make test

# Commit and PR
git add .
genesis commit -m "deprecate: mark old code for removal in issue #$1"
gh pr create --title "deprecate: issue #$1" \
  --body "Deprecated old code with migration path per issue #$1"

# Return to main
cd ../../
genesis status
echo "✅ SUCCESS: Deprecation completed for issue #$1"
```
