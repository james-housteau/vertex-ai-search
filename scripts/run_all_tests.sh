#!/bin/bash
# Run tests for each module separately to avoid conftest import conflicts

set -e

echo "Running tests for each module..."
FAILED_MODULES=""
TOTAL_FAILURES=0

for module_dir in */; do
    if [ -d "${module_dir}tests" ]; then
        module_name=$(basename "$module_dir")
        echo "================================================"
        echo "Testing module: $module_name"
        echo "================================================"

        cd "$module_dir"
        if poetry run pytest tests/ -v --tb=short -m "not slow and not integration" --maxfail=5 2>&1; then
            echo "✅ $module_name: PASSED"
        else
            echo "❌ $module_name: FAILED"
            FAILED_MODULES="$FAILED_MODULES $module_name"
            ((TOTAL_FAILURES++))
        fi
        cd ..
        echo ""
    fi
done

if [ -n "$FAILED_MODULES" ]; then
    echo "================================================"
    echo "❌ FAILED MODULES:$FAILED_MODULES"
    echo "Total modules with failures: $TOTAL_FAILURES"
    exit 1
else
    echo "================================================"
    echo "✅ All tests passed!"
    exit 0
fi
