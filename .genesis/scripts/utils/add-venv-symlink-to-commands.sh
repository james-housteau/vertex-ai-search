#!/usr/bin/env bash
# Add .venv symlink creation to all slash commands

set -euo pipefail

echo "🔧 Adding .venv symlink creation to slash commands..."

# Commands to update
COMMANDS=(
    "bug"
    "cleanup"
    "deprecate"
    "optimize"
    "refactor"
)

for cmd in "${COMMANDS[@]}"; do
    file=".claude/commands/${cmd}.md"

    if [[ ! -f "$file" ]]; then
        echo "⚠️  Skipping $file - not found"
        continue
    fi

    echo "📝 Adding .venv symlink to $file..."

    # Add .venv symlink creation after cd to worktree
    # Look for the pattern where we cd into the worktree and add the symlink after

    # For bug command which uses fix-$1
    if [[ "$cmd" == "bug" ]]; then
        sed -i.bak2 '/^cd \.\.\/worktrees\/fix-\$1\//,/^pwd.*VERIFY/{
            /^pwd.*VERIFY/i\
\
# Create symlink to virtual environment for Python development\
ln -sf ../../.venv .venv || {\
    echo "⚠ Warning: Could not create .venv symlink"\
}\

        }' "$file"
    else
        # For other commands using their own naming
        sed -i.bak2 '/^cd worktrees\/.*-\$1\//,/^pwd.*VERIFY/{
            /^pwd.*VERIFY/i\
\
# Create symlink to virtual environment for Python development\
ln -sf ../../.venv .venv || {\
    echo "⚠ Warning: Could not create .venv symlink"\
}\

        }' "$file"
    fi

    # Add pure module isolation context at the beginning
    if ! grep -q "Pure Module Isolation" "$file"; then
        sed -i.bak3 '/^# .* Workflow for Issue #\$1$/a\
\
## CONTEXT: Pure Module Isolation\
\
This workflow creates a Genesis worktree with all supporting files needed for pure module isolation.\
A functional module requires not just its own code, but the Genesis infrastructure (.genesis/),\
shared utilities (shared-python/), and Python environment files (pyproject.toml, poetry.lock, .venv).
        ' "$file"
    fi

    echo "✅ Updated $file"
done

echo ""
echo "✅ All slash commands updated with .venv symlink creation!"
echo ""
echo "Changes made:"
echo "  • Added .venv symlink creation after cd to worktree"
echo "  • Added Pure Module Isolation context documentation"
echo "  • Ensures Python virtual environment is available in worktree"
