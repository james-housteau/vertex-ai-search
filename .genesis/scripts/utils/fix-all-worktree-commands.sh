#!/usr/bin/env bash
# Comprehensive fix for all worktree commands and templates
# Updates both .claude/commands/*.md and templates/shared/.claude/commands/*.md.template

set -euo pipefail

echo "🔧 Fixing ALL worktree commands and templates for pure module isolation..."
echo ""

# Define the correct worktree creation pattern
CORRECT_PATTERN='genesis worktree create $NAME \
  --focus genesis/ \
  --focus .genesis/ \
  --focus shared-python/ \
  --focus Makefile \
  --focus pyproject.toml \
  --focus poetry.lock \
  --focus pytest.ini \
  --focus .envrc \
  --focus .pre-commit-config.yaml \
  --max-files 80'

# Function to fix a single file
fix_worktree_file() {
    local file="$1"
    local worktree_name="$2"

    echo "📝 Fixing $file..."

    # Create backup
    cp "$file" "${file}.backup.$(date +%s)"

    # Step 1: Remove old --include patterns and replace with --focus
    sed -i '' 's/--include/--focus/g' "$file"

    # Step 2: Fix the worktree create command structure
    # This is complex, so we'll use a more targeted approach

    # First, find and replace the entire worktree create block
    python3 << EOF
import re
import sys

with open("$file", 'r') as f:
    content = f.read()

# Pattern to match the old worktree create command
old_pattern = r'genesis worktree create ([^\s]+).*?(?:--max-files \d+)?'
old_pattern_multiline = r'genesis worktree create ([^\s\\\\]+)[^#]*?(?=\n(?:[^\\s]|\$|#))'

# First, fix single-line patterns
content = re.sub(
    r'genesis worktree create fix-\\\$1 --focus src/ --max-files 30.*?--include \.pre-commit-config\.yaml',
    '''genesis worktree create fix-\$1 \\\\
  --focus genesis/ \\\\
  --focus .genesis/ \\\\
  --focus shared-python/ \\\\
  --focus Makefile \\\\
  --focus pyproject.toml \\\\
  --focus poetry.lock \\\\
  --focus pytest.ini \\\\
  --focus .envrc \\\\
  --focus .pre-commit-config.yaml \\\\
  --max-files 80''',
    content,
    flags=re.DOTALL
)

# Fix for feature command
content = re.sub(
    r'genesis worktree create feature-\\\$1[^#]*?--max-files \d+',
    '''genesis worktree create feature-\$1 \\\\
  --focus genesis/ \\\\
  --focus .genesis/ \\\\
  --focus shared-python/ \\\\
  --focus Makefile \\\\
  --focus pyproject.toml \\\\
  --focus poetry.lock \\\\
  --focus pytest.ini \\\\
  --focus .envrc \\\\
  --focus .pre-commit-config.yaml \\\\
  --max-files 80''',
    content,
    flags=re.DOTALL
)

# Fix for bug command
content = re.sub(
    r'genesis worktree create fix-\\\$1[^#]*?--max-files \d+',
    '''genesis worktree create fix-\$1 \\\\
  --focus genesis/ \\\\
  --focus .genesis/ \\\\
  --focus shared-python/ \\\\
  --focus Makefile \\\\
  --focus pyproject.toml \\\\
  --focus poetry.lock \\\\
  --focus pytest.ini \\\\
  --focus .envrc \\\\
  --focus .pre-commit-config.yaml \\\\
  --max-files 80''',
    content,
    flags=re.DOTALL
)

# Fix for cleanup command
content = re.sub(
    r'genesis worktree create cleanup-\\\$1[^#]*?--max-files \d+',
    '''genesis worktree create cleanup-\$1 \\\\
  --focus genesis/ \\\\
  --focus .genesis/ \\\\
  --focus shared-python/ \\\\
  --focus Makefile \\\\
  --focus pyproject.toml \\\\
  --focus poetry.lock \\\\
  --focus pytest.ini \\\\
  --focus .envrc \\\\
  --focus .pre-commit-config.yaml \\\\
  --max-files 80''',
    content,
    flags=re.DOTALL
)

# Fix for deprecate command
content = re.sub(
    r'genesis worktree create deprecate-\\\$1[^#]*?--max-files \d+',
    '''genesis worktree create deprecate-\$1 \\\\
  --focus genesis/ \\\\
  --focus .genesis/ \\\\
  --focus shared-python/ \\\\
  --focus Makefile \\\\
  --focus pyproject.toml \\\\
  --focus poetry.lock \\\\
  --focus pytest.ini \\\\
  --focus .envrc \\\\
  --focus .pre-commit-config.yaml \\\\
  --max-files 80''',
    content,
    flags=re.DOTALL
)

# Fix for optimize command
content = re.sub(
    r'genesis worktree create optimize-\\\$1[^#]*?--max-files \d+',
    '''genesis worktree create optimize-\$1 \\\\
  --focus genesis/ \\\\
  --focus .genesis/ \\\\
  --focus shared-python/ \\\\
  --focus Makefile \\\\
  --focus pyproject.toml \\\\
  --focus poetry.lock \\\\
  --focus pytest.ini \\\\
  --focus .envrc \\\\
  --focus .pre-commit-config.yaml \\\\
  --max-files 80''',
    content,
    flags=re.DOTALL
)

# Fix for refactor command
content = re.sub(
    r'genesis worktree create refactor-\\\$1[^#]*?--max-files \d+',
    '''genesis worktree create refactor-\$1 \\\\
  --focus genesis/ \\\\
  --focus .genesis/ \\\\
  --focus shared-python/ \\\\
  --focus Makefile \\\\
  --focus pyproject.toml \\\\
  --focus poetry.lock \\\\
  --focus pytest.ini \\\\
  --focus .envrc \\\\
  --focus .pre-commit-config.yaml \\\\
  --max-files 80''',
    content,
    flags=re.DOTALL
)

# Fix for tdd command
content = re.sub(
    r'genesis worktree create fix-\\\$1 --focus src/ --max-files 30[^#]*?\.pre-commit-config\.yaml',
    '''genesis worktree create fix-\$1 \\\\
  --focus genesis/ \\\\
  --focus .genesis/ \\\\
  --focus shared-python/ \\\\
  --focus Makefile \\\\
  --focus pyproject.toml \\\\
  --focus poetry.lock \\\\
  --focus pytest.ini \\\\
  --focus .envrc \\\\
  --focus .pre-commit-config.yaml \\\\
  --max-files 80''',
    content,
    flags=re.DOTALL
)

with open("$file", 'w') as f:
    f.write(content)
EOF

    # Step 3: Add .venv symlink if not present
    if ! grep -q "ln -sf.*\.venv" "$file"; then
        # Add after cd to worktree
        sed -i '' '/^cd.*worktrees.*\$1/a\
\
# Create symlink to virtual environment for Python development\
ln -sf ../../.venv .venv || {\
    echo "⚠ Warning: Could not create .venv symlink"\
}
' "$file"
    fi

    # Step 4: Add Pure Module Isolation context if not present
    if ! grep -q "Pure Module Isolation" "$file"; then
        sed -i '' '/^# .* Workflow.*#\$1/a\
\
## CONTEXT: Pure Module Isolation\
\
This workflow creates a Genesis worktree with all supporting files needed for pure module isolation.\
A functional module requires not just its own code, but the Genesis infrastructure (.genesis/),\
shared utilities (shared-python/), and Python environment files (pyproject.toml, poetry.lock, .venv).
' "$file"
    fi

    # Step 5: Fix the verification loop
    sed -i '' 's/for component in \.genesis \.claude scripts shared-python Makefile/for component in .genesis genesis shared-python Makefile pyproject.toml poetry.lock pytest.ini .envrc/g' "$file"

    # Step 6: Fix sparse-checkout add command
    sed -i '' 's/git sparse-checkout add \.genesis\/ \.claude\/ scripts\/ shared-python\/ Makefile/git sparse-checkout add .genesis\/ genesis\/ shared-python\/ Makefile pyproject.toml poetry.lock pytest.ini .envrc .pre-commit-config.yaml/g' "$file"

    echo "✅ Fixed $file"
}

