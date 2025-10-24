#!/bin/bash
# Pre-tool hook to check if we're in a worktree and provide safety warnings
# Used by Claude Code to prevent orchestrator issues when working in worktrees

set -euo pipefail

# Read the tool use details from stdin
TOOL_INPUT=$(cat)

# Extract tool name from JSON input (simple grep approach)
TOOL_NAME=$(echo "$TOOL_INPUT" | grep -o '"tool_name": "[^"]*"' | cut -d'"' -f4 2>/dev/null || echo "unknown")

# Check if we're in a Git repository
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    # Not in a Git repo, allow execution
    echo '{"decision": "approve", "reason": "Not in Git repository"}'
    exit 0
fi

# Check if we're in a worktree
WORKTREE_DIR=$(git rev-parse --git-dir 2>/dev/null || echo "")
if [[ "$WORKTREE_DIR" == *"/worktrees/"* ]]; then
    # We're in a worktree - this could be problematic for orchestration
    MAIN_REPO=$(git rev-parse --git-common-dir | sed 's|/.git$||' 2>/dev/null || echo "unknown")
    CURRENT_DIR=$(pwd)

    # Check if this is a Task tool call (agent launch) - this is especially dangerous
    if [[ "$TOOL_NAME" == "Task" ]]; then
        echo "{
            \"decision\": \"deny\",
            \"reason\": \"🚫 ORCHESTRATION SAFETY: Cannot launch agents from worktree '$CURRENT_DIR'. Agent coordination requires main repository. Switch to main repo: cd '$MAIN_REPO'\"
        }"
        exit 0
    fi

    # For other tools, provide warning but allow (with information)
    echo "{
        \"decision\": \"approve\",
        \"reason\": \"⚠️ WORKTREE DETECTED: Currently in worktree '$CURRENT_DIR'. Main repo at '$MAIN_REPO'. Some orchestration features may not work properly.\"
    }"
    exit 0
fi

# We're in main repository - all good
echo '{"decision": "approve", "reason": "In main repository - safe for orchestration"}'
