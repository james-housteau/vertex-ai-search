"""Tests for data models."""

from cli_orchestrator.models import ExecutionResult


class TestExecutionResult:
    """Test ExecutionResult model."""

    def test_creation_minimal(self) -> None:
        """Test ExecutionResult creation with minimal data."""
        result = ExecutionResult(task="test", success=True, duration=1.0)

        assert result.task == "test"
        assert result.success is True
        assert result.duration == 1.0
        assert result.output == ""
        assert result.error == ""

    def test_creation_full(self) -> None:
        """Test ExecutionResult creation with all data."""
        result = ExecutionResult(
            task="test command",
            success=False,
            duration=2.5,
            output="some output",
            error="some error",
        )

        assert result.task == "test command"
        assert result.success is False
        assert result.duration == 2.5
        assert result.output == "some output"
        assert result.error == "some error"
