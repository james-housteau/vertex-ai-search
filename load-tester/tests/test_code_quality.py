"""Regression tests for code quality standards (Bug #16)."""

import subprocess
import sys
from pathlib import Path


class TestCodeQuality:
    """Test code quality compliance for load-tester module."""

    def test_ruff_linting_passes(self) -> None:
        """Test that ruff linting passes with no violations.

        Regression test for Bug #16: 155 ruff linting violations blocking commits.
        This test currently FAILS (155 violations) and will PASS once fixed.
        """
        # Get the load-tester module directory
        module_path = Path(__file__).parent.parent

        # Run ruff check on the load-tester module
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", str(module_path)],
            capture_output=True,
            text=True,
            cwd=module_path,
            check=False,
        )

        # Test passes when ruff returns exit code 0 (no violations)
        # Test fails when ruff returns exit code 1 (violations found)
        assert result.returncode == 0, (
            f"Ruff linting failed with {result.returncode} exit code. "
            f"Violations found:\n{result.stdout}\n{result.stderr}"
        )
