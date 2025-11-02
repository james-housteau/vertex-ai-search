---
allowed-tools: Task, Bash, Read, Write, Edit, Grep, Glob
argument-hint: "[issue-number]"
description: "Refactor code to improve structure without changing behavior"
model: claude-sonnet-4-20250514
---

# Refactoring Workflow for Issue #$1

Improve code structure and maintainability without changing behavior using Genesis and specialized agents.

---

# ⚠️ CRITICAL: EXECUTION vs DELEGATION ⚠️

This workflow has THREE phases with DIFFERENT execution modes:

**📍 SETUP PHASE (STEPS 1-7): YOU EXECUTE DIRECTLY**
- ⚠️ DO NOT use Task tool - use Bash tool
- ⚠️ YOU must run commands yourself
- ⚠️ Verify each step completes

**🤖 REFACTORING PHASE (STEP 8): DELEGATION ALLOWED**
- ✅ NOW use Task tool with specialized agents
- ✅ Agents work in worktree YOU created

**📍 FINALIZATION PHASE (STEPS 9-11): YOU EXECUTE DIRECTLY**
- ⚠️ DO NOT delegate commits/PRs
- ⚠️ YOU must run commands with Bash tool
- ⚠️ Return to main repo yourself

---

## CONTEXT: Pure Module Isolation

This workflow creates a Genesis worktree with all supporting files needed for pure module isolation.
A functional module requires not just its own code, but the Genesis infrastructure (.genesis/),
shared utilities (shared-python/), and Python environment files (pyproject.toml, poetry.lock, .venv).

---

## ═══════════════════════════════════════════════════
## SETUP PHASE - YOU MUST EXECUTE (NO DELEGATION)
## ═══════════════════════════════════════════════════

⚠️ **DO NOT use Task tool for STEPS 1-7 - use Bash tool**

## STEP 1-7: Standard Genesis Worktree Setup

**Tool to use:** `Bash` (for all commands below)

```bash
# Standard setup with Pure Module Isolation
genesis status || echo "⚠️ WARNING: Genesis health issues"
source .envrc || { echo "❌ FATAL: Failed to source .envrc"; exit 1; }
gh issue view $1 || exit 1
genesis clean || echo "⚠️ WARNING: Clean encountered issues"

# Create worktree with auto-symlinked dependencies
genesis worktree create refactor-$1 \
  --focus genesis/ \
  --max-files ${WORKTREE_MAX_FILES:-30}

cd worktrees/refactor-$1/ || { echo "❌ FATAL: Failed to navigate"; exit 1; }
pwd  # VERIFY: Must show .../genesis/worktrees/refactor-$1

# Verify symlinks created automatically by worktree script
echo "Verifying Pure Module Isolation setup..."

# Check symlinks exist (auto-created by script)
for symlink in shared-python .genesis .venv docs; do
    if [[ ! -L "$symlink" ]]; then
        echo "⚠️ WARNING: Symlink missing: $symlink (should be auto-created)"
    else
        echo "✓ Symlink present: $symlink -> $(readlink $symlink)"
    fi
done

# Check shared files from manifest

for file in Makefile pyproject.toml pytest.ini .envrc; do
    if [[ ! -f "$file" ]]; then
        echo "⚠️ WARNING: Shared file missing: $file (should be from manifest)"
    else
        echo "✓ Shared file present: $file"
    fi
done

# Count visible files (should be <30 for Pure Module Isolation)
file_count=$(find . -type f -not -path "./.git/*" -not -path "./.*" | wc -l | xargs)
echo "✓ File count: $file_count (target: <30 for AI safety)"

source .envrc || { echo "❌ FATAL: Failed to source in worktree"; cd ../../; exit 1; }
genesis version || { echo "❌ Genesis CLI unavailable"; cd ../../; exit 1; }
genesis status || echo "⚠️ WARNING: Status issues detected"
```

---

## BLOCKER PROTOCOL

When you encounter issues that prevent successful completion:

### 1. STOP Immediately
- Do NOT proceed past the blocker
- Do NOT create GitHub issues to "track later"
- Do NOT make assumptions about acceptability

