#!/bin/bash
# Post-bootstrap validation script - ensures a newly created project is fully functional

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default to current directory, but allow override
PROJECT_PATH="${1:-.}"
TOTAL_ISSUES=0

echo "🔍 Validating bootstrapped project at: $PROJECT_PATH"
echo

cd "$PROJECT_PATH"

log_check() {
    echo -e "${BLUE}🔍 $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
}

detect_project_type() {
    if [ -f "pyproject.toml" ]; then
        echo "python"
    elif [ -f "package.json" ]; then
        echo "nodejs"
    elif [ -f "main.tf" ]; then
        echo "terraform"
    else
        echo "unknown"
    fi
}

validate_basic_structure() {
    log_check "Checking basic project structure"

    local required_files=("README.md" "Makefile")
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            log_success "$file present"
        else
            log_error "Missing required file: $file"
        fi
    done

    local required_dirs=("scripts" "docs")
    for dir in "${required_dirs[@]}"; do
        if [ -d "$dir" ]; then
            log_success "$dir/ directory present"
        else
            log_warning "Missing recommended directory: $dir/"
        fi
    done

    echo
}

validate_makefile_targets() {
    log_check "Checking Makefile targets"

    if [ ! -f "Makefile" ]; then
        log_error "Makefile not found"
        echo
        return
    fi

    local required_targets=("help" "setup")
    for target in "${required_targets[@]}"; do
        if grep -q "^$target:" Makefile; then
            log_success "Makefile has $target target"
        else
            log_error "Makefile missing $target target"
        fi
    done

    local recommended_targets=("test" "clean" "check-org")
    for target in "${recommended_targets[@]}"; do
        if grep -q "^$target:" Makefile; then
            log_success "Makefile has $target target"
        else
            log_warning "Makefile missing recommended target: $target"
        fi
    done

    echo
}

