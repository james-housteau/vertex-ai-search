"""Main entry point for document uploader CLI."""

import click
from pathlib import Path
from .uploader import DocumentUploader


@click.group()
def main() -> None:
    """Document uploader for Vertex AI search functionality."""
    pass


@main.command()
@click.argument("local_path", type=click.Path(exists=True, path_type=Path))
@click.option("--bucket", required=True, help="GCS bucket name")
@click.option("--project", required=True, help="Google Cloud project ID")
@click.option("--gcs-key", help="Custom GCS key for the file")
def upload_file(local_path: Path, bucket: str, project: str, gcs_key: str) -> None:
    """Upload a single file to GCS."""
    uploader = DocumentUploader(bucket_name=bucket, project_id=project)
    result = uploader.upload_file(local_path, gcs_key=gcs_key)

    if result.success:
        click.echo(f"✓ Uploaded {local_path} to {result.gcs_uri}")
    else:
        click.echo(f"✗ Failed to upload {local_path}: {result.error_message}")


@main.command()
@click.argument(
    "local_dir", type=click.Path(exists=True, file_okay=False, path_type=Path)
)
@click.option("--bucket", required=True, help="GCS bucket name")
@click.option("--project", required=True, help="Google Cloud project ID")
@click.option("--prefix", default="", help="GCS prefix for uploaded files")
@click.option("--workers", default=4, help="Number of parallel upload workers")
def upload_directory(
    local_dir: Path, bucket: str, project: str, prefix: str, workers: int
) -> None:
    """Upload all files from a directory to GCS."""
    uploader = DocumentUploader(
        bucket_name=bucket, project_id=project, max_workers=workers
    )
    result = uploader.upload_directory(local_dir, gcs_prefix=prefix)

    click.echo(f"Uploaded {result.successful_uploads}/{result.total_files} files")
    if result.failed_uploads > 0:
        click.echo(f"Failed uploads: {result.failed_files}")


if __name__ == "__main__":
    main()