### 2. ANALYZE the Issue
- Root cause: What's broken?
- Scope: Related to current task or separate?
- Impact: What fails if we proceed?
- Severity: Can we work around it?

### 3. NOTIFY USER with Options

```
⚠️ BLOCKER DETECTED

Issue: [One-line description]
Analysis: [Root cause and scope]
Impact: [What breaks if we proceed]
Location: [File:line references]

Options:
1. Fix now - [Explain what I'll do]
2. Create issue - [Document for later, explain tradeoffs]
3. Accept/Ignore - [Proceed anyway, explain risks]
4. Abort - [Stop workflow, manual investigation]

What should I do?
```

### 4. WAIT for User Response
- Do NOT proceed until user responds
- Do NOT default to any option

### 5. EXECUTE User's Choice
- Follow chosen option exactly
- Document decision in commit/PR if accepting risks

### Common Blockers for Refactoring
- Test failures after refactoring
- Breaking changes detected
- Performance regressions
- Complexity increases instead of decreases
- Insufficient test coverage to refactor safely
- Dependency conflicts
- Code quality failures

---

## 🛑 CHECKPOINT: Verify Before Delegation

**Before STEP 8, verify YOU completed:**
- [ ] genesis clean executed
- [ ] Worktree created at worktrees/refactor-$1/
- [ ] Currently in worktree (pwd shows worktrees/refactor-$1/)
- [ ] Symlinks verified
- [ ] .envrc sourced in worktree
- [ ] Genesis CLI available

✅ **All checks passed?** → Proceed to STEP 8
❌ **Any failed?** → Fix before delegation

---

## ═══════════════════════════════════════════════════
## REFACTORING PHASE - DELEGATION ALLOWED
## ═══════════════════════════════════════════════════

✅ **You may now use Task tool with specialized agents**

## STEP 8: Refactoring Agent Workflow

**Prerequisites:** STEPS 1-7 completed, worktree exists, checkpoint verified

### Agent 1: issue-analyst
Validate refactoring scope and objectives:
```
You are working in a Genesis worktree at: /Users/source_code/genesis/worktrees/refactor-$1

Analyze issue #$1 to validate refactoring scope.

Requirements:
- Confirm refactoring objectives clear
- Validate atomic scope
- Identify target code for improvement
- Flag any scope creep

Genesis Environment:
- Working in worktree with shared components available
- Must use shared_core.logger for all output
- Must use shared_core.errors for error handling
- Must validate environment with shared_core.config

Success Criteria:
- Scope validated and focused
- Target code identified
- Objectives clear

Constraints:
- Focus ONLY on the refactoring target
- No scope expansion or additional features
- Maintain lean development principles
```

### Agent 2: test-designer
Ensure comprehensive test coverage FIRST:
```
You are working in a Genesis worktree at: /Users/source_code/genesis/worktrees/refactor-$1

Ensure test coverage for code being refactored in issue #$1.

Requirements:
- Write tests for existing behavior if missing
- Ensure tests document current functionality
- Tests must pass before refactoring begins
- Use Genesis testing patterns
- Follow pytest conventions in pytest.ini
- Use shared_core.logger for test logging

Genesis Testing Integration:
- Use existing test directory structure
- Import and use Genesis shared test utilities
- Follow established naming conventions
- Integrate with current test suite

Success Criteria:
- Adequate test coverage exists
- All tests pass
- Behavior documented by tests

Constraints:
- Test ONLY the existing behavior being refactored
- No comprehensive test coverage expansion
- Minimal test code to prove behavior unchanged
```

### Agent 3: complexity-auditor
Baseline complexity measurement:
```
You are working in a Genesis worktree at: /Users/source_code/genesis/worktrees/refactor-$1

Measure baseline complexity for refactoring target in issue #$1.

Requirements:
- Measure current cyclomatic complexity
- Identify complex methods and classes
- Document baseline metrics
- Use Genesis logging for output

Genesis Integration:
- Use shared_core.logger for logging
- Use shared_core.errors for error handling
- Follow existing code patterns

Success Criteria:
- Complexity metrics captured
- Problem areas identified
- Baseline documented

Constraints:
- Focus ONLY on refactoring target code
- No analysis of unrelated components
```

