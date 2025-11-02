---
allowed-tools: Task, Bash(gh:*), Read, Grep
argument-hint: [action-term] [instructions]
description: Create GitHub issue from current context
model: claude-sonnet-4-20250514
---

## Create GitHub Issue

Analyze the current conversation context and create a well-scoped GitHub issue.

### Context Analysis
Current discussion: Review the conversation to understand what needs to be done
Arguments provided: $ARGUMENTS

Parse the arguments to extract:
- Action term (first word): feature, bug, refactor, optimize, deprecate, cleanup, docs, test, etc.
- Instructions (rest of arguments): specific details about what needs to be done

### Issue Creation Process

Use the issue-analyst agent to ensure proper scoping:

1. Extract the core problem or feature from context
2. Create atomic, testable issue
3. Define clear success criteria
4. Ensure single deliverable

### Issue Format

Use the action term from arguments to create appropriate issue:

```markdown
## Title
[{ACTION_TERM}] {Component}: {Specific Behavior}
Example: "feature: Add dark mode toggle to settings"
Example: "bug: Fix authentication timeout on mobile"
Example: "refactor: Extract payment processing into service layer"

## Description
Clear statement of what needs to be done based on the instructions provided

## Success Criteria
- [ ] Specific, testable requirement
- [ ] Observable behavior change
- [ ] Tests pass

## Scope
- IN: What's included
- OUT: What's explicitly not included

## Technical Notes
Any implementation hints or constraints

---

## 🚫 NO SHORTCUTS POLICY

**CRITICAL: This workflow enforces the NO SHORTCUTS POLICY from CLAUDE.md.**

### Absolutely Forbidden

You MUST NEVER suggest or use these shortcuts when implementing this issue:

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
```

### Labels
Apply appropriate label based on action term:
- feature → "enhancement"
- bug → "bug"
- refactor → "refactoring"
- optimize → "performance"
- deprecate → "deprecation"
- cleanup → "cleanup"
- docs → "documentation"
- test → "testing"

### Command to Execute
```bash
gh issue create --title "TITLE" --body "BODY" --label "LABEL"
```

Return the created issue number for use in subsequent commands.
