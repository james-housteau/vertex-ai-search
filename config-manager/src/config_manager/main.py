"""CLI interface for config-manager."""

from pathlib import Path

import click

from .loader import load_config
from .models import ConfigManager


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """Configuration management for Vertex AI search functionality."""
    pass


@cli.command()
@click.option(
    "--environment",
    "-e",
    default="development",
    help="Environment to load configuration for",
)
@click.option(
    "--config-dir",
    "-c",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Configuration directory path",
)
def load(environment: str, config_dir: Path | None) -> None:
    """Load and display configuration for an environment."""
    try:
        config = load_config(environment, config_dir)
        click.echo(f"Configuration for environment '{environment}':")
        click.echo("")

        # Display key configuration values
        click.echo(f"App Name: {config.app_name}")
        click.echo(f"Version: {config.version}")
        click.echo(f"Debug: {config.debug}")
        click.echo(f"Log Level: {config.log_level}")
        click.echo(f"Host: {config.host}")
        click.echo(f"Port: {config.port}")
        click.echo(f"Timeout: {config.timeout}s")

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e
    except ValueError as e:
        click.echo(f"Configuration validation error: {e}", err=True)
        raise click.Abort() from e


@cli.command()
@click.option(
    "--config-dir",
    "-c",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Configuration directory path",
)
def list_environments(config_dir: Path | None) -> None:
    """List available environment configurations."""
    config_manager = ConfigManager(config_dir)
    environments = config_manager.get_available_environments()

    if environments:
        click.echo("Available environments:")
        for env in environments:
            click.echo(f"  - {env}")
    else:
        click.echo("No environment configurations found.")


@cli.command()
@click.option(
    "--environment",
    "-e",
    default="development",
    help="Environment to validate configuration for",
)
@click.option(
    "--config-dir",
    "-c",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Configuration directory path",
)
def validate(environment: str, config_dir: Path | None) -> None:
    """Validate configuration for an environment."""
    try:
        config = load_config(environment, config_dir)
        click.echo(f" Configuration for '{environment}' is valid")
        click.echo(f"  App: {config.app_name} v{config.version}")
        click.echo(f"  Host: {config.host}:{config.port}")
    except FileNotFoundError as e:
        click.echo(f" Error: {e}", err=True)
        raise click.Abort() from e
    except ValueError as e:
        click.echo(f" Validation failed: {e}", err=True)
        raise click.Abort() from e


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
