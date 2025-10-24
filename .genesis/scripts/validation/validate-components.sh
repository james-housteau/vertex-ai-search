#!/bin/bash
# Component validation script - ensures AI safety limits

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔍 Validating Genesis component structure for AI safety..."
echo

# Auto-detect modules based on Pure Module Isolation principles
detect_modules() {
    local modules=()
    for dir in */; do
        if [[ -d "$dir" && "$dir" != "." && "$dir" != ".." ]]; then
            local dir_name="${dir%/}"
            # Skip non-module directories
            if [[ ! "$dir_name" =~ ^(\.|node_modules|venv|\.venv|__pycache__|\.git|scratch|dist|build|htmlcov|examples|docs|scripts|src|tests|workspace|worktrees|test-config)$ ]]; then
                # Check if directory has module characteristics
                if [[ -f "$dir/Makefile" ]] || [[ -f "$dir/pyproject.toml" ]] || [[ -f "$dir/package.json" ]] || [[ -d "$dir/src" ]] || [[ -d "$dir/tests" ]]; then
                    modules+=("$dir_name")
                fi
            fi
        fi
    done
    if [ ${#modules[@]} -gt 0 ]; then
        printf '%s\n' "${modules[@]}"
    fi
}

# Get modules dynamically
components=($(detect_modules))
max_files=60  # Updated to match AI safety limits from Pure Module Isolation
total_components=0
valid_components=0

if [ ${#components[@]} -gt 0 ]; then
    echo "📋 Detected modules: ${components[*]}"
else
    echo "📋 No modules detected - single component project"
fi
echo

if [ ${#components[@]} -eq 0 ]; then
    echo "📁 Single component project detected"
    echo "✅ SAFE for AI development (no multi-component structure)"
    echo
    echo "📊 Summary:"
    echo "  Components checked: 1 (single component)"
    echo "  AI-safe components: 1"
    echo -e "${GREEN}✅ Project is AI-safe!${NC}"
    exit 0
fi

for component in "${components[@]}"; do
    if [ -d "$component" ]; then
        file_count=$(find "$component" -type f | wc -l | tr -d ' ')
        total_components=$((total_components + 1))

        echo "📁 $component: $file_count files"

        if [ "$file_count" -le "$max_files" ]; then
            echo "  ✅ SAFE for AI development"
            valid_components=$((valid_components + 1))
        else
            echo "  ❌ EXCEEDS AI safety limit ($max_files files)"
        fi

        # Check for README
        if [ -f "$component/README.md" ]; then
            echo "  📖 README.md present"
        else
            echo "  ⚠️  Missing README.md"
        fi

        echo
    fi
done

echo "📊 Summary:"
echo "  Components checked: $total_components"
echo "  AI-safe components: $valid_components"

if [ "$valid_components" -eq "$total_components" ]; then
    echo -e "${GREEN}✅ All components are AI-safe!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some components exceed AI safety limits${NC}"
    exit 1
fi
