"""CLI commands for vertex-ai-search."""

import click
from rich.console import Console
from rich.panel import Panel

console = Console()

# Default values for CLI options
DEFAULT_GREETING_NAME = "World"
DEFAULT_GREETING_COUNT = 1
DEFAULT_DISPLAY_STYLE = "info"

@click.group()
@click.version_option(version="0.1.0", prog_name="vertex-ai-search")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """A vertex-ai-search project created with Genesis"""
    ctx.ensure_object(dict)

@cli.command()
@click.option('--name', '-n', help='Name to greet')
@click.option('--count', '-c', type=int, help='Number of greetings')
def hello(name: str, count: int) -> None:
    """Say hello to someone."""
    name = name or DEFAULT_GREETING_NAME
    count = count or DEFAULT_GREETING_COUNT
    for _ in range(count):
        console.print(f"Hello {name}! 👋")

@cli.command()
@click.argument('text')
@click.option(
    '--style',
    type=click.Choice(['info', 'success', 'warning', 'error']),
    help='Display style'
)
def display(text: str, style: str) -> None:
    """Display text with styling."""
    style = style or DEFAULT_DISPLAY_STYLE
    styles = {
        'info': 'blue',
        'success': 'green',
        'warning': 'yellow',
        'error': 'red'
    }

    panel = Panel(
        text,
        title=f"vertex-ai-search - {style.title()}",
        border_style=styles[style]
    )
    console.print(panel)

@cli.command()
def status() -> None:
    """Show application status."""
    console.print("✅ vertex-ai-search is running!")
    console.print("📦 Version: 0.1.0")
    console.print("🐍 Python CLI Tool")

if __name__ == '__main__':
    cli()
