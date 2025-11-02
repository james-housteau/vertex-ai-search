---
allowed-tools: Task, Bash, Read, Write, Edit, Grep, Glob
argument-hint: "[issue-number]"
description: "Optimize performance based on measured bottlenecks"
model: claude-sonnet-4-20250514
---

# Optimization Workflow for Issue #$1

Improve performance based on measured bottlenecks using Genesis and specialized agents.

---

# ⚠️ CRITICAL: EXECUTION vs DELEGATION ⚠️

**📍 SETUP PHASE (STEPS 1-7): YOU EXECUTE DIRECTLY**
- ⚠️ DO NOT use Task tool - use Bash tool
- ⚠️ YOU must run commands yourself

**🤖 OPTIMIZATION PHASE (STEP 8): DELEGATION ALLOWED**
- ✅ NOW use Task tool with specialized agents

**📍 FINALIZATION PHASE (STEPS 9-11): YOU EXECUTE DIRECTLY**
- ⚠️ DO NOT delegate commits/PRs
- ⚠️ YOU must run commands with Bash tool

---

## CONTEXT: Pure Module Isolation

This workflow creates a Genesis worktree with all supporting files needed for pure module isolation.

---

## ═══════════════════════════════════════════════════
## SETUP PHASE - YOU MUST EXECUTE (NO DELEGATION)
## ═══════════════════════════════════════════════════

⚠️ **DO NOT use Task tool for STEPS 1-7 - use Bash tool**

## STEP 1-7: Standard Genesis Worktree Setup

**Tool to use:** `Bash`

```bash
genesis status || echo "⚠️ WARNING: Genesis health issues"
source .envrc || { echo "❌ FATAL: Failed to source .envrc"; exit 1; }
gh issue view $1 || exit 1
genesis clean || echo "⚠️ WARNING: Clean encountered issues"

genesis worktree create optimize-$1 \
  --focus genesis/ \
  --max-files ${WORKTREE_MAX_FILES:-30}

cd worktrees/optimize-$1/ || { echo "❌ FATAL: Failed to navigate"; exit 1; }
pwd  # VERIFY: Must show .../genesis/worktrees/optimize-$1

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

### Common Blockers for Optimization
- Performance improvements break functionality
- Test failures after optimization
- Optimization increases code complexity unacceptably
- Cannot reliably measure performance improvements
- Optimization causes correctness issues
- Breaking changes to existing APIs
- Code quality failures (complexity metrics worse)

---

## 🛑 CHECKPOINT: Verify Before Delegation

**Before STEP 8:**
- [ ] Worktree created at worktrees/optimize-$1/
- [ ] Currently in worktree
- [ ] Symlinks verified
- [ ] Genesis CLI available

✅ **All checks passed?** → Proceed to STEP 8

---

## ═══════════════════════════════════════════════════
## OPTIMIZATION PHASE - DELEGATION ALLOWED
## ═══════════════════════════════════════════════════

✅ **You may now use Task tool with specialized agents**

## STEP 8: Optimization Agent Workflow

**IMPORTANT PREREQUISITES:**
- You have completed STEPS 1-7 yourself (setup phase)
- Worktree exists at `worktrees/optimize-$1/`
- You have verified the checkpoint criteria above
- You are ready to delegate the optimization work

**How to delegate optimization:**

You can either use a single agent for the complete optimization workflow, or use specialized agents for each phase.

### Option A: Single Agent for Complete Optimization Workflow

Use the lean-implementer agent for the entire optimization workflow:

```
Use Task tool with lean-implementer agent:

You are working in a Genesis worktree at: /Users/source_code/genesis/worktrees/optimize-$1

Optimize performance for issue #$1 based on measured bottlenecks:

**Context:**
- Pure module isolation worktree already created
- Environment already configured
- Genesis CLI available

**Optimization Workflow:**
1. Validate optimization scope and performance targets
2. Establish baseline performance metrics
3. Profile and identify bottlenecks
4. Implement minimal optimizations for measured bottlenecks
5. Verify performance improvements achieved

