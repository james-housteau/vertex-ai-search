---
allowed-tools: Bash(gh:*, git:*), Task
argument-hint: [issue-number]
description: Clean up after PR merge
model: claude-sonnet-4-20250514
---

## Genesis Post-Merge Cleanup

Clean up after pull request has been merged using Genesis worktree management.

### Issue Detection

Auto-detect issue number from current context:
```bash
# Auto-detect issue number from argument or worktree
ISSUE_NUM=${1:-$(basename $(pwd) | sed 's/fix-//' | grep -E '^[0-9]+$')}
```

### Issue Cleanup

Close the GitHub issue:
```bash
# Get PR number from GitHub (if available)
PR_NUMBER=$(gh pr list --state merged --limit 1 --json number --jq '.[0].number' 2>/dev/null || echo "merged")

# Close issue with comment
gh issue close $ISSUE_NUM --comment "Resolved in PR #$PR_NUMBER"
```

### Genesis Worktree Cleanup

Use Genesis to clean up worktree and branches:
```bash
# Detect worktree context and navigate to main repo
REPO_ROOT=$(git rev-parse --git-common-dir | sed 's/\.git$//')

# Check if we're in a worktree context
if [[ "$(pwd)" =~ worktrees ]] || [[ "$(git branch --show-current)" =~ ^fix- ]]; then
    echo "Detected worktree context, using main repo: $REPO_ROOT"

    # Remove Genesis worktree from main repo context
    # Note: genesis worktree remove must be called with repo root context
    if ! (cd "$REPO_ROOT" && genesis worktree remove fix-$ISSUE_NUM); then
        echo "⚠️ genesis worktree remove failed - attempting manual cleanup"
        echo "Note: This is acceptable for post-merge cleanup operations"
        # Manual cleanup from main repo (no quality gates to bypass)
        (cd "$REPO_ROOT" && {
            git checkout --quiet main || git checkout --quiet master
            git pull --quiet
            # Detect branch name (handles both sparse-fix- and fix- patterns)
            BRANCH_NAME=$(git branch --list | grep -E "(sparse-)?fix-$ISSUE_NUM$" | tr -d ' ' || echo "")
            if [ -n "$BRANCH_NAME" ]; then
                git branch -d "$BRANCH_NAME" 2>/dev/null || echo "Branch already deleted"
                git push origin --delete "$BRANCH_NAME" 2>/dev/null || echo "Remote branch already deleted"
            else
                echo "Branch already deleted"
            fi
        })
    fi
else
    # Not in worktree, standard cleanup
    if ! genesis worktree remove fix-$ISSUE_NUM; then
        echo "⚠️ genesis worktree remove failed - attempting manual cleanup"
        echo "Note: This is acceptable for post-merge cleanup operations"
        git checkout --quiet main || git checkout --quiet master
        git pull --quiet
        # Detect branch name (handles both sparse-fix- and fix- patterns)
        BRANCH_NAME=$(git branch --list | grep -E "(sparse-)?fix-$ISSUE_NUM$" | tr -d ' ' || echo "")
        if [ -n "$BRANCH_NAME" ]; then
            git branch -d "$BRANCH_NAME" 2>/dev/null || echo "Branch already deleted"
            git push origin --delete "$BRANCH_NAME" 2>/dev/null || echo "Remote branch already deleted"
        else
            echo "Branch already deleted"
        fi
    fi
fi
```

### Documentation Update

Check if docs need updating:
- Use documentation-minimalist to update ONLY if needed
- Remove outdated documentation
- Don't add unless critical

### Final Status

Report cleanup complete:
```
✅ Issue #$ISSUE_NUM closed
✅ Genesis worktree removed
✅ Branch cleaned up automatically
✅ Main branch updated
✅ Ready for next issue
```

### Optional: Update Metrics

If tracking metrics, update:
- Issues resolved count
- Code reduction achieved
- Complexity improvements

---

## 🚫 NO SHORTCUTS POLICY

**Remember:** The work completed for this issue followed the NO SHORTCUTS POLICY.

**Verification Checklist:**
- ✅ No `# type: ignore` or `# noqa` in merged code
- ✅ No `try/except: pass` patterns
- ✅ No skipped or commented-out tests
- ✅ All quality gates passed properly
- ✅ Root causes were fixed, not symptoms silenced

If you notice any shortcuts in the merged code, create a follow-up issue to fix them properly.

See CLAUDE.md section "NO SHORTCUTS POLICY" for full details.
