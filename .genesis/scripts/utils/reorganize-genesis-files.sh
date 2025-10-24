#!/usr/bin/env bash
# Genesis File Reorganization Script
#
# This script reorganizes Genesis projects to use the proper subdirectory structure
# for .genesis/scripts/ and removes duplicate files. It can be run on both the
# Genesis development project and client projects using Genesis.
#
# Directory Structure:
# .genesis/scripts/
# ├── build/           - Build, release, and version management scripts
# ├── docker/          - Container management scripts
# ├── setup/           - Project setup and installation scripts
# ├── utils/           - Shared utilities and common functions
# └── validation/      - Quality gates, linting, and validation scripts
#
# Author: Genesis Framework
# Version: 1.0.0

set -euo pipefail

# Configuration
DRY_RUN=false
VERBOSE=false
PROJECT_ROOT=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Reorganizes Genesis project files into proper subdirectory structure.

OPTIONS:
    -d, --dry-run       Show what would be done without making changes
    -v, --verbose       Enable verbose output
    -h, --help          Show this help message
    -r, --root PATH     Specify project root (default: auto-detect)

EXAMPLES:
    $0                              # Reorganize current project
    $0 --dry-run                    # Preview changes
    $0 --root /path/to/project      # Reorganize specific project

DESCRIPTION:
    This script reorganizes Genesis project files by:
    1. Creating proper .genesis/scripts/ subdirectory structure
    2. Moving scripts to appropriate categories
    3. Removing duplicate files from root scripts/
    4. Updating all file references in configurations

    Safe to run multiple times - idempotent operation.
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
    local genesis_scripts="$PROJECT_ROOT/.genesis/scripts"

    log_info "Creating .genesis/scripts subdirectory structure..."

    local directories=(
        "build"
        "docker"
        "setup"
        "utils"
        "validation"
    )

    for dir in "${directories[@]}"; do
        local target_dir="$genesis_scripts/$dir"
        if [[ "$DRY_RUN" == "true" ]]; then
            log_verbose "Would create directory: $target_dir"
        else
            mkdir -p "$target_dir"
            log_verbose "Created directory: $target_dir"
        fi
    done
}

get_script_category() {
    local script_name="$1"

    case "$script_name" in
        # Build category
        build.sh|bump-version.sh|release.sh|sync-versions.py|update-embedded-manifest.py|update-releases-manifest.sh|version.py)
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
        check-*.sh|validate-*.sh|find-*.sh|*-check-*.sh|validate-*.py)
            echo "validation"
            ;;
        # Utils category (fallback for common utilities)
        common-*.sh|audit-*.sh|*-functions.sh)
            echo "utils"
            ;;
        *)
            # Unknown - put in utils as fallback
            log_warning "Unknown script category for $script_name, placing in utils/"
            echo "utils"
            ;;
    esac
}

reorganize_scripts() {
    local genesis_scripts="$PROJECT_ROOT/.genesis/scripts"

    if [[ ! -d "$genesis_scripts" ]]; then
        log_warning "No .genesis/scripts directory found"
        return 0
    fi

    log_info "Reorganizing scripts in .genesis/scripts/..."

    # Find all scripts in root of .genesis/scripts
    while IFS= read -r -d '' script_file; do
        local script_name="$(basename "$script_file")"
        local category="$(get_script_category "$script_name")"
        local target_dir="$genesis_scripts/$category"
        local target_file="$target_dir/$script_name"

        # Skip if already in correct location
        if [[ "$(dirname "$script_file")" == "$target_dir" ]]; then
            log_verbose "Script $script_name already in correct location: $category/"
            continue
        fi

        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "Would move: $script_name -> $category/"
        else
            mv "$script_file" "$target_file"
            log_success "Moved: $script_name -> $category/"
        fi
    done < <(find "$genesis_scripts" -maxdepth 1 -type f \( -name "*.sh" -o -name "*.py" \) -print0 2>/dev/null || true)
}

remove_duplicate_scripts() {
    local root_scripts="$PROJECT_ROOT/scripts"

    if [[ ! -d "$root_scripts" ]]; then
        log_verbose "No root scripts/ directory found"
        return 0
    fi

    log_info "Checking for duplicate scripts in root scripts/ directory..."

    # Find scripts that might be duplicates of .genesis/scripts
    while IFS= read -r -d '' script_file; do
        local script_name="$(basename "$script_file")"
        local category="$(get_script_category "$script_name")"
        local genesis_equivalent="$PROJECT_ROOT/.genesis/scripts/$category/$script_name"

        if [[ -f "$genesis_equivalent" ]]; then
            if [[ "$DRY_RUN" == "true" ]]; then
                log_info "Would remove duplicate: scripts/$script_name (exists in .genesis/scripts/$category/)"
            else
                rm "$script_file"
                log_success "Removed duplicate: scripts/$script_name"
            fi
        fi
    done < <(find "$root_scripts" -type f \( -name "*.sh" -o -name "*.py" \) -print0 2>/dev/null || true)

    # Remove empty directories
    if [[ "$DRY_RUN" == "false" ]]; then
        find "$root_scripts" -type d -empty -delete 2>/dev/null || true
    fi
}

