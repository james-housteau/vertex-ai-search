"""Main entry point for nq-downloader CLI."""

import os
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from .downloader import NQDownloader


console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """Natural Questions dataset downloader for Vertex AI search."""
    pass


@cli.command()
@click.option(
    "--shard",
    default="00",
    help="Shard ID to download (e.g., '00', '01', '02')",
    show_default=True,
)
@click.option(
    "--project-id",
    envvar="GOOGLE_CLOUD_PROJECT",
    help="Google Cloud project ID (can be set via GOOGLE_CLOUD_PROJECT env var)",
    required=True,
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=Path("./data"),
    help="Output directory for downloaded files",
    show_default=True,
)
@click.option(
    "--no-progress",
    is_flag=True,
    help="Disable progress bar display",
)
def download(shard: str, project_id: str, output_dir: Path, no_progress: bool) -> None:
    """Download a shard of the Natural Questions dataset."""
    console.print("[bold blue]NQ Downloader v0.1.0[/bold blue]")
    console.print(f"Project ID: {project_id}")
    console.print(f"Shard: {shard}")
    console.print(f"Output directory: {output_dir}")
    console.print()

    try:
        downloader = NQDownloader(project_id=project_id, output_dir=output_dir)

        console.print(f"[yellow]Starting download of shard {shard}...[/yellow]")
        result = downloader.download_shard(
            shard_id=shard, show_progress=not no_progress
        )

        if result.success:
            console.print("[green]✓ Download completed successfully![/green]")

            # Display results table
            table = Table(title="Download Summary")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("File", str(result.local_path))
            table.add_row("Size", f"{result.file_size:,} bytes")
            table.add_row("Time", f"{result.download_time_seconds:.2f} seconds")
            table.add_row(
                "Speed",
                f"{result.file_size / result.download_time_seconds / 1024 / 1024:.2f} MB/s",
            )
            table.add_row("Checksum", result.checksum[:16] + "...")

            console.print(table)
        else:
            console.print(f"[red]✗ Download failed: {result.error_message}[/red]")
            raise click.ClickException(f"Download failed: {result.error_message}")

    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise click.ClickException(str(e))


@cli.command()
@click.argument("file_path", type=click.Path(exists=True, path_type=Path))
def validate(file_path: Path) -> None:
    """Validate a downloaded NQ dataset file."""
    console.print(f"[bold blue]Validating file: {file_path}[/bold blue]")

    # Basic file validation
    if not file_path.exists():
        console.print("[red]✗ File does not exist[/red]")
        raise click.ClickException("File validation failed")

    if file_path.suffix != ".gz":
        console.print(
            f"[yellow]⚠ Warning: Expected .gz file, got {file_path.suffix}[/yellow]"
        )

    file_size = file_path.stat().st_size
    console.print("[green]✓ File exists[/green]")
    console.print(f"[green]✓ Size: {file_size:,} bytes[/green]")

    # Calculate checksum
    downloader = NQDownloader(
        project_id="dummy"
    )  # Project ID not needed for validation
    try:
        checksum = downloader._calculate_checksum(file_path)
        console.print(f"[green]✓ Checksum: {checksum}[/green]")
    except Exception as e:
        console.print(f"[red]✗ Checksum calculation failed: {str(e)}[/red]")
        raise click.ClickException("Checksum calculation failed")


@cli.command()
def status() -> None:
    """Display application status and environment information."""
    console.print("[bold blue]NQ Downloader Status[/bold blue]")
    console.print()

    # Environment info
    table = Table(title="Environment Information")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Version", "0.1.0")
    table.add_row("Python Path", str(Path(__file__).parent))

    # Check environment variables
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if project_id:
        table.add_row("GOOGLE_CLOUD_PROJECT", project_id)
    else:
        table.add_row("GOOGLE_CLOUD_PROJECT", "[red]Not set[/red]")

    # Check Google Cloud credentials
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if creds_path:
        table.add_row("GOOGLE_APPLICATION_CREDENTIALS", creds_path)
    else:
        table.add_row(
            "GOOGLE_APPLICATION_CREDENTIALS",
            "[yellow]Using default credentials[/yellow]",
        )

    console.print(table)


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
