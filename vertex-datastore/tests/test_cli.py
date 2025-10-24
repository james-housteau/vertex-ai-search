"""Tests for the CLI interface."""

from click.testing import CliRunner

from vertex_datastore.cli import cli


class TestCLI:
    """Tests for the command-line interface."""

    def test_cli_help(self) -> None:
        """Test CLI help output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Vertex AI Data Store Manager CLI" in result.output

    def test_create_command_help(self) -> None:
        """Test create command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--project-id", "test", "create", "--help"])
        assert result.exit_code == 0
        assert "Create a new data store" in result.output

    def test_create_command(self) -> None:
        """Test create command execution."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--project-id",
                "test-project",
                "create",
                "test-datastore",
                "gs://test-bucket/",
            ],
        )
        assert result.exit_code == 0
        assert "Data store created successfully" in result.output
        assert "test-datastore" in result.output

    def test_import_docs_command(self) -> None:
        """Test import-docs command execution."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--project-id",
                "test-project",
                "import-docs",
                "test-datastore",
                "gs://test-bucket/",
            ],
        )
        assert result.exit_code == 0
        assert "Document import started" in result.output

    def test_status_command(self) -> None:
        """Test status command execution."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--project-id",
                "test-project",
                "status",
                "projects/test-project/operations/import-123",
            ],
        )
        assert result.exit_code == 0
        assert "Import Status" in result.output

    def test_serving_config_command(self) -> None:
        """Test serving-config command execution."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["--project-id", "test-project", "serving-config", "test-datastore"]
        )
        assert result.exit_code == 0
        assert "Serving Config Path" in result.output
        assert "test-datastore" in result.output

    def test_delete_command_with_force(self) -> None:
        """Test delete command with force flag."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["--project-id", "test-project", "delete", "--force", "test-datastore"]
        )
        assert result.exit_code == 0
        assert "deleted successfully" in result.output

    def test_delete_command_without_force(self) -> None:
        """Test delete command without force (should prompt for confirmation)."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["--project-id", "test-project", "delete", "test-datastore"],
            input="n\n",
        )  # Respond "no" to confirmation
        assert result.exit_code == 1  # Aborted by user

    def test_missing_project_id(self) -> None:
        """Test CLI without required project-id."""
        runner = CliRunner()
        result = runner.invoke(cli, ["create", "test", "gs://bucket/"])
        assert result.exit_code == 2  # Missing required option
        assert "project-id" in result.output

    def test_custom_location(self) -> None:
        """Test CLI with custom location."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--project-id",
                "test-project",
                "--location",
                "us-central1",
                "serving-config",
                "test-datastore",
            ],
        )
        assert result.exit_code == 0
        assert "us-central1" in result.output
