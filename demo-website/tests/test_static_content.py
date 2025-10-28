"""Tests for static content functionality."""

from pathlib import Path

import pytest


@pytest.fixture
def static_dir() -> Path:
    """Get static directory path."""
    return Path(__file__).parent.parent / "src" / "demo_website" / "static"


def test_index_html_exists(static_dir: Path) -> None:
    """Test index.html file exists."""
    index_file = static_dir / "index.html"
    assert index_file.exists()


def test_index_html_has_search_interface(static_dir: Path) -> None:
    """Test index.html contains search interface elements."""
    index_file = static_dir / "index.html"
    content = index_file.read_text()
    assert "search" in content.lower()
    assert "input" in content.lower()
    assert "button" in content.lower()


def test_css_file_exists(static_dir: Path) -> None:
    """Test style.css file exists."""
    css_file = static_dir / "style.css"
    assert css_file.exists()


def test_css_has_responsive_design(static_dir: Path) -> None:
    """Test CSS includes responsive design."""
    css_file = static_dir / "style.css"
    content = css_file.read_text()
    # Should have media queries for responsive design
    assert "@media" in content.lower()


def test_js_file_exists(static_dir: Path) -> None:
    """Test app.js file exists."""
    js_file = static_dir / "app.js"
    assert js_file.exists()


def test_js_has_fetch_api_calls(static_dir: Path) -> None:
    """Test JavaScript uses fetch API."""
    js_file = static_dir / "app.js"
    content = js_file.read_text()
    assert "fetch" in content.lower()


def test_js_handles_search_endpoint(static_dir: Path) -> None:
    """Test JavaScript handles /search endpoint."""
    js_file = static_dir / "app.js"
    content = js_file.read_text()
    assert "/search" in content


def test_js_handles_summarize_endpoint(static_dir: Path) -> None:
    """Test JavaScript handles /summarize endpoint."""
    js_file = static_dir / "app.js"
    content = js_file.read_text()
    assert "/summarize" in content


def test_js_handles_sse_streaming(static_dir: Path) -> None:
    """Test JavaScript handles SSE streaming."""
    js_file = static_dir / "app.js"
    content = js_file.read_text()
    # Should use EventSource or handle streaming
    assert "eventsource" in content.lower() or "stream" in content.lower()
