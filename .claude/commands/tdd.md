---
allowed-tools: Task, Bash, Read, Write, Edit, Grep, Glob
argument-hint: [issue-number]
description: Resolve GitHub issue using TDD workflow
model: claude-sonnet-4-20250514
---

# TDD Resolution Workflow for Issue #$1

Resolve issue using strict Test-Driven Development with Genesis integration and lean principles.

---

# ⚠️ CRITICAL: EXECUTION vs DELEGATION ⚠️

This workflow has THREE phases with DIFFERENT execution modes:

**📍 SETUP PHASE (STEPS 1-7): YOU EXECUTE DIRECTLY**
- ⚠️ DO NOT use Task tool for these steps
- ⚠️ YOU must run bash commands yourself using the Bash tool
- ⚠️ Verify each step completes before proceeding

**🤖 TDD PHASE (STEP 8): DELEGATION ALLOWED**
- ✅ NOW you can use Task tool with specialized agents
- ✅ Agents work in the worktree YOU created above

**📍 FINALIZATION PHASE (STEPS 9-11): YOU EXECUTE DIRECTLY**
- ⚠️ DO NOT delegate commits/PRs to agents
- ⚠️ YOU must run bash commands yourself using the Bash tool
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

⚠️ **DO NOT use Task tool for STEPS 1-7**
⚠️ **YOU must run these bash commands directly using the Bash tool**

## STEP 1: Environment and Health Validation

**Tool to use:** `Bash`

```bash
genesis status || echo "⚠️ WARNING: Genesis project health issues detected"
source .envrc || {
    echo "❌ FATAL: Failed to source .envrc"
    exit 1
}

if ! gh issue view $1 2>/dev/null; then
    echo "❌ ERROR: Issue #$1 not found or not accessible"
    exit 1
fi
```

## STEP 2: Clean Workspace

**Tool to use:** `Bash`

```bash
genesis clean || echo "⚠️ WARNING: Genesis clean encountered issues"
```

## STEP 3: Create Genesis Worktree

**Tool to use:** `Bash`

```bash
genesis worktree create tdd-$1 \
  --focus genesis/ \
  --max-files ${WORKTREE_MAX_FILES:-30}
```

## STEP 4: Navigate to Worktree

**Tool to use:** `Bash`

```bash
cd worktrees/tdd-$1/ || {
    echo "❌ FATAL: Failed to navigate to worktree"
    exit 1
}
pwd  # VERIFY: Must show .../genesis/worktrees/tdd-$1
```

## STEP 5: Verify Pure Module Isolation Setup

**Tool to use:** `Bash`

```bash
echo "Verifying Pure Module Isolation setup..."
for symlink in shared-python .genesis .venv docs; do
    if [[ ! -L "$symlink" ]]; then
        echo "⚠️ WARNING: Symlink missing: $symlink"
    else
        echo "✓ Symlink present: $symlink -> $(readlink $symlink)"
    fi
done

for file in Makefile pyproject.toml pytest.ini .envrc; do
    if [[ ! -f "$file" ]]; then
        echo "⚠️ WARNING: Shared file missing: $file"
    else
        echo "✓ Shared file present: $file"
    fi
done

file_count=$(find . -type f -not -path "./.git/*" -not -path "./.*" | wc -l | xargs)
echo "✓ File count: $file_count (target: <30 for AI safety)"
```

## STEP 6: Source Genesis Environment

**Tool to use:** `Bash`

```bash
source .envrc || {
    echo "❌ FATAL: Failed to source .envrc in worktree"
    cd ../../
    exit 1
}

genesis version || {
    echo "❌ CRITICAL ERROR: Genesis CLI not available in worktree"
    cd ../../
    exit 1
}
```

## STEP 7: Genesis Project Health Check

**Tool to use:** `Bash`

