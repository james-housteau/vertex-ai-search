"""Tests for CLI interface."""

from click.testing import CliRunner
from cli_orchestrator.cli import cli


class TestCLI:
    """Test CLI commands."""

    def test_status(self) -> None:
        """Test status command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["status"])

        assert result.exit_code == 0
        assert "CLI Orchestrator v0.1.0" in result.output
        assert "Active" in result.output

    def test_execute_no_tasks(self) -> None:
        """Test execute command with no tasks."""
        runner = CliRunner()
        result = runner.invoke(cli, ["execute"])

        assert result.exit_code == 0
        assert "No tasks specified" in result.output

    def test_execute_with_tasks(self) -> None:
        """Test execute command with tasks."""
        runner = CliRunner()
        result = runner.invoke(cli, ["execute", "echo test"])

        assert result.exit_code == 0
        assert "Executing 1 tasks" in result.output
        assert "Execution Results" in result.output
