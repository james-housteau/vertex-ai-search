"""CLI interface for orchestrator."""

import click
from rich.console import Console
from rich.table import Table

from .task_manager import TaskManager

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """CLI Orchestrator - Framework for coordinating multiple tools and workflows."""
    pass


@cli.command()
@click.argument("tasks", nargs=-1)
@click.option("--parallel", is_flag=True, help="Run tasks in parallel")
@click.option("--timeout", default=300, help="Timeout for tasks")
def execute(tasks: tuple[str, ...], parallel: bool, timeout: int) -> None:
    """Execute a series of tasks."""
    if not tasks:
        console.print("[red]No tasks specified[/red]")
        return

    task_manager = TaskManager()

    console.print(f"[blue]Executing {len(tasks)} tasks[/blue]")

    if parallel:
        results = task_manager.run_parallel(list(tasks), timeout)
    else:
        results = task_manager.run_sequential(list(tasks), timeout)

    # Display results
    table = Table(title="Execution Results")
    table.add_column("Task", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Duration", style="yellow")

    for result in results:
        status = "✓ Success" if result.success else "✗ Failed"
        table.add_row(result.task, status, f"{result.duration:.2f}s")

    console.print(table)


@cli.command()
def status() -> None:
    """Show orchestrator status."""
    console.print("[green]CLI Orchestrator v0.1.0[/green]")
    console.print("Status: [green]Active[/green]")