```bash
genesis status || echo "⚠️ WARNING: Genesis project health issues detected"
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

### Common Blockers for TDD Workflow
- RED phase: Cannot write meaningful failing tests
- GREEN phase: Tests pass but implementation is incorrect
- Test failures (existing or new tests)
- Code quality failures (linting, typing)
- Missing dependencies or test infrastructure
- Unclear requirements preventing test design
- Breaking changes to existing APIs

---

## 🛑 CHECKPOINT: Verify Before Delegation

**Before proceeding to STEP 8 (TDD Phase), verify YOU have completed:**

**Environment Setup:**
- [ ] Verified: `pwd` shows `.../genesis` (main repo)
- [ ] Executed: `source .envrc` successfully
- [ ] Executed: `genesis status` completed
- [ ] Executed: `genesis clean` completed

**Worktree Creation:**
- [ ] Executed: `genesis worktree create tdd-$1` successfully
- [ ] Executed: `cd worktrees/tdd-$1/` successfully
- [ ] Verified: `pwd` shows `.../genesis/worktrees/tdd-$1`
- [ ] Verified: Pure Module Isolation setup complete
- [ ] Executed: `source .envrc` in worktree successfully

**Current State:**
- [ ] You are currently in the worktree directory (not main repo)
- [ ] Genesis CLI is available in worktree
- [ ] Virtual environment is activated

✅ **All checks passed?** → Proceed to STEP 8 and use Task tool
❌ **Any checks failed?** → Fix the issue before delegation

---

## ═══════════════════════════════════════════════════
## TDD PHASE - DELEGATION ALLOWED
## ═══════════════════════════════════════════════════

✅ **You may now use Task tool with specialized agents**
✅ **Agents will work in the worktree you created above**

## STEP 8: TDD Agent Workflow (RED-GREEN-REFACTOR)

**IMPORTANT PREREQUISITES:**
- You have completed STEPS 1-7 yourself (setup phase)
- Worktree exists at `worktrees/tdd-$1/`
- You have verified the checkpoint criteria above
- You are ready to delegate the TDD workflow

### Option A: Single Agent for Complete TDD Workflow

Use lean-implementer for full RED-GREEN-REFACTOR cycle:

```
Use Task tool with lean-implementer agent:

You are working in a Genesis worktree at: /Users/source_code/genesis/worktrees/tdd-$1

Implement solution for issue #$1 using strict TDD (RED-GREEN-REFACTOR):

**Context:**
- Pure module isolation worktree already created
- Environment already configured
- Genesis CLI available

**RED Phase:**
- Analyze issue requirements
- Write minimal failing tests
- Tests define expected behavior
- Verify tests fail for right reason

**GREEN Phase:**
- Implement simplest code to pass tests
- Use Genesis shared components
- No over-engineering
- Direct solutions only

**REFACTOR Phase:**
- Improve code quality
- Eliminate duplication
- Maintain test passage
- Follow Genesis patterns

**Success Criteria:**
- All tests pass
- Code is clean and simple
- No scope creep
- Ready for quality gates
```

### Option B: Phased Agents for Detailed TDD Workflow

Or use specialized agents for each TDD phase:

#### Agent 1: Issue Analysis

Use issue-analyst agent:

```
Analyze GitHub issue #$1 to ensure atomic scope and clear requirements.

Requirements:
- Verify single, atomic issue
- Extract clear acceptance criteria
- Identify core functionality
- Flag any scope creep

Success Criteria:
- Issue scope validated
- Requirements clear
- Implementation approach identified
```

#### Agent 2: RED Phase - Write Failing Tests

Use test-designer agent:

```
Write minimal failing tests for issue #$1 following TDD RED phase.

Requirements:
- Write tests that define expected behavior
- Tests must currently FAIL
- Focus on critical path only
- Use Genesis testing patterns
- Minimal test code

Success Criteria:
- Tests written and failing appropriately
- Tests clearly define expected behavior
- Critical path covered
```

#### Agent 3: GREEN Phase - Minimal Implementation

Use lean-implementer agent:

```
Implement minimal code to make tests pass for issue #$1.

Requirements:
- Simplest possible implementation
- Use Genesis shared components
- No over-engineering
- Direct solutions only

Success Criteria:
- All tests now pass
- Implementation is minimal
- No unnecessary complexity
```

#### Agent 4: REFACTOR Phase - Improve Quality

Use refactoring-specialist agent:

```
Improve code quality while maintaining test passage for issue #$1.

