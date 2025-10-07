#!/usr/bin/env bash
# Check for proper file organization and detect clutter

set -euo pipefail

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

ISSUES_FOUND=0

log_check() {
    echo -e "${BLUE}🔍 $1${NC}"
}

log_issue() {
    echo -e "${YELLOW}📋 $1${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

detect_project_type() {
    if [ -f "pyproject.toml" ] || [ -f "requirements.txt" ] || [ -f "setup.py" ]; then
        echo "python"
    elif [ -f "package.json" ]; then
        echo "nodejs"
    elif [ -f "Cargo.toml" ]; then
        echo "rust"
    elif [ -f "main.tf" ] || [ -f "variables.tf" ]; then
        echo "terraform"
    elif [ -f "go.mod" ]; then
        echo "golang"
    else
        echo "generic"
    fi
}

# Pure Module Isolation Detection
detect_architecture() {
    # Check for Pure Module Isolation indicators
    local isolated_modules=()

    for dir in */; do
        if [[ -d "$dir" && "$dir" != "." && "$dir" != ".." ]]; then
            local dir_name="${dir%/}"
            # Skip common non-module directories
            if [[ ! "$dir_name" =~ ^(\.|node_modules|venv|\.venv|__pycache__|\.git|scratch|dist|build)$ ]]; then
                # Check if directory has module characteristics
                if [[ -f "$dir/Makefile" ]] || [[ -f "$dir/pyproject.toml" ]] || [[ -f "$dir/package.json" ]]; then
                    isolated_modules+=("$dir_name")
                fi
            fi
        fi
    done

    if [[ ${#isolated_modules[@]} -gt 0 ]]; then
        echo "pure_module_isolation"
    else
        echo "traditional"
    fi
}

echo "🗂️  Checking project file organization..."
PROJECT_TYPE=$(detect_project_type)
log_check "Detected project type: $PROJECT_TYPE"

# Define expected structure based on architecture
ARCHITECTURE=$(detect_architecture)
log_check "Detected architecture: $ARCHITECTURE"
echo

get_allowed_root_files() {
    local project_type="$1"
    local files=(
        # Universal files
        "README\.md"
        "CLAUDE\.md"
        "CHANGELOG\.md"
        "Makefile"
        "LICENSE"
        "SECURITY\.md"
        "CONTRIBUTING\.md"
        "CODE_OF_CONDUCT\.md"
        "\.gitignore"
        "\.envrc"
        "\.env\.example"
        # Docker files
        "Dockerfile"
        "docker-compose\.yml"
        "\.dockerignore"
    )

    case "$project_type" in
        python)
            files+=(
                "pyproject\.toml"
                "poetry\.lock"
                "requirements\.txt"
                "requirements-dev\.txt"
                "setup\.py"
                "pytest\.ini"
                "tox\.ini"
            )
            ;;
        nodejs)
            files+=(
                "package\.json"
                "package-lock\.json"
                "yarn\.lock"
                "pnpm-lock\.yaml"
                "tsconfig\.json"
                "jest\.config\.js"
                "\.nvmrc"
            )
            ;;
        rust)
            files+=(
                "Cargo\.toml"
                "Cargo\.lock"
            )
            ;;
        terraform)
            files+=(
                "main\.tf"
                "variables\.tf"
                "outputs\.tf"
                "terraform\.tfvars\.example"
                "versions\.tf"
            )
            ;;
        golang)
            files+=(
                "go\.mod"
                "go\.sum"
            )
            ;;
    esac

    printf '%s\n' "${files[@]}"
}

# Get allowed files for the detected project type
ALLOWED_ROOT_FILES=($(get_allowed_root_files "$PROJECT_TYPE"))

