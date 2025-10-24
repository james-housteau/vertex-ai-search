"""Unit tests for GCSManager class."""

from unittest.mock import Mock, patch

from gcs_manager.gcs_manager import GCSManager
from gcs_manager.models import BucketConfig


class TestGCSManager:
    """Unit tests for GCSManager class."""

    def test_init_with_default_config(self):
        """Test GCSManager initialization with default config."""
        with patch("google.cloud.storage.Client"):
            manager = GCSManager(project_id="test-project")

            assert manager.project_id == "test-project"
            assert isinstance(manager.config, BucketConfig)
            assert manager.config.name == "default"

    def test_init_with_custom_config(self):
        """Test GCSManager initialization with custom config."""
        config = BucketConfig(name="custom", region="eu", lifecycle_days=7)

        with patch("google.cloud.storage.Client"):
            manager = GCSManager(project_id="test-project", config=config)

            assert manager.project_id == "test-project"
            assert manager.config == config
            assert manager.config.lifecycle_days == 7

    @patch("google.cloud.storage.Client")
    def test_ensure_unique_bucket_name_available(self, mock_client):
        """Test unique name generation when original name is available."""
        mock_bucket = Mock()
        mock_bucket.exists.return_value = False
        mock_client.return_value.bucket.return_value = mock_bucket

        manager = GCSManager(project_id="test-project")
        result = manager._ensure_unique_bucket_name("available-bucket")

        assert result == "available-bucket"

    @patch("google.cloud.storage.Client")
    def test_ensure_unique_bucket_name_conflict(self, mock_client):
        """Test unique name generation when original name conflicts."""
        mock_bucket = Mock()
        mock_bucket.exists.return_value = True
        mock_client.return_value.bucket.return_value = mock_bucket

        manager = GCSManager(project_id="test-project")
        result = manager._ensure_unique_bucket_name("conflicting-bucket")

        assert result.startswith("conflicting-bucket-")
        assert len(result) > len("conflicting-bucket-")

    @patch("google.cloud.storage.Client")
    def test_configure_lifecycle_policy(self, mock_client):
        """Test lifecycle policy configuration."""
        mock_bucket = Mock()
        mock_bucket.lifecycle_rules = []

        config = BucketConfig(name="test", lifecycle_days=14)
        manager = GCSManager(project_id="test-project", config=config)
        manager._configure_lifecycle_policy(mock_bucket)

        # Verify lifecycle rule was set
        assert mock_bucket.lifecycle_rules is not None
        assert len(mock_bucket.lifecycle_rules) == 1
        assert mock_bucket.lifecycle_rules[0]["condition"]["age"] == 14
        mock_bucket.patch.assert_called_once()

    @patch("google.cloud.storage.Client")
    def test_configure_uniform_access_enabled(self, mock_client):
        """Test uniform access configuration when enabled."""
        mock_bucket = Mock()
        mock_iam_config = Mock()
        mock_bucket.iam_configuration = mock_iam_config

        config = BucketConfig(name="test", uniform_access=True)
        manager = GCSManager(project_id="test-project", config=config)
        manager._configure_uniform_access(mock_bucket)

        assert mock_iam_config.uniform_bucket_level_access_enabled is True
        mock_bucket.patch.assert_called_once()

    @patch("google.cloud.storage.Client")
    def test_configure_uniform_access_disabled(self, mock_client):
        """Test uniform access configuration when disabled."""
        mock_bucket = Mock()

        config = BucketConfig(name="test", uniform_access=False)
        manager = GCSManager(project_id="test-project", config=config)
        manager._configure_uniform_access(mock_bucket)

        # Should not modify bucket when uniform_access is False
        mock_bucket.patch.assert_not_called()

    @patch("google.cloud.storage.Client")
    def test_bucket_exists_exception_handling(self, mock_client):
        """Test bucket_exists handles exceptions gracefully."""
        mock_client.return_value.bucket.side_effect = Exception("Network error")

        manager = GCSManager(project_id="test-project")
        result = manager.bucket_exists("error-bucket")

        assert result is False

    @patch("google.cloud.storage.Client")
    def test_delete_bucket_nonexistent(self, mock_client):
        """Test deleting non-existent bucket."""
        mock_bucket = Mock()
        mock_bucket.exists.return_value = False
        mock_client.return_value.bucket.return_value = mock_bucket

        manager = GCSManager(project_id="test-project")
        result = manager.delete_bucket("nonexistent-bucket")

        assert result is False
        mock_bucket.delete.assert_not_called()

    @patch("google.cloud.storage.Client")
    def test_delete_bucket_with_exception(self, mock_client):
        """Test delete_bucket handles exceptions gracefully."""
        mock_bucket = Mock()
        mock_bucket.exists.side_effect = Exception("Network error")
        mock_client.return_value.bucket.return_value = mock_bucket

        manager = GCSManager(project_id="test-project")
        result = manager.delete_bucket("error-bucket")

        assert result is False

    @patch("google.cloud.storage.Client")
    def test_get_bucket_info_exception_handling(self, mock_client):
        """Test get_bucket_info handles exceptions gracefully."""
        mock_client.return_value.bucket.side_effect = Exception("Network error")

        manager = GCSManager(project_id="test-project")
        result = manager.get_bucket_info("error-bucket")

        assert result is None
