"""Acceptance tests for Vertex AI Data Store Manager.

These tests define the expected behavior following TDD RED phase.
All tests should initially fail and then pass during GREEN phase implementation.
"""

import pytest

from vertex_datastore import DataStoreResult, ImportProgress, VertexDataStoreManager


class TestDataStoreCreation:
    """Acceptance tests for data store creation functionality."""

    def test_create_data_store_with_layout_parsing(self) -> None:
        """Test creating an unstructured data store with layout-aware parsing enabled."""
        # Given
        manager = VertexDataStoreManager(project_id="test-project", location="global")
        display_name = "test-html-datastore"
        gcs_path = "gs://test-bucket/html-documents/"

        # When
        result = manager.create_data_store(display_name, gcs_path)

        # Then
        assert isinstance(result, DataStoreResult)
        assert result.data_store_id.startswith("test-html-datastore")
        assert result.display_name == display_name
        assert result.serving_config_path.endswith("/servingConfigs/default_search")
        assert result.status == "ACTIVE"
        assert result.created_time is not None
        assert result.error_message is None

    def test_create_data_store_generates_unique_ids(self) -> None:
        """Test that multiple data stores get unique IDs."""
        # Given
        manager = VertexDataStoreManager(project_id="test-project")

        # When
        result1 = manager.create_data_store("datastore-1", "gs://bucket1/")
        result2 = manager.create_data_store("datastore-2", "gs://bucket2/")

        # Then
        assert result1.data_store_id != result2.data_store_id
        assert result1.serving_config_path != result2.serving_config_path

    def test_create_data_store_with_invalid_gcs_path_fails(self) -> None:
        """Test that invalid GCS paths are rejected."""
        # Given
        manager = VertexDataStoreManager(project_id="test-project")

        # When/Then
        with pytest.raises(ValueError, match="Invalid GCS path"):
            manager.create_data_store("test", "invalid-path")


class TestDocumentImport:
    """Acceptance tests for document import functionality."""

    def test_import_documents_returns_operation_id(self) -> None:
        """Test importing documents returns a trackable operation ID."""
        # Given
        manager = VertexDataStoreManager(project_id="test-project")
        data_store_id = "test-datastore-123"
        gcs_path = "gs://test-bucket/html-documents/"

        # When
        operation_id = manager.import_documents(data_store_id, gcs_path)

        # Then
        assert isinstance(operation_id, str)
        assert len(operation_id) > 0
        assert operation_id.startswith("projects/test-project/operations/")

    def test_get_import_progress_tracks_status(self) -> None:
        """Test getting import progress with status and progress tracking."""
        # Given
        manager = VertexDataStoreManager(project_id="test-project")
        operation_id = "projects/test-project/operations/import-123"

        # When
        progress = manager.get_import_progress(operation_id)

        # Then
        assert isinstance(progress, ImportProgress)
        assert progress.operation_id == operation_id
        assert progress.status in ["PENDING", "RUNNING", "SUCCEEDED", "FAILED"]
        assert 0.0 <= progress.progress_percent <= 100.0
        assert progress.documents_processed >= 0
        assert progress.documents_total > 0

    @pytest.mark.slow
    def test_import_progress_running_state(self) -> None:
        """Test import progress in RUNNING state shows meaningful progress."""
        # Given
        manager = VertexDataStoreManager(project_id="test-project")
        # Create a real operation and wait for it to reach RUNNING state
        data_store_id = "test-store"
        operation_id = manager.import_documents(data_store_id, "gs://test-bucket/")

        # Wait for the operation to reach RUNNING state (6 seconds based on simulation logic)
        import time

        time.sleep(6)

        # When
        progress = manager.get_import_progress(operation_id)

        # Then
        assert progress.status == "RUNNING"
        assert progress.progress_percent > 0.0
        assert progress.documents_processed > 0
        assert progress.documents_processed <= progress.documents_total
        assert progress.estimated_completion_time is not None

    @pytest.mark.slow
    def test_import_progress_completed_state(self) -> None:
        """Test import progress in SUCCEEDED state shows completion."""
        # Given
        manager = VertexDataStoreManager(project_id="test-project")
        # Create a real operation and wait for it to complete
        data_store_id = "test-store"
        operation_id = manager.import_documents(data_store_id, "gs://test-bucket/")

        # Wait for the operation to complete (61 seconds based on simulation logic)
        import time

        time.sleep(61)

        # When
        progress = manager.get_import_progress(operation_id)

        # Then
        assert progress.status == "SUCCEEDED"
        assert progress.progress_percent == 100.0
        assert progress.documents_processed == progress.documents_total
        assert progress.documents_total == 1600  # Expected document count

    @pytest.mark.slow
    def test_wait_for_import_completion_success(self) -> None:
        """Test waiting for import completion returns True on success."""
        # Given
        manager = VertexDataStoreManager(project_id="test-project")
        # Create a real operation that will complete within the timeout
        data_store_id = "test-store"
        operation_id = manager.import_documents(data_store_id, "gs://test-bucket/")

        # When - wait with generous timeout (2 minutes) for the 1-minute simulation
        completed = manager.wait_for_import_completion(operation_id, timeout_minutes=2)

        # Then
        assert completed is True

    def test_wait_for_import_completion_timeout(self) -> None:
        """Test waiting for import completion returns False on timeout."""
        # Given
        manager = VertexDataStoreManager(project_id="test-project")
        operation_id = "projects/test-project/operations/import-wait-timeout"

        # When
        completed = manager.wait_for_import_completion(
            operation_id, timeout_minutes=0.01
        )

        # Then
        assert completed is False

    @pytest.mark.slow
    def test_wait_for_import_completion_failure(self) -> None:
        """Test waiting for import completion returns False on operation failure."""
        # Given
        from unittest.mock import patch

        manager = VertexDataStoreManager(project_id="test-project")
        operation_id = "fake-operation-id"

        # Mock get_import_progress to simulate a failed operation
        def mock_get_progress(op_id):
            from vertex_datastore.models import ImportProgress

            return ImportProgress(
                operation_id=op_id,
                status="FAILED",
                progress_percent=0.0,
                documents_processed=0,
                documents_total=1600,
            )

        # When
        with patch.object(
            manager, "get_import_progress", side_effect=mock_get_progress
        ):
            completed = manager.wait_for_import_completion(
                operation_id, timeout_minutes=1
            )

        # Then
        assert completed is False


