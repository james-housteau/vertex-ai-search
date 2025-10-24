#!/usr/bin/env bash
# Audit script that properly validates project files against sync.yml manifest
# Shows what's missing, what's extra, and what has wrong permissions

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Configuration
PROJECT_PATH="${1:-.}"
VERBOSE="${VERBOSE:-false}"
FIX="${FIX:-false}"

# Counters
MISSING_FILES=0
WRONG_PERMS=0
EXTRA_FILES=0
CORRECT_FILES=0
TOTAL_CHECKS=0

# Arrays to track files
declare -a MANIFEST_FILES
declare -a FOUND_FILES

# Helper functions
log_error() {
    echo -e "${RED}✗${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_verbose() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${CYAN}  →${NC} $1"
    fi
}

# Check if sync.yml exists
check_sync_yml() {
    local sync_file="$PROJECT_PATH/.genesis/sync.yml"

    if [[ ! -f "$sync_file" ]]; then
        log_error "No .genesis/sync.yml found in $PROJECT_PATH"
        echo "This script requires a Genesis project with sync.yml manifest."
        exit 1
    fi

    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}    Genesis Manifest Audit Report${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo
    echo -e "${BLUE}📋 Project:${NC} $(basename "$PROJECT_PATH")"
    echo -e "${BLUE}📁 Location:${NC} $PROJECT_PATH"
    echo -e "${BLUE}📄 Manifest:${NC} .genesis/sync.yml"

    # Get Genesis version from sync.yml
    local genesis_version=$(grep "genesis_version:" "$sync_file" | head -1 | awk '{print $2}')
    if [[ -n "$genesis_version" ]]; then
        echo -e "${BLUE}🏷️  Version:${NC} Genesis $genesis_version"
    fi
    echo
}

# Process a single manifest entry
process_manifest_entry() {
    if [[ -z "$current_dest" ]]; then
        return
    fi

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    local full_path="$PROJECT_PATH/$current_dest"
    local status_icon=""
    local status_msg=""

    # Default policy if not set
    if [[ -z "$current_policy" ]]; then
        current_policy="always"
    fi

    # Check if file exists
    if [[ ! -e "$full_path" ]]; then
        MISSING_FILES=$((MISSING_FILES + 1))
        status_icon="${RED}✗ MISSING${NC}"
        status_msg="File not found"

        if [[ "$FIX" == "true" ]] && [[ "$current_policy" != "never" ]]; then
            log_verbose "Would restore via 'genesis sync'"
        fi
    else
        # File exists, check permissions if it should be executable
        local perm_ok=true
        local perm_msg=""

        if [[ "$current_executable" == "true" ]] && [[ ! -x "$full_path" ]]; then
            WRONG_PERMS=$((WRONG_PERMS + 1))
            perm_ok=false
            perm_msg=" ${YELLOW}[NOT EXECUTABLE]${NC}"

            if [[ "$FIX" == "true" ]]; then
                chmod +x "$full_path"
                perm_msg=" ${GREEN}[FIXED: +x]${NC}"
                WRONG_PERMS=$((WRONG_PERMS - 1))
                CORRECT_FILES=$((CORRECT_FILES + 1))
            fi
        elif [[ "$current_executable" == "false" ]] && [[ -x "$full_path" ]] && [[ -f "$full_path" ]]; then
            # Only check if regular file (not directory) should not be executable
            if [[ "$full_path" != *.sh ]] && [[ "$full_path" != *.py ]]; then
                WRONG_PERMS=$((WRONG_PERMS + 1))
                perm_ok=false
                perm_msg=" ${YELLOW}[SHOULD NOT BE EXECUTABLE]${NC}"

                if [[ "$FIX" == "true" ]]; then
                    chmod -x "$full_path"
                    perm_msg=" ${GREEN}[FIXED: -x]${NC}"
                    WRONG_PERMS=$((WRONG_PERMS - 1))
                    CORRECT_FILES=$((CORRECT_FILES + 1))
                fi
            else
                CORRECT_FILES=$((CORRECT_FILES + 1))
            fi
        else
            CORRECT_FILES=$((CORRECT_FILES + 1))
        fi

        if [[ "$perm_ok" == true ]] && [[ -z "$perm_msg" ]]; then
            status_icon="${GREEN}✓${NC}"
            status_msg="OK"
        else
            status_icon="${YELLOW}⚠${NC}"
            status_msg="Exists$perm_msg"
        fi
    fi

    # Count by policy type
    case "$current_policy" in
        always) always_sync=$((always_sync + 1)) ;;
        if_unchanged) if_unchanged=$((if_unchanged + 1)) ;;
        never) never_sync=$((never_sync + 1)) ;;
    esac

    # Display based on status or verbosity
    if [[ "$status_icon" != "${GREEN}✓${NC}" ]] || [[ "$VERBOSE" == "true" ]]; then
        printf "  %s %-50s [%s]\n" "$status_icon" "$current_dest" "$current_policy"
        if [[ -n "$status_msg" ]] && [[ "$status_msg" != "OK" ]]; then
            log_verbose "$status_msg"
        fi
    fi
}

