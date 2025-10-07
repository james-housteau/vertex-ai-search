---
allowed-tools: Task, Bash, Read, Write, Edit
argument-hint: [issue-number]
description: Resolve GitHub issue using TDD workflow
model: claude-sonnet-4-20250514
---

## TDD Resolution Workflow

Resolve issue #$1 using strict Test-Driven Development with lean principles.

### Phase 0: Setup Genesis Worktree
```bash
# Create AI-safe isolated worktree for issue with shared files
genesis worktree create fix-$1 --focus src/ --max-files 30 \
  --include .claude/ \
  --include .genesis/scripts/ \
  --include Makefile \
  --include .gitignore \
  --include .pre-commit-config.yaml

# CRITICAL: Navigate to isolated worktree
cd ../worktrees/fix-$1/

# Verify .claude directory is present for commands
ls -la .claude/ || echo "⚠️ .claude directory missing - some commands may not work"
```

### Phase 1: Analyze Issue
```bash
# Get issue details
gh issue view $1
```

Use issue-analyst to verify scope is atomic and clear.

### Phase 2: RED - Write Failing Tests

Use test-designer agent:
- Write minimal tests for core functionality
- Verify tests fail for the right reason
- No edge case obsession
- Focus on critical path only

### Phase 3: GREEN - Minimal Implementation

Use lean-implementer agent:
- Write simplest code that passes tests
- No abstractions or patterns
- Direct solutions only
- YAGNI always

Run tests with build-validator agent:
```bash
# Detect and run appropriate test command
make test || npm test || pytest || cargo test
```

### Phase 4: REFACTOR - Simplify

Use refactoring-specialist agent:
- Reduce code complexity
- Eliminate duplication
- Remove unnecessary abstractions
- Maintain all tests passing

### Phase 5: Validate

Run audit agents in sequence:
1. scope-guardian: Verify no scope creep
2. bloat-detector: Find unnecessary code
3. complexity-auditor: Check complexity metrics
4. dependency-tracker: Verify no new dependencies

### Phase 6: Final Quality Check

Use build-validator to run full quality suite:
```bash
make quality || npm run lint || ruff
```

### Success Criteria
- ✅ All tests passing
- ✅ No scope creep
- ✅ Complexity metrics within limits
- ✅ No unnecessary dependencies added
- ✅ Quality checks pass

### Phase 7: Stage Changes
```bash
# Stage all changes for commit
git add .
```

Report status and readiness for Genesis commit.
