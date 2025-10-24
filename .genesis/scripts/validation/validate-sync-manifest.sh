#!/usr/bin/env bash
# Validates Genesis client project against sync.yml manifest
# Ensures all required files exist, are in correct locations, and have proper permissions

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
PROJECT_PATH="."
VERBOSE="${VERBOSE:-false}"
FIX_ISSUES="${FIX:-false}"
TOTAL_ERRORS=0
TOTAL_WARNINGS=0
TOTAL_SUCCESS=0

# Parse command line arguments first
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --fix)
            FIX_ISSUES=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS] [PROJECT_PATH]"
            echo ""
            echo "Options:"
            echo "  --verbose, -v    Show detailed output"
            echo "  --fix           Attempt to fix issues automatically"
            echo "  --help, -h      Show this help message"
            echo ""
            echo "Environment variables:"
            echo "  VERBOSE=true    Same as --verbose"
            echo "  FIX=true        Same as --fix"
            exit 0
            ;;
        *)
            PROJECT_PATH="$1"
            shift
            ;;
    esac
done

echo "🔍 Validating Genesis project against manifest: $PROJECT_PATH"
echo

cd "$PROJECT_PATH"

# Helper functions
log_error() {
    echo -e "${RED}❌ $1${NC}" >&2
    TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    TOTAL_WARNINGS=$((TOTAL_WARNINGS + 1))
}

log_success() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${GREEN}✅ $1${NC}"
    fi
    TOTAL_SUCCESS=$((TOTAL_SUCCESS + 1))
}

log_info() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${BLUE}ℹ️  $1${NC}"
    fi
}

# Check if Genesis directory exists
check_genesis_dir() {
    if [[ ! -d ".genesis" ]]; then
        log_error ".genesis directory not found - not a Genesis project"
        exit 1
    fi
    log_success ".genesis directory exists"
}

# Load and validate sync.yml
validate_sync_config() {
    local sync_file=".genesis/sync.yml"

    if [[ ! -f "$sync_file" ]]; then
        log_error "$sync_file not found - run 'genesis init' to create it"
        return 1
    fi

    log_success "Found sync.yml configuration"

    # Parse sync.yml and validate files
    # Create a temporary Python script to parse YAML
    cat > /tmp/parse_sync_yml.py << 'PYTHON_EOF'
import yaml
import sys
import os

try:
    with open('.genesis/sync.yml', 'r') as f:
        config = yaml.safe_load(f)

    if 'files' not in config:
        print("NO_FILES_SECTION")
        sys.exit(0)

    for file_entry in config.get('files', []):
        dest = file_entry.get('dest', '')
        sync_policy = file_entry.get('sync', 'if_unchanged')
        if dest:
            print(f"{dest}|{sync_policy}")

except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_EOF

    # Execute the Python script
    if python3 /tmp/parse_sync_yml.py 2>/dev/null; then
        rm -f /tmp/parse_sync_yml.py
        return 0
    else
        rm -f /tmp/parse_sync_yml.py
        log_error "Failed to parse sync.yml - ensure it's valid YAML"
        return 1
    fi
}

# Validate files from sync.yml
validate_manifest_files() {
    log_info "Checking files from sync manifest..."

    # Get file list from sync.yml
    local files_list
    files_list=$(validate_sync_config)

    if [[ "$files_list" == "NO_FILES_SECTION" ]]; then
        log_warning "No files section in sync.yml"
        return 0
    fi

    if [[ -z "$files_list" ]]; then
        return 1
    fi

    # Process each file
    while IFS='|' read -r file_path sync_policy; do
        if [[ -z "$file_path" ]]; then
            continue
        fi

        if [[ -f "$file_path" ]]; then
            log_success "$file_path exists (sync: $sync_policy)"

            # Check if it's a symlink when it shouldn't be
            if [[ -L "$file_path" ]]; then
                log_warning "$file_path is a symlink"
            fi
        else
            # Determine severity based on sync policy
            case "$sync_policy" in
                "always")
                    log_error "$file_path missing (required, sync: always)"
                    if [[ "$FIX_ISSUES" == "true" ]]; then
                        echo "  🔧 Run 'genesis sync' to restore this file"
                    fi
                    ;;
                "if_unchanged")
                    log_warning "$file_path missing (optional, sync: if_unchanged)"
                    ;;
                "never")
                    # Files with 'never' policy are completely optional
                    log_info "$file_path not required (sync: never)"
                    ;;
            esac
        fi
    done <<< "$files_list"
}

