#!/usr/bin/env python3
"""Quick validation script to test mock configuration fixes."""

import subprocess
import sys
from pathlib import Path


def run_tests():
    """Run a subset of tests to validate mock configuration."""
    print("🔍 Running test validation...")

    # Add src to path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))

    # Run specific test files to validate mock configuration
    test_commands = [
        ["poetry", "run", "pytest", "tests/test_models.py", "-v"],
        [
            "poetry",
            "run",
            "pytest",
            "tests/test_search_engine.py::TestSearchEngine::test_initialization",
            "-v",
        ],
        [
            "poetry",
            "run",
            "pytest",
            "tests/test_acceptance.py::TestSearchEngineAPIContract::test_search_result_dataclass_structure",
            "-v",
        ],
    ]

    all_passed = True

    for i, cmd in enumerate(test_commands, 1):
        print(f"\n📝 Test {i}: {' '.join(cmd[-2:])}")
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=Path(__file__).parent
            )
            if result.returncode == 0:
                print("   ✅ PASSED")
            else:
                print("   ❌ FAILED")
                print(f"   STDOUT: {result.stdout}")
                print(f"   STDERR: {result.stderr}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            all_passed = False

    return all_passed


def main():
    """Main validation function."""
    print("🚀 Search Engine Mock Configuration Validation")
    print("=" * 50)

    if run_tests():
        print("\n🎉 Mock configuration validation PASSED!")
        print("   Tests are properly configured with mocking.")
        return 0
    else:
        print("\n💥 Mock configuration validation FAILED!")
        print("   There are still issues with test configuration.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