check_root_clutter() {
    log_check "Checking for files cluttering project root"

    local found_issues=false

    # Check all files in root (not directories) - only if they exist
    for file in *; do
        # Skip if file doesn't exist (e.g., glob didn't match anything)
        if [ ! -e "$file" ]; then
            continue
        fi

        if [ -f "$file" ]; then
            local allowed=false

            # Check against allowed patterns
            for pattern in "${ALLOWED_ROOT_FILES[@]}"; do
                if [[ "$file" =~ ^${pattern}$ ]]; then
                    allowed=true
                    break
                fi
            done

            if [ "$allowed" = false ]; then
                if [ "$found_issues" = false ]; then
                    log_issue "Files in wrong location - should be moved:"
                    found_issues=true
                fi
                echo "  ❌ File '$file' should not be in root directory"

                # Suggest where it should go
                case "$file" in
                    *.md)
                        if [[ ! "$file" =~ ^(README|CLAUDE|SECURITY|LICENSE|CHANGELOG)\.md$ ]]; then
                            echo "  ℹ️    → Move to: docs/"
                        fi
                        ;;
                    *.sh)
                        echo "  ℹ️    → Move to: scripts/"
                        ;;
                    *.py)
                        if [[ "$file" =~ ^test_ ]] || [[ "$file" == *test.py ]] || [[ "$file" == conftest.py ]]; then
                            echo "  ℹ️    → Move to: tests/"
                        else
                            echo "  ℹ️    → Move to: src/"
                        fi
                        ;;
                    *.js|*.ts)
                        if [[ "$file" =~ \.test\. ]] || [[ "$file" =~ \.spec\. ]]; then
                            echo "  ℹ️    → Move to: tests/"
                        else
                            echo "  ℹ️    → Move to: src/"
                        fi
                        ;;
                    *.json)
                        if [[ ! "$file" =~ ^(package|package-lock|yarn|pnpm-lock|tsconfig|jest\.config)\.json$ ]]; then
                            echo "  ℹ️    → Move to: config/"
                        fi
                        ;;
                    *.yml|*.yaml)
                        if [[ ! "$file" =~ ^(docker-compose)\.ya?ml$ ]]; then
                            echo "  ℹ️    → Move to: .github/workflows/ or config/"
                        fi
                        ;;
                    .*)
                        if [[ ! "$file" =~ ^\.(gitignore|envrc|env\.example|dockerignore)$ ]]; then
                            echo "  ℹ️    → Consider organizing into appropriate subdirectory"
                        fi
                        ;;
                    *)
                        echo "  ℹ️    → Consider organizing into appropriate subdirectory"
                        ;;
                esac
            fi
        fi
    done

    if [ "$found_issues" = false ]; then
        log_success "Project root is clean"
    fi
    echo
}

check_misplaced_scripts() {
    log_check "Checking for scripts outside scripts/ directory"

    local found_issues=false

    if [[ "$ARCHITECTURE" == "pure_module_isolation" ]]; then
        # In Pure Module Isolation, scripts can be in module directories or main scripts/
        if command -v find >/dev/null 2>&1; then
            local misplaced_scripts=$(find . -name "*.sh" \
                -not -path "./scripts/*" \
                -not -path "./*/scripts/*" \
                -not -path "./.genesis/*" \
                -not -path "./.claude/*" \
                -not -path "./.git/*" \
                -not -path "./node_modules/*" \
                -not -path "./.venv/*" \
                -not -path "./venv/*" \
                2>/dev/null || true)

            if [ -n "$misplaced_scripts" ]; then
                log_issue "Shell scripts in wrong location:"
                echo "$misplaced_scripts" | while read -r script; do
                    echo "  $script → Should be in scripts/"
                done
                found_issues=true
            fi
        fi
    else
        # Traditional structure - scripts should be in scripts/ directory
        if command -v find >/dev/null 2>&1; then
            local misplaced_scripts=$(find . -name "*.sh" \
                -not -path "./scripts/*" \
                -not -path "./*/src/*" \
                -not -path "./*/tests/*" \
                -not -path "./.genesis/*" \
                -not -path "./.claude/*" \
                -not -path "./.git/*" \
                -not -path "./node_modules/*" \
                -not -path "./.venv/*" \
                -not -path "./venv/*" \
                2>/dev/null || true)

            if [ -n "$misplaced_scripts" ]; then
                log_issue "Shell scripts in wrong location:"
                echo "$misplaced_scripts" | while read -r script; do
                    echo "  $script → Should be in scripts/"
                done
                found_issues=true
            fi
        fi
    fi

    if [ "$found_issues" = false ]; then
        log_success "All shell scripts properly located"
    fi
    echo
}

