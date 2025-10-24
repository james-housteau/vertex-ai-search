"""Main entry point for CLI Orchestrator."""

from rich.console import Console

from .cli import cli


def main() -> None:
    """Main entry point."""
    try:
        cli()
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
    except Exception as e:
        console = Console()
        console.print(f"[red]Error: {e}[/red]")
        raise


if __name__ == "__main__":
    main()
