#!/usr/bin/env bash
# Fix all slash command worktree instructions for pure module isolation

set -euo pipefail

echo "🔧 Fixing slash command worktree instructions for pure module isolation..."

# Commands to fix
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

    echo "📝 Updating $file..."

    # Fix 1: Replace --include with --focus and correct the file list
    sed -i.bak 's/--include \.genesis\//--focus .genesis\//g' "$file"
    sed -i.bak 's/--include \.claude\//--focus genesis\//g' "$file"
    sed -i.bak 's/--include scripts\//--focus shared-python\//g' "$file"
    sed -i.bak 's/--include shared-python\//--focus shared-python\//g' "$file"
    sed -i.bak 's/--include Makefile/--focus Makefile/g' "$file"
    sed -i.bak 's/--include pyproject\.toml/--focus pyproject.toml/g' "$file"
    sed -i.bak 's/--include pytest\.ini/--focus pytest.ini \\/' "$file"
    sed -i.bak 's/--include \.pre-commit-config\.yaml/--focus poetry.lock \\\n  --focus .pre-commit-config.yaml/g' "$file"
    sed -i.bak 's/--include \.envrc/--focus .envrc/g' "$file"

    # Fix 2: Move --max-files to the end of the command
    sed -i.bak 's/--max-files 30 \\/--max-files 80/g' "$file"
    sed -i.bak '/genesis worktree create/,/--focus \.envrc/{
        /--max-files 80/d
    }' "$file"
    sed -i.bak '/--focus \.envrc/a\
  --max-files 80' "$file"

    # Fix 3: Add .venv symlink creation after cd to worktree
    # This is more complex and needs careful pattern matching

    # Fix 4: Update verification loop to check correct files
    sed -i.bak 's/for component in \.genesis \.claude scripts shared-python Makefile/for component in .genesis genesis shared-python Makefile pyproject.toml poetry.lock pytest.ini .envrc/g' "$file"

    # Fix 5: Update sparse-checkout add command
    sed -i.bak 's/git sparse-checkout add \.genesis\/ \.claude\/ scripts\/ shared-python\/ Makefile/git sparse-checkout add .genesis\/ genesis\/ shared-python\/ Makefile pyproject.toml poetry.lock pytest.ini .envrc .pre-commit-config.yaml/g' "$file"

    echo "✅ Updated $file"
done

echo ""
echo "✅ All slash commands updated for pure module isolation!"
echo ""
echo "Key changes made:"
echo "  • Replaced --include with --focus"
echo "  • Added poetry.lock to file list"
echo "  • Removed .claude/ and scripts/ (replaced with genesis/)"
echo "  • Increased --max-files from 30 to 80"
echo "  • Updated verification to check all required files"
echo ""
echo "Note: Manual review recommended to add:"
echo "  • .venv symlink creation after cd to worktree"
echo "  • Pure module isolation context documentation"