Requirements:
- Eliminate duplication
- Improve readability
- Follow Genesis patterns
- All tests must pass

Success Criteria:
- Code is clean and maintainable
- Tests continue passing
- Genesis standards followed
```

#### Agent 5: Validation

Use scope-guardian and build-validator agents:

```
Validate solution meets requirements with no scope creep.

Validation:
- Run genesis autofix
- Run full test suite
- Verify no scope creep
- Check Genesis quality standards

Success Criteria:
- All tests pass
- No scope creep
- Quality gates satisfied
```

---

## ═══════════════════════════════════════════════════
## FINALIZATION PHASE - YOU MUST EXECUTE (NO DELEGATION)
## ═══════════════════════════════════════════════════

⚠️ **DO NOT delegate STEPS 9-11 to agents**
⚠️ **YOU must run these commands directly using the Bash tool**

## STEP 9: Genesis Quality Gates

**Tool to use:** `Bash`

```bash
echo "🔍 Running Genesis quality gates..."

genesis autofix || {
    echo "⚠️ WARNING: Genesis autofix encountered issues"
    echo "Attempting to continue..."
}

genesis status || echo "⚠️ WARNING: Genesis status shows issues"

if [[ -f "Makefile" ]] && grep -q "^test:" Makefile; then
    make test || echo "⚠️ WARNING: Some tests failed"
elif [[ -f "pytest.ini" ]]; then
    pytest || echo "⚠️ WARNING: Some tests failed"
elif [[ -f "package.json" ]]; then
    npm test || echo "⚠️ WARNING: Some tests failed"
else
    echo "ℹ️ No test command found, verify manually"
fi
```

## STEP 10: Genesis Commit and PR Creation

**Tool to use:** `Bash`

```bash
echo "📝 Creating Genesis commit..."

git add .
genesis commit --no-approve -m "feat: resolve issue #$1 using TDD

Closes #$1

- Implemented using strict TDD methodology (RED-GREEN-REFACTOR)
- Created tests defining expected behavior
- Applied minimal implementation
- Refactored for quality
- No scope creep"

echo "🚀 Creating PR..."
gh pr create \
  --title "feat: resolve issue #$1 using TDD" \
  --body "$(cat <<'EOF'
Closes #$1

## TDD Workflow Completed
- ✅ RED: Tests written and failing
- ✅ GREEN: Minimal implementation passes tests
- ✅ REFACTOR: Code quality improved
- ✅ Genesis quality gates passed

## Changes Made
- Created tests defining expected behavior
- Implemented minimal solution
- Refactored for maintainability
- All existing tests continue to pass

## Testing
- ✅ All tests passing
- ✅ Genesis health checks pass
- ✅ No scope creep detected
EOF
)" \
  --assignee @me || {
    echo "⚠️ WARNING: PR creation failed - you may need to create manually"
}
```

## STEP 11: Return to Main Repository

**Tool to use:** `Bash`

```bash
cd ../../ || {
    echo "⚠️ WARNING: Failed to return to main directory"
    echo "Current directory: $(pwd)"
}
pwd  # VERIFY: Must show .../genesis (main repo root)

genesis status

echo "✅ SUCCESS: TDD workflow completed for issue #$1"
echo "📋 Next: Review PR, merge when ready, then run: /close $1"
```

---

## 🚫 COMMON MISTAKES TO AVOID

**❌ WRONG - Delegating setup:**
```
<invoke name="Task">
  <parameter name="prompt">Run genesis clean and create worktree...</parameter>
</invoke>
```

**✅ CORRECT - Executing setup yourself:**
```
<invoke name="Bash">
  <parameter name="command">genesis clean</parameter>
</invoke>
<invoke name="Bash">
  <parameter name="command">genesis worktree create tdd-$1</parameter>
</invoke>
```

**❌ WRONG - Using Task tool before worktree exists**
**✅ CORRECT - Complete STEPS 1-7, verify checkpoint, THEN use Task tool**

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
- ✅ RED: Tests written and failing
- ✅ GREEN: Implementation passes tests
- ✅ REFACTOR: Code quality improved
- ✅ All Genesis quality gates pass
- ✅ PR created and ready for review
- ✅ No scope creep
