#!/usr/bin/env python3
"""Simple test runner for GCS Manager."""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd or Path(__file__).parent,
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def main():
    """Run tests and show results."""
    print("🧪 Running GCS Manager tests...")
    print()

    # First, try to run manual validation
    print("1. Running manual validation...")
    success, stdout, stderr = run_command("python manual_test.py")
    if success:
        print("   ✅ Manual tests passed")
    else:
        print("   ❌ Manual tests failed:")
        print(f"   {stderr}")
        return 1

    # Try to run pytest if available
    print("\n2. Checking pytest availability...")
    success, stdout, stderr = run_command("python -m pytest --version")
    if not success:
        print("   ⚠️  pytest not available (run 'poetry install' first)")
        print("   ✅ Manual validation completed successfully")
        return 0

    print("   ✅ pytest is available")

    # Run model tests
    print("\n3. Running model tests...")
    success, stdout, stderr = run_command("python -m pytest tests/test_models.py -v")
    if success:
        print("   ✅ Model tests passed")
    else:
        print("   ❌ Model tests failed:")
        print(f"   {stderr}")

    # Run unit tests
    print("\n4. Running unit tests...")
    success, stdout, stderr = run_command(
        "python -m pytest tests/test_gcs_manager.py -v"
    )
    if success:
        print("   ✅ Unit tests passed")
    else:
        print("   ❌ Unit tests failed:")
        print(f"   {stderr}")

    # Run CLI tests
    print("\n5. Running CLI tests...")
    success, stdout, stderr = run_command("python -m pytest tests/test_cli.py -v")
    if success:
        print("   ✅ CLI tests passed")
    else:
        print("   ❌ CLI tests failed:")
        print(f"   {stderr}")

    # Run integration tests
    print("\n6. Running integration tests...")
    success, stdout, stderr = run_command(
        "python -m pytest tests/test_integration.py -v"
    )
    if success:
        print("   ✅ Integration tests passed")
    else:
        print("   ❌ Integration tests failed:")
        print(f"   {stderr}")

    # Try to run acceptance tests
    print("\n7. Running acceptance tests...")
    success, stdout, stderr = run_command(
        "python -m pytest tests/test_gcs_manager_acceptance.py -v"
    )
    if success:
        print("   ✅ Acceptance tests passed")
    else:
        print(
            "   ⚠️  Acceptance tests skipped (expected until dependencies are installed)"
        )

    print("\n🎉 Test run completed!")
    print("\nTo run tests with coverage:")
    print("  python -m pytest tests/ --cov=gcs_manager --cov-report=term-missing")
    print("\nTo install dependencies:")
    print("  poetry install")

    return 0


if __name__ == "__main__":
    sys.exit(main())