# Parse sync.yml and validate files
validate_manifest_files() {
    local sync_file="$PROJECT_PATH/.genesis/sync.yml"

    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${MAGENTA}Validating Files from Manifest${NC}"
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo

    # Track categories
    always_sync=0
    if_unchanged=0
    never_sync=0

    # Parse sync_policies section
    local in_sync_policies=false
    current_dest=""
    current_executable="false"  # Default to false
    current_policy=""

    while IFS= read -r line; do
        # Check if we're entering sync_policies section
        if [[ "$line" =~ ^sync_policies: ]]; then
            in_sync_policies=true
            continue
        fi

        # Exit if we hit another top-level section
        if [[ "$in_sync_policies" == true ]] && [[ "$line" =~ ^[a-z_]+: ]] && [[ ! "$line" =~ ^[[:space:]] ]]; then
            # Process last entry if we have one
            if [[ -n "$current_dest" ]]; then
                process_manifest_entry
            fi
            break
        fi

        if [[ "$in_sync_policies" == true ]]; then
            # New entry starts with "- source:"
            if [[ "$line" =~ ^-[[:space:]]+source: ]]; then
                # Process previous entry if we have one
                if [[ -n "$current_dest" ]]; then
                    process_manifest_entry
                fi
                # Reset for new entry
                current_dest=""
                current_executable="false"
                current_policy=""
                continue
            fi

            # Parse dest field
            if [[ "$line" =~ ^[[:space:]]+dest:[[:space:]](.+) ]]; then
                current_dest="${BASH_REMATCH[1]}"
                MANIFEST_FILES+=("$current_dest")
            fi

            # Parse executable field
            if [[ "$line" =~ ^[[:space:]]+executable:[[:space:]](.+) ]]; then
                current_executable="${BASH_REMATCH[1]}"
            fi

            # Parse sync field (policy)
            if [[ "$line" =~ ^[[:space:]]+sync:[[:space:]](.+) ]]; then
                current_policy="${BASH_REMATCH[1]}"
            fi

            # Parse policy field (alternative name)
            if [[ "$line" =~ ^[[:space:]]+policy:[[:space:]](.+) ]]; then
                current_policy="${BASH_REMATCH[1]}"
            fi
        fi
    done < "$sync_file"

    # Process final entry if exists
    if [[ -n "$current_dest" ]]; then
        process_manifest_entry
    fi

    # Summary for this section
    echo
    echo -e "${BLUE}📊 Manifest Files Summary:${NC}"
    echo -e "  Total files in manifest: ${TOTAL_CHECKS}"
    echo -e "  ${GREEN}✓${NC} Correct: ${CORRECT_FILES}"
    if [[ $MISSING_FILES -gt 0 ]]; then
        echo -e "  ${RED}✗${NC} Missing: ${MISSING_FILES}"
    fi
    if [[ $WRONG_PERMS -gt 0 ]]; then
        echo -e "  ${YELLOW}⚠${NC} Wrong permissions: ${WRONG_PERMS}"
    fi
    echo
    echo -e "${BLUE}📁 By sync policy:${NC}"
    echo -e "  Always sync: ${always_sync}"
    echo -e "  If unchanged: ${if_unchanged}"
    echo -e "  Never sync: ${never_sync}"
}