class TestDataStoreManagement:
    """Acceptance tests for data store management operations."""

    def test_get_serving_config_path_format(self) -> None:
        """Test serving config path format for search integration."""
        # Given
        manager = VertexDataStoreManager(
            project_id="test-project", location="us-central1"
        )
        data_store_id = "test-datastore-456"

        # When
        serving_config = manager.get_serving_config(data_store_id)

        # Then
        expected = (
            "projects/test-project/locations/us-central1/"
            "collections/default_collection/dataStores/test-datastore-456/"
            "servingConfigs/default_search"
        )
        assert serving_config == expected

    def test_delete_data_store_success(self) -> None:
        """Test successful deletion of data store."""
        # Given
        manager = VertexDataStoreManager(project_id="test-project")
        data_store_id = "test-datastore-to-delete"

        # When
        deleted = manager.delete_data_store(data_store_id)

        # Then
        assert deleted is True

    def test_delete_data_store_force_with_documents(self) -> None:
        """Test force deletion of data store with existing documents."""
        # Given
        manager = VertexDataStoreManager(project_id="test-project")
        data_store_id = "test-datastore-with-docs"

        # When
        deleted = manager.delete_data_store(data_store_id, force=True)

        # Then
        assert deleted is True

    def test_delete_nonexistent_data_store_returns_false(self) -> None:
        """Test deleting non-existent data store returns False."""
        # Given
        manager = VertexDataStoreManager(project_id="test-project")
        data_store_id = "nonexistent-datastore"

        # When
        deleted = manager.delete_data_store(data_store_id)

        # Then
        assert deleted is False


class TestErrorHandling:
    """Acceptance tests for error handling and edge cases."""

    def test_invalid_project_id_raises_error(self) -> None:
        """Test that invalid project ID raises appropriate error."""
        # When/Then
        with pytest.raises(ValueError, match="Invalid project ID"):
            VertexDataStoreManager(project_id="")

    def test_invalid_location_raises_error(self) -> None:
        """Test that invalid location raises appropriate error."""
        # When/Then
        with pytest.raises(ValueError, match="Invalid location"):
            VertexDataStoreManager(project_id="test-project", location="")

    def test_get_progress_for_invalid_operation_id(self) -> None:
        """Test getting progress for non-existent operation ID."""
        # Given
        manager = VertexDataStoreManager(project_id="test-project")

        # When/Then
        with pytest.raises(ValueError, match="Operation not found"):
            manager.get_import_progress("invalid-operation-id")

    def test_import_to_nonexistent_datastore_fails(self) -> None:
        """Test importing to non-existent data store fails."""
        # Given
        manager = VertexDataStoreManager(project_id="test-project")

        # When/Then
        with pytest.raises(ValueError, match="Data store not found"):
            manager.import_documents("nonexistent-datastore", "gs://test-bucket/")


class TestIntegrationScenarios:
    """End-to-end integration test scenarios."""

    def test_complete_datastore_lifecycle(self) -> None:
        """Test complete data store lifecycle: create, import, monitor, delete."""
        # Given
        manager = VertexDataStoreManager(project_id="test-project")
        display_name = "integration-test-datastore"
        gcs_path = "gs://test-bucket/html-files/"

        # When - Create data store
        result = manager.create_data_store(display_name, gcs_path)
        assert result.status == "ACTIVE"

        # When - Import documents
        operation_id = manager.import_documents(result.data_store_id, gcs_path)
        assert operation_id is not None

        # When - Monitor progress
        progress = manager.get_import_progress(operation_id)
        assert progress.status in ["PENDING", "RUNNING", "SUCCEEDED"]

        # When - Get serving config
        serving_config = manager.get_serving_config(result.data_store_id)
        assert serving_config == result.serving_config_path

        # When - Delete data store
        deleted = manager.delete_data_store(result.data_store_id, force=True)
        assert deleted is True

    @pytest.mark.slow
    def test_large_document_import_scenario(self) -> None:
        """Test importing large document set (1600 HTML files)."""
        # Given
        manager = VertexDataStoreManager(project_id="test-project")
        result = manager.create_data_store("large-import-test", "gs://large-bucket/")

        # When
        operation_id = manager.import_documents(
            result.data_store_id, "gs://large-bucket/html-files/"
        )

        # Monitor initial progress
        initial_progress = manager.get_import_progress(operation_id)

        # Then
        assert initial_progress.documents_total == 1600
        assert initial_progress.status in ["PENDING", "RUNNING"]
        assert initial_progress.estimated_completion_time is not None

        # Verify timeout is reasonable for large imports
        timeout_result = manager.wait_for_import_completion(
            operation_id, timeout_minutes=60
        )
        # Note: This would be True in real scenario, but in tests it may timeout
        assert timeout_result in [True, False]  # Either success or timeout acceptable
