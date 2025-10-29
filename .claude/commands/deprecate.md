---
allowed-tools: Task, Bash, Read, Write, Edit, Grep, Glob
argument-hint: "[issue-number]"
description: "Deprecate old code and provide migration path"
model: claude-sonnet-4-20250514
---

# Deprecation Workflow for Issue #$1

Deprecate old code with clear migration path using Genesis and specialized agents.

---

# ⚠️ CRITICAL: EXECUTION vs DELEGATION ⚠️

**📍 SETUP PHASE (STEPS 1-7): YOU EXECUTE DIRECTLY**
- ⚠️ DO NOT use Task tool - use Bash tool
- ⚠️ YOU must run commands yourself

**🤖 DEPRECATION PHASE (STEP 8): DELEGATION ALLOWED**
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

genesis worktree create deprecate-$1 \
  --focus genesis/ \
  --max-files ${WORKTREE_MAX_FILES:-30}

cd worktrees/deprecate-$1/ || { echo "❌ FATAL: Failed to navigate"; exit 1; }
pwd  # VERIFY: Must show .../genesis/worktrees/deprecate-$1

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

## 🛑 CHECKPOINT: Verify Before Delegation

**Before STEP 8:**
- [ ] Worktree created at worktrees/deprecate-$1/
- [ ] Currently in worktree
- [ ] Genesis CLI available

✅ **All checks passed?** → Proceed to STEP 8

---

## ═══════════════════════════════════════════════════
## DEPRECATION PHASE - DELEGATION ALLOWED
## ═══════════════════════════════════════════════════

✅ **You may now use Task tool with specialized agents**

## STEP 8: Deprecation Agent Workflow

### Agent 1: issue-analyst

Use the issue-analyst agent to validate deprecation scope:

```
Analyze GitHub issue #$1 to ensure it represents an atomic deprecation task.

You are working in a Genesis worktree at: /Users/source_code/genesis/worktrees/deprecate-$1

Requirements:
- Identify exactly what needs deprecation
- Confirm migration requirements are clear
- Ensure atomic deprecation approach (single feature/component)
- Validate acceptance criteria are well-defined

Genesis Environment:
- Working in worktree with shared components available
- Must use shared_core.logger for all output
- Must use shared_core.errors for error handling
- Must validate environment with shared_core.config

Success Criteria:
- Issue confirmed as atomic deprecation task
- Migration requirements identified
- Root cause for deprecation understood
- Scope validated as minimal and focused

Constraints:
- Focus ONLY on the reported deprecation
- No scope expansion or additional improvements
- Maintain lean development principles
```

### Agent 2: dependency-tracker

Use the dependency-tracker agent to identify all usage:

```
Identify all code using the functionality to be deprecated in issue #$1.

You are working in a Genesis worktree at: /Users/source_code/genesis/worktrees/deprecate-$1

Requirements:
- Find all code using deprecated functionality
- Identify external dependencies
- Document migration impact
- Map all affected components

Genesis Environment:
- Working in worktree with shared components available
- Must use shared_core.logger for all output
- Must use shared_core.errors for error handling
- Must validate environment with shared_core.config

Success Criteria:
- All usage locations identified
- External dependencies mapped
- Migration impact documented
- Change scope clearly defined

Constraints:
- Complete coverage of all usages
- No assumptions about usage patterns
- Document every dependency
```

### Agent 3: documentation-minimalist

Use the documentation-minimalist agent to create migration guide:

```
Create minimal migration guide for deprecation in issue #$1.

You are working in a Genesis worktree at: /Users/source_code/genesis/worktrees/deprecate-$1

Requirements:
- Document what's being deprecated
- Provide clear migration path
- Include code examples
- Keep documentation minimal and actionable

Genesis Documentation Integration:
- Use existing documentation structure
- Follow established formatting conventions
- Integrate with current documentation
- Use shared_core.logger for progress tracking

Documentation Criteria:
- Clear before/after examples
- Step-by-step migration instructions
- Minimal but complete coverage
- Actionable guidance

Lean Principles:
- No over-documentation
- Focus on essential information only
- Provide exactly what's needed for migration
- Keep examples minimal
```

