#!/usr/bin/env bash
# Comprehensive File Organization Script for Genesis Projects
#
# This script enforces Genesis project file organization standards:
# 1. Organizes .genesis/scripts/ into proper subdirectories
# 2. Cleans up root directory clutter
# 3. Moves files to their proper locations
#
# Author: Genesis Framework
# Version: 2.0.0

set -euo pipefail

# Configuration
DRY_RUN=false
VERBOSE=false
AUTO_MODE=false  # Run without prompts (for hooks)
PROJECT_ROOT=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Statistics
MOVED_COUNT=0
CREATED_DIRS=0
SKIPPED_COUNT=0
TRASH_COUNT=0
TRASH_FILES=()

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Comprehensive file organization for Genesis projects.

OPTIONS:
    -d, --dry-run       Show what would be done without making changes
    -v, --verbose       Enable verbose output
    -a, --auto          Run automatically without prompts (for git hooks)
    -h, --help          Show this help message
    -r, --root PATH     Specify project root (default: auto-detect)

EXAMPLES:
    $0                              # Interactive organization
    $0 --dry-run                    # Preview changes
    $0 --auto                       # Run in hook mode (no prompts)
    $0 --root /path/to/project      # Organize specific project

DESCRIPTION:
    This script enforces two levels of organization:

    1. .genesis/scripts/ subdirectory structure:
       ├── build/       - Build, release, version management
       ├── docker/      - Container management
       ├── setup/       - Project setup and installation
       ├── utils/       - Shared utilities and common functions
       └── validation/  - Quality gates, linting, validation

    2. Root directory cleanup:
       - Documentation (.md) → docs/
       - Scripts (.sh) → scripts/
       - Tests (test_*, conftest.py) → tests/
       - Config files (.json, .yml) → config/

    Only these files allowed in root:
    - README.md, CLAUDE.md, LICENSE, SECURITY.md
    - Makefile, pyproject.toml, package.json
    - .gitignore, .envrc, .pre-commit-config.yaml
    - Dockerfile, docker-compose.yml
    - Main infrastructure files (main.tf, etc.)

EOF
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" >&2
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_verbose() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${BLUE}[VERBOSE]${NC} $1" >&2
    fi
}

detect_project_root() {
    local current_dir="$PWD"

    # Look for Genesis markers
    while [[ "$current_dir" != "/" ]]; do
        if [[ -f "$current_dir/pyproject.toml" ]] && [[ -d "$current_dir/.genesis" ]]; then
            echo "$current_dir"
            return 0
        elif [[ -f "$current_dir/package.json" ]] && [[ -d "$current_dir/.genesis" ]]; then
            echo "$current_dir"
            return 0
        elif [[ -f "$current_dir/Makefile" ]] && [[ -d "$current_dir/.genesis" ]]; then
            echo "$current_dir"
            return 0
        fi
        current_dir="$(dirname "$current_dir")"
    done

    # Fallback to current directory if .genesis exists
    if [[ -d "$PWD/.genesis" ]]; then
        echo "$PWD"
        return 0
    fi

    log_error "Could not detect Genesis project root. Use --root to specify."
    exit 1
}

create_directory_structure() {
    log_info "Creating directory structure..."

    # .genesis/scripts subdirectories
    local genesis_dirs=(
        ".genesis/scripts/build"
        ".genesis/scripts/docker"
        ".genesis/scripts/setup"
        ".genesis/scripts/utils"
        ".genesis/scripts/validation"
    )

    # Root organization directories
    local root_dirs=(
        "docs"
        "docs/summaries"
        "scripts"
        "scripts/testing"
        "tests"
        "config"
    )

    for dir in "${genesis_dirs[@]}" "${root_dirs[@]}"; do
        local target_dir="$PROJECT_ROOT/$dir"
        if [[ ! -d "$target_dir" ]]; then
            if [[ "$DRY_RUN" == "true" ]]; then
                log_verbose "Would create directory: $dir"
            else
                mkdir -p "$target_dir"
                log_verbose "Created directory: $dir"
                ((CREATED_DIRS++))
            fi
        fi
    done
}

