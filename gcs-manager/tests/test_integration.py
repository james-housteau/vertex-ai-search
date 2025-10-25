"""Integration tests for GCS Manager."""

from unittest.mock import Mock, patch

from gcs_manager import BucketConfig, GCSManager
from google.cloud.exceptions import Forbidden


class TestGCSManagerIntegration:
    """Integration tests with mocked GCS client."""

    @patch("google.cloud.storage.Client")
    def test_full_bucket_lifecycle(self, mock_client_class):
        """Test complete bucket lifecycle: create, check, get info, delete."""
        # Setup mock
        mock_client = Mock()
        mock_bucket = Mock()

        mock_bucket.name = "integration-test-bucket"
        mock_bucket.location = "US"
        mock_bucket.exists.return_value = False
        mock_bucket.lifecycle_rules = []
        mock_bucket.iam_configuration = Mock()

        mock_client.bucket.return_value = mock_bucket
        mock_client.create_bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client

        # Initialize manager
        config = BucketConfig(
            name="integration-test-bucket",
            region="us",
            lifecycle_days=14,
            uniform_access=True,
        )
        manager = GCSManager(project_id="test-project", config=config)

        # Test 1: Create bucket
        result = manager.create_bucket("integration-test-bucket")
        assert result.created is True
        assert result.bucket_name == "integration-test-bucket"
        assert result.bucket_uri == "gs://integration-test-bucket"

        # Verify lifecycle and access were configured
        assert mock_bucket.lifecycle_rules == [
            {"action": {"type": "Delete"}, "condition": {"age": 14}}
        ]
        assert mock_bucket.iam_configuration.uniform_bucket_level_access_enabled is True
        assert mock_bucket.patch.call_count == 2  # Once for lifecycle, once for access

        # Test 2: Check if bucket exists (now it should)
        mock_bucket.exists.return_value = True
        exists = manager.bucket_exists("integration-test-bucket")
        assert exists is True

        # Test 3: Get bucket info
        mock_bucket.reload = Mock()  # Add reload method
        info = manager.get_bucket_info("integration-test-bucket")
        assert info is not None
        assert info.bucket_name == "integration-test-bucket"
        assert info.created is False  # Existing bucket
        mock_bucket.reload.assert_called_once()

        # Test 4: Delete bucket
        success = manager.delete_bucket("integration-test-bucket")
        assert success is True
        mock_bucket.delete.assert_called_once()

    @patch("google.cloud.storage.Client")
    def test_bucket_name_conflict_resolution(self, mock_client_class):
        """Test automatic bucket name conflict resolution."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # First bucket exists, subsequent ones don't
        def bucket_exists_side_effect():
            bucket_mock = Mock()
            bucket_mock.exists.side_effect = [
                True,
                False,
            ]  # First exists, second doesn't
            return bucket_mock

        mock_client.bucket.side_effect = lambda name: bucket_exists_side_effect()

        # Mock successful creation for the new name
        mock_new_bucket = Mock()
        mock_new_bucket.name = "conflicting-bucket-12345"
        mock_new_bucket.location = "US"
        mock_new_bucket.lifecycle_rules = []
        mock_new_bucket.iam_configuration = Mock()
        mock_client.create_bucket.return_value = mock_new_bucket

        manager = GCSManager(project_id="test-project")

        # This should automatically generate a new name
        with patch("uuid.uuid4") as mock_uuid:
            mock_uuid.return_value.hex = "12345"
            result = manager.create_bucket("conflicting-bucket")

        assert result.created is True
        assert "conflicting-bucket" in result.bucket_name
        # The exact name depends on UUID generation

    @patch("google.cloud.storage.Client")
    def test_bucket_deletion_with_force(self, mock_client_class):
        """Test bucket deletion with force flag to remove contents."""
        mock_client = Mock()
        mock_bucket = Mock()

        # Mock bucket with some blobs
        mock_blob1 = Mock()
        mock_blob2 = Mock()
        mock_bucket.list_blobs.return_value = [mock_blob1, mock_blob2]
        mock_bucket.exists.return_value = True

        mock_client.bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client

        manager = GCSManager(project_id="test-project")
        success = manager.delete_bucket("bucket-with-contents", force=True)

        assert success is True
        # Verify all blobs were deleted
        mock_blob1.delete.assert_called_once()
        mock_blob2.delete.assert_called_once()
        mock_bucket.delete.assert_called_once()

    @patch("google.cloud.storage.Client")
    def test_error_handling_patterns(self, mock_client_class):
        """Test various error handling scenarios."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        manager = GCSManager(project_id="test-project")

        # Test 1: Permission error during creation
        mock_client.create_bucket.side_effect = Forbidden("Access denied")
        result = manager.create_bucket("permission-denied-bucket")

        assert result.created is False
        assert "Access denied" in result.error_message

        # Test 2: General GCS error during creation
        from google.cloud.exceptions import GoogleCloudError

        mock_client.create_bucket.side_effect = GoogleCloudError("Network error")
        result = manager.create_bucket("network-error-bucket")

        assert result.created is False
        assert "Network error" in result.error_message

        # Test 3: Error during bucket_exists check
        mock_client.bucket.side_effect = Exception("Connection failed")
        exists = manager.bucket_exists("error-bucket")
        assert exists is False

        # Test 4: Error during get_bucket_info
        info = manager.get_bucket_info("error-bucket")
        assert info is None

        # Test 5: Error during delete
        success = manager.delete_bucket("error-bucket")
        assert success is False

    @patch("google.cloud.storage.Client")
    def test_lifecycle_policy_variations(self, mock_client_class):
        """Test different lifecycle policy configurations."""
        mock_client = Mock()
        mock_bucket = Mock()
        mock_bucket.name = "lifecycle-test"
        mock_bucket.location = "US"
        mock_bucket.exists.return_value = False
        mock_bucket.lifecycle_rules = []
        mock_bucket.iam_configuration = Mock()

        mock_client.bucket.return_value = mock_bucket
        mock_client.create_bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client

        # Test different lifecycle day settings
        for days in [1, 7, 30, 90, 365]:
            config = BucketConfig(name=f"lifecycle-{days}", lifecycle_days=days)
            manager = GCSManager(project_id="test-project", config=config)

            result = manager.create_bucket(f"lifecycle-{days}")

            assert result.created is True
            expected_rule = {"action": {"type": "Delete"}, "condition": {"age": days}}
            assert mock_bucket.lifecycle_rules == [expected_rule]

    @patch("google.cloud.storage.Client")
    def test_uniform_access_configuration_variations(self, mock_client_class):
        """Test uniform access configuration options."""
        mock_client = Mock()
        mock_bucket = Mock()
        mock_bucket.name = "access-test"
        mock_bucket.location = "US"
        mock_bucket.exists.return_value = False
        mock_bucket.lifecycle_rules = []
        mock_bucket.iam_configuration = Mock()

        mock_client.bucket.return_value = mock_bucket
        mock_client.create_bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client

        # Test with uniform access enabled
        config_enabled = BucketConfig(name="access-enabled", uniform_access=True)
        manager_enabled = GCSManager(project_id="test-project", config=config_enabled)

        result = manager_enabled.create_bucket("access-enabled")
        assert result.created is True
        assert mock_bucket.iam_configuration.uniform_bucket_level_access_enabled is True

        # Reset mock for next test
        mock_bucket.reset_mock()
        mock_bucket.iam_configuration = Mock()

        # Test with uniform access disabled
        config_disabled = BucketConfig(name="access-disabled", uniform_access=False)
        manager_disabled = GCSManager(project_id="test-project", config=config_disabled)

        result = manager_disabled.create_bucket("access-disabled")
        assert result.created is True
        # When disabled, we shouldn't call uniform_bucket_level_access_enabled setter
        # Since we reset the mock, it should not have been accessed
        assert (
            not mock_bucket.iam_configuration.uniform_bucket_level_access_enabled.called
        )
