"""Core filename sanitization logic."""

import re
import unicodedata
from pathlib import Path
from typing import Optional, Set


# Reserved names on Windows
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
}

# Characters that are problematic across platforms
INVALID_CHARS = r"[<>:\"/\\|?*'\x00-\x1f]"

# Maximum filename length (conservative for all platforms)
MAX_FILENAME_LENGTH = 200


def sanitize_filename(
    filename: str,
    replacement: str = "_",
    max_length: Optional[int] = None,
    normalize_unicode: bool = True,
) -> str:
    """
    Sanitize a filename to be safe across platforms.

    Args:
        filename: The original filename to sanitize
        replacement: Character to replace invalid characters with
        max_length: Maximum length for the filename (default: 200)
        normalize_unicode: Whether to normalize Unicode characters

    Returns:
        Sanitized filename safe for use across platforms
    """
    if not filename:
        return "untitled"

    # Normalize Unicode if requested
    if normalize_unicode:
        filename = unicodedata.normalize("NFKC", filename)

    # Remove or replace invalid characters
    sanitized = re.sub(INVALID_CHARS, replacement, filename)

    # Check if it's only an extension before stripping
    is_extension_only = (
        filename.strip(" ").startswith(".") and filename.strip(" ").count(".") == 1
    )

    # Handle leading/trailing spaces and dots
    sanitized = sanitized.strip(" .")

    # If we only have an extension left after stripping, handle it
    if is_extension_only and sanitized:
        # This was just an extension like ".txt"
        sanitized = f"untitled.{sanitized}"

    # Handle reserved names
    name_part = Path(sanitized).stem.upper()
    if name_part in WINDOWS_RESERVED_NAMES:
        extension = Path(sanitized).suffix
        sanitized = f"{sanitized}{replacement}safe{extension}"

    # Get extension for later use
    path_obj = Path(sanitized)
    extension = path_obj.suffix
    stem = path_obj.stem

    # Handle length constraints
    max_len = max_length or MAX_FILENAME_LENGTH
    if len(sanitized) > max_len:
        # Try to preserve extension
        if extension:
            max_stem_length = max_len - len(extension)
            sanitized = stem[:max_stem_length] + extension
        else:
            sanitized = sanitized[:max_len]

    # Ensure we don't end up with an empty filename or just underscores
    if (
        not sanitized
        or sanitized == extension
        or set(sanitized.replace(".", "")) <= {"_"}
    ):
        sanitized = f"untitled{extension}" if extension else "untitled"

    return sanitized


def is_valid_filename(filename: str, check_length: bool = True) -> bool:
    """
    Check if a filename is valid across platforms.

    Args:
        filename: The filename to validate
        check_length: Whether to check length constraints

    Returns:
        True if the filename is valid, False otherwise
    """
    if not filename:
        return False

    # Check for invalid characters
    if re.search(INVALID_CHARS, filename):
        return False

    # Check for leading/trailing spaces or dots
    if filename != filename.strip(" ."):
        return False

    # Check for reserved names
    name_part = Path(filename).stem.upper()
    if name_part in WINDOWS_RESERVED_NAMES:
        return False

    # Check length if requested
    if check_length and len(filename) > MAX_FILENAME_LENGTH:
        return False

    return True


def get_safe_filename_variants(base_filename: str, existing_files: Set[str]) -> str:
    """
    Generate a safe filename variant that doesn't conflict with existing files.

    Args:
        base_filename: The base filename to make unique
        existing_files: Set of existing filenames to avoid conflicts with

    Returns:
        A unique, safe filename
    """
    sanitized = sanitize_filename(base_filename)

    if sanitized not in existing_files:
        return sanitized

    # Generate variants with numbers
    path_obj = Path(sanitized)
    stem = path_obj.stem
    extension = path_obj.suffix

    counter = 1
    while True:
        variant = f"{stem}_{counter}{extension}"
        if variant not in existing_files:
            return variant
        counter += 1