get_genesis_script_category() {
    local script_name="$1"

    case "$script_name" in
        # Build category
        build.sh|bump-version.sh|release.sh|sync-versions.py|update-*.sh|version.py)
            echo "build"
            ;;
        # Docker category
        container-*.sh|docker-*.sh)
            echo "docker"
            ;;
        # Setup category
        install-*.sh|setup*.sh|setup-*.sh|*-setup.sh)
            echo "setup"
            ;;
        # Validation category
        validate*.sh|check-*.sh|audit-*.sh|*-validation.sh|validate-*.py)
            echo "validation"
            ;;
        # Utils category (default)
        *)
            echo "utils"
            ;;
    esac
}

organize_genesis_scripts() {
    log_info "Organizing .genesis/scripts/..."

    local genesis_scripts="$PROJECT_ROOT/.genesis/scripts"

    # Find all scripts directly in .genesis/scripts/
    while IFS= read -r -d '' script; do
        local script_name
        script_name="$(basename "$script")"
        local category
        category="$(get_genesis_script_category "$script_name")"
        local target_dir="$genesis_scripts/$category"
        local target_file="$target_dir/$script_name"

        # Skip if already in correct location
        if [[ "$script" == "$target_file" ]]; then
            log_verbose "Skipping (already organized): $script_name"
            ((SKIPPED_COUNT++))
            continue
        fi

        # Skip if in a subdirectory already
        if [[ "$(dirname "$script")" != "$genesis_scripts" ]]; then
            log_verbose "Skipping (in subdirectory): $script_name"
            ((SKIPPED_COUNT++))
            continue
        fi

        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "Would move: $script_name → .genesis/scripts/$category/"
        else
            mv "$script" "$target_file"
            log_success "Moved: $script_name → .genesis/scripts/$category/"
            ((MOVED_COUNT++))
        fi
    done < <(find "$genesis_scripts" -maxdepth 1 -type f \( -name "*.sh" -o -name "*.py" \) -print0 2>/dev/null || true)
}

should_keep_in_root() {
    local filename="$1"

    # Allowed files in root directory
    case "$filename" in
        # Documentation
        README.md|CLAUDE.md|LICENSE|SECURITY.md|CHANGELOG.md)
            return 0
            ;;
        # Configuration
        Makefile|pyproject.toml|package.json|poetry.lock|package-lock.json|poetry.toml)
            return 0
            ;;
        # Environment
        .gitignore|.envrc|.pre-commit-config.yaml|.env.example)
            return 0
            ;;
        # Infrastructure
        Dockerfile|docker-compose.yml|main.tf|variables.tf|versions.tf|terraform.tfvars)
            return 0
            ;;
        # Build artifacts (directories)
        pytest.ini|conftest.py)
            # These should be in tests/ but check if user customized
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

get_target_location() {
    local filename="$1"

    case "$filename" in
        # Summary/notes documentation
        *_SUMMARY.md|*_NOTES.md|*_CHECKLIST.md|IMPLEMENTATION_*.md|VERIFICATION*.md|ISSUE_*.md|BUG_*.md|FEATURE_*.md|FIX_*.md)
            echo "docs/summaries"
            ;;
        # General documentation
        *.md)
            echo "docs"
            ;;
        # Test scripts
        test_*.sh|validate_*.sh|*_test.sh|test-*.sh)
            echo "scripts/testing"
            ;;
        # Utility scripts
        *.sh)
            echo "scripts"
            ;;
        # Test files
        test_*.py|*_test.py|conftest.py)
            echo "tests"
            ;;
        # Configuration files
        *.json|*.yml|*.yaml|*.toml)
            # Exclude root-level config files
            if should_keep_in_root "$filename"; then
                echo "root"
            else
                echo "config"
            fi
            ;;
        # Unknown - skip
        *)
            echo "skip"
            ;;
    esac
}

is_trash_file() {
    local filename="$1"

    # Trash file patterns
    case "$filename" in
        # Backup files
        *.bak|*.backup|*~|*.orig|*.swp|*.swo)
            echo "backup"
            return 0
            ;;
        # Log and temp files
        *.log|*.tmp|*-output.txt|*.cache)
            echo "log/temp"
            return 0
            ;;
        # Diff and patch files (usually temporary)
        *.diff|*.patch)
            echo "diff/patch"
            return 0
            ;;
        # Compiled Python in wrong places
        *.pyc|*.pyo|__pycache__)
            echo "compiled"
            return 0
            ;;
        # OS junk
        .DS_Store|Thumbs.db|desktop.ini)
            echo "OS junk"
            return 0
            ;;
        # Editor junk
        *~|*.swp|*.swo|*.swn|.*.swp)
            echo "editor"
            return 0
            ;;
        # Empty or placeholder files
        .gitkeep|.keep)
            echo "placeholder"
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

