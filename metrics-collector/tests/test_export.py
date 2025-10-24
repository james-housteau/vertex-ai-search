"""Test export functionality of MetricsCollector."""

import csv
import json
from pathlib import Path

from metrics_collector import ConversationResult, MetricsCollector, SearchResult


class TestJSONExport:
    """Test JSON export functionality."""

    def test_json_export_with_search_metrics(self, tmp_path: Path) -> None:
        """Test JSON export with search metrics."""
        collector = MetricsCollector()

        # Add test search metrics
        search_result = SearchResult(
            query="test search",
            results=[{"title": "Result 1"}],
            result_count=1,
            execution_time_ms=150.0,
            relevance_scores=[0.95],
            success=True,
        )
        collector.record_search_metric(search_result)

        json_file = tmp_path / "search_metrics.json"
        success = collector.export_to_json(json_file)

        assert success is True
        assert json_file.exists()

        # Verify JSON content
        with Path(json_file).open() as f:
            data = json.load(f)

        assert "export_timestamp" in data
        assert "metrics" in data
        assert "raw_data" in data

        metrics = data["metrics"]
        assert metrics["operation_type"] == "search"
        assert metrics["total_operations"] == 1
        assert metrics["success_rate"] == 100.0
        assert metrics["avg_response_time_ms"] == 150.0
        assert metrics["error_count"] == 0

        raw_data = data["raw_data"]
        assert raw_data["search_operations"] == 1
        assert raw_data["conversation_operations"] == 0

    def test_json_export_with_conversation_metrics(self, tmp_path: Path) -> None:
        """Test JSON export with conversation metrics."""
        collector = MetricsCollector()

        # Add test conversation metrics
        conversation_result = ConversationResult(
            query="test question",
            answer="test answer",
            response_time_ms=200.0,
            success=True,
            context_used=True,
        )
        collector.record_conversation_metric(conversation_result)

        json_file = tmp_path / "conversation_metrics.json"
        success = collector.export_to_json(json_file)

        assert success is True
        assert json_file.exists()

        # Verify JSON content
        with Path(json_file).open() as f:
            data = json.load(f)

        metrics = data["metrics"]
        assert metrics["operation_type"] == "conversation"
        assert metrics["total_operations"] == 1
        assert metrics["success_rate"] == 100.0
        assert metrics["avg_response_time_ms"] == 200.0

        raw_data = data["raw_data"]
        assert raw_data["search_operations"] == 0
        assert raw_data["conversation_operations"] == 1

    def test_json_export_with_mixed_metrics(self, tmp_path: Path) -> None:
        """Test JSON export with mixed metrics."""
        collector = MetricsCollector()

        # Add both search and conversation metrics
        search_result = SearchResult(
            query="search",
            results=[],
            result_count=0,
            execution_time_ms=100.0,
            relevance_scores=[],
            success=True,
        )
        conversation_result = ConversationResult(
            query="conversation",
            answer="answer",
            response_time_ms=300.0,
            success=False,
            error_message="Error",
        )

        collector.record_search_metric(search_result)
        collector.record_conversation_metric(conversation_result)

        json_file = tmp_path / "mixed_metrics.json"
        success = collector.export_to_json(json_file)

        assert success is True

        # Verify JSON content
        with Path(json_file).open() as f:
            data = json.load(f)

        metrics = data["metrics"]
        assert metrics["operation_type"] == "mixed"
        assert metrics["total_operations"] == 2
        assert metrics["success_rate"] == 50.0  # 1 success out of 2
        assert metrics["error_count"] == 1

        raw_data = data["raw_data"]
        assert raw_data["search_operations"] == 1
        assert raw_data["conversation_operations"] == 1

    def test_json_export_with_empty_metrics(self, tmp_path: Path) -> None:
        """Test JSON export with no metrics."""
        collector = MetricsCollector()

        json_file = tmp_path / "empty_metrics.json"
        success = collector.export_to_json(json_file)

        assert success is True
        assert json_file.exists()

        # Verify JSON content
        with Path(json_file).open() as f:
            data = json.load(f)

        metrics = data["metrics"]
        assert metrics["total_operations"] == 0
        assert metrics["success_rate"] == 0.0
        assert metrics["error_count"] == 0

    def test_json_export_error_handling(self) -> None:
        """Test JSON export error handling with invalid path."""
        collector = MetricsCollector()

        # Try to export to a path that doesn't exist and can't be created
        invalid_path = Path("/invalid/path/that/does/not/exist.json")
        success = collector.export_to_json(invalid_path)

        assert success is False


