#!/usr/bin/env bash
# Check for forbidden shortcut patterns that bypass quality standards
# This enforces the NO SHORTCUTS POLICY from CLAUDE.md

set -euo pipefail

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

VIOLATIONS_FOUND=0

log_check() {
    echo -e "${BLUE}🔍 $1${NC}"
}

log_violation() {
    echo -e "${RED}❌ $1${NC}"
    VIOLATIONS_FOUND=$((VIOLATIONS_FOUND + 1))
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo "🚫 Checking for forbidden shortcut patterns..."
echo -e "${YELLOW}NO SHORTCUTS POLICY: Fix root causes, never silence symptoms${NC}"
echo

# Define shortcut patterns - each line is "pattern|description"
SHORTCUT_PATTERNS=(
    "# type: ignore|Type error suppression - Fix the type error properly"
    "# mypy: ignore|MyPy error suppression - Fix the type issue properly"
    "# noqa|Lint suppression - Fix the lint issue properly"
    "# pylint: disable|Pylint suppression - Fix the pylint issue properly"
    "# flake8: noqa|Flake8 suppression - Fix the flake8 issue properly"
    "# ruff: noqa|Ruff suppression - Fix the ruff issue properly"
    "@pytest.mark.skip|Test skipping - Fix the test or fix the code"
    "@unittest.skip|Test skipping - Fix the test or fix the code"
    "pytest.skip|Test skipping - Fix the test or fix the code"
    "except.*:.*pass|Empty exception handler - Handle errors properly"
    "except Exception:|Bare exception catch - Catch specific exceptions"
    "TODO|TODO comment - Fix it now, don't defer"
    "FIXME|FIXME comment - Fix it now, don't defer"
    "HACK|HACK comment - Implement properly, don't hack"
    "XXX|XXX comment - Fix it now, don't defer"
)

# File patterns to check
FILE_PATTERNS=(
    "*.py"
    "*.ts"
    "*.tsx"
    "*.js"
    "*.jsx"
    "*.go"
)

# Directories to exclude
EXCLUDE_PATHS=(
    ".venv"
    "venv"
    "node_modules"
    ".git"
    "build"
    "dist"
    "__pycache__"
    ".pytest_cache"
    ".mypy_cache"
    "htmlcov"
    ".next"
    "*.egg-info"
)

# Build exclude arguments for find
EXCLUDE_ARGS=()
for path in "${EXCLUDE_PATHS[@]}"; do
    EXCLUDE_ARGS+=(-not -path "*/${path}/*")
done

# Check each shortcut pattern
for entry in "${SHORTCUT_PATTERNS[@]}"; do
    pattern="${entry%%|*}"
    description="${entry#*|}"
    log_check "Checking for: $pattern"

    # Search for pattern in source files
    if command -v rg >/dev/null 2>&1; then
        # Use ripgrep if available (faster)
        results=$(rg --line-number --no-heading --color never \
            --type py --type js --type ts \
            "$pattern" . 2>/dev/null || true)
    else
        # Fallback to find + grep
        results=""
        for file_pattern in "${FILE_PATTERNS[@]}"; do
            while IFS= read -r file; do
                matches=$(grep -n -E "$pattern" "$file" 2>/dev/null || true)
                if [ -n "$matches" ]; then
                    results+="$file:$matches"$'\n'
                fi
            done < <(find . -type f -name "$file_pattern" "${EXCLUDE_ARGS[@]}" 2>/dev/null || true)
        done
    fi

    if [ -n "$results" ]; then
        log_violation "Found forbidden shortcut: $pattern"
        echo -e "${YELLOW}   Reason: $description${NC}"
        echo -e "${YELLOW}   Violations:${NC}"
        echo "$results" | head -10 | while IFS= read -r line; do
            echo "     $line"
        done

        # Count total violations for this pattern
        violation_count=$(echo "$results" | grep -c "^" || true)
        if [ "$violation_count" -gt 10 ]; then
            echo -e "${YELLOW}   ... and $((violation_count - 10)) more${NC}"
        fi
        echo
    else
        log_success "No shortcuts found for: $pattern"
    fi
done

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

if [ $VIOLATIONS_FOUND -eq 0 ]; then
    echo -e "${GREEN}🎉 NO SHORTCUTS FOUND - Excellent code quality!${NC}"
    echo
    exit 0
else
    echo -e "${RED}⚠️  FOUND $VIOLATIONS_FOUND SHORTCUT VIOLATIONS${NC}"
    echo
    echo -e "${YELLOW}📋 NO SHORTCUTS POLICY (from CLAUDE.md):${NC}"
    echo
    echo "  These shortcuts are BANNED because they:"
    echo "  • Hide real bugs and issues"
    echo "  • Accumulate technical debt"
    echo "  • Break quality standards"
    echo "  • Undermine codebase trust"
    echo
    echo -e "${YELLOW}✅ What to do instead:${NC}"
    echo
    echo "  1. Understand the root cause"
    echo "  2. Fix the actual problem (not the symptom)"
    echo "  3. Ask questions if unclear"
    echo "  4. Refactor if needed"
    echo
    echo -e "${YELLOW}📖 See CLAUDE.md section 'NO SHORTCUTS POLICY' for:${NC}"
    echo "  • Detailed explanations"
    echo "  • Correct approaches for each error type"
    echo "  • Rare exception guidelines (with required format)"
    echo
    echo -e "${RED}🚫 FIX THE ROOT CAUSE. NEVER TAKE SHORTCUTS.${NC}"
    echo
    exit 1
fi
