#!/usr/bin/env bash
# Find hardcoded values and dangerous defaults in Genesis codebase

set -euo pipefail

echo "🔍 Searching for hardcoded values and dangerous defaults..."
echo

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

ISSUES_FOUND=0

check_pattern() {
    local pattern="$1"
    local description="$2"
    local files="$3"
    local exclude_pattern="${4:-}"  # Optional pattern to exclude from results

    echo -e "${YELLOW}🔍 Checking: $description${NC}"

    # Use git ls-files to respect .gitignore, then grep the results
    # Exclude documentation, test files, and templates
    if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
        # In a git repo - use git ls-files to respect .gitignore, exclude docs/tests/templates
        results=$(git ls-files '*.py' '*.ts' '*.tsx' '*.js' '*.jsx' | grep -v -E '(test_|_test\.|\.test\.|/tests/|/templates/|\.md$|conftest\.py|/fixtures/|mock_)' | xargs grep -E -n "$pattern" 2>/dev/null || true)
    else
        # Fallback for non-git directories
        results=$(grep -rn -E "$pattern" "$files" 2>/dev/null || true)
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

# Function parameter defaults (dangerous - numbers, strings, hardcoded values)
check_pattern 'def [^(]*\([^)]*=[ \t]*[0-9"[{]' "Function parameters with dangerous default values" "."

# Click command defaults (exclude standard conventions like "." for build context)
check_pattern '@click\.option\([^)]*default=' "Click options with default values" "." 'default="\."'

# Environment variable fallbacks
check_pattern 'os\.environ\.get\([^,)]*,\s*["\047][^"\047]*["\047]\)' "Environment variable fallbacks with hardcoded strings" "."

# Dataclass field defaults
check_pattern '@dataclass.*\n.*=.*[0-9]' "Dataclass fields with numeric defaults" "."

# Hardcoded ports/URLs/hostnames
check_pattern '["\047](https?://|localhost|127\.0\.0\.1|0\.0\.0\.0)["\047]' "Hardcoded URLs and localhost references" "."

# Hardcoded ports
check_pattern ':[0-9]{2,5}(?![0-9])' "Hardcoded port numbers" "."

# Hardcoded timeouts (seconds/milliseconds)
check_pattern 'timeout[^=]*=[ \t]*[0-9]+' "Hardcoded timeout values" "."

# Hardcoded file paths (exclude module-level constants and function returns)
check_pattern '["\047]/.+["\047]' "Hardcoded absolute file paths" "." ':[A-Z_]+\s*=|:\s+return\s+\[|:\s+"/|:DEFAULT_|:FORBIDDEN_'

# Hardcoded versions in templates
check_pattern '"version":\s*"[0-9]+\.[0-9]+\.[0-9]+"' "Hardcoded versions in JSON" "templates/"

# Hardcoded database/service names
check_pattern '["\047](postgresql://|mongodb://|mysql://)[^"\047]*["\047]' "Hardcoded connection strings" "."

# Hardcoded log levels
check_pattern 'level["\047\s]*=["\047\s]*(DEBUG|INFO|WARN|ERROR)["\047\s]*' "Hardcoded log levels" "."

# Magic numbers (common dangerous values)
check_pattern '\b(5000|8080|3000|5432|27017|6379)\b' "Common port numbers as magic values" "."

# Hardcoded retry counts/delays (exclude constants and docstrings)
check_pattern '(max_attempts|max_retries|retry_count)[^=]*=[ \t]*[0-9]+' "Hardcoded retry parameters" "." '(^[A-Z_]+\s*=|^\s*#|^\s*"""|\s+@)'

# Hardcoded buffer/cache sizes
check_pattern '(buffer_size|cache_size|max_size)[^=]*=[ \t]*[0-9]+' "Hardcoded buffer/cache sizes" "."

# Hardcoded version numbers (only flag if NOT in __init__.py or version.py - those are source of truth)
check_pattern '__version__\s*=\s*["\047][0-9]+\.[0-9]+\.[0-9]+["\047]' "Hardcoded __version__ in non-version files" "." '(__init__\.py|version\.py|test_|_test\.|/tests/|/docs/|CHANGELOG)'

# Hardcoded version in manifests/configs (these become stale and should be dynamic)
# Exclude embedded manifests in dependencies.py which are fallbacks that get updated during version bumps
check_pattern '["\047]latest["\047]:\s*["\047]v?[0-9]+\.[0-9]+\.[0-9]+["\047]' "Hardcoded 'latest' version (should be dynamic)" "." 'test_|dependencies\.py|dependencies_optimized\.py'

# FORBIDDEN AI SIGNATURES (exclude documentation files)
echo -e "${YELLOW}🔍 Checking: Forbidden AI attribution signatures (code files only)${NC}"
if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
    # In a git repo - check code files only, exclude .md files and validation scripts
    ai_results=$(git ls-files '*.py' '*.ts' '*.tsx' '*.js' '*.jsx' '*.sh' '*.yaml' '*.yml' '*.json' | grep -v -E '(test_|_test\.|\.test\.|/tests/|/templates/|conftest\.py|/fixtures/|mock_|check-ai-signatures|find-hardcoded-values)' | xargs grep -E -n 'Generated with.*Claude Code|Co-Authored-By.*Claude|Generated by Claude|Created with Claude Code|Claude AI assistance|AI-generated code|claude\.ai/code|anthropic\.com|noreply@anthropic\.com' 2>/dev/null || true)
else
    # Fallback for non-git directories - exclude .md files and validation scripts
    ai_results=$(find . -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -o -name "*.sh" -o -name "*.yaml" -o -name "*.yml" -o -name "*.json" \) ! -path "*/tests/*" ! -path "*/templates/*" ! -name "*test*" ! -name "conftest.py" ! -path "*/fixtures/*" ! -name "*mock*" ! -name "*check-ai-signatures*" ! -name "*find-hardcoded-values*" | xargs grep -E -n 'Generated with.*Claude Code|Co-Authored-By.*Claude|Generated by Claude|Created with Claude Code|Claude AI assistance|AI-generated code|claude\.ai/code|anthropic\.com|noreply@anthropic\.com' 2>/dev/null || true)
fi

if [ -n "$ai_results" ]; then
    echo -e "${RED}❌ Found issues:${NC}"
    echo "$ai_results" | head -20
    echo
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✅ No issues found${NC}"
fi
echo

# TEMPLATE VERSION HARDCODING
echo -e "${YELLOW}🔍 Checking: Hardcoded versions in template.json files${NC}"
template_results=$(find templates/ -name "template.json" -exec grep -Hn '".*_version":[[:space:]]*"[0-9]' {} \; 2>/dev/null || true)
if [ -n "$template_results" ]; then
    echo -e "${RED}❌ Found issues:${NC}"
    echo "$template_results"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✅ No issues found${NC}"
fi
echo

echo
if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}🎉 No hardcoded values found!${NC}"
else
    echo -e "${RED}⚠️  Found $ISSUES_FOUND categories of hardcoded values${NC}"
    echo "Review the output above and fix critical issues."
    exit 1
fi
