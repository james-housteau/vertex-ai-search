"""Tests for Natural Questions CLI functionality."""

import gzip
import json
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner
from html_extractor.main import main


@pytest.fixture
def sample_nq_jsonl_gz():
    """Create sample Natural Questions JSONL.gz file for testing."""
    data = [
        {
            "example_id": "1",
            "document_title": "Test Doc 1",
            "document_html": "<html>Content 1</html>",
            "document_url": "http://test1.com",
        },
        {
            "example_id": "2",
            "document_title": "Test Doc 2",
            "document_html": "<html>Content 2</html>",
            "document_url": "http://test2.com",
        },
    ]

    with tempfile.NamedTemporaryFile(mode="wb", suffix=".jsonl.gz", delete=False) as f:
        with gzip.open(f.name, "wt", encoding="utf-8") as gz_file:
            for entry in data:
                gz_file.write(json.dumps(entry) + "\n")
        return Path(f.name)


class TestCLI:
    """Test CLI commands."""

    def test_process_nq_dataset_stats_only(self, sample_nq_jsonl_gz):
        """Test processing dataset with stats-only flag."""
        runner = CliRunner()
        result = runner.invoke(
            main, ["process-nq-dataset", str(sample_nq_jsonl_gz), "--stats-only"]
        )

        assert result.exit_code == 0
        assert "Total JSONL entries" in result.output
        assert "Unique documents" in result.output

    def test_process_nq_dataset_with_output(self, sample_nq_jsonl_gz):
        """Test processing dataset with output file."""
        runner = CliRunner()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as output_file:
            output_path = Path(output_file.name)
            result = runner.invoke(
                main,
                [
                    "process-nq-dataset",
                    str(sample_nq_jsonl_gz),
                    "--output",
                    str(output_path),
                ],
            )

            assert result.exit_code == 0
            assert output_path.exists()

            with open(output_path, encoding="utf-8") as f:
                documents = json.load(f)
                assert len(documents) == 2
                assert documents[0]["title"] == "Test Doc 1"

    def test_process_nq_dataset_file_not_found(self):
        """Test processing with non-existent file."""
        runner = CliRunner()
        result = runner.invoke(
            main, ["process-nq-dataset", "/nonexistent/file.jsonl.gz"]
        )
        assert result.exit_code != 0

    def test_main_command_help(self):
        """Test main command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert (
            "HTML document extraction from Natural Questions dataset" in result.output
        )

    def test_process_nq_dataset_help(self):
        """Test process-nq-dataset command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["process-nq-dataset", "--help"])
        assert result.exit_code == 0
        assert "Process Natural Questions JSONL.gz dataset" in result.output
