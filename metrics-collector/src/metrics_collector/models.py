"""Data models for metrics-collector module."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class SearchResult:
    """Search result data model matching search-engine module specification."""

    query: str
    results: list[dict[str, Any]]
    result_count: int
    execution_time_ms: float
    relevance_scores: list[float]
    success: bool
    error_message: str | None = None


@dataclass
class ConversationResult:
    """Conversation result data model for answer-service integration."""

    query: str
    answer: str
    response_time_ms: float
    success: bool
    error_message: str | None = None
    context_used: bool = True


@dataclass
class PerformanceMetrics:
    """Performance metrics data model as specified in Stream 4."""

    operation_type: str  # 'search' or 'conversation'
    total_operations: int
    success_rate: float
    avg_response_time_ms: float
    median_response_time_ms: float
    p95_response_time_ms: float
    error_count: int
    timestamp: datetime
