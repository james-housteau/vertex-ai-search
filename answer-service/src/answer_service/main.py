"""Main entry point for Answer Service CLI."""

import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """Answer Service CLI for Vertex AI conversation testing."""
    pass


@main.command()
@click.option("--project-id", required=True, help="Google Cloud project ID")
@click.option("--question", required=True, help="Question to ask")
@click.option("--context", help="Optional context for the question")
def ask(project_id: str, question: str, context: str) -> None:
    """Ask a question using the conversation service."""
    from .service import AnswerService

    service = AnswerService(project_id=project_id, conversation_id="")
    conversation_id = service.start_conversation()

    result = service.ask_question(question=question, context=context)

    if result.success:
        console.print(f"[green]Question:[/green] {result.query}")
        console.print(f"[blue]Answer:[/blue] {result.answer}")
        console.print(f"[yellow]Confidence:[/yellow] {result.confidence_score:.2f}")
        console.print(f"[cyan]Response Time:[/cyan] {result.response_time_ms:.2f}ms")
        if result.sources:
            console.print(f"[magenta]Sources:[/magenta] {', '.join(result.sources)}")
    else:
        console.print(f"[red]Error:[/red] {result.error_message}")

    service.end_conversation(conversation_id)


@main.command()
def status() -> None:
    """Show application status."""
    console.print("[green]Answer Service v0.1.0[/green]")
    console.print("[blue]Ready for conversation testing[/blue]")


if __name__ == "__main__":
    main()
