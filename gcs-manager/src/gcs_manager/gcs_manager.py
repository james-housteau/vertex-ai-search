"""Google Cloud Storage Manager implementation."""

import uuid
from typing import Optional
from google.cloud import storage  # type: ignore[attr-defined]
from google.cloud.exceptions import GoogleCloudError, Forbidden

from .models import BucketResult, BucketConfig


class GCSManager:
    """Manages GCS buckets for Vertex AI document hosting."""

    def __init__(self, project_id: str, config: Optional[BucketConfig] = None):
        """Initialize GCS manager with project and configuration."""
        self.project_id = project_id
        self.config = config or BucketConfig(name="default")
        self.client = storage.Client(project=project_id)

    def create_bucket(self, bucket_name: str, region: str = "us") -> BucketResult:
        """Create GCS bucket with proper permissions and lifecycle."""
        try:
            # Handle name conflicts with auto-generation
            final_bucket_name = self._ensure_unique_bucket_name(bucket_name)

            # Create bucket
            bucket = self.client.bucket(final_bucket_name)
            bucket = self.client.create_bucket(bucket, location=region.upper())

            # Configure lifecycle policy
            self._configure_lifecycle_policy(bucket)

            # Configure uniform access
            self._configure_uniform_access(bucket)

            return BucketResult(
                bucket_name=bucket.name,
                bucket_uri=f"gs://{bucket.name}",
                region=bucket.location,
                created=True,
            )

        except Forbidden as e:
            return BucketResult(
                bucket_name=bucket_name,
                bucket_uri="",
                region=region,
                created=False,
                error_message=f"Access denied: {str(e)}",
            )
        except GoogleCloudError as e:
            return BucketResult(
                bucket_name=bucket_name,
                bucket_uri="",
                region=region,
                created=False,
                error_message=f"GCS error: {str(e)}",
            )

    def bucket_exists(self, bucket_name: str) -> bool:
        """Check if bucket exists and is accessible."""
        try:
            bucket = self.client.bucket(bucket_name)
            return bool(bucket.exists())
        except (GoogleCloudError, Exception):
            # Catch any exception and return False for safety
            return False

    def delete_bucket(self, bucket_name: str, force: bool = False) -> bool:
        """Delete bucket and optionally all contents."""
        try:
            bucket = self.client.bucket(bucket_name)

            if not bucket.exists():
                return False

            if force:
                # Delete all objects first
                blobs = bucket.list_blobs()
                for blob in blobs:
                    blob.delete()

            bucket.delete()
            return True

        except (GoogleCloudError, Exception):
            return False

    def get_bucket_info(self, bucket_name: str) -> Optional[BucketResult]:
        """Get detailed information about existing bucket."""
        try:
            bucket = self.client.bucket(bucket_name)

            if not bucket.exists():
                return None

            # Reload to get current metadata
            bucket.reload()

            return BucketResult(
                bucket_name=bucket.name,
                bucket_uri=f"gs://{bucket.name}",
                region=bucket.location,
                created=False,  # Existing bucket, not newly created
            )

        except (GoogleCloudError, Exception):
            return None

    def _ensure_unique_bucket_name(self, base_name: str) -> str:
        """Ensure bucket name is unique by appending UUID if needed."""
        if not self.bucket_exists(base_name):
            return base_name

        # Generate unique name with UUID suffix
        unique_suffix = str(uuid.uuid4())[:8]
        return f"{base_name}-{unique_suffix}"

    def _configure_lifecycle_policy(self, bucket: storage.Bucket) -> None:
        """Configure lifecycle policy for automatic deletion."""
        lifecycle_days = self.config.lifecycle_days

        # Add lifecycle rule for automatic deletion
        rule = {"action": {"type": "Delete"}, "condition": {"age": lifecycle_days}}

        bucket.lifecycle_rules = [rule]
        bucket.patch()

    def _configure_uniform_access(self, bucket: storage.Bucket) -> None:
        """Configure uniform bucket-level access."""
        if self.config.uniform_access:
            bucket.iam_configuration.uniform_bucket_level_access_enabled = True
            bucket.patch()