update_makefile_references() {
    local makefile="$PROJECT_ROOT/Makefile"

    if [[ ! -f "$makefile" ]]; then
        log_verbose "No Makefile found"
        return 0
    fi

    log_info "Updating Makefile script references..."

    # Define path mappings (old_path -> new_path)
    declare -A path_mappings=(
        ["./.genesis/scripts/build.sh"]="./.genesis/scripts/build/build.sh"
        ["./.genesis/scripts/bump-version.sh"]="./.genesis/scripts/build/bump-version.sh"
        ["./.genesis/scripts/release.sh"]="./.genesis/scripts/build/release.sh"
        ["./.genesis/scripts/check-file-organization.sh"]="./.genesis/scripts/validation/check-file-organization.sh"
        ["./.genesis/scripts/validate-bootstrap.sh"]="./.genesis/scripts/validation/validate-bootstrap.sh"
        ["./scripts/setup/setup.sh"]="./.genesis/scripts/setup/setup.sh"
    )

    if [[ "$DRY_RUN" == "true" ]]; then
        for old_path in "${!path_mappings[@]}"; do
            if grep -q "$old_path" "$makefile"; then
                log_info "Would update Makefile: $old_path -> ${path_mappings[$old_path]}"
            fi
        done
    else
        for old_path in "${!path_mappings[@]}"; do
            local new_path="${path_mappings[$old_path]}"
            if grep -q "$old_path" "$makefile"; then
                sed -i.bak "s|$old_path|$new_path|g" "$makefile"
                log_success "Updated Makefile: $old_path -> $new_path"
            fi
        done
    fi
}

update_precommit_config() {
    local precommit_config="$PROJECT_ROOT/.pre-commit-config.yaml"

    if [[ ! -f "$precommit_config" ]]; then
        log_verbose "No .pre-commit-config.yaml found"
        return 0
    fi

    log_info "Updating .pre-commit-config.yaml script references..."

    # Define path mappings for pre-commit hooks
    declare -A precommit_mappings=(
        [".genesis/scripts/find-hardcoded-values.sh"]=".genesis/scripts/validation/find-hardcoded-values.sh"
        [".genesis/scripts/check-variable-defaults.sh"]=".genesis/scripts/validation/check-variable-defaults.sh"
        [".genesis/scripts/check-ai-signatures.sh"]=".genesis/scripts/validation/check-ai-signatures.sh"
        [".genesis/scripts/check-genesis-components.sh"]=".genesis/scripts/validation/check-genesis-components.sh"
        [".genesis/scripts/validate-components.sh"]=".genesis/scripts/validation/validate-components.sh"
        [".genesis/scripts/check-file-organization.sh"]=".genesis/scripts/validation/check-file-organization.sh"
    )

    if [[ "$DRY_RUN" == "true" ]]; then
        for old_path in "${!precommit_mappings[@]}"; do
            if grep -q "$old_path" "$precommit_config"; then
                log_info "Would update .pre-commit-config.yaml: $old_path -> ${precommit_mappings[$old_path]}"
            fi
        done
    else
        for old_path in "${!precommit_mappings[@]}"; do
            local new_path="${precommit_mappings[$old_path]}"
            if grep -q "$old_path" "$precommit_config"; then
                sed -i.bak "s|$old_path|$new_path|g" "$precommit_config"
                log_success "Updated .pre-commit-config.yaml: $old_path -> $new_path"
            fi
        done
    fi
}

main() {
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

    # Detect project root if not specified
    if [[ -z "$PROJECT_ROOT" ]]; then
        PROJECT_ROOT="$(detect_project_root)"
    fi

    if [[ ! -d "$PROJECT_ROOT" ]]; then
        log_error "Project root does not exist: $PROJECT_ROOT"
        exit 1
    fi

    log_info "Working with project root: $PROJECT_ROOT"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN MODE - No changes will be made"
    fi

    # Execute reorganization steps
    create_directory_structure
    reorganize_scripts
    remove_duplicate_scripts
    update_makefile_references
    update_precommit_config

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry run complete. Use without --dry-run to apply changes."
    else
        log_success "Genesis file reorganization complete!"
        log_info "Backup files (*.bak) created for modified configuration files."
    fi
}

# Run main function
main "$@"
