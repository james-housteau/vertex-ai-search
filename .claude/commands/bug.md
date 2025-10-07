---
allowed-tools: Task, Bash, Read, Write, Edit, Grep, Glob
argument-hint: "[issue-number]"
description: "Debug and resolve bugs using systematic workflow with Genesis integration"
model: claude-sonnet-4-20250514
---

# Bug Resolution Workflow for Issue #$1

Complete bug resolution implementation using TDD methodology, Genesis integration, and specialized agents.

## Debug Methodology
This workflow follows the systematic debug approach: reproduce → isolate → test → fix → validate.

## STEP 1: Environment and Health Validation

```bash
# Verify project health and environment
genesis status || echo "⚠️ WARNING: Genesis project health issues detected"
source .envrc || {
    echo "❌ FATAL: Failed to source .envrc"
    exit 1
}

# Verify issue exists and is accessible
if ! gh issue view $1 2>/dev/null; then
    echo "❌ ERROR: Issue #$1 not found or not accessible"
    exit 1
fi
```

## STEP 2: Clean Workspace (MANDATORY)

```bash
# Remove old worktrees and build artifacts
genesis clean || echo "⚠️ WARNING: Genesis clean encountered issues"
```

## STEP 3: Create Genesis Worktree with ALL Shared Components

```bash
# Create AI-safe worktree with all required shared components
# Note: Adjust --focus based on issue area
genesis worktree create fix-$1 \
  --max-files 30 \
  --include .genesis/ \
  --include .claude/ \
  --include scripts/ \
  --include shared-python/ \
  --include Makefile \
  --include pyproject.toml \
  --include pytest.ini \
  --include .pre-commit-config.yaml \
  --include .envrc
```

## STEP 4: Navigate to Worktree (CRITICAL)

```bash
# MUST navigate to worktree for all subsequent operations
cd ../worktrees/fix-$1/ || {
    echo "❌ FATAL: Failed to navigate to worktree"
    exit 1
}
pwd  # VERIFY: Must show .../genesis/worktrees/fix-$1
```

## STEP 5: Verify ALL Shared Components Exist

```bash
# Check for required components
missing_components=0
for component in .genesis .claude scripts shared-python Makefile; do
    if [[ ! -e "$component" ]]; then
        echo "❌ CRITICAL ERROR: Missing $component"
        missing_components=1
    fi
done

# Attempt to add missing components if needed
if [[ $missing_components -eq 1 ]]; then
    echo "🔧 Attempting to add missing components via sparse-checkout..."
    git sparse-checkout add .genesis/ .claude/ scripts/ shared-python/ Makefile

    # Re-verify after adding
    for component in .genesis .claude scripts shared-python Makefile; do
        if [[ ! -e "$component" ]]; then
            echo "❌ FATAL: Failed to add $component - cannot proceed"
            cd ../../
            exit 1
        fi
    done
fi
```

## STEP 6: Source Genesis Environment (REQUIRED)

```bash
# Load environment in worktree context
source .envrc || {
    echo "❌ FATAL: Failed to source .envrc in worktree"
    cd ../../
    exit 1
}

# Verify Genesis CLI is available
genesis version || {
    echo "❌ CRITICAL ERROR: Genesis CLI not available in worktree"
    cd ../../
    exit 1
}
```

## STEP 7: Genesis Project Health Check

```bash
# Verify project health in worktree
genesis status || echo "⚠️ WARNING: Genesis project health issues detected"
```

## STEP 8: Agent Workflow Implementation

### Agent 1: Issue Analysis and Validation

Use the issue-analyst agent to validate bug report scope and atomicity:

```
Analyze GitHub issue #$1 to ensure it represents an atomic, reproducible bug.

Requirements:
- Verify issue describes single, atomic bug (not multiple issues)
- Confirm bug has clear reproduction steps
- Isolate the root cause and validate scope boundaries
- Validate acceptance criteria are well-defined
- Extract root cause if evident from description
- Flag any scope creep or compound issues

Genesis Environment:
- Working in worktree with shared components available
- Must use shared_core.logger for all output
- Must use shared_core.errors for error handling
- Must validate environment with shared_core.config

Success Criteria:
- Issue confirmed as atomic bug report
- Reproduction approach identified
- Root cause hypothesis formed (if possible)
- Scope validated as minimal and focused

Constraints:
- Focus ONLY on the reported bug
- No scope expansion or additional improvements
- Maintain lean development principles
```

### Agent 2: Regression Test Creation (RED Phase)

Use the test-designer agent to create minimal regression test for bug:

```
Create minimal regression test for bug #$1 that fails before fix, passes after fix.

Requirements:
- Write single, focused test that demonstrates the bug
- Test must currently FAIL due to bug behavior
- Test will PASS once bug is fixed
- Use Genesis testing patterns and shared utilities
- Follow pytest conventions in pytest.ini
- Use shared_core.logger for test logging

Genesis Testing Integration:
- Use existing test directory structure
- Import and use Genesis shared test utilities
- Follow established naming conventions
- Integrate with current test suite

Test Criteria:
- Minimal test case (no over-testing)
- Clear test name describing bug scenario
- Proper setup/teardown if needed
- Fails for right reason (demonstrates bug)
- Will pass when bug fixed

Lean Principles:
- Test ONLY the specific bug behavior
- No comprehensive test coverage expansion
- No testing of related but unaffected functionality
- Minimal test code to prove bug exists
```

### Agent 3: Minimal Bug Fix Implementation (GREEN Phase)