**Genesis Integration:**
- Use shared_core.logger for logging
- Use shared_core.errors for error handling
- Follow existing code patterns

**Success Criteria:**
- Performance measured before and after
- Optimization targets met
- All tests still pass
- No unnecessary complexity added

Run tests frequently to verify progress.
```

### Option B: Phased Agents for Detailed Optimization Workflow

Or use specialized agents for each phase:

#### Agent 1: Issue Analysis and Validation

Use the issue-analyst agent to validate optimization scope:

```
Analyze GitHub issue #$1 to validate optimization scope and specific performance targets.

Requirements:
- Verify issue describes specific performance problem
- Confirm performance targets are measurable
- Validate scope is focused on measured bottlenecks
- Extract baseline performance expectations
- Flag any scope creep or premature optimization

Genesis Environment:
- Working in worktree with shared components available
- Must use shared_core.logger for all output
- Must use shared_core.errors for error handling
- Must validate environment with shared_core.config

Success Criteria:
- Issue confirmed as performance optimization request
- Performance targets clearly identified
- Scope validated as minimal and focused
- Baseline expectations established

Constraints:
- Focus ONLY on measured bottlenecks
- No premature optimization
- Maintain lean development principles
```

#### Agent 2: Baseline Performance Measurement

Use the performance-monitor agent to establish baseline metrics:

```
Establish baseline performance metrics for optimization issue #$1.

Requirements:
- Measure current performance with profiling tools
- Profile execution time for bottleneck areas
- Identify specific performance bottlenecks
- Document baseline numbers with precision
- Create reproducible measurement methodology

Genesis Performance Integration:
- Use shared_core.logger for performance logging
- Document measurements in structured format
- Follow established profiling patterns
- Integrate with current monitoring approach

Performance Criteria:
- Baseline metrics captured accurately
- Bottlenecks clearly identified
- Measurements are reproducible
- Documentation is clear and precise

Lean Principles:
- Measure ONLY what's needed for this optimization
- No comprehensive performance audit
- Focus on specific bottleneck areas
- Minimal overhead for measurement
```

#### Agent 3: Baseline Complexity Measurement

Use the complexity-auditor agent for baseline complexity measurement:

```
Document baseline complexity metrics to ensure optimization won't increase complexity.

Requirements:
- Measure current code complexity metrics
- Document cognitive complexity of affected code
- Establish complexity baseline for comparison
- Identify complexity hotspots in optimization area
- Create reproducible complexity measurement

Genesis Complexity Integration:
- Use shared_core.logger for complexity logging
- Follow established complexity measurement patterns
- Document metrics in structured format
- Integrate with Genesis quality standards

Complexity Criteria:
- Baseline complexity documented
- Metrics are objective and measurable
- Can detect complexity increases
- Clear threshold for acceptable changes

Constraints:
- Focus ONLY on code affected by optimization
- No comprehensive complexity audit
- Minimal overhead for measurement
- Simple, clear metrics only
```

#### Agent 4: Minimal Optimization Implementation

Use the lean-implementer agent to implement optimizations:

```
Implement minimal optimizations for issue #$1 targeting only measured bottlenecks.

Requirements:
- Target ONLY measured performance bottlenecks
- Apply minimal changes for maximum performance impact
- Avoid premature or speculative optimization
- Keep changes focused and minimal
- No refactoring or improvements 'while we're here'

Genesis Shared Components Integration:
- Use shared_core.logger for any new logging
- Use shared_core.errors for any error handling
- Use shared_core.config for any configuration access
- Follow existing import patterns

Lean Implementation Principles:
- Absolute minimal code change required
- No architectural modifications
- No refactoring of surrounding code
- No additional features or improvements
- Only optimize measured bottlenecks

Constraints:
- ONLY optimize the specific bottlenecks identified
- No scope creep beyond exact optimization targets
- No code style improvements unless required
- No additional optimizations beyond measured needs
- Maintain existing API contracts

Success Criteria:
- Performance targets met
- Changes are minimal and focused
- No unrelated functionality affected
- All existing tests continue to pass
```

#### Agent 5: Performance Improvement Validation

Use the performance-monitor agent to verify improvements:

```
Verify performance improvements achieved for optimization issue #$1.