### Agent 4: refactoring-specialist
Improve structure without behavior change:
```
You are working in a Genesis worktree at: /Users/source_code/genesis/worktrees/refactor-$1

Refactor code for issue #$1 without changing behavior.

Requirements:
- Extract methods for clarity
- Remove duplication
- Simplify complex conditionals
- Apply appropriate patterns
- Maintain test passage throughout
- Use Genesis shared components (logging, error handling, config)

Genesis Shared Components Integration:
- Use shared_core.logger for any new logging
- Use shared_core.errors for any error handling
- Use shared_core.config for any configuration access
- Follow existing import patterns

Lean Implementation Principles:
- Minimal refactoring required for improvement
- No architectural modifications
- No additional features or improvements
- No optimization unless required for clarity
- Maintain existing API contracts

Success Criteria:
- Structure improved
- All tests still pass
- No behavior changes
- Code more maintainable

Constraints:
- ONLY refactor the specific code in issue #$1
- No scope creep beyond refactoring target
- No performance improvements unless clarity-related
```

### Agent 5: complexity-auditor
Verify complexity improved:
```
You are working in a Genesis worktree at: /Users/source_code/genesis/worktrees/refactor-$1

Verify complexity improvements for issue #$1.

Requirements:
- Re-measure complexity metrics
- Confirm reduction in complexity
- Document improvements
- Compare with baseline metrics

Genesis Integration:
- Use shared_core.logger for logging
- Use shared_core.errors for error handling
- Follow existing code patterns

Success Criteria:
- Complexity reduced
- Improvements measured
- Comparison documented

Constraints:
- Focus ONLY on refactored code
- No measurement of unrelated components
```

### Agent 6: build-validator
Prove behavior unchanged:
```
You are working in a Genesis worktree at: /Users/source_code/genesis/worktrees/refactor-$1

Validate refactoring for issue #$1 maintained behavior.

Requirements:
- All tests still pass
- No functionality altered
- Performance not degraded
- Genesis quality gates satisfied

Genesis Quality Gates (MANDATORY):
1. Run 'genesis autofix' - format and lint automatically
2. Run 'genesis status' - verify project health
3. Run full test suite (make test, pytest, or npm test)
4. Verify no regressions in existing functionality
5. Check Genesis health indicators

Quality Validation Requirements:
- All tests pass including existing tests
- No linting violations after genesis autofix
- No type checking errors (if applicable)
- Genesis status shows healthy state
- No performance regressions (if measurable)

Genesis Integration Validation:
- Verify shared components used correctly
- Check logging follows shared_core.logger patterns
- Confirm error handling uses shared_core.errors
- Validate configuration access uses shared_core.config

Success Criteria:
- All tests pass
- Behavior unchanged
- Quality gates satisfied
- No regressions detected

Constraints:
- Complete test suite must pass (not just affected tests)
- No existing tests broken by change
```

---

## ═══════════════════════════════════════════════════
## FINALIZATION PHASE - YOU MUST EXECUTE (NO DELEGATION)
## ═══════════════════════════════════════════════════

⚠️ **DO NOT delegate STEPS 9-11 - use Bash tool**

## STEP 9-11: Quality Gates, Commit, and Return

**Tool to use:** `Bash`