identify_trash_files() {
    log_info "Identifying trash files..."

    # Find potential trash in root and subdirectories
    while IFS= read -r -d '' file; do
        local filename
        filename="$(basename "$file")"
        local trash_type

        if trash_type="$(is_trash_file "$filename")"; then
            TRASH_FILES+=("$file:$trash_type")
            ((TRASH_COUNT++))
            log_warning "Trash file ($trash_type): $file"
        fi
    done < <(find "$PROJECT_ROOT" -maxdepth 3 -type f \
        \( -name "*.bak" -o -name "*.backup" -o -name "*~" -o -name "*.orig" \
        -o -name "*.log" -o -name "*.tmp" -o -name "*.diff" -o -name "*.patch" \
        -o -name "*.pyc" -o -name "*.pyo" -o -name ".DS_Store" \
        -o -name "*.swp" -o -name "*.swo" \) \
        ! -path "*/.git/*" ! -path "*/.venv/*" ! -path "*/node_modules/*" \
        -print0 2>/dev/null || true)

    # Check for duplicate scripts (in both scripts/ and .genesis/scripts/)
    if [[ -d "$PROJECT_ROOT/scripts" ]] && [[ -d "$PROJECT_ROOT/.genesis/scripts" ]]; then
        while IFS= read -r -d '' script_file; do
            local script_name
            script_name="$(basename "$script_file")"
            local category
            category="$(get_genesis_script_category "$script_name")"
            local genesis_equivalent="$PROJECT_ROOT/.genesis/scripts/$category/$script_name"

            if [[ -f "$genesis_equivalent" ]]; then
                TRASH_FILES+=("$script_file:duplicate")
                ((TRASH_COUNT++))
                log_warning "Duplicate script: $script_file (exists in .genesis/scripts/$category/)"
            fi
        done < <(find "$PROJECT_ROOT/scripts" -type f \( -name "*.sh" -o -name "*.py" \) -print0 2>/dev/null || true)
    fi

    # Check for empty files (potential trash)
    while IFS= read -r -d '' empty_file; do
        # Skip intentional empty files
        local filename
        filename="$(basename "$empty_file")"
        if [[ "$filename" != ".gitkeep" ]] && [[ "$filename" != ".keep" ]] && [[ "$filename" != "__init__.py" ]]; then
            TRASH_FILES+=("$empty_file:empty")
            ((TRASH_COUNT++))
            log_warning "Empty file: $empty_file"
        fi
    done < <(find "$PROJECT_ROOT" -maxdepth 2 -type f -empty \
        ! -path "*/.git/*" ! -path "*/.venv/*" ! -name ".gitkeep" ! -name ".keep" ! -name "__init__.py" \
        -print0 2>/dev/null || true)
}

