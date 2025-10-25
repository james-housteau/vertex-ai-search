"""Core orchestrator for managing CLI workflows."""

import subprocess
import time

from .models import ExecutionResult


class CLIOrchestrator:
    """Main orchestrator for coordinating CLI operations."""

    def __init__(self) -> None:
        """Initialize orchestrator."""
        self.execution_history: list[ExecutionResult] = []

    def execute_command(self, command: str, timeout: int = 300) -> ExecutionResult:
        """Execute a single command."""
        start_time = time.time()

        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=timeout
            )

            duration = time.time() - start_time
            execution_result = ExecutionResult(
                task=command,
                success=result.returncode == 0,
                duration=duration,
                output=result.stdout,
                error=result.stderr,
            )

            self.execution_history.append(execution_result)
            return execution_result

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            execution_result = ExecutionResult(
                task=command,
                success=False,
                duration=duration,
                output="",
                error="Command timed out",
            )

            self.execution_history.append(execution_result)
            return execution_result

    def get_history(self) -> list[ExecutionResult]:
        """Get execution history."""
        return self.execution_history.copy()

    def clear_history(self) -> None:
        """Clear execution history."""
        self.execution_history.clear()
