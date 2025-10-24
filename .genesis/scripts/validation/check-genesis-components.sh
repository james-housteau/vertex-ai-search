#!/usr/bin/env bash
# Check Genesis module isolation - ensures modules follow pure module isolation principles

set -euo pipefail

echo "🔍 Checking Genesis module isolation compliance..."
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
    # Exclude documentation, test files, templates, and core implementation files
    if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
        # In a git repo - use git ls-files to respect .gitignore, exclude docs/tests/templates/core implementations
        results=$(git ls-files '*.py' '*.ts' '*.tsx' '*.js' '*.jsx' | grep -v -E '(test_|_test\.|\.test\.|/tests/|/templates/|\.md$|conftest\.py|/fixtures/|mock_|/docs/|genesis/core/logger\.py|shared-python/src/shared_core/logger\.py|genesis/core/retry\.py|genesis/core/constants\.py|genesis/core/config\.py)' | xargs grep -E -n "$pattern" 2>/dev/null || true)
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

# Check for forbidden cross-module imports (../imports)
check_pattern 'from \.\.' "Cross-module imports (violates pure module isolation)" "." ''

check_pattern 'import \.\.' "Cross-module imports (violates pure module isolation)" "." ''

# Check for sibling module imports without proper dependency declaration
check_pattern 'from [a-zA-Z_][a-zA-Z0-9_]*\.(?!tests|test_)' "Potential sibling module imports (verify dependency declaration)" "." '(from shared_core|from genesis\.|import shared_core|import genesis\.)'

# Check for modules that can build independently
echo -e "${YELLOW}🔍 Checking: Module independence (can build in isolation)${NC}"

# Find directories with Makefile or pyproject.toml (potential modules)
# Exclude build artifacts, virtual environments, and other non-source directories
module_dirs=$(find . -name "Makefile" -o -name "pyproject.toml" | grep -v "^\./Makefile" | grep -v "^\./pyproject.toml" | grep -v -E '(\.venv|venv|__pycache__|\.git|node_modules|\.pytest_cache|build/|dist/|\.tox|\.coverage)' | xargs dirname | sort -u)

if [ -n "$module_dirs" ]; then
    failed_modules=""
    for module_dir in $module_dirs; do
        # Check if module has required isolation files
        module_name=$(basename "$module_dir")

        # Skip if it's a test directory or template
        if [[ "$module_dir" =~ (test|template) ]]; then
            continue
        fi

        missing_files=""
        if [ ! -f "$module_dir/Makefile" ] && [ ! -f "$module_dir/pyproject.toml" ]; then
            missing_files="$missing_files build configuration (Makefile or pyproject.toml), "
        fi

        if [ ! -d "$module_dir/tests" ] && [ ! -f "$module_dir/test_*.py" ]; then
            missing_files="$missing_files test suite, "
        fi

        if [ -n "$missing_files" ]; then
            failed_modules="$failed_modules$module_dir: Missing ${missing_files%%, }\n"
        fi
    done

    if [ -n "$failed_modules" ]; then
        echo -e "${RED}❌ Modules missing isolation requirements:${NC}"
        echo -e "$failed_modules"
        echo
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        echo -e "${GREEN}✅ All modules have proper isolation structure${NC}"
        echo
    fi
else
    echo -e "${GREEN}✅ No isolated modules found${NC}"
    echo
fi

# Check for proper dependency declaration in modules
echo -e "${YELLOW}🔍 Checking: Dependency declaration in modules${NC}"

if [ -n "$module_dirs" ]; then
    undeclared_deps=""
    for module_dir in $module_dirs; do
        # Skip test directories and templates
        if [[ "$module_dir" =~ (test|template) ]]; then
            continue
        fi

        # Look for imports in Python files
        if [ -d "$module_dir" ]; then
            python_files=$(find "$module_dir" -name "*.py" -not -path "*/tests/*" -not -name "test_*.py" 2>/dev/null || true)

            if [ -n "$python_files" ]; then
                # Extract imported packages (excluding standard library and relative imports)
                imports=$(echo "$python_files" | xargs grep -h -E "^(import|from) [a-zA-Z]" 2>/dev/null | grep -v -E "(^from \.|^import \.|test|mock)" | sed -E 's/^(import|from) ([a-zA-Z0-9_]+).*/\2/' | sort -u || true)

                if [ -n "$imports" ]; then
                    # Check if module has dependency declaration file
                    if [ -f "$module_dir/pyproject.toml" ]; then
                        # Extract dependencies from pyproject.toml
                        declared_deps=$(grep -A 20 "dependencies\s*=" "$module_dir/pyproject.toml" 2>/dev/null | grep -E "^\s*\"[a-zA-Z]" | sed -E 's/^\s*"([a-zA-Z0-9_-]+).*/\1/' || true)
                    elif [ -f "$module_dir/requirements.txt" ]; then
                        declared_deps=$(grep -E "^[a-zA-Z]" "$module_dir/requirements.txt" | sed -E 's/([a-zA-Z0-9_-]+).*/\1/' || true)
                    else
                        declared_deps=""
                    fi

                    # Check for undeclared imports (basic heuristic)
                    for import_pkg in $imports; do
                        # Skip standard library and genesis imports
                        if [[ ! "$import_pkg" =~ (os|sys|json|re|time|datetime|collections|itertools|functools|pathlib|genesis|shared_core) ]]; then
                            if [ -n "$declared_deps" ]; then
                                if ! echo "$declared_deps" | grep -q "$import_pkg"; then
                                    undeclared_deps="$undeclared_deps$module_dir: imports '$import_pkg' but not declared\n"
                                fi
                            else
                                undeclared_deps="$undeclared_deps$module_dir: imports '$import_pkg' but no dependency file found\n"
                            fi
                        fi
                    done
                fi
            fi
        fi
    done

    if [ -n "$undeclared_deps" ]; then
        echo -e "${RED}❌ Modules with potentially undeclared dependencies:${NC}"
        echo -e "$undeclared_deps" | head -10
        echo
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        echo -e "${GREEN}✅ All module dependencies appear to be declared${NC}"
        echo
    fi