remove_trash_files() {
    if [[ ${#TRASH_FILES[@]} -eq 0 ]]; then
        log_info "No trash files to remove"
        return 0
    fi

    log_info "Removing ${#TRASH_FILES[@]} trash files..."

    for trash_entry in "${TRASH_FILES[@]}"; do
        local file="${trash_entry%:*}"
        local trash_type="${trash_entry#*:}"

        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "Would remove ($trash_type): $file"
        else
            rm -f "$file"
            log_success "Removed ($trash_type): $(basename "$file")"
        fi
    done
}

organize_root_directory() {
    log_info "Organizing root directory..."

    # Find all files in root (excluding hidden files and directories)
    while IFS= read -r -d '' file; do
        local filename
        filename="$(basename "$file")"

        # Skip if should stay in root
        if should_keep_in_root "$filename"; then
            log_verbose "Keeping in root: $filename"
            continue
        fi

        # Get target location
        local target_location
        target_location="$(get_target_location "$filename")"

        # Skip if no target
        if [[ "$target_location" == "skip" ]] || [[ "$target_location" == "root" ]]; then
            log_verbose "Skipping: $filename"
            ((SKIPPED_COUNT++))
            continue
        fi

        local target_dir="$PROJECT_ROOT/$target_location"
        local target_file="$target_dir/$filename"

        # Skip if target already exists
        if [[ -e "$target_file" ]]; then
            log_warning "Target exists, skipping: $filename (would go to $target_location/)"
            ((SKIPPED_COUNT++))
            continue
        fi

        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "Would move: $filename → $target_location/"
        else
            mv "$file" "$target_file"
            log_success "Moved: $filename → $target_location/"
            ((MOVED_COUNT++))
        fi
    done < <(find "$PROJECT_ROOT" -maxdepth 1 -type f ! -name ".*" -print0 2>/dev/null || true)
}

print_summary() {
    echo ""
    log_info "═══════════════════════════════════════════════════"
    log_info "Organization Summary"
    log_info "═══════════════════════════════════════════════════"
    log_success "Directories created: $CREATED_DIRS"
    log_success "Files moved: $MOVED_COUNT"
    log_warning "Trash files found: $TRASH_COUNT"
    log_info "Files skipped: $SKIPPED_COUNT"

    if [[ "$TRASH_COUNT" -gt 0 ]]; then
        echo ""
        log_info "Trash files by type:"
        local backup_count=0
        local log_count=0
        local diff_count=0
        local duplicate_count=0
        local empty_count=0
        local other_count=0

        for trash_entry in "${TRASH_FILES[@]}"; do
            local trash_type="${trash_entry#*:}"
            case "$trash_type" in
                backup) ((backup_count++)) ;;
                "log/temp") ((log_count++)) ;;
                "diff/patch") ((diff_count++)) ;;
                duplicate) ((duplicate_count++)) ;;
                empty) ((empty_count++)) ;;
                *) ((other_count++)) ;;
            esac
        done

        [[ $backup_count -gt 0 ]] && log_info "  • Backup files: $backup_count"
        [[ $log_count -gt 0 ]] && log_info "  • Log/temp files: $log_count"
        [[ $diff_count -gt 0 ]] && log_info "  • Diff/patch files: $diff_count"
        [[ $duplicate_count -gt 0 ]] && log_info "  • Duplicate scripts: $duplicate_count"
        [[ $empty_count -gt 0 ]] && log_info "  • Empty files: $empty_count"
        [[ $other_count -gt 0 ]] && log_info "  • Other trash: $other_count"
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        echo ""
        log_warning "DRY RUN - No changes were made"
        log_info "Run without --dry-run to apply changes"
    fi

    echo ""
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -a|--auto)
            AUTO_MODE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -r|--root)
            PROJECT_ROOT="$2"
            shift 2
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    log_info "Genesis File Organization Script v2.0.0"
    echo ""

    # Detect project root if not specified
    if [[ -z "$PROJECT_ROOT" ]]; then
        PROJECT_ROOT="$(detect_project_root)"
    fi

    log_info "Project root: $PROJECT_ROOT"
    echo ""

    # Confirm if not in auto mode
    if [[ "$AUTO_MODE" == "false" ]] && [[ "$DRY_RUN" == "false" ]]; then
        read -p "Proceed with file organization? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_warning "Cancelled by user"
            exit 0
        fi
    fi

    # Create directory structure
    create_directory_structure

    # Organize files
    organize_genesis_scripts
    organize_root_directory

    # Identify trash files
    identify_trash_files

    # Remove trash files (with confirmation if not auto mode)
    if [[ "$TRASH_COUNT" -gt 0 ]]; then
        if [[ "$AUTO_MODE" == "false" ]] && [[ "$DRY_RUN" == "false" ]]; then
            echo ""
            read -p "Remove $TRASH_COUNT trash files? (y/N) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                remove_trash_files
            else
                log_info "Skipping trash removal"
            fi
        elif [[ "$AUTO_MODE" == "true" ]] && [[ "$DRY_RUN" == "false" ]]; then
            # In auto mode, remove trash without prompting
            remove_trash_files
        fi
    fi

    # Print summary
    print_summary

    # Exit with appropriate code
    if [[ "$MOVED_COUNT" -gt 0 ]]; then
        exit 0
    else
        log_info "No files needed organization"
        exit 0
    fi
}

main
