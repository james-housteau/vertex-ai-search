"""Main entry point for search-engine CLI."""

import click

from .search_engine import SearchEngine


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """Search Engine CLI for Vertex AI Agent Builder."""
    pass


@cli.command()
@click.option("--project-id", required=True, help="Google Cloud Project ID")
@click.option("--data-store-id", required=True, help="Vertex AI Data Store ID")
@click.option("--query", required=True, help="Search query")
@click.option("--max-results", default=10, help="Maximum number of results")
def search(project_id: str, data_store_id: str, query: str, max_results: int) -> None:
    """Execute a search query."""
    engine = SearchEngine(project_id, data_store_id)
    result = engine.search(query, max_results)

    if result.success:
        click.echo(f"Query: {result.query}")
        click.echo(f"Results: {result.result_count}")
        click.echo(f"Execution time: {result.execution_time_ms:.2f}ms")
        for i, doc in enumerate(result.results):
            click.echo(f"  {i+1}. {doc.get('title', 'No title')}")
    else:
        click.echo(f"Search failed: {result.error_message}")


@cli.command()
@click.option("--project-id", required=True, help="Google Cloud Project ID")
@click.option("--data-store-id", required=True, help="Vertex AI Data Store ID")
def validate(project_id: str, data_store_id: str) -> None:
    """Validate connection to Vertex AI search service."""
    engine = SearchEngine(project_id, data_store_id)
    is_valid = engine.validate_connection()

    if is_valid:
        click.echo("✅ Connection to Vertex AI search service is valid")
    else:
        click.echo("❌ Connection to Vertex AI search service failed")


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
