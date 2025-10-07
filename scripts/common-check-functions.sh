#!/bin/bash
# Common check functions for vertex-ai-search maintenance scripts
# This file provides shared functionality for validation scripts

# Colors for output (shared across all check scripts)
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

# Initialize issue counter
ISSUES_FOUND=0

# Common pattern checking function
check_pattern() {
    local pattern="$1"
    local description="$2"
    local files="$3"
    local exclude_pattern="${4:-}"  # Optional pattern to exclude from results

    echo -e "${YELLOW}🔍 Checking: $description${NC}"

    # Use git ls-files to respect .gitignore, then grep the results
    # Exclude documentation, test files, templates, and other non-source files
    if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
        # In a git repo - use git ls-files to respect .gitignore
        # Generic exclusions for test/template/doc files that commonly contain examples
        results=$(git ls-files '*.py' '*.ts' '*.tsx' '*.js' '*.jsx' '*.go' '*.rb' '*.java' '*.sh' '*.yaml' '*.yml' '*.json' | \
                 grep -v -E '(test_|_test\.|\.test\.|\.spec\.|/tests?/|/specs?/|/templates?/|/examples?/|/fixtures?/|/mocks?/|\.md$|conftest\.py|/docs/|shared-python/src/shared_core/)' | \
                 xargs grep -E -n "$pattern" 2>/dev/null || true)
    else
        # Fallback for non-git directories - recursive search
        results=$(find . -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -o -name "*.go" -o -name "*.rb" -o -name "*.java" -o -name "*.sh" -o -name "*.yaml" -o -name "*.yml" -o -name "*.json" \) \
                 -not -path "*/test*" -not -path "*/spec*" -not -path "*/template*" -not -path "*/example*" -not -path "*/fixture*" -not -path "*/mock*" \
                 -exec grep -E -n "$pattern" {} \; 2>/dev/null || true)
    fi

    # Apply exclusion filter if provided
    if [ -n "$exclude_pattern" ] && [ -n "$results" ]; then
        results=$(echo "$results" | grep -v -E "$exclude_pattern" || true)
    fi

    if [ -n "$results" ]; then
        echo -e "${RED}❌ Found issues:${NC}"
        echo "$results" | head -20  # Limit output
        echo
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        echo -e "${GREEN}✅ No issues found${NC}"
        echo
    fi
}

# Report final results
report_final_results() {
    local script_name="$1"
    local success_message="$2"
    local failure_message="$3"

    echo
    if [ $ISSUES_FOUND -eq 0 ]; then
        echo -e "${GREEN}🎉 $success_message${NC}"
    else
        echo -e "${RED}⚠️  Found $ISSUES_FOUND categories of issues in $script_name${NC}"
        echo "$failure_message"
        exit 1
    fi
}
