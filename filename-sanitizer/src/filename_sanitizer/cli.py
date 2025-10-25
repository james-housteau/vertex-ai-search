"""CLI interface for filename sanitizer."""

import glob
import re
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from . import __version__
from .sanitizer import get_safe_filename_variants, is_valid_filename, sanitize_filename

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="filename-sanitizer")
def cli() -> None:
    """Cross-platform filename sanitization tool."""
    pass


@cli.command()
@click.argument("filename")
@click.option(
    "--replacement",
    "-r",
    default="_",
    help="Character to replace invalid characters with",
)
@click.option("--max-length", "-l", type=int, help="Maximum filename length")
@click.option("--no-unicode-normalize", is_flag=True, help="Skip Unicode normalization")
def sanitize(
    filename: str, replacement: str, max_length: int, no_unicode_normalize: bool
) -> None:
    """Sanitize a single filename."""
    sanitized = sanitize_filename(
        filename,
        replacement=replacement,
        max_length=max_length,
        normalize_unicode=not no_unicode_normalize,
    )

    console.print(f"[blue]Original:[/blue] {filename}")
    console.print(f"[green]Sanitized:[/green] {sanitized}")

    if filename != sanitized:
        console.print(
            "[yellow]Changes were made to ensure cross-platform compatibility.[/yellow]"
        )
    else:
        console.print("[green] Filename is already safe for all platforms.[/green]")


@cli.command()
@click.argument("pattern")
@click.option(
    "--replacement",
    "-r",
    default="_",
    help="Character to replace invalid characters with",
)
@click.option("--max-length", "-l", type=int, help="Maximum filename length")
@click.option("--no-unicode-normalize", is_flag=True, help="Skip Unicode normalization")
@click.option(
    "--dry-run",
    "-n",
    is_flag=True,
    help="Show what would be done without making changes",
)
def batch_sanitize(
    pattern: str,
    replacement: str,
    max_length: int,
    no_unicode_normalize: bool,
    dry_run: bool,
) -> None:
    """Batch sanitize files matching a pattern."""
    files = glob.glob(pattern)

    if not files:
        console.print(f"[red]No files found matching pattern: {pattern}[/red]")
        return

    table = Table(title="Batch Sanitization Results")
    table.add_column("Original", style="blue")
    table.add_column("Sanitized", style="green")
    table.add_column("Status", style="yellow")

    changes_made = 0
    existing_files = set(Path(f).name for f in files)

    for file_path in files:
        original_name = Path(file_path).name
        sanitized_name = get_safe_filename_variants(
            sanitize_filename(
                original_name,
                replacement=replacement,
                max_length=max_length,
                normalize_unicode=not no_unicode_normalize,
            ),
            existing_files,
        )

        if original_name != sanitized_name:
            status = "Needs change" if dry_run else "Changed"
            changes_made += 1

            if not dry_run:
                # Perform the rename
                old_path = Path(file_path)
                new_path = old_path.parent / sanitized_name
                try:
                    old_path.rename(new_path)
                    status = " Renamed"
                except OSError as e:
                    status = f" Error: {e}"
        else:
            status = "No change needed"

        table.add_row(original_name, sanitized_name, status)

    console.print(table)

    if dry_run and changes_made > 0:
        console.print(
            f"\n[yellow]Dry run: {changes_made} files would be renamed.[/yellow]"
        )
        console.print("[dim]Run without --dry-run to apply changes.[/dim]")
    elif changes_made > 0:
        console.print(f"\n[green]Successfully processed {changes_made} files.[/green]")
    else:
        console.print("\n[green]All files already have safe names.[/green]")


@cli.command()
@click.argument("filename")
@click.option(
    "--no-check-length", is_flag=True, help="Skip filename length constraints check"
)
def validate(filename: str, no_check_length: bool) -> None:
    """Check if a filename is valid across platforms."""
    is_valid = is_valid_filename(filename, check_length=not no_check_length)

    console.print(f"[blue]Filename:[/blue] {filename}")

    if is_valid:
        console.print("[green] Valid filename for all platforms[/green]")
    else:
        console.print("[red] Invalid filename[/red]")

        # Provide specific feedback
        issues: list[str] = []

        if not filename:
            issues.append("Empty filename")
        else:
            from .sanitizer import (
                INVALID_CHARS,
                MAX_FILENAME_LENGTH,
                WINDOWS_RESERVED_NAMES,
            )

            if re.search(INVALID_CHARS, filename):
                issues.append("Contains invalid characters")

            if filename != filename.strip(" ."):
                issues.append("Has leading/trailing spaces or dots")

            name_part = Path(filename).stem.upper()
            if name_part in WINDOWS_RESERVED_NAMES:
                issues.append(f"'{name_part}' is a reserved name on Windows")

            if not no_check_length and len(filename) > MAX_FILENAME_LENGTH:
                issues.append(f"Too long (>{MAX_FILENAME_LENGTH} characters)")

        if issues:
            console.print("[yellow]Issues found:[/yellow]")
            for issue in issues:
                console.print(f"  • {issue}")

        # Show sanitized version
        sanitized = sanitize_filename(filename)
        console.print(f"[cyan]Suggested:[/cyan] {sanitized}")


@cli.command()
def status() -> None:
    """Show application status and version information."""
    console.print("=� [bold]Filename Sanitizer[/bold]")
    console.print(f"Version: {__version__}")
    console.print("Status: [green]Ready[/green]")

    # Show configuration
    from .sanitizer import MAX_FILENAME_LENGTH, WINDOWS_RESERVED_NAMES

    table = Table(title="Configuration")
    table.add_column("Setting", style="blue")
    table.add_column("Value", style="green")

    table.add_row("Max filename length", str(MAX_FILENAME_LENGTH))
    table.add_row(
        "Reserved names", f"{len(WINDOWS_RESERVED_NAMES)} Windows reserved names"
    )
    table.add_row("Unicode normalization", "NFKC")

    console.print(table)
