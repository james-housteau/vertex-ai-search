"""MetricsCollector implementation for performance metrics collection and analysis."""

import csv
import json
import statistics
import threading
from datetime import UTC, datetime
from pathlib import Path

from .models import ConversationResult, PerformanceMetrics, SearchResult


class MetricsCollector:
    """Thread-safe metrics collector for search and conversation operations."""

    def __init__(self, output_dir: Path = Path("./metrics")) -> None:
        """Initialize metrics collector with output directory."""
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Thread-safe storage for metrics
        self._lock = threading.Lock()
        self._search_metrics: list[SearchResult] = []
        self._conversation_metrics: list[ConversationResult] = []

    def record_search_metric(self, search_result: SearchResult) -> None:
        """Record a search operation metric in a thread-safe manner."""
        with self._lock:
            self._search_metrics.append(search_result)

    def record_conversation_metric(
        self, conversation_result: ConversationResult
    ) -> None:
        """Record a conversation operation metric in a thread-safe manner."""
        with self._lock:
            self._conversation_metrics.append(conversation_result)

    def generate_report(self) -> PerformanceMetrics:
        """Generate comprehensive performance metrics report."""
        with self._lock:
            all_operations = self._search_metrics + self._conversation_metrics

            if not all_operations:
                return PerformanceMetrics(
                    operation_type="mixed",
                    total_operations=0,
                    success_rate=0.0,
                    avg_response_time_ms=0.0,
                    median_response_time_ms=0.0,
                    p95_response_time_ms=0.0,
                    error_count=0,
                    timestamp=datetime.now(tz=UTC),
                )

            # Calculate statistics
            total_operations = len(all_operations)
            successful_operations = sum(1 for op in all_operations if op.success)
            success_rate = (successful_operations / total_operations) * 100.0
            error_count = total_operations - successful_operations

            # Extract response times
            response_times = []
            for op in all_operations:
                if isinstance(op, SearchResult):
                    response_times.append(op.execution_time_ms)
                else:  # ConversationResult
                    response_times.append(op.response_time_ms)

            # Calculate time statistics
            avg_response_time = (
                statistics.mean(response_times) if response_times else 0.0
            )
            median_response_time = (
                statistics.median(response_times) if response_times else 0.0
            )

            # Calculate p95 (95th percentile)
            if response_times:
                sorted_times = sorted(response_times)
                p95_index = min(int(0.95 * len(sorted_times)), len(sorted_times) - 1)
                p95_response_time = sorted_times[p95_index]
            else:
                p95_response_time = 0.0

            # Determine operation type
            search_count = len(self._search_metrics)
            conversation_count = len(self._conversation_metrics)

            if search_count > 0 and conversation_count > 0:
                operation_type = "mixed"
            elif search_count > 0:
                operation_type = "search"
            elif conversation_count > 0:
                operation_type = "conversation"
            else:
                operation_type = "mixed"

            return PerformanceMetrics(
                operation_type=operation_type,
                total_operations=total_operations,
                success_rate=success_rate,
                avg_response_time_ms=avg_response_time,
                median_response_time_ms=median_response_time,
                p95_response_time_ms=p95_response_time,
                error_count=error_count,
                timestamp=datetime.now(tz=UTC),
            )

    def export_to_json(self, file_path: Path) -> bool:
        """Export metrics data to JSON format."""
        try:
            metrics = self.generate_report()

            # Prepare data for JSON export
            export_data = {
                "export_timestamp": datetime.now(tz=UTC).isoformat(),
                "metrics": {
                    "operation_type": metrics.operation_type,
                    "total_operations": metrics.total_operations,
                    "success_rate": metrics.success_rate,
                    "avg_response_time_ms": metrics.avg_response_time_ms,
                    "median_response_time_ms": metrics.median_response_time_ms,
                    "p95_response_time_ms": metrics.p95_response_time_ms,
                    "error_count": metrics.error_count,
                    "timestamp": metrics.timestamp.isoformat(),
                },
                "raw_data": {
                    "search_operations": len(self._search_metrics),
                    "conversation_operations": len(self._conversation_metrics),
                },
            }

            with Path(file_path).open("w") as f:
                json.dump(export_data, f, indent=2)
        except (OSError, ValueError):
            return False
        else:
            return True

    def export_to_csv(self, file_path: Path) -> bool:
        """Export raw metrics data to CSV format using built-in csv module."""
        try:
            with self._lock:
                # Define all possible fieldnames for both operation types
                fieldnames = [
                    "operation_type",
                    "query",
                    "execution_time_ms",
                    "success",
                    "error_message",
                    "result_count",
                    "relevance_scores_count",
                    "answer",
                    "context_used",
                ]

                with Path(file_path).open("w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()

                    # Add search metrics
                    for metric in self._search_metrics:
                        writer.writerow(
                            {
                                "operation_type": "search",
                                "query": metric.query,
                                "execution_time_ms": metric.execution_time_ms,
                                "success": metric.success,
                                "error_message": metric.error_message,
                                "result_count": metric.result_count,
                                "relevance_scores_count": len(metric.relevance_scores),
                                "answer": None,  # Not applicable for search
                                "context_used": None,  # Not applicable for search
                            }
                        )

                    # Add conversation metrics
                    for conv_metric in self._conversation_metrics:
                        writer.writerow(
                            {
                                "operation_type": "conversation",
                                "query": conv_metric.query,
                                "execution_time_ms": conv_metric.response_time_ms,
                                "success": conv_metric.success,
                                "error_message": conv_metric.error_message,
                                "result_count": None,  # N/A for conversations
                                "relevance_scores_count": None,  # N/A for conversations
                                "answer": conv_metric.answer,
                                "context_used": conv_metric.context_used,
                            }
                        )
        except (OSError, ValueError):
            return False
        else:
            return True