fi

# Check for proper use of shared components when modules have declared Genesis dependencies
echo -e "${YELLOW}🔍 Checking: Use of shared components in modules with Genesis dependencies${NC}"

if [ -n "$module_dirs" ]; then
    misused_components=""
    for module_dir in $module_dirs; do
        # Skip test directories and templates
        if [[ "$module_dir" =~ (test|template) ]]; then
            continue
        fi

        # Check if module declares Genesis/shared_core dependencies
        has_genesis_deps=false
        if [ -f "$module_dir/pyproject.toml" ]; then
            if grep -q -E "(shared.core|genesis)" "$module_dir/pyproject.toml" 2>/dev/null; then
                has_genesis_deps=true
            fi
        elif [ -f "$module_dir/requirements.txt" ]; then
            if grep -q -E "(shared.core|genesis)" "$module_dir/requirements.txt" 2>/dev/null; then
                has_genesis_deps=true
            fi
        fi

        # Only check component usage if module has declared Genesis dependencies
        if [ "$has_genesis_deps" = true ]; then
            python_files=$(find "$module_dir" -name "*.py" -not -path "*/tests/*" -not -name "test_*.py" 2>/dev/null || true)

            if [ -n "$python_files" ]; then
                # Check for raw logging instead of shared logger
                # Raw logging imports should be replaced with shared_core logger
                raw_logging=$(echo "$python_files" | xargs grep -E "^import logging$|^from logging import|logging\.getLogger" 2>/dev/null || true)
                if [ -n "$raw_logging" ]; then
                    misused_components="$misused_components$module_dir: Uses raw logging instead of shared_core logger\n"
                fi

                # Check for raw env access instead of shared env utilities
                raw_env=$(echo "$python_files" | xargs grep -E "os\.environ\.get\(" 2>/dev/null || true)
                if [ -n "$raw_env" ]; then
                    misused_components="$misused_components$module_dir: Uses os.environ.get instead of shared_core.env\n"
                fi

                # Check for raw exceptions instead of shared error handling
                raw_exceptions=$(echo "$python_files" | xargs grep -E "raise (Exception|ValueError|RuntimeError|TypeError)\(" 2>/dev/null || true)
                if [ -n "$raw_exceptions" ]; then
                    misused_components="$misused_components$module_dir: Uses raw exceptions instead of shared error handling\n"
                fi
            fi
        fi
    done

    if [ -n "$misused_components" ]; then
        echo -e "${RED}❌ Modules with Genesis deps not using shared components:${NC}"
        echo -e "$misused_components" | head -10
        echo
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        echo -e "${GREEN}✅ Modules with Genesis deps properly use shared components${NC}"
        echo
    fi
fi

# Check for AI safety compliance (file count limits)
echo -e "${YELLOW}🔍 Checking: AI safety file count limits${NC}"

if [ -n "$module_dirs" ]; then
    large_modules=""
    for module_dir in $module_dirs; do
        # Skip test directories and templates
        if [[ "$module_dir" =~ (test|template) ]]; then
            continue
        fi

        # Count files in module (excluding hidden files and build artifacts)
        file_count=$(find "$module_dir" -type f -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" | grep -v -E '(__pycache__|\.git|node_modules|\.pytest_cache|build/|dist/)' | wc -l)

        if [ "$file_count" -gt 60 ]; then
            large_modules="$large_modules$module_dir: $file_count files (limit: 60)\n"
        fi
    done

    if [ -n "$large_modules" ]; then
        echo -e "${RED}❌ Modules exceeding AI safety file limits:${NC}"
        echo -e "$large_modules"
        echo
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        echo -e "${GREEN}✅ All modules within AI safety file limits${NC}"
        echo
    fi
fi

echo
if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}🎉 All modules follow pure module isolation principles!${NC}"
    echo -e "${GREEN}✅ Codebase maintains proper module boundaries${NC}"
else
    echo -e "${RED}❌ Found $ISSUES_FOUND categories of module isolation violations${NC}"
    echo -e "${YELLOW}💡 Fix suggestions:${NC}"
    echo "  • Remove '../' imports - use declared dependencies instead"
    echo "  • Add Makefile with test, build, lint, clean targets to modules"
    echo "  • Add independent test suites to each module"
    echo "  • Split large modules to stay under 60 files for AI safety"
    echo "  • Declare all external dependencies in pyproject.toml or requirements"
    echo "  • Use shared_core components when module declares Genesis dependencies"
    echo "  • Ensure modules can build and test independently"
    echo
    echo -e "${YELLOW}📖 See docs/architecture/pure-module-isolation.md for details${NC}"
    echo
    exit 1
fi