validate_scripts() {
    log_check "Checking scripts directory"

    if [ ! -d "scripts" ]; then
        log_error "scripts/ directory missing"
        echo
        return
    fi

    # Check required scripts
    local required_scripts=("check-file-organization.sh")
    for script in "${required_scripts[@]}"; do
        if [ -f ".genesis/scripts/$script" ]; then
            log_success "$script present"

            if [ -x ".genesis/scripts/$script" ]; then
                log_success "$script is executable"
            else
                log_error "$script not executable (chmod +x needed)"
            fi
        else
            log_error "Missing required script: .genesis/scripts/$script"
        fi
    done

    # Check optional but common scripts
    local optional_scripts=("setup.sh")
    for script in "${optional_scripts[@]}"; do
        if [ -f "scripts/$script" ]; then
            log_success "$script present"

            if [ -x "scripts/$script" ]; then
                log_success "$script is executable"
            else
                log_error "$script not executable (chmod +x needed)"
            fi
        fi
    done

    # Check all shell scripts in scripts/ are executable
    local non_executable_scripts=()
    for script in scripts/*.sh; do
        if [ -f "$script" ] && [ ! -x "$script" ]; then
            non_executable_scripts+=("$(basename "$script")")
        fi
    done

    if [ ${#non_executable_scripts[@]} -gt 0 ]; then
        log_error "Non-executable shell scripts found: ${non_executable_scripts[*]}"
        log_error "Run: chmod +x scripts/*.sh"
    else
        log_success "All shell scripts in scripts/ are executable"
    fi

    echo
}

validate_git_setup() {
    log_check "Checking git and hooks setup"

    if [ -d ".git" ]; then
        log_success "Git repository initialized"
    else
        log_warning "Git repository not initialized (run 'git init')"
    fi

    if [ -f ".gitignore" ]; then
        log_success ".gitignore present"
    else
        log_warning "Missing .gitignore file"
    fi

    if [ -f ".pre-commit-config.yaml" ]; then
        log_success "Pre-commit configuration present"
    else
        log_error "Missing .pre-commit-config.yaml"
    fi

    echo
}

validate_claude_setup() {
    log_check "Checking Claude Code configuration"

    if [ -d ".claude" ]; then
        log_success ".claude/ directory present"

        if [ -f ".claude/settings.json" ]; then
            log_success "Claude settings present"

            # Check for MCP server configuration
            if grep -q "enabledMcpjsonServers" ".claude/settings.json"; then
                log_success "MCP servers enabled in Claude settings"
            else
                log_warning "No MCP servers configured in Claude settings"
            fi
        else
            log_warning "Missing .claude/settings.json"
        fi

        if [ -f ".claude/hooks/block-bypass-commands.md" ]; then
            log_success "Claude hooks present"
        else
            log_warning "Missing .claude/hooks/block-bypass-commands.md"
        fi

        if [ -f ".claude/hooks/validate-bash-command.sh" ]; then
            if [ -x ".claude/hooks/validate-bash-command.sh" ]; then
                log_success "Bash validation hook is executable"
            else
                log_error "Bash validation hook not executable"
            fi
        else
            log_warning "Missing .claude/hooks/validate-bash-command.sh"
        fi
    else
        log_warning "Missing .claude/ directory (for Claude Code integration)"
    fi

    # Check for MCP server configuration file
    if [ -f ".mcp.json" ]; then
        log_success "MCP server configuration present"

        # Check if Ref server is configured
        if grep -q "Ref" ".mcp.json"; then
            log_success "Ref MCP server configured"
        else
            log_warning "Ref MCP server not found in .mcp.json"
        fi
    else
        log_warning "Missing .mcp.json (MCP server configuration)"
    fi

    echo
}

test_make_targets() {
    log_check "Testing make targets functionality"

    # Test help target
    if make help >/dev/null 2>&1; then
        log_success "make help works"
    else
        log_error "make help failed"
    fi

    # Test check-org if it exists
    if grep -q "^check-org:" Makefile; then
        if make check-org >/dev/null 2>&1; then
            log_success "make check-org works"
        else
            log_warning "make check-org failed"
        fi
    fi

    echo
}

validate_project_type_specific() {
    local project_type="$1"
    log_check "Checking $project_type-specific requirements"

    case "$project_type" in
        python)
            if [ -f "pyproject.toml" ]; then
                log_success "Python project configuration present"
            else
                log_error "Missing pyproject.toml"
            fi

            if [ -d "src" ]; then
                log_success "src/ directory present"
            else
                log_warning "Missing src/ directory"
            fi

            if [ -d "tests" ]; then
                log_success "tests/ directory present"
            else
                log_warning "Missing tests/ directory"
            fi

            # Test if we can run python-specific targets
            local python_targets=("install" "test")
            for target in "${python_targets[@]}"; do
                if grep -q "^$target:" Makefile; then
                    log_success "Python target '$target' present"
                else
                    log_warning "Missing Python target: $target"
                fi
            done
            ;;

        nodejs)
            if [ -f "package.json" ]; then
                log_success "Node.js project configuration present"
            else
                log_error "Missing package.json"
            fi

            if [ -f "tsconfig.json" ]; then
                log_success "TypeScript configuration present"
            else
                log_warning "Missing tsconfig.json (if TypeScript project)"
            fi

            local node_targets=("install" "build")
            for target in "${node_targets[@]}"; do
                if grep -q "^$target:" Makefile; then
                    log_success "Node.js target '$target' present"
                else
                    log_warning "Missing Node.js target: $target"
                fi
            done
            ;;

        terraform)
            if [ -f "main.tf" ]; then
                log_success "Terraform main configuration present"
            else
                log_error "Missing main.tf"
            fi

            if [ -f "variables.tf" ]; then
                log_success "Terraform variables present"
            else
                log_warning "Missing variables.tf"
            fi

            local tf_targets=("init" "plan" "validate")
            for target in "${tf_targets[@]}"; do
                if grep -q "^$target:" Makefile; then
                    log_success "Terraform target '$target' present"
                else
                    log_warning "Missing Terraform target: $target"
                fi
            done
            ;;
    esac

    echo
}

test_setup_process() {
    local project_type="$1"
    log_check "Testing setup process (dry run)"

    case "$project_type" in
        python)
            if [ -f "scripts/setup.sh" ]; then
                # Check if setup script would work (without actually running it)
                if grep -q "poetry install" scripts/setup.sh || grep -q "make" scripts/setup.sh; then
                    log_success "Setup script appears functional"
                else
                    log_warning "Setup script may not be functional"
                fi
            fi
            ;;
        nodejs)
            if grep -q "npm install" Makefile; then
                log_success "Node.js setup appears functional"
            else
                log_warning "Node.js setup may not be functional"
            fi
            ;;
        terraform)
            if grep -q "terraform init" Makefile; then
                log_success "Terraform setup appears functional"
            else
                log_warning "Terraform setup may not be functional"
            fi
            ;;
    esac

    echo
}

# Main validation flow
PROJECT_TYPE=$(detect_project_type)
echo "🎯 Detected project type: $PROJECT_TYPE"
echo

validate_basic_structure
validate_makefile_targets
validate_scripts
validate_git_setup
validate_claude_setup
test_make_targets
validate_project_type_specific "$PROJECT_TYPE"
test_setup_process "$PROJECT_TYPE"

# Summary
echo "📊 Bootstrap Validation Summary:"
echo "  Project type: $PROJECT_TYPE"
echo "  Project path: $(pwd)"
echo "  Issues found: $TOTAL_ISSUES"

if [ $TOTAL_ISSUES -eq 0 ]; then
    echo -e "${GREEN}🎉 Bootstrap validation passed! Project is ready for development.${NC}"
    echo -e "${BLUE}💡 Next steps: Run 'make setup' to initialize your development environment${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Found $TOTAL_ISSUES issues that should be addressed${NC}"
    echo -e "${BLUE}💡 Most issues are warnings and won't prevent development${NC}"
    echo -e "${BLUE}💡 Run 'make help' to see available commands${NC}"
    exit 1
fi