# Check for Genesis scripts in .genesis/scripts
validate_genesis_scripts() {
    echo
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${MAGENTA}Checking Genesis Scripts${NC}"
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo

    local genesis_scripts_dir="$PROJECT_PATH/.genesis/scripts"

    if [[ ! -d "$genesis_scripts_dir" ]]; then
        log_warning "No .genesis/scripts directory found"
        return
    fi

    # Expected subdirectories
    local expected_dirs=("build" "docker" "setup" "utils" "validation")
    local missing_dirs=0

    echo -e "${BLUE}📁 Expected subdirectories:${NC}"
    for dir in "${expected_dirs[@]}"; do
        if [[ -d "$genesis_scripts_dir/$dir" ]]; then
            local count=$(find "$genesis_scripts_dir/$dir" -type f \( -name "*.sh" -o -name "*.py" \) 2>/dev/null | wc -l | tr -d ' ')
            log_success "$dir/ ($count scripts)"
        else
            log_error "$dir/ (missing)"
            missing_dirs=$((missing_dirs + 1))
        fi
    done

    # Check for misplaced scripts in root
    local misplaced=$(find "$genesis_scripts_dir" -maxdepth 1 -type f \( -name "*.sh" -o -name "*.py" \) 2>/dev/null)
    if [[ -n "$misplaced" ]]; then
        echo
        echo -e "${YELLOW}⚠ Scripts in wrong location (should be in subdirectories):${NC}"
        while IFS= read -r script; do
            echo -e "  ${YELLOW}→${NC} $(basename "$script")"
        done <<< "$misplaced"
    fi

    # Check all .sh files are executable
    echo
    echo -e "${BLUE}🔧 Checking script permissions:${NC}"
    local non_exec_count=0
    while IFS= read -r script; do
        if [[ ! -x "$script" ]]; then
            non_exec_count=$((non_exec_count + 1))
            if [[ "$VERBOSE" == "true" ]] || [[ $non_exec_count -le 5 ]]; then
                log_warning "Not executable: ${script#$PROJECT_PATH/}"
            fi
            if [[ "$FIX" == "true" ]]; then
                chmod +x "$script"
            fi
        fi
    done < <(find "$genesis_scripts_dir" -type f -name "*.sh" 2>/dev/null)

    if [[ $non_exec_count -gt 0 ]]; then
        if [[ "$FIX" == "true" ]]; then
            echo -e "  ${GREEN}✓ Fixed $non_exec_count non-executable scripts${NC}"
        else
            echo -e "  ${YELLOW}⚠ Found $non_exec_count non-executable scripts${NC}"
            echo -e "  ${BLUE}💡 Run with FIX=true to fix${NC}"
        fi
    else
        log_success "All scripts have correct permissions"
    fi
}

