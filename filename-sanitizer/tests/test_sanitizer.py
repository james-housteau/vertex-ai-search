"""Tests for the sanitizer module."""

from filename_sanitizer.sanitizer import (
    sanitize_filename,
    is_valid_filename,
    get_safe_filename_variants,
    WINDOWS_RESERVED_NAMES,
    MAX_FILENAME_LENGTH,
)


class TestSanitizeFilename:
    """Test the sanitize_filename function."""

    def test_empty_filename(self):
        """Test handling of empty filename."""
        assert sanitize_filename("") == "untitled"
        assert sanitize_filename("   ") == "untitled"

    def test_valid_filename(self):
        """Test that valid filenames pass through unchanged."""
        valid_names = [
            "document.txt",
            "my_file.pdf",
            "image123.jpg",
            "simple",
        ]
        for name in valid_names:
            assert sanitize_filename(name) == name

    def test_invalid_characters(self):
        """Test removal of invalid characters."""
        test_cases = [
            ("file<name>.txt", "file_name_.txt"),
            ("document:with|problems?.pdf", "document_with_problems_.pdf"),
            ("test\\file/path.txt", "test_file_path.txt"),
            ("file*with\"quotes'.txt", "file_with_quotes_.txt"),
        ]
        for original, expected in test_cases:
            assert sanitize_filename(original) == expected

    def test_custom_replacement(self):
        """Test custom replacement character."""
        assert sanitize_filename("file<name>.txt", replacement="-") == "file-name-.txt"

    def test_reserved_names(self):
        """Test handling of Windows reserved names."""
        for reserved in ["CON", "PRN", "AUX", "NUL"]:
            result = sanitize_filename(f"{reserved}.txt")
            assert result != f"{reserved}.txt"
            assert "_safe" in result

    def test_length_constraints(self):
        """Test filename length constraints."""
        long_name = "a" * 300 + ".txt"
        result = sanitize_filename(long_name)
        assert len(result) <= MAX_FILENAME_LENGTH
        assert result.endswith(".txt")

    def test_custom_max_length(self):
        """Test custom maximum length."""
        long_name = "a" * 100 + ".txt"
        result = sanitize_filename(long_name, max_length=50)
        assert len(result) <= 50
        assert result.endswith(".txt")

    def test_unicode_normalization(self):
        """Test Unicode normalization."""
        # Test with composed and decomposed Unicode
        filename = "cafe.txt"  # simple test
        result = sanitize_filename(filename, normalize_unicode=True)
        assert result == "cafe.txt"

    def test_leading_trailing_spaces_dots(self):
        """Test removal of leading/trailing spaces and dots."""
        test_cases = [
            ("  filename.txt  ", "filename.txt"),
            ("..filename.txt..", "filename.txt"),
            (" .filename.txt. ", "filename.txt"),
        ]
        for original, expected in test_cases:
            assert sanitize_filename(original) == expected

    def test_extension_preservation(self):
        """Test that file extensions are preserved when possible."""
        long_stem = "a" * 300
        result = sanitize_filename(f"{long_stem}.txt", max_length=50)
        assert result.endswith(".txt")
        assert len(result) <= 50


class TestIsValidFilename:
    """Test the is_valid_filename function."""

    def test_valid_filenames(self):
        """Test valid filenames."""
        valid_names = [
            "document.txt",
            "my_file.pdf",
            "image123.jpg",
            "simple",
        ]
        for name in valid_names:
            assert is_valid_filename(name) is True

    def test_invalid_filenames(self):
        """Test invalid filenames."""
        invalid_names = [
            "",
            "file<name>.txt",
            "document:with|problems?.pdf",
            "CON.txt",
            " filename.txt",
            "filename.txt ",
            ".filename.txt",
        ]
        for name in invalid_names:
            assert is_valid_filename(name) is False

    def test_length_checking(self):
        """Test length constraint checking."""
        long_name = "a" * (MAX_FILENAME_LENGTH + 1)
        assert is_valid_filename(long_name, check_length=True) is False
        assert is_valid_filename(long_name, check_length=False) is True

    def test_reserved_names(self):
        """Test Windows reserved names."""
        for reserved in WINDOWS_RESERVED_NAMES:
            assert is_valid_filename(f"{reserved}.txt") is False
            assert is_valid_filename(f"{reserved.lower()}.txt") is False


class TestGetSafeFilenameVariants:
    """Test the get_safe_filename_variants function."""

    def test_no_conflict(self):
        """Test when no conflicts exist."""
        result = get_safe_filename_variants("test.txt", set())
        assert result == "test.txt"

    def test_with_conflicts(self):
        """Test when conflicts exist."""
        existing = {"test.txt", "test_1.txt"}
        result = get_safe_filename_variants("test.txt", existing)
        assert result == "test_2.txt"

    def test_multiple_conflicts(self):
        """Test with multiple conflicts."""
        existing = {"test.txt", "test_1.txt", "test_2.txt", "test_3.txt"}
        result = get_safe_filename_variants("test.txt", existing)
        assert result == "test_4.txt"

    def test_sanitization_and_conflicts(self):
        """Test sanitization with conflict resolution."""
        existing = {"file_name_.txt"}
        result = get_safe_filename_variants("file<name>.txt", existing)
        assert result == "file_name__1.txt"


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_only_extension(self):
        """Test filename with only extension."""
        result = sanitize_filename(".txt")
        assert result == "untitled.txt"

    def test_no_extension_long_name(self):
        """Test long filename without extension."""
        long_name = "a" * 300
        result = sanitize_filename(long_name, max_length=50)
        assert len(result) == 50
        assert "." not in result

    def test_all_invalid_chars(self):
        """Test filename with all invalid characters."""
        result = sanitize_filename('<>:"/\\|?*')
        assert result == "untitled"

    def test_unicode_only_invalid(self):
        """Test Unicode filename with invalid characters."""
        result = sanitize_filename("cafe<>test.txt")
        assert "cafe" in result
        assert "<>" not in result

    def test_reserved_name_with_path(self):
        """Test reserved name handling with complex paths."""
        result = sanitize_filename("CON")
        assert result != "CON"
        assert "_safe" in result