check_documentation_organization() {
    log_check "Checking and cleaning up documentation organization"

    local files_moved=0

    # Ensure scratch directory exists
    mkdir -p scratch/

    # Find loose .md files in project root and move to scratch/
    # Skip important root documentation files
    if command -v find >/dev/null 2>&1; then
        local loose_docs=$(find . -maxdepth 1 -name "*.md" \
            -not -name "README.md" \
            -not -name "CLAUDE.md" \
            -not -name "CHANGELOG.md" \
            -not -name "CONTRIBUTING.md" \
            -not -name "CODE_OF_CONDUCT.md" \
            -not -name "SECURITY.md" \
            -not -name "LICENSE.md" \
            2>/dev/null || true)

        if [ -n "$loose_docs" ]; then
            echo -e "${YELLOW}📦 Moving loose documentation files to scratch/${NC}"
            echo "$loose_docs" | while read -r doc; do
                if [ -f "$doc" ]; then
                    mv "$doc" "scratch/"
                    echo "  Moved: $doc → scratch/"
                    files_moved=$((files_moved + 1))
                fi
            done
        fi

        # Find files directly in docs/ root (except README.md and CLAUDE.md) and move to scratch/
        if [ -d "docs" ]; then
            local docs_root_files=$(find ./docs -maxdepth 1 -name "*.md" \
                -not -name "README.md" \
                -not -name "CLAUDE.md" \
                2>/dev/null || true)

            if [ -n "$docs_root_files" ]; then
                echo -e "${YELLOW}📦 Moving files from docs/ root to scratch/${NC}"
                echo "$docs_root_files" | while read -r doc; do
                    if [ -f "$doc" ]; then
                        filename=$(basename "$doc")
                        mv "$doc" "scratch/docs-${filename}"
                        echo "  Moved: $doc → scratch/docs-${filename}"
                        files_moved=$((files_moved + 1))
                    fi
                done
            fi
        fi
    fi

    if [ $files_moved -eq 0 ]; then
        log_success "Documentation properly organized"
    else
        echo -e "${GREEN}✅ Moved $files_moved files to scratch/ for reorganization${NC}"
    fi
    echo
}

check_test_organization() {
    log_check "Checking test file organization"

    local found_issues=false

    # Find test files outside of tests/ directories
    if command -v find >/dev/null 2>&1; then
        local misplaced_tests=$(find . \( -name "*test*.py" -o -name "*test*.js" -o -name "*test*.ts" -o -name "conftest.py" \) \
            -not -path "./tests/*" \
            -not -path "./**/tests/*" \
            -not -path "./.git/*" \
            -not -path "./node_modules/*" \
            -not -path "./.venv/*" \
            -not -path "./venv/*" \
            2>/dev/null || true)

        if [ -n "$misplaced_tests" ]; then
            log_issue "Test files in wrong location:"
            echo "$misplaced_tests" | while read -r test; do
                echo "  $test → Should be in tests/"
            done
            found_issues=true
        fi
    fi

    if [ "$found_issues" = false ]; then
        log_success "Test files properly organized"
    fi
    echo
}

