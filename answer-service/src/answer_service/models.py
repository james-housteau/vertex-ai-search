"""Data models for Answer Service."""

from dataclasses import dataclass


@dataclass
class ConversationResult:
    """Result of conversation query containing answer and metadata."""

    query: str
    answer: str
    confidence_score: float
    sources: list[str]
    conversation_id: str
    response_time_ms: float
    success: bool
    error_message: str | None = None
