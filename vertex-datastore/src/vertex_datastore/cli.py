"""Command-line interface for vertex-datastore."""


import click

from .datastore_manager import VertexDataStoreManager


@click.group()
@click.option("--project-id", required=True, help="Google Cloud project ID")
@click.option("--location", default="global", help="Vertex AI location")
@click.pass_context
def cli(ctx: click.Context, project_id: str, location: str) -> None:
    """Vertex AI Data Store Manager CLI."""
    ctx.ensure_object(dict)
    ctx.obj["manager"] = VertexDataStoreManager(project_id, location)


@cli.command()
@click.argument("display_name")
@click.argument("gcs_path")
@click.pass_context
def create(ctx: click.Context, display_name: str, gcs_path: str) -> None:
    """Create a new data store."""
    manager: VertexDataStoreManager = ctx.obj["manager"]
    result = manager.create_data_store(display_name, gcs_path)

    click.echo("✅ Data store created successfully!")
    click.echo(f"   ID: {result.data_store_id}")
    click.echo(f"   Display Name: {result.display_name}")
    click.echo(f"   Status: {result.status}")
    click.echo(f"   Serving Config: {result.serving_config_path}")


@cli.command()
@click.argument("data_store_id")
@click.argument("gcs_path")
@click.pass_context
def import_docs(ctx: click.Context, data_store_id: str, gcs_path: str) -> None:
    """Import documents into a data store."""
    manager: VertexDataStoreManager = ctx.obj["manager"]
    operation_id = manager.import_documents(data_store_id, gcs_path)

    click.echo("📥 Document import started!")
    click.echo(f"   Operation ID: {operation_id}")
    click.echo("   Use 'status' command to monitor progress.")


@cli.command()
@click.argument("operation_id")
@click.pass_context
def status(ctx: click.Context, operation_id: str) -> None:
    """Check import operation status."""
    manager: VertexDataStoreManager = ctx.obj["manager"]
    progress = manager.get_import_progress(operation_id)

    click.echo(f"📊 Import Status: {progress.status}")
    click.echo(f"   Progress: {progress.progress_percent:.1f}%")
    click.echo(
        f"   Documents: {progress.documents_processed}/{progress.documents_total}"
    )

    if progress.estimated_completion_time:
        click.echo(f"   Estimated completion: {progress.estimated_completion_time}")


@cli.command()
@click.argument("data_store_id")
@click.option("--force", is_flag=True, help="Force deletion even with documents")
@click.pass_context
def delete(ctx: click.Context, data_store_id: str, force: bool) -> None:
    """Delete a data store."""
    manager: VertexDataStoreManager = ctx.obj["manager"]

    if not force:
        click.confirm(
            f"Are you sure you want to delete data store '{data_store_id}'?", abort=True
        )

    deleted = manager.delete_data_store(data_store_id, force=force)

    if deleted:
        click.echo(f"🗑️  Data store '{data_store_id}' deleted successfully!")
    else:
        click.echo(f"❌ Failed to delete data store '{data_store_id}'")


@cli.command()
@click.argument("data_store_id")
@click.pass_context
def serving_config(ctx: click.Context, data_store_id: str) -> None:
    """Get serving config path for a data store."""
    manager: VertexDataStoreManager = ctx.obj["manager"]
    config_path = manager.get_serving_config(data_store_id)

    click.echo("🔧 Serving Config Path:")
    click.echo(f"   {config_path}")


if __name__ == "__main__":
    cli()
