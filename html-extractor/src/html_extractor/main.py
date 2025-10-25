"""Main entry point for html-extractor CLI."""

import json
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from .extractor import NaturalQuestionsExtractor, Stats

console = Console()


@click.group()
def main() -> None:
    """HTML document extraction from Natural Questions dataset."""
    pass


@main.command()
@click.argument("jsonl_gz_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output JSON file for extracted documents",
)
@click.option(
    "--stats-only", is_flag=True, help="Show only statistics without saving documents"
)
def process_nq_dataset(jsonl_gz_path: Path, output: Path, stats_only: bool) -> None:
    """Process Natural Questions JSONL.gz dataset and extract HTML documents."""
    console.print(f"[blue]Processing Natural Questions dataset: {jsonl_gz_path}[/blue]")

    extractor = NaturalQuestionsExtractor()
    result = extractor.extract_html_documents(jsonl_gz_path)

    if not result.success:
        console.print(f"[red]Error: {result.error_message}[/red]")
        return

    if result.stats:
        _display_statistics(result.stats)

    if not stats_only:
        if output:
            _save_documents(result.documents, output)
        else:
            console.print(
                f"[green]Successfully processed {len(result.documents)} unique documents[/green]"
            )
            console.print("[yellow]Use --output to save documents to file[/yellow]")


def _display_statistics(stats: Stats) -> None:
    """Display extraction statistics in a formatted table."""
    table = Table(title="Natural Questions Processing Statistics")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Count", style="magenta")

    table.add_row("Total JSONL entries", str(stats.total_entries))
    table.add_row("Unique documents", str(stats.unique_documents))
    table.add_row("Duplicates removed", str(stats.duplicates_removed))

    console.print(table)


def _save_documents(documents: list, output_path: Path) -> None:
    """Save extracted documents to JSON file."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(documents, f, indent=2, ensure_ascii=False)
        console.print(
            f"[green]Saved {len(documents)} documents to {output_path}[/green]"
        )
    except Exception as e:
        console.print(f"[red]Failed to save documents: {e}[/red]")


if __name__ == "__main__":
    main()
