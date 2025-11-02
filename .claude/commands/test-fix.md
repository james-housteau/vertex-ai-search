---
allowed-tools: Task, Bash, Read, Write, Edit, Grep, Glob
argument-hint: "[test-path-or-pattern]"
description: "Fix failing tests by treating tests as source of truth, not code"
model: claude-sonnet-4-20250514
---

# Test Fix Workflow

## CRITICAL: Tests Are The Source of Truth

Fix failing tests by analyzing requirements and ensuring code meets test expectations.
Tests define the contract - if tests fail, the code is wrong, not the tests.

## Philosophy

1. **Tests are the specification** - They define what the code SHOULD do
2. **Never fix tests to match broken code** - Fix the code to match test expectations
3. **Remove only obsolete tests** - Tests for removed features or changed requirements
4. **Update tests only for new requirements** - When requirements legitimately change
5. **If no requirement changed and test fails** - The code is broken, fix it

## Before You Start: Verify Test Context

Answer these three questions for EACH failing test BEFORE attempting any fix:

### 1. When was this test written?
```bash
# Find when test file was created
git log --diff-filter=A --follow --format="%aI %s" -- path/to/test_file.py | tail -1

# Find when specific test function was added
git log -p --all -S "def test_specific_name" -- path/to/test_file.py | head -50
```

### 2. What was the test validating?
```bash
# Read test name, docstring, and assertions
cat path/to/test_file.py | grep -A 20 "def test_name"

# Check commit message when test was added
git log --follow -p -- path/to/test_file.py | grep -B 5 -A 10 "def test_name" | head -30
```

### 3. Has anything changed since then?
```bash
# Find commits modifying implementation AFTER test was written
# Replace YYYY-MM-DD with test creation date from step 1
git log --since="YYYY-MM-DD" --oneline -- path/to/implementation.py

# Find related issues/PRs merged after test was written
gh issue list --search "closed:>YYYY-MM-DD" --limit 20
gh pr list --search "merged:>YYYY-MM-DD" --limit 20
```

**STOP**: If you cannot answer all three questions with concrete evidence, you are not ready to categorize the failure.

## Workflow

### Phase 1: Analyze Test Failures

```bash
# Run tests to identify failures
make test || pytest [test-path-or-pattern] -v --tb=short

# Capture all failure details
pytest --tb=long --no-header -rN > /tmp/test-failures.txt
```

### Phase 2: Evidence-Based Categorization

For EACH failing test, collect evidence FIRST, then categorize:

#### Evidence Collection (REQUIRED)

**Test Creation Evidence:**
```bash
# When was test created?
git log --diff-filter=A --format="%aI %s" -- path/to/test_file.py

# What commit added this test?
git log --diff-filter=A --oneline -- path/to/test_file.py

# What was the commit message and context?
git show <commit-hash> --stat
```

**Requirement Change Evidence:**
```bash
# Find related issues closed AFTER test was written (use date from above)
gh issue list --search "closed:>2024-01-15 label:enhancement" --limit 20

# Find commits mentioning requirement changes
git log --since="2024-01-15" --grep="requirement\|feature\|spec\|breaking" --oneline

# Find PRs that changed behavior
gh pr list --search "merged:>2024-01-15" --limit 20
```

**Code Change Evidence:**
```bash
# What changed in implementation since test was written?
git log --since="2024-01-15" -p -- path/to/implementation.py

# Who changed it and why?
git log --since="2024-01-15" --format="%an: %s" -- path/to/implementation.py
```

#### Categorization (Based on Evidence)

**Only after collecting evidence above**, categorize into ONE of these:

1. **Obsolete Test**: Feature was removed or deprecated
   - ✅ **Evidence REQUIRED**: Commit/PR showing feature removal with issue reference
   - ✅ **Evidence REQUIRED**: Issue documenting deprecation decision
   - ✅ **Evidence REQUIRED**: Documentation update removing feature
   - **Action**: Remove test with reference to removal commit
   - **Example**: "Feature removed in commit abc123 (issue #456)"

