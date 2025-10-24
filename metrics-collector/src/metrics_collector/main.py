"""Main CLI entry point for metrics-collector module."""

from datetime import UTC, datetime
from pathlib import Path

import click

from .metrics_collector import MetricsCollector


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """Metrics Collector - Performance metrics collection and analysis."""


@cli.command()
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=Path("./metrics"),
    help="Output directory for metrics data",
)
def status(output_dir: Path) -> None:
    """Show metrics collector status and basic information."""
    collector = MetricsCollector(output_dir=output_dir)

    click.echo("Metrics Collector Status")
    click.echo("========================")
    click.echo(f"Output Directory: {output_dir.absolute()}")
    click.echo(f"Directory Exists: {output_dir.exists()}")
    click.echo(f"Current Time: {datetime.now(tz=UTC).strftime('%Y-%m-%d %H:%M:%S')}")

    # Generate empty report to show structure
    report = collector.generate_report()
    click.echo(f"Report Structure Ready: {type(report).__name__}")


@cli.command()
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=Path("./metrics"),
    help="Output directory for metrics data",
)
@click.option(
    "--json-file", type=click.Path(path_type=Path), help="Export metrics to JSON file"
)
@click.option(
    "--csv-file", type=click.Path(path_type=Path), help="Export metrics to CSV file"
)
def export(output_dir: Path, json_file: Path | None, csv_file: Path | None) -> None:
    """Export collected metrics to JSON or CSV format."""
    collector = MetricsCollector(output_dir=output_dir)

    if json_file:
        success = collector.export_to_json(json_file)
        if success:
            click.echo(f"✓ Metrics exported to JSON: {json_file}")
        else:
            click.echo(f"✗ Failed to export metrics to JSON: {json_file}")

    if csv_file:
        success = collector.export_to_csv(csv_file)
        if success:
            click.echo(f"✓ Metrics exported to CSV: {csv_file}")
        else:
            click.echo(f"✗ Failed to export metrics to CSV: {csv_file}")

    if not json_file and not csv_file:
        click.echo("No export format specified. Use --json-file or --csv-file options.")


@cli.command()
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=Path("./metrics"),
    help="Output directory for metrics data",
)
def report(output_dir: Path) -> None:
    """Generate and display performance metrics report."""
    collector = MetricsCollector(output_dir=output_dir)
    metrics = collector.generate_report()

    click.echo("Performance Metrics Report")
    click.echo("==========================")
    click.echo(f"Operation Type: {metrics.operation_type}")
    click.echo(f"Total Operations: {metrics.total_operations}")
    click.echo(f"Success Rate: {metrics.success_rate:.2f}%")
    click.echo(f"Error Count: {metrics.error_count}")
    click.echo(f"Average Response Time: {metrics.avg_response_time_ms:.2f}ms")
    click.echo(f"Median Response Time: {metrics.median_response_time_ms:.2f}ms")
    click.echo(f"95th Percentile Response Time: {metrics.p95_response_time_ms:.2f}ms")
    click.echo(f"Report Generated: {metrics.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")


def main() -> None:
    """Main entry point for the CLI application."""
    cli()


if __name__ == "__main__":
    main()
