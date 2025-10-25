"""Pytest configuration for vector-search-index tests."""

import pytest


@pytest.fixture(autouse=True)
def reset_environment() -> None:
    """Reset environment before each test."""
    pass
