#!/bin/bash
# Genesis Bash Command Validation Hook
# Blocks bypass commands and enforces Genesis development patterns

set -euo pipefail

# Establish stable paths using CLAUDE_PROJECT_DIR if available
if [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then
    # Use Claude's project directory for stable paths
    PROJECT_ROOT="$CLAUDE_PROJECT_DIR"
    HOOK_DIR="$CLAUDE_PROJECT_DIR/.claude/hooks"
else
    # Fallback to finding hook's directory if CLAUDE_PROJECT_DIR not set
    HOOK_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    PROJECT_ROOT="$( cd "$HOOK_DIR/../.." && pwd )"
fi

# Debug output (can be commented out in production)
# echo "Hook executing from: $HOOK_DIR" >&2
# echo "Project root: $PROJECT_ROOT" >&2

# Read hook input from stdin
input=$(cat)

# Extract command from JSON input
command=$(echo "$input" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    cmd = data.get('tool_input', {}).get('command', '')
    print(cmd)
except:
    pass
")

# Skip if no command
if [[ -z "$command" ]]; then
    exit 0
fi

# Color codes for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to show Genesis alternative
show_genesis_alternative() {
    local blocked_cmd="$1"
    local genesis_cmd="$2"
    local reason="$3"

    echo -e "${RED}❌ $blocked_cmd blocked${NC}" >&2
    echo -e "${YELLOW}Reason: $reason${NC}" >&2
    echo -e "${GREEN}✅ Use instead: $genesis_cmd${NC}" >&2
    echo "" >&2
}

# Function to show make alternative
show_make_alternative() {
    local blocked_cmd="$1"
    local make_cmd="$2"
    local reason="$3"

    echo -e "${RED}❌ $blocked_cmd blocked${NC}" >&2
    echo -e "${YELLOW}Reason: $reason${NC}" >&2
    echo -e "${GREEN}✅ Use instead: $make_cmd${NC}" >&2
    echo "" >&2
}

# Check for SKIP_TESTS environment variable bypass attempt
if echo "$command" | grep -E "SKIP_TESTS=1" >/dev/null 2>&1; then
    echo -e "${RED}❌ SKIP_TESTS=1 blocked${NC}" >&2
    echo -e "${YELLOW}Reason: Tests must pass before committing. Skipping tests compromises code quality.${NC}" >&2
    echo -e "${GREEN}✅ Fix the failing tests or use 'git stash' to save your work temporarily${NC}" >&2
    echo "" >&2
    exit 1
fi

# Check for blocked git operations
if echo "$command" | grep -E "^git commit" >/dev/null 2>&1; then
    show_genesis_alternative \
        "git commit" \
        "genesis commit -m 'your message'" \
        "Direct git commits bypass quality gates and Genesis workflow"
    exit 1
fi

if echo "$command" | grep -E "^git rm" >/dev/null 2>&1; then
    echo -e "${RED}❌ git rm blocked${NC}" >&2
    echo -e "${YELLOW}Reason: git rm can permanently delete files and bypass Genesis safety mechanisms${NC}" >&2
    echo -e "${GREEN}✅ Use File System operations instead: rm <file> then git add -A${NC}" >&2
    echo -e "${BLUE}ℹ️  Or use Edit tool to remove content, then regular file operations${NC}" >&2
    echo "" >&2
    exit 1
fi

if echo "$command" | grep -E "^git worktree add" >/dev/null 2>&1; then
    show_genesis_alternative \
        "git worktree add" \
        "genesis worktree create <name> --focus <path>" \
        "Genesis provides AI-safe worktrees with file count limits"
    exit 1
fi

# Check for blocked dependency installation
if echo "$command" | grep -E "(^pip install|^poetry install|^npm install)" >/dev/null 2>&1; then
    show_make_alternative \
        "$(echo "$command" | cut -d' ' -f1-2)" \
        "make setup" \
        "Use standardized dependency management"
    exit 1
fi

# Check for blocked testing commands
if echo "$command" | grep -E "^pytest" >/dev/null 2>&1; then
    show_make_alternative \
        "pytest" \
        "make test" \
        "Use standardized test configuration"
    exit 1
fi

# Check for blocked linting/formatting
if echo "$command" | grep -E "^(ruff|black|flake8|pylint)" >/dev/null 2>&1; then
    show_make_alternative \
        "$(echo "$command" | cut -d' ' -f1)" \
        "make lint or genesis autofix" \
        "Use standardized code quality tools"
    exit 1
fi

# Check for blocked Docker operations
if echo "$command" | grep -E "^docker (build|run|exec)" >/dev/null 2>&1; then
    show_genesis_alternative \
        "docker $(echo "$command" | cut -d' ' -f2)" \
        "genesis container $(echo "$command" | cut -d' ' -f2)" \
        "Use Genesis container management"
    exit 1
fi

# Check for blocked cleanup operations
if echo "$command" | grep -E "^rm -rf (build|dist)" >/dev/null 2>&1; then
    show_make_alternative \
        "$(echo "$command" | cut -d' ' -f1-3)" \
        "make clean" \
        "Use standardized cleanup process"
    exit 1
fi

# Allow other commands
exit 0