2. **Requirement Changed**: Requirements legitimately evolved
   - ✅ **Evidence REQUIRED**: Issue/PR showing new requirement AFTER test was written
   - ✅ **Evidence REQUIRED**: Commit message explicitly explaining behavior change
   - ✅ **Evidence REQUIRED**: Documentation update reflecting new behavior
   - **Action**: Update test with reference to requirement change
   - **Example**: "Requirement changed in issue #789 (merged 2024-02-15), test written 2024-01-10"

3. **Code Regression**: Code broke, test is correct (**MOST COMMON - 90% of cases**)
   - ❌ No evidence of requirement change found
   - ❌ No evidence of feature removal found
   - ✅ Test was correct when written
   - **Action**: Fix code to pass test
   - **Default action when no evidence exists**

4. **Test Bug**: Test itself has a bug (**RARE - <5% of cases**)
   - ✅ **Evidence REQUIRED**: Test expectations are logically impossible
   - ✅ **Evidence REQUIRED**: Test conflicts with documented behavior from when it was written
   - ✅ **Evidence REQUIRED**: Test was broken from the start (never passed)
   - **Action**: Fix test bug with detailed explanation

### Phase 3: Apply Fix Based on Evidence

#### For Obsolete Tests (Evidence Required):
```bash
# Verify feature removal with specific commit
git log --oneline --all --grep="<feature-name>" | grep -i "remove\|deprecate"

# Check for issues documenting the removal
gh issue list --search "is:closed <feature-name> remove" --limit 10

# Document removal
cat >> test-changes.log <<LOG
Test: test_obsolete_feature
Removed: $(date -u +"%Y-%m-%d")
Reason: Feature removed in commit <hash>
Issue: #<number>
LOG

# Remove test file
git rm path/to/obsolete_test.py
```

#### For Changed Requirements (Strong Evidence Required):
```bash
# Document evidence of requirement change
cat >> test-changes.log <<LOG
Test: test_specific_behavior
Test written: 2024-01-10
Requirement changed: 2024-02-15
Evidence: Issue #XXX, PR #YYY
Commit: <hash>
Details: <what changed and why>
LOG

# Update test to match new requirement
# Add comment in test file explaining the change:
# "Updated 2024-02-15: Requirement changed per issue #XXX"
```

#### For Code Regressions (DEFAULT - No Evidence Needed):
```bash
# Read test to understand what it expects
cat path/to/test_file.py | grep -A 30 "def test_failing_name"

# Fix implementation to meet test expectations
# This is the DEFAULT action when no evidence of changes exists

# Run test repeatedly until passing
pytest path/to/test_file.py::test_failing_name -v --tb=short

# Verify no regressions
pytest path/to/test_file.py -v
```

### Phase 4: Validation

```bash
# Run specific fixed tests
pytest path/to/fixed_test.py -v --tb=short

# Run full test suite
make test

# Verify no new failures introduced
pytest --tb=short -v
```

## Evidence-Based Decision Tree

```
Test Failing?
│
├─> Collect Evidence (git log, gh issue, PR history)
│   - When was test written?
│   - What was it testing?
│   - What changed since then?
│
├─> Can you show commit/issue proving feature was REMOVED?
│   └─> YES: Remove test (cite commit hash and issue number)
│   └─> NO: Continue
│
├─> Can you show issue/PR proving requirement CHANGED after test was written?
│   └─> YES: Update test (cite issue/PR number, dates, and commit)
│   └─> NO: Continue
│
├─> Are test expectations logically impossible or contradictory?
│   └─> YES: Fix test (explain why expectations are wrong)
│   └─> NO: Continue
│
└─> DEFAULT: Code is broken - FIX THE CODE, NOT THE TEST
    - Test was correct when written
    - No evidence of legitimate changes
    - This is the most common case
```

## Evidence Standards

### Weak Evidence (NOT SUFFICIENT):
- ❌ "I think the requirement changed"
- ❌ "The code doesn't match the test"
- ❌ "This test seems wrong"
- ❌ "It works in production differently"

