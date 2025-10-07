---
allowed-tools: Task, Bash, Read, Write, Edit, Grep, Glob
argument-hint: "[issue-number]"
description: "Optimize performance based on measured bottlenecks"
model: claude-sonnet-4-20250514
---

# Optimization Workflow for Issue #$1

Improve performance based on measured bottlenecks using Genesis and specialized agents.

## STEP 1-7: Standard Genesis Worktree Setup

```bash
# Standard setup (see /bug command for full details)
genesis status
source .envrc
gh issue view $1 || exit 1
genesis clean
genesis worktree create optimize-$1 --max-files 30 \
  --include .genesis/ --include .claude/ --include scripts/ \
  --include shared-python/ --include Makefile --include pyproject.toml \
  --include pytest.ini --include .pre-commit-config.yaml --include .envrc
cd worktrees/optimize-$1/
source .envrc
genesis status
```

## STEP 8: Optimization Agent Workflow (CORRECTED ORDER)

### Agent 1: issue-analyst
Validate optimization scope and specific performance targets.

### Agent 2: performance-monitor
Establish baseline metrics:
- Measure current performance
- Profile execution time
- Identify bottlenecks
- Document baseline numbers

### Agent 3: complexity-auditor
Baseline complexity measurement:
- Ensure optimization won't increase complexity
- Document current complexity metrics

### Agent 4: lean-implementer
Implement optimizations:
- Target only measured bottlenecks
- Apply minimal changes for maximum impact
- Avoid premature optimization
- Keep changes focused and minimal

### Agent 5: performance-monitor
Verify performance improved:
- Re-measure performance metrics
- Confirm improvement achieved
- Document performance gains

### Agent 6: complexity-auditor
Ensure complexity not increased:
- Re-measure complexity
- Verify no over-engineering introduced

### Agent 7: build-validator
Validate improvements and no regressions:
- All tests pass
- Performance targets met
- No functionality broken
- Genesis quality gates satisfied

## STEP 9-11: Quality Gates, Commit, and Return

```bash
# Quality validation
genesis autofix
make test

# Commit and PR
git add .
genesis commit -m "perf: optimize performance for issue #$1"
gh pr create --title "perf: optimize issue #$1" \
  --body "Performance optimization based on measured bottlenecks per issue #$1"

# Return to main
cd ../../
genesis status
echo "✅ SUCCESS: Optimization completed for issue #$1"
```
