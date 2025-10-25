"""Unit tests for GCS Manager data models."""

from gcs_manager.models import BucketConfig, BucketResult


class TestBucketResult:
    """Test BucketResult dataclass."""

    def test_bucket_result_creation(self):
        """Test creating BucketResult with all fields."""
        result = BucketResult(
            bucket_name="test-bucket",
            bucket_uri="gs://test-bucket",
            region="US",
            created=True,
            error_message=None,
        )

        assert result.bucket_name == "test-bucket"
        assert result.bucket_uri == "gs://test-bucket"
        assert result.region == "US"
        assert result.created is True
        assert result.error_message is None

    def test_bucket_result_with_error(self):
        """Test creating BucketResult with error message."""
        result = BucketResult(
            bucket_name="failed-bucket",
            bucket_uri="",
            region="US",
            created=False,
            error_message="Access denied",
        )

        assert result.bucket_name == "failed-bucket"
        assert result.bucket_uri == ""
        assert result.region == "US"
        assert result.created is False
        assert result.error_message == "Access denied"

    def test_bucket_result_minimal(self):
        """Test creating BucketResult with minimal required fields."""
        result = BucketResult(
            bucket_name="minimal-bucket",
            bucket_uri="gs://minimal-bucket",
            region="US",
            created=True,
        )

        assert result.bucket_name == "minimal-bucket"
        assert result.bucket_uri == "gs://minimal-bucket"
        assert result.region == "US"
        assert result.created is True
        assert result.error_message is None  # Default value


class TestBucketConfig:
    """Test BucketConfig dataclass."""

    def test_bucket_config_defaults(self):
        """Test BucketConfig with default values."""
        config = BucketConfig(name="test-bucket")

        assert config.name == "test-bucket"
        assert config.region == "us"
        assert config.lifecycle_days == 30
        assert config.uniform_access is True

    def test_bucket_config_custom_values(self):
        """Test BucketConfig with custom values."""
        config = BucketConfig(
            name="custom-bucket",
            region="us-central1",
            lifecycle_days=7,
            uniform_access=False,
        )

        assert config.name == "custom-bucket"
        assert config.region == "us-central1"
        assert config.lifecycle_days == 7
        assert config.uniform_access is False

    def test_bucket_config_partial_custom(self):
        """Test BucketConfig with some custom values."""
        config = BucketConfig(name="partial-bucket", region="eu", lifecycle_days=60)

        assert config.name == "partial-bucket"
        assert config.region == "eu"
        assert config.lifecycle_days == 60
        assert config.uniform_access is True  # Default value