### Strong Evidence (REQUIRED):
- ✅ "Issue #123 merged 2024-02-15 changed behavior, test written 2024-01-10"
- ✅ "Commit abc123 removed feature with message 'deprecate old API'"
- ✅ "PR #456 explicitly states new requirement conflicts with test expectations"
- ✅ "Documentation updated in commit def789 showing different contract"

## Red Flags (Never Do These)

❌ Changing test assertions to match current broken output
❌ Adding skip decorators without issue reference
❌ Modifying expected values to make tests pass
❌ Weakening test conditions to accommodate bugs
❌ Removing tests because "they're hard to fix"
❌ Updating tests without citing specific evidence

## Green Flags (Always Do These)

✅ Read test name and docstring to understand intent
✅ Check git history for when test was added and why
✅ Verify test expectations match documented behavior from that time
✅ Fix code to meet test's contract (default action)
✅ Keep tests as strict as originally intended
✅ Document why a test was removed with commit/issue references
✅ Cite specific evidence when updating tests

## Example Scenarios

### Scenario 1: Test Expects Specific Error Message (Code Regression)
```python
def test_validation_error_message():
    # Test expects: "Invalid email format"
    # Code returns: "Email invalid"

# Evidence check:
# - No issues showing requirement change
# - No commits changing error message contract
# - Test written before code broke

# ACTION: Fix code to return expected message
```

### Scenario 2: Test Expects Certain Behavior (Code Regression)
```python
def test_file_creation():
    # Test expects: File created with 0644 permissions
    # Code creates: File with 0600 permissions

# Evidence check:
# - No security policy changes found
# - No issues about permission changes
# - Test documented correct behavior

# ACTION: Fix code to use 0644 permissions
```

### Scenario 3: Test No Longer Relevant (Obsolete - Evidence Found)
```python
def test_deprecated_api_endpoint():
    # Test for: /api/v1/old-endpoint

# Evidence check:
# ✅ Found: Commit abc123 "remove deprecated v1 API (issue #789)"
# ✅ Found: Issue #789 documents deprecation plan
# ✅ Found: PR #790 removed the endpoint code

# ACTION: Remove test, document evidence:
# "Removed: Feature deprecated in issue #789, removed in commit abc123"
```

### Scenario 4: Requirement Actually Changed (Evidence Found)
```python
def test_pagination_default():
    # Test expects: 10 items per page
    # Code returns: 25 items per page

# Evidence check:
# ✅ Found: Issue #555 "Increase default pagination to 25" (merged 2024-03-01)
# ✅ Found: PR #556 updated implementation (merged 2024-03-01)
# ✅ Found: Test written 2024-01-15 (before requirement change)
# ✅ Found: Documentation updated to show 25 as default

# ACTION: Update test to expect 25, cite issue #555 and date
```

## Success Criteria

- ✅ All tests pass
- ✅ No tests modified to accommodate bugs
- ✅ Code changes minimal and focused
- ✅ Obsolete tests documented with evidence and removed
- ✅ Test updates include evidence citations
- ✅ Test suite represents current requirements

## Report Format

After completion, report:
1. Tests fixed by correcting code: X
2. Tests updated for new requirements: Y (with evidence citations)
3. Tests removed as obsolete: Z (with evidence citations)
4. Total passing tests: N

**For each test update or removal, include:**
- Test name and file
- Evidence: Issue/PR/Commit reference
- Date of change vs date test was written
- Brief explanation

Remember: **Tests define truth. If test fails, assume code is wrong until proven otherwise with concrete evidence.**

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
- `@pytest.mark.skip` without evidence - Provide concrete evidence or fix the test

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
- ❌ `pytest --skip-tests` or commenting out tests
- ✅ Fix the code to make the test pass OR provide concrete evidence (Issue/PR/Commit) for removal

**Error Handling:**
- ❌ `try: operation() except: pass`
- ✅ `try: operation() except SpecificError as e: logger.error(f"Failed: {e}")`

### Pre-commit Protection

The pre-commit hook will **REJECT** commits containing shortcut patterns.
See `.pre-commit-config.yaml` for the `no-shortcuts` hook configuration.

### Summary

**FIX THE ROOT CAUSE. NEVER TAKE SHORTCUTS.**

This is non-negotiable. Quality code requires quality discipline.