Requirements:
- Re-measure performance using same methodology as baseline
- Confirm improvement targets achieved
- Document performance gains with precision
- Compare before/after metrics objectively
- Validate improvements are consistent

Genesis Performance Validation:
- Use shared_core.logger for validation logging
- Document comparison in structured format
- Follow established validation patterns
- Integrate with Genesis quality standards

Performance Validation Criteria:
- Performance targets met or exceeded
- Measurements use identical methodology
- Improvements are reproducible
- No performance regressions in other areas

Success Criteria:
- Clear improvement demonstrated
- Targets achieved as specified
- No unintended side effects
- Performance gains are stable
```

#### Agent 6: Complexity Validation

Use the complexity-auditor agent to ensure complexity not increased:

```
Ensure optimization for issue #$1 did not increase code complexity.

Requirements:
- Re-measure complexity using same methodology as baseline
- Compare before/after complexity metrics
- Verify no over-engineering introduced
- Validate optimization maintains or reduces complexity
- Flag any complexity increases

Genesis Complexity Validation:
- Use shared_core.logger for validation logging
- Document comparison in structured format
- Follow Genesis complexity standards
- Validate lean principles maintained

Complexity Validation Criteria:
- Complexity not increased
- Measurements use identical methodology
- No over-engineering detected
- Code remains simple and maintainable

Success Criteria:
- Complexity baseline maintained or improved
- No unnecessary abstractions added
- Code remains clear and simple
- Lean principles followed
```

#### Agent 7: Quality Gates and Regression Testing

Use the build-validator agent to validate improvements:

```
Run complete quality validation for performance optimization #$1 using Genesis quality pipeline.

Genesis Quality Gates (MANDATORY):
1. Run 'genesis autofix' - format and lint automatically
2. Run 'genesis status' - verify project health
3. Run full test suite (make test, pytest, or npm test)
4. Verify no regressions in existing functionality
5. Confirm performance targets met
6. Check Genesis health indicators

Quality Validation Requirements:
- All tests pass without regressions
- No linting violations after genesis autofix
- No type checking errors (if applicable)
- Genesis status shows healthy state
- Performance improvements verified

Genesis Integration Validation:
- Verify shared components used correctly
- Check logging follows shared_core.logger patterns
- Confirm error handling uses shared_core.errors
- Validate configuration access uses shared_core.config

Test Suite Validation:
- Full test suite passes (not just affected tests)
- No existing tests broken by changes
- Performance improvements are stable
- Test coverage maintained

Success Criteria:
- Complete test suite passes
- All Genesis quality gates satisfied
- No regressions detected in any area
- Performance targets achieved
- Code meets Genesis quality standards
```

---

## ═══════════════════════════════════════════════════
## FINALIZATION PHASE - YOU MUST EXECUTE (NO DELEGATION)
## ═══════════════════════════════════════════════════

⚠️ **DO NOT delegate STEPS 9-11 - use Bash tool**

## STEP 9-11: Quality Gates, Commit, and Return

**Tool to use:** `Bash`

```bash
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

git add .
genesis commit --no-approve -m "perf: optimize performance for issue #$1

Closes #$1

- Optimized based on measured bottlenecks
- Performance targets met
- No functionality altered
- All tests pass"

gh pr create \
  --title "perf: optimize performance for issue #$1" \
  --body "Performance optimization based on measured bottlenecks per issue #$1" \
  --assignee @me || echo "⚠️ WARNING: PR creation failed"

cd ../../ || echo "⚠️ WARNING: Failed to return"
pwd  # VERIFY: Should show .../genesis
genesis status

echo "✅ SUCCESS: Optimization completed for issue #$1"
```

---

## 🚫 COMMON MISTAKES TO AVOID

**❌ WRONG:** Delegating setup to agents
**✅ CORRECT:** Execute STEPS 1-7 with Bash tool, THEN use Task tool in STEP 8

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
- ✅ Performance measured before and after
- ✅ Optimization targets met
- ✅ All tests still pass
- ✅ No unnecessary complexity added
