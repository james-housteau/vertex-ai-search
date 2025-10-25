"""Tests for retry functionality."""

import time
from unittest.mock import Mock

import pytest
from document_uploader.retry import retry_with_backoff


class TestRetryWithBackoff:
    """Test retry logic implementation."""

    def test_successful_operation_no_retry(self) -> None:
        """Test that successful operations don't trigger retries."""
        mock_func = Mock(return_value="success")
        decorated_func = retry_with_backoff(max_retries=3)(mock_func)

        result = decorated_func("arg1", kwarg1="value1")

        assert result == "success"
        assert mock_func.call_count == 1
        mock_func.assert_called_with("arg1", kwarg1="value1")

    def test_retry_on_exception(self) -> None:
        """Test that operations are retried on specified exceptions."""
        mock_func = Mock(
            side_effect=[ValueError("fail"), ValueError("fail"), "success"]
        )
        decorated_func = retry_with_backoff(
            max_retries=3,
            base_delay=0.01,  # Very short delay for testing
            exceptions=(ValueError,),
        )(mock_func)

        result = decorated_func()

        assert result == "success"
        assert mock_func.call_count == 3

    def test_retry_exhausted_reraises_exception(self) -> None:
        """Test that exception is re-raised after max retries."""
        mock_func = Mock(side_effect=ValueError("persistent failure"))
        decorated_func = retry_with_backoff(
            max_retries=2, base_delay=0.01, exceptions=(ValueError,)
        )(mock_func)

        with pytest.raises(ValueError, match="persistent failure"):
            decorated_func()

        assert mock_func.call_count == 3  # Initial call + 2 retries

    def test_retry_only_specified_exceptions(self) -> None:
        """Test that only specified exceptions trigger retries."""
        mock_func = Mock(side_effect=RuntimeError("different error"))
        decorated_func = retry_with_backoff(
            max_retries=3,
            base_delay=0.01,
            exceptions=(ValueError,),  # Only retry on ValueError
        )(mock_func)

        with pytest.raises(RuntimeError, match="different error"):
            decorated_func()

        assert mock_func.call_count == 1  # No retries for RuntimeError

    def test_exponential_backoff_timing(self) -> None:
        """Test that delays follow exponential backoff pattern."""
        call_times = []

        def failing_func() -> None:
            call_times.append(time.time())
            raise ValueError("test failure")

        decorated_func = retry_with_backoff(
            max_retries=2, base_delay=0.1, exceptions=(ValueError,)
        )(failing_func)

        with pytest.raises(ValueError):
            decorated_func()

        # Check that we have 3 calls (initial + 2 retries)
        assert len(call_times) == 3

        # Check timing approximately (allowing for some variance)
        time_diff_1 = call_times[1] - call_times[0]
        time_diff_2 = call_times[2] - call_times[1]

        assert 0.08 <= time_diff_1 <= 0.15  # ~0.1s ±50%
        assert 0.15 <= time_diff_2 <= 0.25  # ~0.2s exponential