# Fix all slash commands
echo "=== Fixing slash commands ==="
for cmd in feature bug cleanup deprecate optimize refactor tdd; do
    if [[ -f ".claude/commands/${cmd}.md" ]]; then
        fix_worktree_file ".claude/commands/${cmd}.md" "${cmd}"
    fi
done

echo ""
echo "=== Fixing template commands ==="
# Fix all templates
for cmd in feature bug cleanup deprecate optimize refactor tdd; do
    template_file="templates/shared/.claude/commands/${cmd}.md.template"
    if [[ -f "$template_file" ]]; then
        fix_worktree_file "$template_file" "${cmd}"
    fi
done

echo ""
echo "=== Cleaning up backup files ==="
rm -f .claude/commands/*.backup.*
rm -f templates/shared/.claude/commands/*.backup.*

echo ""
echo "✅ ALL worktree commands and templates have been fixed!"
echo ""
echo "Summary of changes:"
echo "  • Fixed worktree create syntax (--include → --focus)"
echo "  • Added all required files for pure module isolation"
echo "  • Added .venv symlink creation"
echo "  • Added Pure Module Isolation context documentation"
echo "  • Updated verification loops"
echo "  • Fixed sparse-checkout commands"
echo ""
echo "Files updated:"
echo "  • 7 slash commands in .claude/commands/"
echo "  • 7 templates in templates/shared/.claude/commands/"
