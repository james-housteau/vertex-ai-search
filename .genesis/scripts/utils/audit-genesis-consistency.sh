#!/bin/bash
# Audit Genesis consistency across projects by reading from manifest.yml

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get script directory and Genesis root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GENESIS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Get projects to audit from command line or default to current directory
if [[ $# -gt 0 ]]; then
    PROJECTS=("$@")
else
    # Default to current directory
    PROJECTS=("$(pwd)")
fi

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}    Genesis Consistency Audit Report${NC}"
echo -e "${BLUE}    (Reading from manifest.yml as source of truth)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo

# Function to parse manifest.yml and extract destination files
parse_manifest() {
    local manifest_file="$1"
    local project_type="${2:-python}"

    if [[ ! -f "$manifest_file" ]]; then
        echo -e "${RED}❌ Cannot find manifest: $manifest_file${NC}" >&2
        exit 1
    fi

    # Extract shared files
    awk '
    /^shared_files:/ { in_shared = 1; next }
    /^[a-z_]+_files:/ { in_shared = 0 }
    in_shared && /^\s+- source:/ { in_file = 1 }
    in_file && /^\s+dest:/ {
        gsub(/^\s+dest:\s*/, "")
        gsub(/\s*$/, "")
        print "shared:" $0
    }
    in_file && /^\s+sync:/ {
        gsub(/^\s+sync:\s*/, "")
        gsub(/\s*$/, "")
        sync_policy = $0
    }
    in_file && /^\s+description:/ {
        in_file = 0
        print "sync:" sync_policy
    }
    ' "$manifest_file"

    # Extract project-specific files (e.g., python_files)
    local project_section="${project_type}_files"
    awk -v section="$project_section" '
    $0 ~ "^" section ":" { in_section = 1; next }
    /^[a-z_]+_files:/ { in_section = 0 }
    in_section && /^\s+- source:/ { in_file = 1 }
    in_file && /^\s+dest:/ {
        gsub(/^\s+dest:\s*/, "")
        gsub(/\s*$/, "")
        print section ":" $0
    }
    in_file && /^\s+sync:/ {
        gsub(/^\s+sync:\s*/, "")
        gsub(/\s*$/, "")
        sync_policy = $0
    }
    in_file && /^\s+description:/ {
        in_file = 0
        print "sync:" sync_policy
    }
    ' "$manifest_file"
}

# Function to get expected Genesis scripts from template directory
get_genesis_scripts() {
    local template_dir="$GENESIS_ROOT/templates/shared/.genesis/scripts"

    if [[ -d "$template_dir" ]]; then
        find "$template_dir" -type f \( -name "*.sh.template" -o -name "*.py.template" \) | while read -r file; do
            # Get relative path from .genesis/scripts/ and remove .template suffix
            rel_path="${file#$GENESIS_ROOT/templates/shared/}"
            rel_path="${rel_path%.template}"
            echo "$rel_path"
        done | sort
    fi
}

# Function to get expected hooks from template directory
get_genesis_hooks() {
    local hooks_dir="$GENESIS_ROOT/templates/shared/.genesis/hooks"

    if [[ -d "$hooks_dir" ]]; then
        find "$hooks_dir" -type f ! -name "*.template" | while read -r file; do
            # Get relative path from .genesis/hooks/
            rel_path="${file#$GENESIS_ROOT/templates/shared/}"
            echo "$rel_path"
        done | sort
    fi
}

# Track overall statistics
total_checks=0
total_failures=0
project_names=()
project_failure_counts=()

# Parse manifest once at the beginning
MANIFEST_FILE="$GENESIS_ROOT/templates/shared/manifest.yml"
echo -e "${BLUE}📖 Reading manifest from: ${NC}templates/shared/manifest.yml"
echo

# Get expected files from manifest
MANIFEST_FILES=$(parse_manifest "$MANIFEST_FILE")
GENESIS_SCRIPTS=$(get_genesis_scripts)
GENESIS_HOOKS=$(get_genesis_hooks)

for project in "${PROJECTS[@]}"; do
    project_name=$(basename "$project")
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Project: $project_name${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    if [[ ! -d "$project" ]]; then
        echo -e "${RED}❌ Project directory not found${NC}"
        continue
    fi

    failures=0
    checks=0

    # Detect project type
    if [[ -f "$project/pyproject.toml" ]]; then
        project_type="python"
    elif [[ -f "$project/package.json" ]]; then
        project_type="typescript"
    else
        project_type="python"  # default
    fi
    echo -e "${BLUE}📦 Project type: $project_type${NC}"

    # Check Genesis scripts (from template directory)
    echo -e "\n${BLUE}📁 Genesis Scripts:${NC}"
    while IFS= read -r expected_file; do
        if [[ -z "$expected_file" ]]; then continue; fi

        full_path="$project/$expected_file"
        checks=$((checks + 1))
        total_checks=$((total_checks + 1))

        if [[ ! -f "$full_path" ]]; then
            echo -e "  ${RED}✗${NC} Missing: $expected_file"
            failures=$((failures + 1))
            total_failures=$((total_failures + 1))
        elif [[ "$expected_file" == *.sh ]] && [[ ! -x "$full_path" ]]; then
            echo -e "  ${YELLOW}⚠${NC} Not executable: $expected_file"
            failures=$((failures + 1))
            total_failures=$((total_failures + 1))
        else
            echo -e "  ${GREEN}✓${NC} $expected_file"
        fi
    done <<< "$GENESIS_SCRIPTS"

    # Check Genesis hooks
    echo -e "\n${BLUE}🪝 Genesis Hooks:${NC}"
    while IFS= read -r expected_file; do
        if [[ -z "$expected_file" ]]; then continue; fi

        full_path="$project/$expected_file"
        checks=$((checks + 1))
        total_checks=$((total_checks + 1))

        if [[ ! -f "$full_path" ]]; then
            echo -e "  ${RED}✗${NC} Missing: $expected_file"
            failures=$((failures + 1))
            total_failures=$((total_failures + 1))
        elif [[ ! -x "$full_path" ]]; then
            echo -e "  ${YELLOW}⚠${NC} Not executable: $expected_file"
            failures=$((failures + 1))
            total_failures=$((total_failures + 1))
        else
            echo -e "  ${GREEN}✓${NC} $expected_file"
        fi
    done <<< "$GENESIS_HOOKS"

    # Check files from manifest (skipping Genesis repo for client scripts)
    echo -e "\n${BLUE}📋 Files from Manifest:${NC}"
    current_sync=""
    while IFS= read -r line; do
        if [[ -z "$line" ]]; then continue; fi

        if [[ "$line" =~ ^sync: ]]; then
            current_sync="${line#sync:}"
            continue
        fi

        if [[ "$line" =~ ^(shared|python_files|typescript_files): ]]; then
            file_path="${line#*:}"

            # Skip client-specific scripts in Genesis repo
            if [[ "$project_name" == "genesis" ]] && [[ "$file_path" =~ ^scripts/ ]]; then
                continue
            fi

            full_path="$project/$file_path"
            checks=$((checks + 1))
            total_checks=$((total_checks + 1))

            if [[ ! -e "$full_path" ]]; then
                if [[ "$current_sync" == "never" ]]; then
                    echo -e "  ${BLUE}○${NC} Optional (never sync): $file_path"
                else
                    echo -e "  ${RED}✗${NC} Missing: $file_path"
                    failures=$((failures + 1))
                    total_failures=$((total_failures + 1))
                fi
            elif [[ -f "$full_path" ]] && [[ "$file_path" == *.sh ]] && [[ ! -x "$full_path" ]]; then
                echo -e "  ${YELLOW}⚠${NC} Not executable: $file_path"
                failures=$((failures + 1))
                total_failures=$((total_failures + 1))
            else
                echo -e "  ${GREEN}✓${NC} $file_path"
            fi
        fi
    done <<< "$MANIFEST_FILES"

    # Check standard files not in manifest but expected
    echo -e "\n${BLUE}📄 Standard Project Files:${NC}"
    for file in ".gitignore" "Makefile" ".pre-commit-config.yaml" ".claude/settings.json"; do
        full_path="$project/$file"
        checks=$((checks + 1))
        total_checks=$((total_checks + 1))

        if [[ ! -e "$full_path" ]]; then
            echo -e "  ${RED}✗${NC} Missing: $file"
            failures=$((failures + 1))
            total_failures=$((total_failures + 1))
        else
            echo -e "  ${GREEN}✓${NC} $file"
        fi
    done

    # Check for misplaced scripts in .genesis/scripts root
    echo -e "\n${BLUE}🔍 Checking for misplaced scripts:${NC}"
    if [[ -d "$project/.genesis/scripts" ]]; then
        misplaced=$(find "$project/.genesis/scripts" -maxdepth 1 -type f \( -name "*.sh" -o -name "*.py" \) 2>/dev/null | wc -l)
        if [[ $misplaced -gt 0 ]]; then
            echo -e "  ${YELLOW}⚠${NC} Found $misplaced scripts in .genesis/scripts root (should be in subdirectories)"
            find "$project/.genesis/scripts" -maxdepth 1 -type f \( -name "*.sh" -o -name "*.py" \) -exec basename {} \; | while read -r script; do
                echo -e "      ${YELLOW}→${NC} $script"
            done
            failures=$((failures + misplaced))
            total_failures=$((total_failures + misplaced))
        else
            echo -e "  ${GREEN}✓${NC} No misplaced scripts"
        fi
    fi

    # Project summary
    project_names+=("$project_name")
    project_failure_counts+=($failures)
    echo -e "\n${BLUE}Summary for $project_name:${NC}"
    if [[ $failures -eq 0 ]]; then
        echo -e "  ${GREEN}✅ All checks passed ($checks checks)${NC}"
    else
        echo -e "  ${RED}❌ $failures issues found out of $checks checks${NC}"
    fi
    echo
done

# Overall summary
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}                    Overall Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo
echo -e "Total checks performed: ${total_checks}"
echo -e "Total issues found: ${total_failures}"
echo
echo -e "${BLUE}Project Status:${NC}"
for i in "${!project_names[@]}"; do
    project_name="${project_names[$i]}"
    failures="${project_failure_counts[$i]}"
    if [[ $failures -eq 0 ]]; then
        echo -e "  ${GREEN}✅${NC} $project_name"
    else
        echo -e "  ${RED}❌${NC} $project_name ($failures issues)"
    fi
done

echo
if [[ $total_failures -eq 0 ]]; then
    echo -e "${GREEN}🎉 All projects have consistent Genesis structure!${NC}"
else
    echo -e "${YELLOW}⚠️  Found $total_failures inconsistencies across projects${NC}"
    echo -e "${BLUE}💡 To fix permission issues, run:${NC}"
    echo -e "    find . -name '*.sh' -type f -exec chmod +x {} \\;"
    echo -e "${BLUE}💡 To sync missing files, run:${NC}"
    echo -e "    genesis sync --refresh"
fi