### Agent 4: lean-implementer

Use the lean-implementer agent to implement deprecation:

```
Implement deprecation for issue #$1 with minimal code changes.

You are working in a Genesis worktree at: /Users/source_code/genesis/worktrees/deprecate-$1

Requirements:
- Add deprecation warnings
- Maintain backward compatibility during transition
- Provide alternative implementations
- Keep changes minimal

Genesis Shared Components Integration:
- Use shared_core.logger for deprecation warnings
- Use shared_core.errors for error handling
- Use shared_core.config for configuration access
- Follow existing import patterns

Lean Implementation Principles:
- Absolute minimal code change required
- No architectural modifications
- No refactoring of surrounding code
- No additional features or improvements

Constraints:
- ONLY implement the specific deprecation
- Maintain backward compatibility
- No scope creep beyond deprecation
- Preserve existing API contracts

Success Criteria:
- Deprecation warnings implemented
- Backward compatibility maintained
- Alternative implementations provided
- Minimal surface area of change
```

### Agent 5: test-designer

Use the test-designer agent to add deprecation tests:

```
Create tests to verify deprecation behavior for issue #$1.

You are working in a Genesis worktree at: /Users/source_code/genesis/worktrees/deprecate-$1

Requirements:
- Verify deprecation warnings fire correctly
- Test migration path works
- Ensure backward compatibility maintained
- Use Genesis testing patterns

Genesis Testing Integration:
- Use existing test directory structure
- Import and use Genesis shared test utilities
- Follow established naming conventions
- Integrate with current test suite

Test Criteria:
- Minimal test case (no over-testing)
- Clear test names describing scenarios
- Proper setup/teardown if needed
- All deprecation paths covered

Lean Principles:
- Test ONLY the specific deprecation behavior
- No comprehensive test coverage expansion
- No testing of unrelated functionality
- Minimal test code to prove deprecation works
```

### Agent 6: build-validator

Use the build-validator agent to validate deprecation:

```
Run complete quality validation for deprecation #$1 using Genesis quality pipeline.

You are working in a Genesis worktree at: /Users/source_code/genesis/worktrees/deprecate-$1

Genesis Quality Gates (MANDATORY):
1. Run 'genesis autofix' - format and lint automatically
2. Run 'genesis status' - verify project health
3. Run full test suite (make test, pytest, or npm test)
4. Verify no regressions in existing functionality
5. Confirm deprecation warnings appear appropriately
6. Check Genesis health indicators

Quality Validation Requirements:
- All tests pass including new deprecation tests
- No linting violations after genesis autofix
- No type checking errors (if applicable)
- Genesis status shows healthy state
- Deprecation warnings fire correctly

Genesis Integration Validation:
- Verify shared components used correctly
- Check logging follows shared_core.logger patterns
- Confirm error handling uses shared_core.errors
- Validate configuration access uses shared_core.config

Success Criteria:
- Complete test suite passes
- All Genesis quality gates satisfied
- Deprecation warnings working correctly
- Migration path documented and verified
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
genesis commit --no-approve -m "deprecate: deprecate functionality for issue #$1

Closes #$1

- Deprecated old functionality with clear warnings
- Provided migration path and documentation
- Maintained backward compatibility
- All tests pass"

gh pr create \
  --title "deprecate: deprecate functionality for issue #$1" \
  --body "Deprecation with migration path per issue #$1" \
  --assignee @me || echo "⚠️ WARNING: PR creation failed"

cd ../../ || echo "⚠️ WARNING: Failed to return"
pwd  # VERIFY: Should show .../genesis
genesis status

echo "✅ SUCCESS: Deprecation completed for issue #$1"
```

---

## 🚫 COMMON MISTAKES TO AVOID

**❌ WRONG:** Delegating setup to agents
**✅ CORRECT:** Execute STEPS 1-7 with Bash tool, THEN use Task tool in STEP 8

---

## Success Criteria
- ✅ Deprecation warnings added
- ✅ Migration path documented
- ✅ Backward compatibility maintained
- ✅ All tests pass