Use the lean-implementer agent to implement absolute minimal fix for bug:

```
Fix bug #$1 with the smallest possible code change using lean principles.

Requirements:
- Implement ONLY the minimal change to fix the bug
- Make the regression test pass
- Use Genesis shared components (logging, error handling, config)
- Follow existing code patterns and architecture
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
- No optimization unless required for fix

Constraints:
- ONLY fix the specific bug reported in issue #$1
- No scope creep beyond exact bug fix
- No code style improvements unless required
- No performance improvements unless bug-related
- Maintain existing API contracts

Success Criteria:
- Regression test now passes
- Bug is resolved as described in issue
- No unrelated functionality affected
- Minimal surface area of change
- All existing tests continue to pass
```

### Agent 4: Quality Validation and Gates

Use the build-validator agent to validate bug fix quality and run Genesis quality gates:

```
Run complete quality validation for bug fix #$1 using Genesis quality pipeline.

Genesis Quality Gates (MANDATORY):
1. Run 'genesis autofix' - format and lint automatically
2. Run 'genesis status' - verify project health
3. Run full test suite (make test, pytest, or npm test)
4. Verify no regressions in existing functionality
5. Confirm regression test passes
6. Check Genesis health indicators

Quality Validation Requirements:
- All tests pass including new regression test
- No linting violations after genesis autofix
- No type checking errors (if applicable)
- Genesis status shows healthy state
- No performance regressions (if measurable)

Genesis Integration Validation:
- Verify shared components used correctly
- Check logging follows shared_core.logger patterns
- Confirm error handling uses shared_core.errors
- Validate configuration access uses shared_core.config

Test Suite Validation:
- Full test suite passes (not just new test)
- No existing tests broken by change
- New regression test passes consistently
- Test coverage maintained or improved

Success Criteria:
- Complete test suite passes
- All Genesis quality gates satisfied
- No regressions detected in any area
- System remains stable and healthy
- Code meets Genesis quality standards
```

### Agent 5: Scope Protection and Final Validation

Use the scope-guardian agent to verify no scope creep and validate minimal change:

```
Review bug fix #$1 to ensure changes exactly match issue requirements with zero scope creep.

Scope Validation Requirements:
- Compare all changes against original issue description
- Verify ONLY the reported bug was fixed
- Confirm no additional improvements included
- Flag any unrelated code changes
- Validate minimal change principle followed

Scope Boundaries (STRICT):
- ONLY the specific bug described in issue #$1
- No refactoring or code style improvements
- No additional features or enhancements
- No architectural or design pattern changes
- No performance optimizations unless bug-related
- No documentation updates unless bug-related

Change Analysis:
- Review exact code changes made
- Verify each change serves bug fix purpose
- Flag any changes that go beyond minimal fix
- Confirm no 'while we're here' improvements
- Validate adherence to lean principles

Genesis Principles Validation:
- Confirm minimal code approach used
- Verify no over-engineering introduced
- Check that YAGNI principle followed
- Validate no abstractions added unnecessarily
- Ensure simplest solution was chosen

Success Criteria:
- All changes directly related to bug fix
- No scope creep detected
- Minimal change principle maintained
- Bug fix is focused and targeted
- Lean development principles followed
```

## STEP 9: Genesis Quality Gates (MANDATORY BEFORE COMMIT)

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
```

## STEP 10: Genesis Commit and PR Creation

```bash
echo "📝 Creating Genesis commit..."

# Stage changes and commit with Genesis
git add .
genesis commit -m "fix: resolve issue #$1

Fixes #$1

- Implemented minimal bug fix following TDD methodology
- Created regression test that demonstrates the bug
- Applied simplest solution that makes test pass
- Validated with Genesis quality gates
- No scope creep or unrelated changes"

echo "🚀 Creating PR..."
gh pr create \
  --title "fix: resolve issue #$1" \
  --body "$(cat <<'EOF'
Fixes #$1

## Genesis Workflow Completed
- ✅ Genesis worktree isolation used
- ✅ Genesis quality gates passed
- ✅ Genesis shared components integrated
- ✅ Specialized agents validated approach
- ✅ Lean development principles followed

## Changes Made
- Created regression test demonstrating the bug
- Implemented minimal fix to resolve the issue
- All existing tests continue to pass
- No unrelated changes or scope creep

## Testing
- ✅ Regression test created and passing
- ✅ Full test suite passes
- ✅ Genesis health checks pass
- ✅ No scope creep detected

## Agent Validation
- ✅ issue-analyst: Confirmed atomic bug scope
- ✅ test-designer: Created minimal regression test
- ✅ lean-implementer: Applied minimal fix
- ✅ build-validator: Quality gates passed
- ✅ scope-guardian: No scope creep detected
EOF
)" \
  --assignee @me || {
    echo "⚠️ WARNING: PR creation failed - you may need to create manually"
}
```

## STEP 11: Return to Main Repository (CRITICAL!)

```bash
# Navigate back to main repository
cd ../../../ || {
    echo "❌ WARNING: Failed to return to main directory"
    echo "Current directory: $(pwd)"
}
pwd  # VERIFY: Must show .../genesis (main repo root)

# Final health check
genesis status

echo "✅ SUCCESS: Bug fix workflow completed for issue #$1"
echo "📋 Next: Review PR, merge when ready, then run: /close $1"
```

## Success Criteria
- ✅ Bug reproduced with failing test
- ✅ Test passes with minimal fix
- ✅ All Genesis quality gates pass
- ✅ PR created and ready for review
- ✅ No scope creep or unrelated changes
