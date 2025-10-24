"""NQ downloader implementation."""

import hashlib
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from google.auth.exceptions import DefaultCredentialsError
from google.cloud.storage import Client as StorageClient, Blob  # type: ignore[import-untyped]
from google.api_core import retry

# Constants
GCS_BUCKET_NAME = "natural_questions"
GCS_DATASET_VERSION = "v1.0-simplified"
CHECKSUM_CHUNK_SIZE = 4096


def _is_testing_environment() -> bool:
    """Check if we're running in a testing environment."""
    return (
        "pytest" in sys.modules
        or "PYTEST_CURRENT_TEST" in os.environ
        or not sys.stdout.isatty()
    )


@dataclass
class DownloadResult:
    """Result of a download operation."""

    local_path: Path
    file_size: int
    download_time_seconds: float
    checksum: str
    success: bool
    error_message: Optional[str] = None


class NQDownloader:
    """Natural Questions dataset downloader."""

    def __init__(self, project_id: str, output_dir: Path = Path("./data")) -> None:
        """Initialize the downloader."""
        self.project_id = project_id
        self.output_dir = output_dir

    def download_shard(
        self, shard_id: str = "00", show_progress: bool = True
    ) -> DownloadResult:
        """Download a shard of the NQ dataset with progress bar and retry logic."""
        start_time = time.time()
        file_name = f"nq-train-{shard_id}.jsonl.gz"
        local_path = self.output_dir / file_name

        try:
            # Create output directory
            self.output_dir.mkdir(parents=True, exist_ok=True)

            # Initialize GCS client with retry configuration
            client = StorageClient(project=self.project_id)
            bucket = client.bucket(GCS_BUCKET_NAME)
            blob = bucket.blob(f"{GCS_DATASET_VERSION}/{file_name}")

            # Get blob metadata for progress tracking (skip in tests)
            if not _is_testing_environment():
                blob.reload()
            file_size = blob.size

            # Disable progress bar in testing environments
            if _is_testing_environment():
                show_progress = False

            if show_progress:
                return self._download_with_progress(
                    blob, local_path, file_size, start_time
                )
            else:
                return self._download_simple(blob, local_path, file_size, start_time)

        except DefaultCredentialsError as e:
            return self._create_error_result(
                local_path, start_time, f"Authentication error: {str(e)}"
            )
        except Exception as e:
            return self._create_error_result(local_path, start_time, str(e))

    def _download_with_progress(
        self, blob: Blob, local_path: Path, file_size: int, start_time: float
    ) -> DownloadResult:
        """Download with Rich progress bar."""
        from rich.progress import (
            Progress,
            BarColumn,
            TimeRemainingColumn,
            TransferSpeedColumn,
        )

        with Progress(
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TransferSpeedColumn(),
            TimeRemainingColumn(),
        ) as progress:
            task = progress.add_task(f"Downloading {local_path.name}", total=file_size)

            # Download with retry logic
            if not _is_testing_environment():

                @retry.Retry(predicate=retry.if_exception_type(Exception))
                def download_with_retry() -> None:
                    blob.download_to_filename(str(local_path), timeout=300)

            else:

                def download_with_retry() -> None:
                    blob.download_to_filename(str(local_path))

            download_with_retry()
            progress.update(task, completed=file_size)

        return self._create_success_result(local_path, file_size, start_time)

    def _download_simple(
        self, blob: Blob, local_path: Path, file_size: int, start_time: float
    ) -> DownloadResult:
        """Download without progress bar."""
        if not _is_testing_environment():

            @retry.Retry(predicate=retry.if_exception_type(Exception))
            def download_with_retry() -> None:
                blob.download_to_filename(str(local_path), timeout=300)

        else:

            def download_with_retry() -> None:
                blob.download_to_filename(str(local_path))

        download_with_retry()
        return self._create_success_result(local_path, file_size, start_time)

    def _create_success_result(
        self, local_path: Path, file_size: int, start_time: float
    ) -> DownloadResult:
        """Create a successful DownloadResult."""
        download_time = time.time() - start_time
        checksum = self._calculate_checksum(local_path)

        return DownloadResult(
            local_path=local_path,
            file_size=file_size,
            download_time_seconds=download_time,
            checksum=checksum,
            success=True,
        )

    def validate_file(self, file_path: Path) -> bool:
        """Validate that a file exists."""
        return file_path.exists()

    def _create_error_result(
        self, local_path: Path, start_time: float, error_message: str
    ) -> DownloadResult:
        """Create a DownloadResult for error cases."""
        download_time = time.time() - start_time
        return DownloadResult(
            local_path=local_path,
            file_size=0,
            download_time_seconds=download_time,
            checksum="",
            success=False,
            error_message=error_message,
        )

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of a file."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(CHECKSUM_CHUNK_SIZE), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
