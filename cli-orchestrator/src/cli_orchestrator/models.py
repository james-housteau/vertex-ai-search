"""Data models for orchestrator."""

from dataclasses import dataclass


@dataclass
class ExecutionResult:
    """Result of a command execution."""

    task: str
    success: bool
    duration: float
    output: str = ""
    error: str = ""
