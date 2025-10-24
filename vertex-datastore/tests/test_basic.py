"""Basic functionality tests to ensure the implementation works."""

from unittest.mock import patch

from vertex_datastore import DataStoreResult, ImportProgress, VertexDataStoreManager
from vertex_datastore.main import main


def test_package_imports() -> None:
    """Test that package imports work correctly."""
    assert VertexDataStoreManager is not None
    assert DataStoreResult is not None
    assert ImportProgress is not None


def test_manager_initialization() -> None:
    """Test basic manager initialization."""
    manager = VertexDataStoreManager("test-project")
    assert manager.project_id == "test-project"
    assert manager.location == "global"


def test_manager_initialization_with_location() -> None:
    """Test manager initialization with custom location."""
    manager = VertexDataStoreManager("test-project", "us-central1")
    assert manager.project_id == "test-project"
    assert manager.location == "us-central1"


@patch("vertex_datastore.main.cli")
def test_main_function(mock_cli) -> None:
    """Test main function calls CLI."""
    main()
    mock_cli.assert_called_once()