# Check executable permissions on scripts
check_script_permissions() {
    log_info "Checking script permissions..."

    local script_dirs=("scripts" ".genesis/scripts")
    local permission_errors=0

    for dir in "${script_dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            continue
        fi

        # Find all .sh files
        while IFS= read -r -d '' script; do
            if [[ ! -x "$script" ]]; then
                log_error "$script is not executable"
                permission_errors=$((permission_errors + 1))

                if [[ "$FIX_ISSUES" == "true" ]]; then
                    chmod +x "$script"
                    echo "  🔧 Fixed: Made $script executable"
                else
                    echo "  💡 Fix with: chmod +x $script"
                fi
            else
                log_success "$script is executable"
            fi
        done < <(find "$dir" -name "*.sh" -type f -print0 2>/dev/null)
    done

    if [[ $permission_errors -eq 0 ]]; then
        log_success "All shell scripts have correct permissions"
    fi
}

# Check core Genesis components
check_genesis_components() {
    log_info "Checking core Genesis components..."

    # Core files that should typically exist
    local core_files=(
        "Makefile:Build automation"
        "pyproject.toml:Python project configuration"
        ".envrc:Environment configuration"
        ".pre-commit-config.yaml:Pre-commit hooks"
    )

    for entry in "${core_files[@]}"; do
        IFS=':' read -r file desc <<< "$entry"

        if [[ -f "$file" ]]; then
            log_success "$file present ($desc)"
        else
            # These are warnings not errors since they may not apply to all project types
            log_warning "$file not found ($desc)"
        fi
    done
}

# Check AI safety file limits
check_ai_safety() {
    log_info "Checking AI safety file limits..."

    local max_files="${AI_MAX_FILES:-550}"
    local worktree_max="${WORKTREE_MAX_FILES:-80}"

    # Count files using git if available
    if git rev-parse --git-dir > /dev/null 2>&1; then
        local file_count
        file_count=$(git ls-files 2>/dev/null | wc -l | tr -d ' ')

        if [[ $file_count -le $max_files ]]; then
            log_success "File count: $file_count (AI-safe: ≤$max_files)"
        else
            log_warning "File count: $file_count exceeds AI limit ($max_files)"
            echo "  💡 Consider using 'genesis worktree create' with limit of $worktree_max files"
        fi
    else
        log_warning "Not a git repository - cannot check file count"
    fi
}

# Fix common issues
fix_issues() {
    if [[ "$FIX_ISSUES" != "true" ]]; then
        return
    fi

    echo
    echo "🔧 Attempting to fix issues..."

    # Run genesis sync for missing files
    if [[ $TOTAL_ERRORS -gt 0 ]] && command -v genesis &> /dev/null; then
        echo "  🔄 Running 'genesis sync' to restore missing files..."
        if genesis sync 2>&1; then
            echo "  ✅ Successfully ran genesis sync"
        else
            echo "  ❌ Genesis sync failed"
        fi
    fi
}

# Main validation flow
main() {
    check_genesis_dir
    validate_manifest_files
    check_script_permissions
    check_genesis_components
    check_ai_safety

    # Summary
    echo
    echo "📊 Validation Summary:"
    echo "  ✅ Success: $TOTAL_SUCCESS checks passed"

    if [[ $TOTAL_WARNINGS -gt 0 ]]; then
        echo "  ⚠️  Warnings: $TOTAL_WARNINGS"
    fi

    if [[ $TOTAL_ERRORS -gt 0 ]]; then
        echo "  ❌ Errors: $TOTAL_ERRORS"
    fi

    # Final status
    echo
    if [[ $TOTAL_ERRORS -eq 0 ]]; then
        if [[ $TOTAL_WARNINGS -gt 0 ]]; then
            echo -e "${GREEN}✅ Validation passed with warnings${NC}"
        else
            echo -e "${GREEN}✅ Validation passed - all checks successful!${NC}"
        fi
        exit 0
    else
        echo -e "${RED}❌ Validation failed with $TOTAL_ERRORS error(s)${NC}"

        if [[ "$FIX_ISSUES" != "true" ]]; then
            echo -e "${BLUE}💡 Run with FIX=true to attempt automatic fixes${NC}"
        fi

        exit 1
    fi
}

# Run validation
main

# Attempt fixes if requested
fix_issues

# Re-run validation if fixes were applied
if [[ "$FIX_ISSUES" == "true" ]] && [[ $TOTAL_ERRORS -gt 0 ]]; then
    echo
    echo "🔍 Re-validating after fixes..."
    TOTAL_ERRORS=0
    TOTAL_WARNINGS=0
    TOTAL_SUCCESS=0
    main
fi
