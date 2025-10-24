"""Tests for task manager."""

from cli_orchestrator.task_manager import TaskManager


class TestTaskManager:
    """Test TaskManager class."""

    def test_init(self) -> None:
        """Test task manager initialization."""
        manager = TaskManager()
        assert manager.orchestrator is not None

    def test_run_sequential_success(self) -> None:
        """Test sequential task execution with success."""
        manager = TaskManager()
        tasks = ["echo 'task1'", "echo 'task2'"]

        results = manager.run_sequential(tasks)

        assert len(results) == 2
        assert all(result.success for result in results)
        assert results[0].task == "echo 'task1'"
        assert results[1].task == "echo 'task2'"

    def test_run_sequential_failure_stops(self) -> None:
        """Test sequential execution stops on failure."""
        manager = TaskManager()
        tasks = ["nonexistent_command", "echo 'task2'"]

        results = manager.run_sequential(tasks)

        assert len(results) == 1  # Should stop after first failure
        assert results[0].success is False

    def test_run_parallel(self) -> None:
        """Test parallel task execution."""
        manager = TaskManager()
        tasks = ["echo 'task1'", "echo 'task2'", "echo 'task3'"]

        results = manager.run_parallel(tasks)

        assert len(results) == 3
        # Results should be in original task order
        assert results[0].task == "echo 'task1'"
        assert results[1].task == "echo 'task2'"
        assert results[2].task == "echo 'task3'"