# Check for extra files not in manifest
check_extra_files() {
    echo
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${MAGENTA}Checking for Extra Files${NC}"
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo

    # Common Genesis-managed directories to check
    local dirs_to_check=(".genesis/hooks" ".genesis/scripts" ".claude/commands" "scripts")

    for dir in "${dirs_to_check[@]}"; do
        local full_dir="$PROJECT_PATH/$dir"
        if [[ ! -d "$full_dir" ]]; then
            continue
        fi

        local extra_found=false
        while IFS= read -r file; do
            local rel_path="${file#$PROJECT_PATH/}"

            # Skip directories and template files
            if [[ -d "$file" ]] || [[ "$file" == *.template ]]; then
                continue
            fi

            # Skip Python cache files
            if [[ "$file" == *__pycache__* ]] || [[ "$file" == *.pyc ]]; then
                continue
            fi

            # Check if this file is in our manifest
            local in_manifest=false
            for manifest_file in "${MANIFEST_FILES[@]}"; do
                if [[ "$rel_path" == "$manifest_file" ]]; then
                    in_manifest=true
                    break
                fi
            done

            if [[ "$in_manifest" == false ]]; then
                if [[ "$extra_found" == false ]]; then
                    echo -e "${BLUE}📂 Extra files in $dir:${NC}"
                    extra_found=true
                fi
                EXTRA_FILES=$((EXTRA_FILES + 1))
                log_warning "$rel_path (not in manifest)"
            fi
        done < <(find "$full_dir" -type f 2>/dev/null)
    done

    if [[ $EXTRA_FILES -eq 0 ]]; then
        log_success "No extra files found (all files are in manifest)"
    else
        echo
        echo -e "${YELLOW}⚠ Found $EXTRA_FILES files not in manifest${NC}"
        echo -e "${BLUE}💡 These may be project-specific files or outdated Genesis files${NC}"
    fi
}

# Main execution
main() {
    cd "$PROJECT_PATH" 2>/dev/null || {
        echo -e "${RED}Error: Cannot access directory $PROJECT_PATH${NC}"
        exit 1
    }

    check_sync_yml
    validate_manifest_files
    validate_genesis_scripts
    check_extra_files

    # Final summary
    echo
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}                    Final Summary${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo

    local total_issues=$((MISSING_FILES + WRONG_PERMS + EXTRA_FILES))

    echo -e "📋 Total files checked: ${TOTAL_CHECKS}"
    echo -e "✅ Correct files: ${CORRECT_FILES}"

    if [[ $MISSING_FILES -gt 0 ]]; then
        echo -e "❌ Missing files: ${MISSING_FILES}"
    fi

    if [[ $WRONG_PERMS -gt 0 ]]; then
        echo -e "⚠️  Wrong permissions: ${WRONG_PERMS}"
    fi

    if [[ $EXTRA_FILES -gt 0 ]]; then
        echo -e "➕ Extra files: ${EXTRA_FILES}"
    fi

    echo
    if [[ $total_issues -eq 0 ]]; then
        echo -e "${GREEN}🎉 Perfect! All files match the manifest exactly.${NC}"
    else
        echo -e "${YELLOW}⚠️  Found $total_issues issues${NC}"
        echo
        echo -e "${BLUE}💡 To fix issues:${NC}"
        if [[ $MISSING_FILES -gt 0 ]]; then
            echo -e "   • Run 'genesis sync' to restore missing files"
        fi
        if [[ $WRONG_PERMS -gt 0 ]]; then
            echo -e "   • Run 'FIX=true $0' to fix permissions"
        fi
        if [[ $EXTRA_FILES -gt 0 ]]; then
            echo -e "   • Review extra files and remove if outdated"
        fi
    fi

    # Exit with appropriate code
    if [[ $MISSING_FILES -gt 0 ]]; then
        exit 1
    elif [[ $total_issues -gt 0 ]]; then
        exit 0  # Warnings only
    else
        exit 0
    fi
}

# Show help if requested
if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
    echo "Usage: $0 [PROJECT_PATH]"
    echo
    echo "Audit Genesis project files against sync.yml manifest"
    echo
    echo "Options:"
    echo "  PROJECT_PATH    Path to Genesis project (default: current directory)"
    echo
    echo "Environment variables:"
    echo "  VERBOSE=true    Show all files (not just issues)"
    echo "  FIX=true        Automatically fix permission issues"
    echo
    echo "Examples:"
    echo "  $0                           # Audit current directory"
    echo "  $0 /path/to/project          # Audit specific project"
    echo "  VERBOSE=true $0              # Show all files"
    echo "  FIX=true $0                  # Fix permission issues"
    echo
    exit 0
fi

# Run main function
main
