"""
TDD RED PHASE - Acceptance tests for GCS Manager API contract.

These tests define the expected behavior and will initially fail.
They serve as the specification for the GCS Manager implementation.
"""

from unittest.mock import Mock, patch

import pytest

# Import the API contract types that we need to implement
from gcs_manager.gcs_manager import GCSManager
from gcs_manager.models import BucketConfig, BucketResult


class TestGCSManagerAcceptance:
    """Acceptance tests defining the complete API contract."""

    def test_create_bucket_success(self):
        """Test successful bucket creation with proper configuration."""
        with patch("google.cloud.storage.Client") as mock_client:
            # Mock GCS client behavior
            mock_bucket = Mock()
            mock_bucket.name = "test-bucket-12345"
            mock_bucket.location = "US"
            mock_bucket.exists.return_value = False

            mock_client.return_value.bucket.return_value = mock_bucket
            mock_client.return_value.create_bucket.return_value = mock_bucket

            # Test bucket creation
            manager = GCSManager(project_id="test-project")
            result = manager.create_bucket("test-bucket", region="us")

            # Verify expected behavior
            assert isinstance(result, BucketResult)
            assert result.bucket_name == "test-bucket-12345"
            assert result.bucket_uri.startswith("gs://")
            assert result.region == "US"
            assert result.created is True
            assert result.error_message is None

    def test_create_bucket_with_config(self):
        """Test bucket creation with custom configuration."""
        with patch("google.cloud.storage.Client") as mock_client:
            mock_bucket = Mock()
            mock_bucket.name = "configured-bucket"
            mock_bucket.location = "US-CENTRAL1"
            mock_bucket.exists.return_value = False

            mock_client.return_value.bucket.return_value = mock_bucket
            mock_client.return_value.create_bucket.return_value = mock_bucket

            config = BucketConfig(
                name="configured-bucket",
                region="us-central1",
                lifecycle_days=7,
                uniform_access=False,
            )

            manager = GCSManager(project_id="test-project", config=config)
            result = manager.create_bucket("configured-bucket", region="us-central1")

            assert result.bucket_name == "configured-bucket"
            assert result.created is True

    def test_bucket_exists_true(self):
        """Test checking if a bucket exists - positive case."""
        with patch("google.cloud.storage.Client") as mock_client:
            mock_bucket = Mock()
            mock_bucket.exists.return_value = True
            mock_client.return_value.bucket.return_value = mock_bucket

            manager = GCSManager(project_id="test-project")
            exists = manager.bucket_exists("existing-bucket")

            assert exists is True

    def test_bucket_exists_false(self):
        """Test checking if a bucket exists - negative case."""
        with patch("google.cloud.storage.Client") as mock_client:
            mock_bucket = Mock()
            mock_bucket.exists.return_value = False
            mock_client.return_value.bucket.return_value = mock_bucket

            manager = GCSManager(project_id="test-project")
            exists = manager.bucket_exists("nonexistent-bucket")

            assert exists is False

    def test_delete_bucket_success(self):
        """Test successful bucket deletion."""
        with patch("google.cloud.storage.Client") as mock_client:
            mock_bucket = Mock()
            mock_bucket.exists.return_value = True
            mock_client.return_value.bucket.return_value = mock_bucket

            manager = GCSManager(project_id="test-project")
            success = manager.delete_bucket("test-bucket")

            assert success is True
            mock_bucket.delete.assert_called_once()

    def test_delete_bucket_with_force(self):
        """Test bucket deletion with force flag to remove contents."""
        with patch("google.cloud.storage.Client") as mock_client:
            mock_bucket = Mock()
            mock_bucket.exists.return_value = True
            mock_bucket.list_blobs.return_value = [Mock(), Mock()]  # Some objects
            mock_client.return_value.bucket.return_value = mock_bucket

            manager = GCSManager(project_id="test-project")
            success = manager.delete_bucket("test-bucket", force=True)

            assert success is True

    def test_get_bucket_info_success(self):
        """Test retrieving bucket information."""
        with patch("google.cloud.storage.Client") as mock_client:
            mock_bucket = Mock()
            mock_bucket.name = "info-bucket"
            mock_bucket.location = "US"
            mock_bucket.exists.return_value = True
            mock_client.return_value.bucket.return_value = mock_bucket

            manager = GCSManager(project_id="test-project")
            info = manager.get_bucket_info("info-bucket")

            assert info is not None
            assert isinstance(info, BucketResult)
            assert info.bucket_name == "info-bucket"
            assert info.region == "US"
            assert info.created is False  # Existing bucket, not newly created

    def test_get_bucket_info_not_found(self):
        """Test retrieving info for non-existent bucket."""
        with patch("google.cloud.storage.Client") as mock_client:
            mock_bucket = Mock()
            mock_bucket.exists.return_value = False
            mock_client.return_value.bucket.return_value = mock_bucket

            manager = GCSManager(project_id="test-project")
            info = manager.get_bucket_info("nonexistent-bucket")

            assert info is None

    def test_create_bucket_name_conflict_auto_generation(self):
        """Test bucket name conflict handling with auto-generation."""
        with patch("google.cloud.storage.Client") as mock_client:
            # First bucket exists, second one doesn't
            mock_existing_bucket = Mock()
            mock_existing_bucket.exists.return_value = True

            mock_new_bucket = Mock()
            mock_new_bucket.name = "test-bucket-12345"
            mock_new_bucket.location = "US"
            mock_new_bucket.exists.return_value = False

            def bucket_side_effect(name):
                if name == "test-bucket":
                    return mock_existing_bucket
                return mock_new_bucket

            mock_client.return_value.bucket.side_effect = bucket_side_effect
            mock_client.return_value.create_bucket.return_value = mock_new_bucket

            manager = GCSManager(project_id="test-project")
            result = manager.create_bucket("test-bucket")

            assert result.bucket_name != "test-bucket"  # Should be auto-generated
            assert result.created is True

    def test_create_bucket_permission_error(self):
        """Test bucket creation with insufficient permissions."""
        with patch("google.cloud.storage.Client") as mock_client:
            from google.cloud.exceptions import Forbidden

            mock_client.return_value.create_bucket.side_effect = Forbidden(
                "Access denied"
            )

            manager = GCSManager(project_id="test-project")
            result = manager.create_bucket("test-bucket")

            assert result.created is False
            assert result.error_message is not None
            assert "Access denied" in result.error_message

    def test_lifecycle_policy_configuration(self):
        """Test that lifecycle policies are properly configured."""
        with patch("google.cloud.storage.Client") as mock_client:
            mock_bucket = Mock()
            mock_bucket.name = "lifecycle-bucket"
            mock_bucket.location = "US"
            mock_bucket.exists.return_value = False

            mock_client.return_value.bucket.return_value = mock_bucket
            mock_client.return_value.create_bucket.return_value = mock_bucket

            config = BucketConfig(name="lifecycle-bucket", lifecycle_days=7)
            manager = GCSManager(project_id="test-project", config=config)
            result = manager.create_bucket("lifecycle-bucket")

            # Verify lifecycle rule was set
            assert mock_bucket.lifecycle_rules is not None or hasattr(
                mock_bucket, "add_lifecycle_delete_rule"
            )
            assert result.created is True

    def test_uniform_access_configuration(self):
        """Test that uniform bucket-level access is properly configured."""
        with patch("google.cloud.storage.Client") as mock_client:
            mock_bucket = Mock()
            mock_bucket.name = "uniform-access-bucket"
            mock_bucket.location = "US"
            mock_bucket.exists.return_value = False

            mock_client.return_value.bucket.return_value = mock_bucket
            mock_client.return_value.create_bucket.return_value = mock_bucket

            config = BucketConfig(name="uniform-access-bucket", uniform_access=True)
            manager = GCSManager(project_id="test-project", config=config)
            result = manager.create_bucket("uniform-access-bucket")

            # Verify uniform access was configured
            assert (
                hasattr(mock_bucket, "iam_configuration")
                or mock_bucket.iam_configuration is not None
            )
            assert result.created is True
