"""Data models for search-engine module."""

from dataclasses import dataclass
from typing import Any


@dataclass
class SearchResult:
    """Search result data model exactly as specified in Stream 4."""

    query: str
    results: list[dict[str, Any]]
    result_count: int
    execution_time_ms: float
    relevance_scores: list[float]
    success: bool
    error_message: str | None = None
