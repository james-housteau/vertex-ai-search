#!/usr/bin/env bash
# Script Reference Update Tool
# Updates all hardcoded script paths to use the new subdirectory structure

set -euo pipefail

PROJECT_ROOT="/Users/source_code/genesis"
DRY_RUN=false

if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
fi

log_info() {
    echo "[INFO] $1" >&2
}

update_file() {
    local file="$1"
    local old_pattern="$2"
    local new_pattern="$3"

    if grep -q "$old_pattern" "$file"; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "Would update $file: $old_pattern -> $new_pattern"
        else
            sed -i.bak "s|$old_pattern|$new_pattern|g" "$file"
            log_info "Updated $file: $old_pattern -> $new_pattern"
        fi
    fi
}

cd "$PROJECT_ROOT"

# Update validation script references
log_info "Updating validation script references..."

find . -name "*.py" -type f -exec grep -l "\.genesis/scripts/check-" {} \; | while read -r file; do
    update_file "$file" "\.genesis/scripts/check-genesis-components\.sh" ".genesis/scripts/validation/check-genesis-components.sh"
    update_file "$file" "\.genesis/scripts/check-variable-defaults\.sh" ".genesis/scripts/validation/check-variable-defaults.sh"
    update_file "$file" "\.genesis/scripts/check-file-organization\.sh" ".genesis/scripts/validation/check-file-organization.sh"
    update_file "$file" "\.genesis/scripts/check-ai-signatures\.sh" ".genesis/scripts/validation/check-ai-signatures.sh"
    update_file "$file" "\.genesis/scripts/find-hardcoded-values\.sh" ".genesis/scripts/validation/find-hardcoded-values.sh"
    update_file "$file" "\.genesis/scripts/validate-components\.sh" ".genesis/scripts/validation/validate-components.sh"
    update_file "$file" "\.genesis/scripts/validate-bootstrap\.sh" ".genesis/scripts/validation/validate-bootstrap.sh"
done

find . -name "*.py" -type f -exec grep -l "templates/shared/\.genesis/scripts/.*\.template" {} \; | while read -r file; do
    update_file "$file" "templates/shared/\.genesis/scripts/check-genesis-components\.sh\.template" "templates/shared/.genesis/scripts/validation/check-genesis-components.sh.template"
    update_file "$file" "templates/shared/\.genesis/scripts/check-variable-defaults\.sh\.template" "templates/shared/.genesis/scripts/validation/check-variable-defaults.sh.template"
    update_file "$file" "templates/shared/\.genesis/scripts/check-file-organization\.sh\.template" "templates/shared/.genesis/scripts/validation/check-file-organization.sh.template"
    update_file "$file" "templates/shared/\.genesis/scripts/check-ai-signatures\.sh\.template" "templates/shared/.genesis/scripts/validation/check-ai-signatures.sh.template"
    update_file "$file" "templates/shared/\.genesis/scripts/find-hardcoded-values\.sh\.template" "templates/shared/.genesis/scripts/validation/find-hardcoded-values.sh.template"
    update_file "$file" "templates/shared/\.genesis/scripts/validate-components\.sh\.template" "templates/shared/.genesis/scripts/validation/validate-components.sh.template"
    update_file "$file" "templates/shared/\.genesis/scripts/validate-bootstrap\.sh\.template" "templates/shared/.genesis/scripts/validation/validate-bootstrap.sh.template"
done

# Update build script references
log_info "Updating build script references..."

find . -name "*.py" -type f -exec grep -l "\.genesis/scripts/bump-version\.sh" {} \; | while read -r file; do
    update_file "$file" "\.genesis/scripts/bump-version\.sh" ".genesis/scripts/build/bump-version.sh"
done

if [[ "$DRY_RUN" == "true" ]]; then
    log_info "Dry run complete. Remove --dry-run to apply changes."
else
    log_info "Script reference updates complete!"
fi
