"""Data models for Vertex AI data store operations."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class DataStoreResult:
    """Result of data store creation operation."""

    data_store_id: str
    display_name: str
    serving_config_path: str
    import_operation_id: str | None = None
    status: str = "PENDING"
    created_time: datetime | None = None
    error_message: str | None = None


@dataclass
class ImportProgress:
    """Progress information for document import operation."""

    operation_id: str
    status: str  # PENDING, RUNNING, SUCCEEDED, FAILED
    progress_percent: float
    documents_processed: int
    documents_total: int
    estimated_completion_time: datetime | None = None
