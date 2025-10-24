"""Unit tests for data models."""

from datetime import UTC, datetime

from vertex_datastore.models import DataStoreResult, ImportProgress


class TestDataStoreResult:
    """Tests for DataStoreResult dataclass."""

    def test_datastore_result_creation(self) -> None:
        """Test creating DataStoreResult with required fields."""
        # Given
        data_store_id = "test-datastore-123"
        display_name = "Test Data Store"
        serving_config_path = "projects/test/locations/global/collections/default_collection/dataStores/test-datastore-123/servingConfigs/default_search"

        # When
        result = DataStoreResult(
            data_store_id=data_store_id,
            display_name=display_name,
            serving_config_path=serving_config_path,
        )

        # Then
        assert result.data_store_id == data_store_id
        assert result.display_name == display_name
        assert result.serving_config_path == serving_config_path
        assert result.import_operation_id is None
        assert result.status == "PENDING"
        assert result.created_time is None
        assert result.error_message is None

    def test_datastore_result_with_all_fields(self) -> None:
        """Test creating DataStoreResult with all fields."""
        # Given
        now = datetime.now(UTC)

        # When
        result = DataStoreResult(
            data_store_id="test-123",
            display_name="Test Store",
            serving_config_path="projects/test/locations/global/collections/default_collection/dataStores/test-123/servingConfigs/default_search",
            import_operation_id="projects/test/operations/import-456",
            status="ACTIVE",
            created_time=now,
            error_message=None,
        )

        # Then
        assert result.data_store_id == "test-123"
        assert result.display_name == "Test Store"
        assert result.import_operation_id == "projects/test/operations/import-456"
        assert result.status == "ACTIVE"
        assert result.created_time == now
        assert result.error_message is None

    def test_datastore_result_with_error(self) -> None:
        """Test creating DataStoreResult with error message."""
        # When
        result = DataStoreResult(
            data_store_id="failed-123",
            display_name="Failed Store",
            serving_config_path="path/to/config",
            status="FAILED",
            error_message="API quota exceeded",
        )

        # Then
        assert result.status == "FAILED"
        assert result.error_message == "API quota exceeded"


class TestImportProgress:
    """Tests for ImportProgress dataclass."""

    def test_import_progress_creation(self) -> None:
        """Test creating ImportProgress with required fields."""
        # When
        progress = ImportProgress(
            operation_id="projects/test/operations/import-123",
            status="RUNNING",
            progress_percent=45.5,
            documents_processed=728,
            documents_total=1600,
        )

        # Then
        assert progress.operation_id == "projects/test/operations/import-123"
        assert progress.status == "RUNNING"
        assert progress.progress_percent == 45.5
        assert progress.documents_processed == 728
        assert progress.documents_total == 1600
        assert progress.estimated_completion_time is None

    def test_import_progress_with_estimated_completion(self) -> None:
        """Test creating ImportProgress with estimated completion time."""
        # Given
        estimated_time = datetime.now(UTC)

        # When
        progress = ImportProgress(
            operation_id="projects/test/operations/import-456",
            status="RUNNING",
            progress_percent=75.0,
            documents_processed=1200,
            documents_total=1600,
            estimated_completion_time=estimated_time,
        )

        # Then
        assert progress.progress_percent == 75.0
        assert progress.documents_processed == 1200
        assert progress.documents_total == 1600
        assert progress.estimated_completion_time == estimated_time

    def test_import_progress_pending_state(self) -> None:
        """Test ImportProgress in PENDING state."""
        # When
        progress = ImportProgress(
            operation_id="projects/test/operations/import-pending",
            status="PENDING",
            progress_percent=0.0,
            documents_processed=0,
            documents_total=1600,
        )

        # Then
        assert progress.status == "PENDING"
        assert progress.progress_percent == 0.0
        assert progress.documents_processed == 0

    def test_import_progress_completed_state(self) -> None:
        """Test ImportProgress in SUCCEEDED state."""
        # When
        progress = ImportProgress(
            operation_id="projects/test/operations/import-success",
            status="SUCCEEDED",
            progress_percent=100.0,
            documents_processed=1600,
            documents_total=1600,
        )

        # Then
        assert progress.status == "SUCCEEDED"
        assert progress.progress_percent == 100.0
        assert progress.documents_processed == 1600
        assert progress.documents_total == 1600

    def test_import_progress_failed_state(self) -> None:
        """Test ImportProgress in FAILED state."""
        # When
        progress = ImportProgress(
            operation_id="projects/test/operations/import-failed",
            status="FAILED",
            progress_percent=30.0,
            documents_processed=480,
            documents_total=1600,
        )

        # Then
        assert progress.status == "FAILED"
        assert progress.progress_percent == 30.0
        assert progress.documents_processed == 480
        assert progress.documents_total == 1600