check_pure_module_isolation() {
    if [[ "$ARCHITECTURE" != "pure_module_isolation" ]]; then
        return
    fi

    log_check "Checking Pure Module Isolation compliance"

    local found_issues=false
    local module_count=0

    # Check each potential module
    for dir in */; do
        if [[ -d "$dir" && "$dir" != "." && "$dir" != ".." ]]; then
            local dir_name="${dir%/}"
            # Skip common non-module directories
            if [[ ! "$dir_name" =~ ^(\.|node_modules|venv|\.venv|__pycache__|\.git|scratch|dist|build)$ ]]; then
                if [[ -f "$dir/Makefile" ]] || [[ -f "$dir/pyproject.toml" ]] || [[ -f "$dir/package.json" ]]; then
                    module_count=$((module_count + 1))

                    # Count files in module (AI safety limit)
                    local file_count=$(find "$dir" -type f 2>/dev/null | wc -l || echo 0)
                    if [[ $file_count -gt 60 ]]; then
                        if [ "$found_issues" = false ]; then
                            log_issue "Modules exceeding AI safety limits:"
                            found_issues=true
                        fi
                        echo "  📁 $dir_name/ ($file_count files) → AI safety limit is <60 files"
                    fi

                    # Check for independent build capability
                    if [[ ! -f "$dir/Makefile" ]]; then
                        if [ "$found_issues" = false ]; then
                            log_issue "Modules missing build files:"
                            found_issues=true
                        fi
                        echo "  📁 $dir_name/ → Missing Makefile for independent build"
                    fi
                fi
            fi
        fi
    done

    if [[ $module_count -gt 0 ]]; then
        log_success "Detected $module_count isolated modules"
    fi

    if [ "$found_issues" = false ]; then
        log_success "Pure Module Isolation compliance looks good"
    fi
    echo
}

check_directory_structure() {
    if [[ "$ARCHITECTURE" == "pure_module_isolation" ]]; then
        check_pure_module_isolation
        return
    fi

    log_check "Checking for standard directory structure"

    local missing_dirs=()
    local suggested_dirs=("src/" "tests/" "docs/" "scripts/" "config/")

    # Check which directories exist
    for dir in "${suggested_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            # src/ and tests/ are more important
            if [[ "$dir" == "src/" ]] || [[ "$dir" == "tests/" ]]; then
                missing_dirs+=("$dir")
            fi
        fi
    done

    if [ ${#missing_dirs[@]} -gt 0 ]; then
        log_issue "Missing important directories:"
        for dir in "${missing_dirs[@]}"; do
            echo "  📁 $dir - recommended for source code and tests"
        done
    fi

    if [ ${#suggested_dirs[@]} -gt 0 ]; then
        log_check "Suggested directories for better organization:"
        for dir in "${suggested_dirs[@]}"; do
            echo "  📁 $dir - helps organize project files"
        done
    fi

    if [ ${#missing_dirs[@]} -eq 0 ] && [ ${#suggested_dirs[@]} -eq 0 ]; then
        log_success "Good directory structure"
    fi
    echo
}

check_directory_documentation() {
    log_check "Checking directory documentation"

    local found_issues=false

    # Important directories that should have documentation
    local important_dirs=(
        "src"
        "scripts"
        "docs"
        "config"
    )

    for dir in "${important_dirs[@]}"; do
        if [ -d "$dir" ]; then
            # Count files in directory (excluding subdirectories and hidden files)
            local file_count=$(find "$dir" -maxdepth 1 -type f -not -name ".*" 2>/dev/null | wc -l || echo 0)

            # Check for README.md only if directory has significant files
            if [ "$file_count" -ge 3 ]; then
                if [ ! -f "$dir/README.md" ]; then
                    if [ "$found_issues" = false ]; then
                        log_issue "Directories missing documentation (README.md):"
                        found_issues=true
                    fi
                    echo "  📝 $dir ($file_count files) - consider adding README.md"
                fi
            fi
        fi
    done

    if [ "$found_issues" = false ]; then
        log_success "Directory documentation looks good"
    fi
    echo
}

# Run all checks
check_root_clutter
check_misplaced_scripts
check_documentation_organization
check_test_organization
check_directory_structure
check_directory_documentation

echo
if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}🎉 Project organization is excellent!${NC}"
    exit 0
else
    echo -e "${YELLOW}📝 File organization check: Found $ISSUES_FOUND suggestions for improvement${NC}"
    echo -e "${BLUE}💡 These are recommendations, not errors - your code works fine!${NC}"
    echo -e "${BLUE}ℹ️  Consider moving files to conventional locations when convenient${NC}"
    # Exit 0 so this doesn't block development - these are just suggestions
    exit 0
fi