class TestCSVExport:
    """Test CSV export functionality."""

    def test_csv_export_with_search_metrics(self, tmp_path: Path) -> None:
        """Test CSV export with search metrics."""
        collector = MetricsCollector()

        # Add test search metrics
        search_results = [
            SearchResult("query1", [], 0, 100.0, [], success=True),
            SearchResult(
                "query2", [], 1, 200.0, [0.8], success=False, error_message="Error"
            ),
        ]

        for result in search_results:
            collector.record_search_metric(result)

        csv_file = tmp_path / "search_metrics.csv"
        success = collector.export_to_csv(csv_file)

        assert success is True
        assert csv_file.exists()

        # Verify CSV content
        with Path(csv_file).open() as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2

        # Check column presence
        expected_columns = [
            "operation_type",
            "query",
            "execution_time_ms",
            "success",
            "error_message",
            "result_count",
            "relevance_scores_count",
        ]
        for col in expected_columns:
            assert col in rows[0]

        # Check data
        search_rows = [row for row in rows if row["operation_type"] == "search"]
        assert len(search_rows) == 2
        assert search_rows[0]["query"] == "query1"
        assert float(search_rows[0]["execution_time_ms"]) == 100.0
        assert search_rows[0]["success"] == "True"
        assert search_rows[1]["success"] == "False"
        assert search_rows[1]["error_message"] == "Error"

    def test_csv_export_with_conversation_metrics(self, tmp_path: Path) -> None:
        """Test CSV export with conversation metrics."""
        collector = MetricsCollector()

        # Add test conversation metrics
        conversation_results = [
            ConversationResult("question1", "answer1", 150.0, success=True),
            ConversationResult(
                "question2",
                "answer2",
                250.0,
                success=False,
                error_message="Timeout",
                context_used=False,
            ),
        ]

        for result in conversation_results:
            collector.record_conversation_metric(result)

        csv_file = tmp_path / "conversation_metrics.csv"
        success = collector.export_to_csv(csv_file)

        assert success is True

        # Verify CSV content
        with Path(csv_file).open() as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2

        # Check conversation-specific columns
        conversation_rows = [
            row for row in rows if row["operation_type"] == "conversation"
        ]
        assert len(conversation_rows) == 2
        assert "answer" in rows[0]
        assert "context_used" in rows[0]

        assert conversation_rows[0]["query"] == "question1"
        assert float(conversation_rows[0]["execution_time_ms"]) == 150.0
        assert conversation_rows[0]["answer"] == "answer1"
        assert conversation_rows[0]["context_used"] == "True"

        assert conversation_rows[1]["success"] == "False"
        assert conversation_rows[1]["error_message"] == "Timeout"
        assert conversation_rows[1]["context_used"] == "False"

    def test_csv_export_with_mixed_metrics(self, tmp_path: Path) -> None:
        """Test CSV export with mixed metrics."""
        collector = MetricsCollector()

        # Add search metric
        search_result = SearchResult("search query", [], 0, 100.0, [], success=True)
        collector.record_search_metric(search_result)

        # Add conversation metric
        conversation_result = ConversationResult(
            "conversation query", "answer", 200.0, success=True
        )
        collector.record_conversation_metric(conversation_result)

        csv_file = tmp_path / "mixed_metrics.csv"
        success = collector.export_to_csv(csv_file)

        assert success is True

        # Verify CSV content
        with Path(csv_file).open() as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2

        search_rows = [row for row in rows if row["operation_type"] == "search"]
        conversation_rows = [
            row for row in rows if row["operation_type"] == "conversation"
        ]

        assert len(search_rows) == 1
        assert len(conversation_rows) == 1

        # Search row should have empty values for conversation-specific fields
        search_row = search_rows[0]
        assert search_row["answer"] == "" or search_row["answer"] == "None"
        assert search_row["context_used"] == "" or search_row["context_used"] == "None"

        # Conversation row should have empty values for search-specific fields
        conversation_row = conversation_rows[0]
        assert (
            conversation_row["result_count"] == ""
            or conversation_row["result_count"] == "None"
        )
        assert (
            conversation_row["relevance_scores_count"] == ""
            or conversation_row["relevance_scores_count"] == "None"
        )

    def test_csv_export_with_empty_metrics(self, tmp_path: Path) -> None:
        """Test CSV export with no metrics."""
        collector = MetricsCollector()

        csv_file = tmp_path / "empty_metrics.csv"
        success = collector.export_to_csv(csv_file)

        assert success is True
        assert csv_file.exists()

        # Should create empty CSV with headers
        with Path(csv_file).open() as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 0
        assert "operation_type" in reader.fieldnames
        assert "query" in reader.fieldnames

    def test_csv_export_error_handling(self) -> None:
        """Test CSV export error handling with invalid path."""
        collector = MetricsCollector()

        # Try to export to a path that doesn't exist and can't be created
        invalid_path = Path("/invalid/path/that/does/not/exist.csv")
        success = collector.export_to_csv(invalid_path)

        assert success is False
