"""Test CLI functionality for metrics-collector."""

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from metrics_collector.main import cli
from metrics_collector.models import PerformanceMetrics


class TestCLICommands:
    """Test CLI command functionality."""

    def test_cli_help(self) -> None:
        """Test CLI help command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Metrics Collector" in result.output
        assert "Performance metrics collection and analysis" in result.output

    def test_cli_version(self) -> None:
        """Test CLI version command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_status_command_default_output_dir(self) -> None:
        """Test status command with default output directory."""
        runner = CliRunner()
        result = runner.invoke(cli, ["status"])

        assert result.exit_code == 0
        assert "Metrics Collector Status" in result.output
        assert "Output Directory:" in result.output
        assert "Directory Exists:" in result.output
        assert "Current Time:" in result.output
        assert "Report Structure Ready:" in result.output

    def test_status_command_custom_output_dir(self, tmp_path: Path) -> None:
        """Test status command with custom output directory."""
        runner = CliRunner()
        custom_dir = tmp_path / "custom_metrics"

        result = runner.invoke(cli, ["status", "--output-dir", str(custom_dir)])

        assert result.exit_code == 0
        assert str(custom_dir) in result.output
        assert custom_dir.exists()  # Should be created by MetricsCollector

    @patch("metrics_collector.main.MetricsCollector")
    def test_export_command_json_success(
        self, mock_collector_class: MagicMock, tmp_path: Path
    ) -> None:
        """Test export command with JSON format success."""
        # Setup mock
        mock_collector = MagicMock()
        mock_collector.export_to_json.return_value = True
        mock_collector_class.return_value = mock_collector

        runner = CliRunner()
        json_file = tmp_path / "test.json"

        result = runner.invoke(cli, ["export", "--json-file", str(json_file)])

        assert result.exit_code == 0
        assert "✓ Metrics exported to JSON" in result.output
        mock_collector.export_to_json.assert_called_once_with(json_file)

    @patch("metrics_collector.main.MetricsCollector")
    def test_export_command_json_failure(
        self, mock_collector_class: MagicMock, tmp_path: Path
    ) -> None:
        """Test export command with JSON format failure."""
        # Setup mock
        mock_collector = MagicMock()
        mock_collector.export_to_json.return_value = False
        mock_collector_class.return_value = mock_collector

        runner = CliRunner()
        json_file = tmp_path / "test.json"

        result = runner.invoke(cli, ["export", "--json-file", str(json_file)])

        assert result.exit_code == 0
        assert "✗ Failed to export metrics to JSON" in result.output

    @patch("metrics_collector.main.MetricsCollector")
    def test_export_command_csv_success(
        self, mock_collector_class: MagicMock, tmp_path: Path
    ) -> None:
        """Test export command with CSV format success."""
        # Setup mock
        mock_collector = MagicMock()
        mock_collector.export_to_csv.return_value = True
        mock_collector_class.return_value = mock_collector

        runner = CliRunner()
        csv_file = tmp_path / "test.csv"

        result = runner.invoke(cli, ["export", "--csv-file", str(csv_file)])

        assert result.exit_code == 0
        assert "✓ Metrics exported to CSV" in result.output
        mock_collector.export_to_csv.assert_called_once_with(csv_file)

    @patch("metrics_collector.main.MetricsCollector")
    def test_export_command_csv_failure(
        self, mock_collector_class: MagicMock, tmp_path: Path
    ) -> None:
        """Test export command with CSV format failure."""
        # Setup mock
        mock_collector = MagicMock()
        mock_collector.export_to_csv.return_value = False
        mock_collector_class.return_value = mock_collector

        runner = CliRunner()
        csv_file = tmp_path / "test.csv"

        result = runner.invoke(cli, ["export", "--csv-file", str(csv_file)])

        assert result.exit_code == 0
        assert "✗ Failed to export metrics to CSV" in result.output

    @patch("metrics_collector.main.MetricsCollector")
    def test_export_command_both_formats(
        self, mock_collector_class: MagicMock, tmp_path: Path
    ) -> None:
        """Test export command with both JSON and CSV formats."""
        # Setup mock
        mock_collector = MagicMock()
        mock_collector.export_to_json.return_value = True
        mock_collector.export_to_csv.return_value = True
        mock_collector_class.return_value = mock_collector

        runner = CliRunner()
        json_file = tmp_path / "test.json"
        csv_file = tmp_path / "test.csv"

        result = runner.invoke(
            cli, ["export", "--json-file", str(json_file), "--csv-file", str(csv_file)]
        )

        assert result.exit_code == 0
        assert "✓ Metrics exported to JSON" in result.output
        assert "✓ Metrics exported to CSV" in result.output

    def test_export_command_no_format_specified(self) -> None:
        """Test export command with no format specified."""
        runner = CliRunner()
        result = runner.invoke(cli, ["export"])

        assert result.exit_code == 0
        assert "No export format specified" in result.output
        assert "Use --json-file or --csv-file options" in result.output

    @patch("metrics_collector.main.MetricsCollector")
    def test_report_command(self, mock_collector_class: MagicMock) -> None:
        """Test report command."""
        # Setup mock
        mock_collector = MagicMock()
        mock_metrics = PerformanceMetrics(
            operation_type="mixed",
            total_operations=100,
            success_rate=95.5,
            avg_response_time_ms=150.25,
            median_response_time_ms=140.00,
            p95_response_time_ms=300.75,
            error_count=5,
            timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC),
        )
        mock_collector.generate_report.return_value = mock_metrics
        mock_collector_class.return_value = mock_collector

        runner = CliRunner()
        result = runner.invoke(cli, ["report"])

        assert result.exit_code == 0
        assert "Performance Metrics Report" in result.output
        assert "Operation Type: mixed" in result.output
        assert "Total Operations: 100" in result.output
        assert "Success Rate: 95.50%" in result.output
        assert "Error Count: 5" in result.output
        assert "Average Response Time: 150.25ms" in result.output
        assert "Median Response Time: 140.00ms" in result.output
        assert "95th Percentile Response Time: 300.75ms" in result.output
        assert "2024-01-01 12:00:00" in result.output

    @patch("metrics_collector.main.MetricsCollector")
    def test_report_command_custom_output_dir(
        self, mock_collector_class: MagicMock, tmp_path: Path
    ) -> None:
        """Test report command with custom output directory."""
        # Setup mock
        mock_collector = MagicMock()
        mock_metrics = PerformanceMetrics(
            operation_type="search",
            total_operations=0,
            success_rate=0.0,
            avg_response_time_ms=0.0,
            median_response_time_ms=0.0,
            p95_response_time_ms=0.0,
            error_count=0,
            timestamp=datetime.now(tz=UTC),
        )
        mock_collector.generate_report.return_value = mock_metrics
        mock_collector_class.return_value = mock_collector

        runner = CliRunner()
        custom_dir = tmp_path / "custom_metrics"

        result = runner.invoke(cli, ["report", "--output-dir", str(custom_dir)])

        assert result.exit_code == 0
        assert "Performance Metrics Report" in result.output
        mock_collector_class.assert_called_once_with(output_dir=custom_dir)

    def test_all_commands_help(self) -> None:
        """Test help for all individual commands."""
        runner = CliRunner()

        commands = ["status", "export", "report"]

        for command in commands:
            result = runner.invoke(cli, [command, "--help"])
            assert result.exit_code == 0
            assert command in result.output.lower()
            assert "--help" in result.output
