"""
Basic import test to verify module structure.
"""

import pytest
from dataclasses import fields


def test_nq_downloader_module_can_be_imported():
    """Test that the nq_downloader module can be imported."""
    try:
        from nq_downloader import downloader

        assert hasattr(downloader, "NQDownloader")
        assert hasattr(downloader, "DownloadResult")
    except ImportError:
        pytest.fail("nq_downloader module not found - implementation needed")


def test_nq_downloader_classes_exist():
    """Test that required classes exist in the module."""
    try:
        from nq_downloader.downloader import NQDownloader, DownloadResult

        # Verify class can be instantiated
        downloader = NQDownloader(project_id="test")
        assert downloader is not None

        # Verify DownloadResult has expected fields (using dataclass fields)
        expected_fields = {
            "local_path",
            "file_size",
            "download_time_seconds",
            "checksum",
            "success",
            "error_message",
        }
        actual_fields = {field.name for field in fields(DownloadResult)}
        assert expected_fields.issubset(actual_fields)

    except ImportError:
        pytest.fail("Required classes not found - implementation needed")
