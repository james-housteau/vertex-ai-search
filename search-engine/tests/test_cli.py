"""Tests for search-engine CLI."""

from unittest.mock import Mock, patch

from click.testing import CliRunner

from search_engine.main import cli
from search_engine.models import SearchResult


class TestCLI:
    """Test CLI functionality."""

    def test_cli_version(self):
        """Test CLI version command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    @patch("search_engine.main.SearchEngine")
    def test_search_command_success(self, mock_engine_class):
        """Test successful search command."""
        # Setup mock
        mock_engine = Mock()
        mock_engine_class.return_value = mock_engine
        mock_engine.search.return_value = SearchResult(
            query="test query",
            results=[
                {"title": "Test Document 1", "content": "Test content"},
                {"title": "Test Document 2", "content": "More content"},
            ],
            result_count=2,
            execution_time_ms=150.5,
            relevance_scores=[0.95, 0.87],
            success=True,
        )

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "search",
                "--project-id",
                "test-project",
                "--data-store-id",
                "test-datastore",
                "--query",
                "test query",
                "--max-results",
                "5",
            ],
        )

        assert result.exit_code == 0
        assert "Query: test query" in result.output
        assert "Results: 2" in result.output
        assert "Execution time: 150.50ms" in result.output
        assert "Test Document 1" in result.output
        assert "Test Document 2" in result.output

        # Verify SearchEngine was initialized correctly
        mock_engine_class.assert_called_once_with("test-project", "test-datastore")
        mock_engine.search.assert_called_once_with("test query", 5)

    @patch("search_engine.main.SearchEngine")
    def test_search_command_failure(self, mock_engine_class):
        """Test search command with failure."""
        # Setup mock
        mock_engine = Mock()
        mock_engine_class.return_value = mock_engine
        mock_engine.search.return_value = SearchResult(
            query="failed query",
            results=[],
            result_count=0,
            execution_time_ms=50.0,
            relevance_scores=[],
            success=False,
            error_message="Connection timeout",
        )

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "search",
                "--project-id",
                "test-project",
                "--data-store-id",
                "test-datastore",
                "--query",
                "failed query",
            ],
        )

        assert result.exit_code == 0
        assert "Search failed: Connection timeout" in result.output

    def test_search_command_missing_required_params(self):
        """Test search command with missing required parameters."""
        runner = CliRunner()
        result = runner.invoke(cli, ["search"])

        assert result.exit_code != 0
        assert "Missing option" in result.output

    @patch("search_engine.main.SearchEngine")
    def test_search_command_default_max_results(self, mock_engine_class):
        """Test search command with default max_results."""
        mock_engine = Mock()
        mock_engine_class.return_value = mock_engine
        mock_engine.search.return_value = SearchResult(
            query="test",
            results=[],
            result_count=0,
            execution_time_ms=100.0,
            relevance_scores=[],
            success=True,
        )

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "search",
                "--project-id",
                "test-project",
                "--data-store-id",
                "test-datastore",
                "--query",
                "test",
            ],
        )

        assert result.exit_code == 0
        # Verify default max_results (10) was used
        mock_engine.search.assert_called_once_with("test", 10)

    @patch("search_engine.main.SearchEngine")
    def test_validate_command_success(self, mock_engine_class):
        """Test successful validate command."""
        mock_engine = Mock()
        mock_engine_class.return_value = mock_engine
        mock_engine.validate_connection.return_value = True

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "validate",
                "--project-id",
                "test-project",
                "--data-store-id",
                "test-datastore",
            ],
        )

        assert result.exit_code == 0
        assert "✅ Connection to Vertex AI search service is valid" in result.output
        mock_engine.validate_connection.assert_called_once()

    @patch("search_engine.main.SearchEngine")
    def test_validate_command_failure(self, mock_engine_class):
        """Test validate command with connection failure."""
        mock_engine = Mock()
        mock_engine_class.return_value = mock_engine
        mock_engine.validate_connection.return_value = False

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "validate",
                "--project-id",
                "test-project",
                "--data-store-id",
                "test-datastore",
            ],
        )

        assert result.exit_code == 0
        assert "❌ Connection to Vertex AI search service failed" in result.output

    def test_validate_command_missing_params(self):
        """Test validate command with missing parameters."""
        runner = CliRunner()
        result = runner.invoke(cli, ["validate"])

        assert result.exit_code != 0
        assert "Missing option" in result.output

    @patch("search_engine.main.SearchEngine")
    def test_search_with_no_title_results(self, mock_engine_class):
        """Test search command with results that have no title."""
        mock_engine = Mock()
        mock_engine_class.return_value = mock_engine
        mock_engine.search.return_value = SearchResult(
            query="test query",
            results=[
                {"content": "Content without title"},
                {"title": "", "content": "Empty title"},
                {"other_field": "No title field"},
            ],
            result_count=3,
            execution_time_ms=100.0,
            relevance_scores=[0.8, 0.7, 0.6],
            success=True,
        )

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "search",
                "--project-id",
                "test-project",
                "--data-store-id",
                "test-datastore",
                "--query",
                "test query",
            ],
        )

        assert result.exit_code == 0
        assert "Results: 3" in result.output
        # Should show "No title" for documents without title
        assert "No title" in result.output
