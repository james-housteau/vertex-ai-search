"""Tests for CLI orchestrator."""

from cli_orchestrator.orchestrator import CLIOrchestrator
from cli_orchestrator.models import ExecutionResult


class TestCLIOrchestrator:
    """Test CLIOrchestrator class."""

    def test_init(self) -> None:
        """Test orchestrator initialization."""
        orchestrator = CLIOrchestrator()
        assert orchestrator.execution_history == []

    def test_execute_command_success(self) -> None:
        """Test successful command execution."""
        orchestrator = CLIOrchestrator()
        result = orchestrator.execute_command("echo 'test'")

        assert isinstance(result, ExecutionResult)
        assert result.success is True
        assert "test" in result.output
        assert result.error == ""
        assert result.duration > 0

    def test_execute_command_failure(self) -> None:
        """Test failed command execution."""
        orchestrator = CLIOrchestrator()
        result = orchestrator.execute_command("nonexistent_command_xyz")

        assert isinstance(result, ExecutionResult)
        assert result.success is False
        assert result.duration > 0

    def test_execution_history(self) -> None:
        """Test execution history tracking."""
        orchestrator = CLIOrchestrator()

        # Execute multiple commands
        orchestrator.execute_command("echo 'test1'")
        orchestrator.execute_command("echo 'test2'")

        history = orchestrator.get_history()
        assert len(history) == 2
        assert history[0].task == "echo 'test1'"
        assert history[1].task == "echo 'test2'"

    def test_clear_history(self) -> None:
        """Test clearing execution history."""
        orchestrator = CLIOrchestrator()

        orchestrator.execute_command("echo 'test'")
        assert len(orchestrator.get_history()) == 1

        orchestrator.clear_history()
        assert len(orchestrator.get_history()) == 0


class TestExecutionResult:
    """Test ExecutionResult model."""

    def test_creation(self) -> None:
        """Test ExecutionResult creation."""
        result = ExecutionResult(
            task="test command",
            success=True,
            duration=1.5,
            output="test output",
            error="",
        )

        assert result.task == "test command"
        assert result.success is True
        assert result.duration == 1.5
        assert result.output == "test output"
        assert result.error == ""
