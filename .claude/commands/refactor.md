---
allowed-tools: Task, Bash, Read, Write, Edit, Grep, Glob
argument-hint: "[issue-number]"
description: "Refactor code to improve structure without changing behavior"
model: claude-sonnet-4-20250514
---

# Refactoring Workflow for Issue #$1

Improve code structure and maintainability without changing behavior using Genesis and specialized agents.

## STEP 1-7: Standard Genesis Worktree Setup

```bash
# Standard setup (see /bug command for full details)
genesis status
source .envrc
gh issue view $1 || exit 1
genesis clean
genesis worktree create refactor-$1 --max-files 30 \
  --include .genesis/ --include .claude/ --include scripts/ \
  --include shared-python/ --include Makefile --include pyproject.toml \
  --include pytest.ini --include .pre-commit-config.yaml --include .envrc
cd worktrees/refactor-$1/
source .envrc
genesis status
```

## STEP 8: Refactoring Agent Workflow (CORRECTED ORDER)

### Agent 1: issue-analyst
Validate refactoring scope and objectives.

### Agent 2: test-designer
Ensure comprehensive test coverage FIRST:
- Write tests for existing behavior if missing
- Ensure tests document current functionality
- Tests must pass before refactoring begins

### Agent 3: complexity-auditor
Baseline complexity measurement:
- Measure current cyclomatic complexity
- Identify complex methods and classes
- Document baseline metrics

### Agent 4: refactoring-specialist
Improve structure without behavior change:
- Extract methods for clarity
- Remove duplication
- Simplify complex conditionals
- Apply appropriate design patterns
- Maintain test passage throughout

### Agent 5: complexity-auditor
Verify complexity improved:
- Re-measure complexity metrics
- Confirm reduction in complexity
- Document improvements

### Agent 6: build-validator
Prove behavior unchanged:
- All tests still pass
- No functionality altered
- Performance not degraded
- Genesis quality gates satisfied

## STEP 9-11: Quality Gates, Commit, and Return

```bash
# Quality validation
genesis autofix
make test

# Commit and PR
git add .
genesis commit -m "refactor: improve code structure for issue #$1"
gh pr create --title "refactor: issue #$1" \
  --body "Improved code structure without changing behavior per issue #$1"

# Return to main
cd ../../
genesis status
echo "✅ SUCCESS: Refactoring completed for issue #$1"
```
