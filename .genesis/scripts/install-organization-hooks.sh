#!/usr/bin/env bash
# Install file organization git hooks

set -euo pipefail

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}" >&2
}

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    log_error "Not in a git repository"
    exit 1
fi

echo -e "${CYAN}🔧 Installing Genesis file organization hooks${NC}"
echo

# Create hooks directory if it doesn't exist
if [ ! -d ".git/hooks" ]; then
    mkdir -p ".git/hooks"
    log_info "Created .git/hooks directory"
fi

# List of hooks to install
hooks=(
    "post-checkout"
    "post-merge"
    "post-commit"
    "pre-push"
)

installed_count=0
skipped_count=0

for hook in "${hooks[@]}"; do
    source_hook=".genesis/hooks/$hook"
    dest_hook=".git/hooks/$hook"

    if [ ! -f "$source_hook" ]; then
        log_warning "Source hook not found: $source_hook"
        continue
    fi

    # Check if hook already exists
    if [ -f "$dest_hook" ]; then
        # Check if it's already our hook
        if grep -q "Genesis file organization" "$dest_hook" 2>/dev/null; then
            log_info "Hook already installed: $hook"
            skipped_count=$((skipped_count + 1))
            continue
        else
            # Backup existing hook
            backup_file="${dest_hook}.backup.$(date +%s)"
            cp "$dest_hook" "$backup_file"
            log_warning "Backed up existing hook: $hook → $(basename "$backup_file")"
        fi
    fi

    # Install the hook
    cp "$source_hook" "$dest_hook"
    chmod +x "$dest_hook"
    log_success "Installed hook: $hook"
    installed_count=$((installed_count + 1))
done

echo
echo -e "${CYAN}📋 Installation Summary:${NC}"
echo -e "  ${GREEN}• Installed: $installed_count hooks${NC}"
echo -e "  ${YELLOW}• Skipped: $skipped_count hooks${NC}"

if [ $installed_count -gt 0 ]; then
    echo
    echo -e "${GREEN}🎉 File organization hooks installed successfully!${NC}"
    echo -e "${BLUE}The hooks will now run automatically on:${NC}"
    echo -e "  • post-checkout: After branch switches"
    echo -e "  • post-merge: After pulls/merges"
    echo -e "  • post-commit: After commits"
    echo -e "  • pre-push: Before pushes"
    echo
    echo -e "${CYAN}💡 To test the organization script manually:${NC}"
    echo -e "  ${BLUE}.genesis/scripts/check-file-organization.sh --help${NC}"
else
    echo
    echo -e "${YELLOW}No new hooks were installed${NC}"
fi

exit 0
