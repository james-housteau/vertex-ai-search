# Slash Command Standardization Template

This template extracts proven patterns from bug.md to standardize refactor.md, optimize.md, and deprecate.md.

---

## 1. AGENT PROMPT STRUCTURE

All agent prompts should follow this complete structure:

### Single Agent Prompt Format

```
Use Task tool with [agent-name] agent:

You are working in a Genesis worktree at: /Users/source_code/genesis/worktrees/[worktree-name]

[Task description and objective]

**Context:**
- Pure module isolation worktree already created
- Environment already configured
- Genesis CLI available

**[Task Type] Workflow:**
1. [Step 1]
2. [Step 2]
3. [Step 3]
4. [Step 4]

**Genesis Integration:**
- Use shared_core.logger for logging
- Use shared_core.errors for error handling
- Follow existing code patterns

**Success Criteria:**
- [Criterion 1]
- [Criterion 2]
- [Criterion 3]
- [Criterion 4]

Run tests frequently to verify progress.
```

### Multi-Phase Agent Prompt Format

Each agent in a multi-phase workflow should include:

```
[Task description for specific agent]

Requirements:
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]
- [Requirement 4]

Genesis Environment:
- Working in worktree with shared components available
- Must use shared_core.logger for all output
- Must use shared_core.errors for error handling
- Must validate environment with shared_core.config

Success Criteria:
- [Success criterion 1]
- [Success criterion 2]
- [Success criterion 3]
- [Success criterion 4]

Constraints:
- [Constraint 1]
- [Constraint 2]
- [Constraint 3]
```

---

## 2. TEST DETECTION LOGIC

**Pattern from bug.md (lines 477-486):**

Replace incomplete test detection with this full block:

```bash
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

**Key Elements:**
- Check Makefile first with grep for `^test:` target
- Fall back to pytest.ini detection
- Support npm test for TypeScript projects
- Provide fallback message for manual verification
- Use consistent error message: "Some tests failed" (not "Tests failed")

---

## 3. VERBOSE SYMLINK VERIFICATION

**Pattern from bug.md (lines 113-137):**

Replace minimal verification with this detailed output:

```bash
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
```

**Key Elements:**
- Explicit "Verifying Pure Module Isolation setup..." message
- Loop through all expected symlinks with readlink output
- Loop through all expected manifest files
- File count verification with AI safety context
- Consistent ✓ and ⚠️ symbols for status

---

## 4. WORKTREE PATH CONTEXT

**Pattern from bug.md (line 223):**

All agent prompts must include explicit worktree path:

```
You are working in a Genesis worktree at: /Users/source_code/genesis/worktrees/[worktree-name]
```

**Why this matters:**
- Agents need explicit path context
- Prevents confusion about working directory
- Makes debugging easier when reviewing agent output
- Matches Genesis isolation principles

---

## 5. CONSISTENT ERROR MESSAGES

**Patterns extracted from bug.md:**

### Test Failures
```bash
make test || echo "⚠️ WARNING: Some tests failed"
pytest || echo "⚠️ WARNING: Some tests failed"
npm test || echo "⚠️ WARNING: Some tests failed"
```
- Use "Some tests failed" consistently
- Use "⚠️ WARNING:" prefix for non-fatal issues

### Autofix Issues
```bash
genesis autofix || {
    echo "⚠️ WARNING: Genesis autofix encountered issues"
    echo "Attempting to continue..."
}
```
- Acknowledge failure but continue workflow
- Provide context about next action

### Health Check Issues
```bash
genesis status || echo "⚠️ WARNING: Genesis project health issues detected"
genesis status || echo "⚠️ WARNING: Genesis status shows issues"
```
- Consistent "⚠️ WARNING:" prefix
- Descriptive message about what failed

### Fatal Errors
```bash
source .envrc || {
    echo "❌ FATAL: Failed to source .envrc"
    exit 1
}

cd worktrees/fix-$1/ || {
    echo "❌ FATAL: Failed to navigate to worktree"
    exit 1
}
```
- Use "❌ FATAL:" for errors requiring exit
- Include clear action that failed

---

## 6. GENESIS INTEGRATION SECTION

**Standard section for all agent prompts:**

```
**Genesis Integration:**
- Use shared_core.logger for logging
- Use shared_core.errors for error handling
- Follow existing code patterns
- [Add task-specific integrations]
```

**Expanded version for detailed agents:**

```
Genesis [Component] Integration:
- Use shared_core.logger for all output
- Use shared_core.errors for error handling
- Use shared_core.config for configuration access
- Follow established naming conventions
- Integrate with current [component] suite
```

---

## 7. QUALITY GATES SECTION

**Standard quality gates block for STEP 9:**

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

**Key Pattern:**
- Always run genesis autofix first
- Always run genesis status second
- Always run test detection third
- Handle failures gracefully with warnings

---

## 8. COMPLETE AGENT WORKFLOW STRUCTURE

**Five-phase agent structure from bug.md:**

### Phase 1: Analysis Agent
- Requirements section
- Genesis Environment section
- Success Criteria section
- Constraints section

### Phase 2: Design/Test Agent
- Requirements section
- Genesis [Component] Integration section
- [Component] Criteria section
- Lean Principles section

### Phase 3: Implementation Agent
- Requirements section
- Genesis Shared Components Integration section
- Lean Implementation Principles section
- Constraints section
- Success Criteria section

### Phase 4: Validation Agent
- Genesis Quality Gates (MANDATORY) section
- Quality Validation Requirements section
- Genesis Integration Validation section
- Test Suite Validation section
- Success Criteria section

### Phase 5: Scope Guardian Agent
- Scope Validation Requirements section
- Scope Boundaries (STRICT) section
- Change Analysis section
- Genesis Principles Validation section
- Success Criteria section

---

## APPLICATION CHECKLIST

When standardizing a slash command, verify:

- [ ] Agent prompts include worktree path context
- [ ] Complete test detection logic (Makefile → pytest.ini → package.json → fallback)
- [ ] Verbose symlink verification with readlink output
- [ ] Consistent error messages ("Some tests failed" not "Tests failed")
- [ ] Genesis Integration section in all agent prompts
- [ ] Requirements section in all agent prompts
- [ ] Success Criteria section in all agent prompts
- [ ] Quality gates block includes all three components (autofix, status, tests)
- [ ] Error handling uses appropriate prefixes (⚠️ WARNING, ❌ FATAL)
- [ ] File count verification with AI safety context

---

## EXTRACTED LINE REFERENCES

These are the exact line numbers in bug.md where patterns are found:

- **Agent prompt structure**: Lines 220-250 (single agent), Lines 260-450 (multi-phase)
- **Worktree path context**: Line 223
- **Test detection logic**: Lines 477-486
- **Verbose symlink verification**: Lines 113-137
- **Error message patterns**: Throughout (lines 59-62, 469-472, 479-486)
- **Genesis Integration section**: Lines 238-242, 273-276, 305-309, 338-343, 388-392
- **Quality gates block**: Lines 465-486

---

## NEXT STEPS

Use this template to:

1. **Update refactor.md**: Add missing agent prompt structure and verbose verification
2. **Update optimize.md**: Add complete test detection and worktree path context
3. **Update deprecate.md**: Add Genesis Integration sections and consistent error messages

Apply patterns exactly as shown in bug.md - they are proven to work.
