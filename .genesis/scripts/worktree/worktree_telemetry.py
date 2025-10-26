#!/usr/bin/env python3
"""
Redirect agent telemetry to worktree for issue-specific debugging.
All telemetry goes to worktrees/solve-{issue}/.solve/telemetry/
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from genesis.core.constants import PathDefaults
except ImportError:
    # Fallback if genesis.core is not available
    class PathDefaults:
        UNIX_PATH_SEPARATOR = "/"


class WorktreeTelemetry:
    """Output telemetry directly to worktree instead of terminal."""

    def __init__(self, issue_number: int | None = None):
        self.issue_number = issue_number or self._detect_issue()
        self.worktree_path = Path(f"worktrees/solve-{self.issue_number}")
        self.telemetry_dir = self.worktree_path / ".solve" / "telemetry"
        self.telemetry_dir.mkdir(parents=True, exist_ok=True)

        # Separate files for easy debugging
        self.files = {
            "tools": self.telemetry_dir / "tools.jsonl",
            "phases": self.telemetry_dir / "phases.jsonl",
            "errors": self.telemetry_dir / "errors.jsonl",
            "tokens": self.telemetry_dir / "tokens.jsonl",
            "all": self.telemetry_dir / "debug.jsonl",
        }

        # Write header to indicate start
        self._write_header()

    def _detect_issue(self) -> int:
        """Auto-detect issue from worktree path."""
        cwd = Path.cwd()
        if "solve-" in str(cwd):
            parts = str(cwd).split("solve-")
            if len(parts) > 1:
                issue_str = parts[-1].split(PathDefaults.UNIX_PATH_SEPARATOR)[0]
                return int(issue_str)
        return 0

    def _write_header(self):
        """Write session header."""
        header = {
            "event": "session_start",
            "timestamp": datetime.now().isoformat(),
            "issue": self.issue_number,
            "worktree": str(self.worktree_path),
        }
        with open(self.files["all"], "a") as f:
            f.write(json.dumps(header) + "\n")

    def log_tool(
        self, tool_name: str, success: bool, duration_ms: int, error: str | None = None
    ):
        """Log tool usage."""
        event = {
            "event": "tool_use",
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "success": success,
            "duration_ms": duration_ms,
        }
        if error:
            event["error"] = error

        self._write_event(event, ["tools", "all"])
        if error:
            self._write_event(event, ["errors"])

    def log_phase(
        self,
        phase: str,
        status: str,
        agent: str | None = None,
        validation: str | None = None,
    ):
        """Log phase event."""
        event = {
            "event": f"phase_{status}",
            "timestamp": datetime.now().isoformat(),
            "phase": phase,
            "status": status,
        }
        if agent:
            event["agent"] = agent
        if validation:
            event["validation"] = validation

        self._write_event(event, ["phases", "all"])

    def log_tokens(
        self, input_tokens: int, output_tokens: int, cache_tokens: int | None = None
    ):
        """Log token usage without cost."""
        event = {
            "event": "token_usage",
            "timestamp": datetime.now().isoformat(),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total": input_tokens + output_tokens,
        }
        if cache_tokens:
            event["cache_tokens"] = cache_tokens

        self._write_event(event, ["tokens", "all"])

    def log_error(self, error: str, phase: str | None = None):
        """Log error event."""
        event = {
            "event": "error",
            "timestamp": datetime.now().isoformat(),
            "error": error,
        }
        if phase:
            event["phase"] = phase

        self._write_event(event, ["errors", "all"])

    def _write_event(self, event: dict[str, Any], file_keys: list):
        """Write event to specified files."""
        for key in file_keys:
            if key in self.files:
                with open(self.files[key], "a") as f:
                    f.write(json.dumps(event) + "\n")

    def analyze(self) -> dict[str, Any]:
        """Quick analysis of telemetry data."""
        analysis = {"issue": self.issue_number, "summary": {}}

        # Count events in each file
        for name, path in self.files.items():
            if path.exists():
                count = sum(1 for _ in open(path))
                analysis["summary"][name] = count

        # Analyze errors if any
        if self.files["errors"].exists():
            errors = []
            with open(self.files["errors"]) as f:
                for line in f:
                    event = json.loads(line)
                    errors.append(event.get("error", "Unknown"))
            analysis["errors"] = errors[:5]  # First 5 errors

        # Token usage
        if self.files["tokens"].exists():
            total_input = 0
            total_output = 0
            with open(self.files["tokens"]) as f:
                for line in f:
                    event = json.loads(line)
                    total_input += event.get("input_tokens", 0)
                    total_output += event.get("output_tokens", 0)
            analysis["tokens"] = {
                "input": total_input,
                "output": total_output,
                "total": total_input + total_output,
            }

        return analysis


# Integration point for SOLVE pipeline
def enable_worktree_telemetry(issue_number: int) -> WorktreeTelemetry:
    """Enable telemetry output to worktree for an issue."""
    wt = WorktreeTelemetry(issue_number)

    # Set environment variable to signal telemetry redirect
    os.environ["TELEMETRY_OUTPUT"] = "worktree"
    os.environ["TELEMETRY_WORKTREE_PATH"] = str(wt.telemetry_dir)

    print(f"✅ Telemetry redirected to: {wt.telemetry_dir}")
    return wt


if __name__ == "__main__":
    # Quick test
    import sys

    if len(sys.argv) > 1:
        issue = int(sys.argv[1])
        wt = enable_worktree_telemetry(issue)

        # Log some test events
        wt.log_tool("Read", True, 45)
        wt.log_phase("scaffold", "start", "scaffold-agent")
        wt.log_tokens(1500, 200, 88000)
        wt.log_error("Agent misunderstood issue", "scaffold")
        wt.log_phase("scaffold", "failed", "scaffold-agent", "validation_failed")

        # Show analysis
        print(json.dumps(wt.analyze(), indent=2))
    else:
        print("Usage: python worktree_telemetry.py <issue_number>")
