#!/usr/bin/env bash
# Fix condensed commands that have incomplete worktree setup

set -euo pipefail

echo "🔧 Fixing condensed slash commands..."

# Commands with condensed setup
CONDENSED_COMMANDS=(
    "cleanup"
    "deprecate"
    "optimize"
    "refactor"
)

for cmd in "${CONDENSED_COMMANDS[@]}"; do
    file=".claude/commands/${cmd}.md"

    if [[ ! -f "$file" ]]; then
        echo "⚠️  Skipping $file - not found"
        continue
    fi

    echo "📝 Fixing $file..."

    # Fix the condensed worktree create command
    # The current version is missing 'genesis worktree create' at the beginning
    sed -i.bak4 's/^  --focus \.genesis\//genesis worktree create '"${cmd}"'-$1 \\\
  --focus .genesis\//g' "$file"

    # Also add the .venv symlink and pwd verification after cd
    sed -i.bak5 '/^cd worktrees\/'"${cmd}"'-\$1\/$/a\
\
# Create symlink to virtual environment for Python development\
ln -sf ../../.venv .venv || {\
    echo "⚠ Warning: Could not create .venv symlink"\
}\
\
pwd  # VERIFY: Must show .../genesis/worktrees/'"${cmd}"'-$1
' "$file"

    echo "✅ Updated $file"
done

# Clean up backup files
rm .claude/commands/*.bak4 .claude/commands/*.bak5 2>/dev/null || true

echo ""
echo "✅ Fixed all condensed commands!"
