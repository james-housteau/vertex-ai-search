#!/usr/bin/env bash
# Test script to validate Genesis file reorganization
# Verifies all script references work after reorganization

set -euo pipefail

PROJECT_ROOT="/Users/source_code/genesis"
cd "$PROJECT_ROOT"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

TESTS_PASSED=0
TESTS_FAILED=0

test_result() {
    local test_name="$1"
    local result="$2"

    if [[ "$result" == "PASS" ]]; then
        echo -e "${GREEN}✓${NC} $test_name"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} $test_name"
        ((TESTS_FAILED++))
    fi
}

echo -e "${BLUE}=== Genesis File Reorganization Validation ===${NC}"
echo ""

# Test 1: Directory structure exists
echo "Testing directory structure..."

if [[ -d ".genesis/scripts/validation" ]] &&
   [[ -d ".genesis/scripts/build" ]] &&
   [[ -d ".genesis/scripts/setup" ]] &&
   [[ -d ".genesis/scripts/docker" ]] &&
   [[ -d ".genesis/scripts/utils" ]]; then
    test_result "Directory structure" "PASS"
else
    test_result "Directory structure" "FAIL"
fi

# Test 2: Key validation scripts exist
echo "Testing validation scripts..."

if [[ -f ".genesis/scripts/validation/check-file-organization.sh" ]] &&
   [[ -f ".genesis/scripts/validation/check-genesis-components.sh" ]] &&
   [[ -f ".genesis/scripts/validation/validate-bootstrap.sh" ]]; then
    test_result "Validation scripts exist" "PASS"
else
    test_result "Validation scripts exist" "FAIL"
fi

# Test 3: Build scripts exist
echo "Testing build scripts..."

if [[ -f ".genesis/scripts/build/build.sh" ]] &&
   [[ -f ".genesis/scripts/build/bump-version.sh" ]] &&
   [[ -f ".genesis/scripts/build/release.sh" ]]; then
    test_result "Build scripts exist" "PASS"
else
    test_result "Build scripts exist" "FAIL"
fi

# Test 4: Setup scripts exist
echo "Testing setup scripts..."

if [[ -f ".genesis/scripts/setup/setup.sh" ]] &&
   [[ -f ".genesis/scripts/setup/install-genesis.sh" ]]; then
    test_result "Setup scripts exist" "PASS"
else
    test_result "Setup scripts exist" "FAIL"
fi

# Test 5: Makefile references work
echo "Testing Makefile references..."

if make check-org --dry-run >/dev/null 2>&1; then
    test_result "Makefile check-org target" "PASS"
else
    test_result "Makefile check-org target" "FAIL"
fi

if make validate-bootstrap --dry-run >/dev/null 2>&1; then
    test_result "Makefile validate-bootstrap target" "PASS"
else
    test_result "Makefile validate-bootstrap target" "FAIL"
fi

# Test 6: Template structure matches
echo "Testing template structure..."

if [[ -d "templates/shared/.genesis/scripts/validation" ]] &&
   [[ -d "templates/shared/.genesis/scripts/build" ]] &&
   [[ -d "templates/shared/.genesis/scripts/setup" ]] &&
   [[ -d "templates/shared/.genesis/scripts/utils" ]]; then
    test_result "Template directory structure" "PASS"
else
    test_result "Template directory structure" "FAIL"
fi

# Test 7: Template files exist in correct locations
echo "Testing template files..."

if [[ -f "templates/shared/.genesis/scripts/validation/check-file-organization.sh.template" ]] &&
   [[ -f "templates/shared/.genesis/scripts/validation/check-genesis-components.sh.template" ]] &&
   [[ -f "templates/shared/.genesis/scripts/build/bump-version.sh.template" ]]; then
    test_result "Template files in subdirectories" "PASS"
else
    test_result "Template files in subdirectories" "FAIL"
fi

# Test 8: Manifest references are updated
echo "Testing manifest references..."

if grep -q "validation/check-file-organization.sh.template" templates/shared/manifest.yml &&
   grep -q "validation/check-genesis-components.sh.template" templates/shared/manifest.yml; then
    test_result "Manifest references validation subdirectory" "PASS"
else
    test_result "Manifest references validation subdirectory" "FAIL"
fi

# Test 9: Pre-commit config references are updated
echo "Testing pre-commit configuration..."

if grep -q ".genesis/scripts/validation/" templates/shared/.pre-commit-config.yaml.template; then
    test_result "Pre-commit config uses validation subdirectory" "PASS"
else
    test_result "Pre-commit config uses validation subdirectory" "FAIL"
fi

# Test 10: No orphaned scripts in root
echo "Testing for orphaned scripts..."

orphaned_scripts=$(find .genesis/scripts -maxdepth 1 -name "*.sh" -o -name "*.py" | wc -l)
if [[ "$orphaned_scripts" -eq 0 ]]; then
    test_result "No orphaned scripts in .genesis/scripts root" "PASS"
else
    test_result "No orphaned scripts in .genesis/scripts root" "FAIL"
fi

echo ""
echo -e "${BLUE}=== Test Results ===${NC}"
echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"

if [[ "$TESTS_FAILED" -eq 0 ]]; then
    echo -e "${GREEN}✓ All reorganization tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some reorganization tests failed.${NC}"
    exit 1
fi