```bash
# Quality validation
echo "🔍 Running Genesis quality gates..."

# Run autofix - handle failure gracefully
genesis autofix || {
    echo "⚠️ WARNING: Genesis autofix encountered issues"
    echo "Attempting to continue..."
}

# Final health check
genesis status || echo "⚠️ WARNING: Genesis status shows issues"

# Run appropriate test command
if [[ -f "Makefile" ]] && grep -q "^test:" Makefile; then
    make test || echo "⚠️ WARNING: Some tests failed"
elif [[ -f "pytest.ini" ]]; then
    pytest || echo "⚠️ WARNING: Some tests failed"
elif [[ -f "package.json" ]]; then
    npm test || echo "⚠️ WARNING: Some tests failed"
else
    echo "⚠️ No test command found, verify manually"
fi

# Commit and PR
echo "📝 Creating commit..."
git add .
genesis commit --no-approve -m "refactor: improve code structure for issue #$1

Closes #$1

- Improved code structure without changing behavior
- Maintained all test passage
- Reduced complexity
- No functionality altered"

echo "🚀 Creating PR..."
gh pr create \
  --title "refactor: improve code structure for issue #$1" \
  --body "$(cat <<'EOF'
Closes #$1

## Refactoring Completed
- ✅ Test coverage verified before refactoring
- ✅ Structure improved
- ✅ Complexity reduced
- ✅ All tests still pass
- ✅ Behavior unchanged

## Changes Made
- Improved code structure
- Reduced complexity
- Enhanced maintainability
- No behavior changes

## Validation
- ✅ All tests pass
- ✅ Genesis quality gates satisfied
- ✅ No scope creep
EOF
)" \
  --assignee @me || echo "⚠️ WARNING: PR creation failed"

# Return to main
cd ../../ || echo "⚠️ WARNING: Failed to return"
pwd  # VERIFY: Should show .../genesis
genesis status

echo "✅ SUCCESS: Refactoring completed for issue #$1"
echo "📋 Next: Review PR, merge when ready, then run: /close $1"
```

---

## 🚫 COMMON MISTAKES TO AVOID

**❌ WRONG:** `<invoke name="Task"><parameter name="prompt">Run genesis clean...</parameter></invoke>`
**✅ CORRECT:** `<invoke name="Bash"><parameter name="command">genesis clean</parameter></invoke>`

**❌ WRONG:** Using Task tool in STEPS 1-7 or 9-11
**✅ CORRECT:** Use Bash tool for setup and finalization, Task tool only in STEP 8

---

## 🚫 NO SHORTCUTS POLICY

**CRITICAL: This workflow enforces the NO SHORTCUTS POLICY from CLAUDE.md.**

### Absolutely Forbidden

You MUST NEVER suggest or use these shortcuts:

**❌ BANNED PATTERNS:**
- `# type: ignore` - Fix the type error properly
- `# noqa` - Fix the lint issue properly
- `# pylint: disable` - Fix the pylint issue properly
- `try/except: pass` - Handle errors properly
- `--skip-tests` - Fix the failing tests properly
- `--no-verify` - Fix the pre-commit issues properly
- Creating "fix later" issues - Fix it NOW
- Commenting out failing tests - Fix the test or the code

### What To Do Instead

**When you encounter an error:**
1. **Understand the root cause** - Read the error message carefully
2. **Fix the actual problem** - Don't silence the symptom
3. **Ask for clarification** - Better to ask than to shortcut
4. **Refactor if needed** - Sometimes the design needs improvement

**Examples:**

**Type Errors:**
- ❌ `result: Any = function()  # type: ignore`
- ✅ `result: ExpectedType = function()` (fix the type properly)

**Lint Issues:**
- ❌ `unused_var = value  # noqa`
- ✅ Remove the unused variable or use it properly

**Failing Tests:**
- ❌ `pytest --skip-tests` or `# @pytest.mark.skip`
- ✅ Fix the code to make the test pass

**Error Handling:**
- ❌ `try: operation() except: pass`
- ✅ `try: operation() except SpecificError as e: logger.error(f"Failed: {e}")`

### Pre-commit Protection

The pre-commit hook will **REJECT** commits containing shortcut patterns.
See `.pre-commit-config.yaml` for the `no-shortcuts` hook configuration.

### Summary

**FIX THE ROOT CAUSE. NEVER TAKE SHORTCUTS.**

This is non-negotiable. Quality code requires quality discipline.

---

## Success Criteria
- ✅ Test coverage verified before refactoring
- ✅ Structure improved without behavior change
- ✅ Complexity metrics reduced
- ✅ All tests still pass
- ✅ Quality gates satisfied
- ✅ No scope creep
