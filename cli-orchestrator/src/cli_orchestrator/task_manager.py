"""Task management for orchestrator."""

import concurrent.futures
from typing import List

from .models import ExecutionResult
from .orchestrator import CLIOrchestrator


class TaskManager:
    """Manages task execution patterns."""

    def __init__(self) -> None:
        """Initialize task manager."""
        self.orchestrator = CLIOrchestrator()

    def run_sequential(
        self, tasks: List[str], timeout: int = 300
    ) -> List[ExecutionResult]:
        """Run tasks sequentially."""
        results = []

        for task in tasks:
            result = self.orchestrator.execute_command(task, timeout)
            results.append(result)

            # Stop on first failure
            if not result.success:
                break

        return results

    def run_parallel(
        self, tasks: List[str], timeout: int = 300
    ) -> List[ExecutionResult]:
        """Run tasks in parallel."""
        results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_task = {
                executor.submit(self.orchestrator.execute_command, task, timeout): task
                for task in tasks
            }

            for future in concurrent.futures.as_completed(future_to_task):
                result = future.result()
                results.append(result)

        # Sort results by original task order
        task_order = {task: i for i, task in enumerate(tasks)}
        results.sort(key=lambda r: task_order.get(r.task, 999))

        return results
