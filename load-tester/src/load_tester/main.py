"""CLI entry point for load-tester module."""

import sys

import click

from .load_tester import create_load_tester_with_mocks
from .models import LoadTestConfig


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """Load Tester - End-to-End Load Testing for Vertex AI Search system."""


@cli.command()
@click.option("--concurrent-users", "-u", default=5, help="Number of concurrent users")
@click.option("--duration", "-d", default=10, help="Test duration in seconds")
@click.option("--ramp-up", "-r", default=0, help="Ramp-up time in seconds")
@click.option("--search-queries", "-s", multiple=True, help="Search queries to test")
@click.option(
    "--conversation-queries",
    "-c",
    multiple=True,
    help="Conversation queries to test",
)
@click.option("--project-id", default="test-project", help="Google Cloud project ID")
@click.option(
    "--data-store-id",
    default="test-datastore",
    help="Vertex AI data store ID",
)
def run_load_test(
    concurrent_users: int,
    duration: int,
    ramp_up: int,
    search_queries: tuple[str, ...],
    conversation_queries: tuple[str, ...],
    project_id: str,
    data_store_id: str,
) -> None:
    """Run comprehensive load test with mixed search and conversation operations."""
    click.echo("🚀 Starting comprehensive load test...")

    # Default queries if none provided
    search_list = (
        list(search_queries)
        if search_queries
        else [
            "What is machine learning?",
            "How does AI work?",
            "Python programming basics",
        ]
    )

    conversation_list = (
        list(conversation_queries)
        if conversation_queries
        else [
            "Explain artificial intelligence",
            "What are the benefits of cloud computing?",
            "How to get started with programming?",
        ]
    )

    # Create load tester with mock services
    load_tester = create_load_tester_with_mocks(project_id, data_store_id)

    # Configure and run test
    config = LoadTestConfig(
        concurrent_users=concurrent_users,
        test_duration_seconds=duration,
        search_queries=search_list,
        conversation_queries=conversation_list,
        ramp_up_time_seconds=ramp_up,
    )

    result = load_tester.run_load_test(config)

    # Generate and display report
    report = load_tester.generate_comprehensive_report(result)
    click.echo(report)

    if result.success:
        click.echo("✅ Load test completed successfully!")
    else:
        click.echo("❌ Load test failed - error rate too high")
        sys.exit(1)


@cli.command()
@click.option("--concurrent-users", "-u", default=5, help="Number of concurrent users")
@click.option("--duration", "-d", default=10, help="Test duration in seconds")
@click.option("--queries", "-q", multiple=True, help="Search queries to test")
@click.option("--project-id", default="test-project", help="Google Cloud project ID")
@click.option(
    "--data-store-id",
    default="test-datastore",
    help="Vertex AI data store ID",
)
def search_load_test(
    concurrent_users: int,
    duration: int,
    queries: tuple[str, ...],
    project_id: str,
    data_store_id: str,
) -> None:
    """Run search-only load test."""
    click.echo("🔍 Starting search load test...")

    # Default queries if none provided
    query_list = (
        list(queries)
        if queries
        else [
            "What is machine learning?",
            "How does AI work?",
            "Python programming basics",
            "Cloud computing concepts",
            "Data science fundamentals",
        ]
    )

    # Create load tester with mock services
    load_tester = create_load_tester_with_mocks(project_id, data_store_id)

    # Run search-only test
    result = load_tester.run_search_load_test(query_list, concurrent_users, duration)

    # Generate and display report
    report = load_tester.generate_comprehensive_report(result)
    click.echo(report)

    if result.success:
        click.echo("✅ Search load test completed successfully!")
    else:
        click.echo("❌ Search load test failed - error rate too high")
        sys.exit(1)


@cli.command()
@click.option("--concurrent-users", "-u", default=5, help="Number of concurrent users")
@click.option("--duration", "-d", default=10, help="Test duration in seconds")
@click.option("--queries", "-q", multiple=True, help="Conversation queries to test")
@click.option("--project-id", default="test-project", help="Google Cloud project ID")
@click.option(
    "--data-store-id",
    default="test-datastore",
    help="Vertex AI data store ID",
)
def conversation_load_test(
    concurrent_users: int,
    duration: int,
    queries: tuple[str, ...],
    project_id: str,
    data_store_id: str,
) -> None:
    """Run conversation-only load test."""
    click.echo("💬 Starting conversation load test...")

    # Default queries if none provided
    query_list = (
        list(queries)
        if queries
        else [
            "Explain artificial intelligence",
            "What are the benefits of cloud computing?",
            "How to get started with programming?",
            "What is the future of AI?",
            "Best practices for software development",
        ]
    )

    # Create load tester with mock services
    load_tester = create_load_tester_with_mocks(project_id, data_store_id)

    # Run conversation-only test
    result = load_tester.run_conversation_load_test(
        query_list,
        concurrent_users,
        duration,
    )

    # Generate and display report
    report = load_tester.generate_comprehensive_report(result)
    click.echo(report)

    if result.success:
        click.echo("✅ Conversation load test completed successfully!")
    else:
        click.echo("❌ Conversation load test failed - error rate too high")
        sys.exit(1)


@cli.command()
@click.option("--project-id", default="test-project", help="Google Cloud project ID")
@click.option(
    "--data-store-id",
    default="test-datastore",
    help="Vertex AI data store ID",
)
def validate(project_id: str, data_store_id: str) -> None:
    """Validate connection to all required services."""
    click.echo("🔧 Validating service connections...")

    # Create load tester with mock services
    load_tester = create_load_tester_with_mocks(project_id, data_store_id)

    # Validate connections
    search_valid = load_tester.search_engine.validate_connection()
    answer_valid = load_tester.answer_service.validate_connection()

    click.echo(f"Search Engine: {'✅ Connected' if search_valid else '❌ Failed'}")
    click.echo(f"Answer Service: {'✅ Connected' if answer_valid else '❌ Failed'}")

    if search_valid and answer_valid:
        click.echo("✅ All services validated successfully!")
    else:
        click.echo("❌ Service validation failed")
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
