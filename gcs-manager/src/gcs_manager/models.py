"""Data models for GCS Manager."""

from dataclasses import dataclass


@dataclass
class BucketResult:
    """Result of bucket operation containing metadata and status."""

    bucket_name: str
    bucket_uri: str
    region: str
    created: bool
    error_message: str | None = None


@dataclass
class BucketConfig:
    """Configuration for bucket creation and management."""

    name: str
    region: str = "us"
    lifecycle_days: int = 30
    uniform_access: bool = True
