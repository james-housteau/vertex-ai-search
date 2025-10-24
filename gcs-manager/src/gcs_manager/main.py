"""Main entry point for GCS Manager CLI."""

import click
from rich.console import Console
from rich.table import Table

from .gcs_manager import GCSManager
from .models import BucketConfig


console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """GCS Manager - Google Cloud Storage bucket management for Vertex AI."""
    pass


@main.command()
@click.argument("bucket_name")
@click.option("--project-id", required=True, help="Google Cloud Project ID")
@click.option("--region", default="us", help="Bucket region (default: us)")
@click.option("--lifecycle-days", default=30, help="Lifecycle deletion days")
def create(bucket_name: str, project_id: str, region: str, lifecycle_days: int) -> None:
    """Create a new GCS bucket."""
    config = BucketConfig(
        name=bucket_name, region=region, lifecycle_days=lifecycle_days
    )

    manager = GCSManager(project_id=project_id, config=config)
    result = manager.create_bucket(bucket_name, region)

    if result.created:
        console.print(
            f"✅ Bucket created successfully: {result.bucket_uri}", style="green"
        )
        console.print(f"   Region: {result.region}")
        console.print(f"   Lifecycle: {lifecycle_days} days")
    else:
        console.print(f"❌ Failed to create bucket: {result.error_message}", style="red")


@main.command()
@click.argument("bucket_name")
@click.option("--project-id", required=True, help="Google Cloud Project ID")
def info(bucket_name: str, project_id: str) -> None:
    """Get information about a bucket."""
    manager = GCSManager(project_id=project_id)
    bucket_info = manager.get_bucket_info(bucket_name)

    if bucket_info:
        table = Table(title=f"Bucket Information: {bucket_name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Name", bucket_info.bucket_name)
        table.add_row("URI", bucket_info.bucket_uri)
        table.add_row("Region", bucket_info.region)

        console.print(table)
    else:
        console.print(f"❌ Bucket not found: {bucket_name}", style="red")


@main.command()
@click.argument("bucket_name")
@click.option("--project-id", required=True, help="Google Cloud Project ID")
@click.option("--force", is_flag=True, help="Delete bucket contents first")
def delete(bucket_name: str, project_id: str, force: bool) -> None:
    """Delete a GCS bucket."""
    if not force:
        if not click.confirm(
            f"Are you sure you want to delete bucket '{bucket_name}'?"
        ):
            console.print("Operation cancelled.", style="yellow")
            return

    manager = GCSManager(project_id=project_id)
    success = manager.delete_bucket(bucket_name, force=force)

    if success:
        console.print(f"✅ Bucket deleted successfully: {bucket_name}", style="green")
    else:
        console.print(f"❌ Failed to delete bucket: {bucket_name}", style="red")


if __name__ == "__main__":
    main()
