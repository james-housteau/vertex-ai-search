"""GCS Manager - Google Cloud Storage bucket management for Vertex AI search."""

from .gcs_manager import GCSManager
from .models import BucketResult, BucketConfig

__version__ = "0.1.0"
__all__ = ["GCSManager", "BucketResult", "BucketConfig"]
