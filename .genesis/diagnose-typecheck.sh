#!/bin/bash
# Genesis Typecheck Diagnostic Script
# Helps understand why genesis typecheck can't find source directories

echo "=== Genesis Typecheck Diagnostic ==="
echo ""
echo "Current directory: $(pwd)"
echo "Project type from .envrc: ${PROJECT_TYPE:-not set}"
echo "Source dir from .envrc: ${SRC_DIR:-not set}"
echo ""

echo "=== What Genesis Typecheck Looks For ==="
echo "Genesis CLI is hardcoded to check these directories:"
echo "  - genesis/"
echo "  - bootstrap/"
echo "  - shared-python/src/"
echo "  - smart-commit/src/"
echo "  - testing/src/"
echo ""

echo "=== Directories Found in This Project ==="
HARDCODED_PATHS=(
  "genesis/"
  "bootstrap/"
  "shared-python/src/"
  "smart-commit/src/"
  "testing/src/"
)

found_count=0
for path in "${HARDCODED_PATHS[@]}"; do
  if [ -d "$path" ]; then
    echo "  ✅ Found: $path"
    ((found_count++))
  else
    echo "  ❌ Missing: $path"
  fi
done

echo ""
if [ $found_count -eq 0 ]; then
  echo "⚠️  No hardcoded directories found - genesis typecheck will fail"
else
  echo "✅ Found $found_count hardcoded directories"
fi

echo ""
echo "=== Actual Source Directories in This Project ==="
if [ -d "src" ]; then
  echo "  📁 src/ directory exists"
  find src -name "*.py" -type f | head -5
  total=$(find src -name "*.py" -type f | wc -l | tr -d ' ')
  echo "  Found $total Python files in src/"
fi

# Check for module-based structure
module_count=$(find . -maxdepth 2 -type d -name "src" 2>/dev/null | wc -l | tr -d ' ')
if [ $module_count -gt 0 ]; then
  echo "  📁 Found $module_count module-level src/ directories:"
  find . -maxdepth 2 -type d -name "src" 2>/dev/null | head -5
fi

echo ""
echo "=== Recommendations ==="
if [ $found_count -eq 0 ]; then
  echo "Genesis typecheck won't work for this project structure."
  echo ""
  echo "Options:"
  echo "1. Use 'make typecheck' instead (if Makefile exists)"
  echo "2. Use 'poetry run mypy -p <package-name>' directly"
  echo "3. Request genesis CLI enhancement to support:"
  echo "   - Reading PROJECT_TYPE and SRC_DIR environment variables"
  echo "   - Auto-discovering Python packages in src/"
  echo "   - Supporting monorepo structures with multiple modules"
fi
