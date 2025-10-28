"""Tests for real-time performance metrics UI functionality."""

from pathlib import Path

import pytest


@pytest.fixture
def static_dir() -> Path:
    """Get static directory path."""
    return Path(__file__).parent.parent / "src" / "demo_website" / "static"


def test_js_has_speed_badge_function(static_dir: Path) -> None:
    """Test JavaScript includes speed badge calculation logic."""
    js_file = static_dir / "app.js"
    content = js_file.read_text()
    # Should have getSpeedBadge function
    assert "getSpeedBadge" in content
    assert "speed-badge" in content


def test_js_has_cache_indicator_logic(static_dir: Path) -> None:
    """Test JavaScript includes cache hit/miss indicator logic."""
    js_file = static_dir / "app.js"
    content = js_file.read_text()
    # Should have getCacheIndicator function
    assert "getCacheIndicator" in content
    assert "cache-indicator" in content


def test_js_speed_badge_performance_tiers(static_dir: Path) -> None:
    """Test JavaScript implements correct performance tier logic."""
    js_file = static_dir / "app.js"
    content = js_file.read_text()
    # Should have Lightning Fast (<50ms), Super Quick (<100ms), Fast (<120ms)
    assert "Lightning Fast" in content
    assert "Super Quick" in content
    assert "Fast" in content


def test_js_metadata_uses_speed_badge(static_dir: Path) -> None:
    """Test JavaScript integrates speed badge into metadata display."""
    js_file = static_dir / "app.js"
    content = js_file.read_text()
    # Should call getSpeedBadge with search_time_ms
    assert "getSpeedBadge(metadata" in content or "getSpeedBadge(metadata?" in content


def test_js_metadata_uses_cache_indicator(static_dir: Path) -> None:
    """Test JavaScript integrates cache indicator into metadata display."""
    js_file = static_dir / "app.js"
    content = js_file.read_text()
    # Should call getCacheIndicator with cache_hit
    assert (
        "getCacheIndicator(metadata" in content
        or "getCacheIndicator(metadata?" in content
    )


def test_css_has_speed_badge_styles(static_dir: Path) -> None:
    """Test CSS includes speed badge styling classes."""
    css_file = static_dir / "style.css"
    content = css_file.read_text()
    # Should have speed-badge class
    assert ".speed-badge" in content


def test_css_has_badge_tier_styles(static_dir: Path) -> None:
    """Test CSS includes all three badge tier styles."""
    css_file = static_dir / "style.css"
    content = css_file.read_text()
    # Should have lightning, super, and fast badge styles
    assert ".badge-lightning" in content
    assert ".badge-super" in content
    assert ".badge-fast" in content


def test_css_has_cache_indicator_styles(static_dir: Path) -> None:
    """Test CSS includes cache indicator styling classes."""
    css_file = static_dir / "style.css"
    content = css_file.read_text()
    # Should have cache-indicator class
    assert ".cache-indicator" in content


def test_css_has_cache_hit_miss_styles(static_dir: Path) -> None:
    """Test CSS includes cache hit and miss styles."""
    css_file = static_dir / "style.css"
    content = css_file.read_text()
    # Should have cache-hit and cache-miss classes
    assert ".cache-hit" in content
    assert ".cache-miss" in content


def test_css_has_performance_tier_colors(static_dir: Path) -> None:
    """Test CSS includes performance tier colors (gold, blue, green)."""
    css_file = static_dir / "style.css"
    content = css_file.read_text()
    # Should have colors for different performance tiers
    # Google colors: blue #4285f4, green #1e8e3e, gold #f9ab00
    has_blue = "#4285f4" in content
    has_green = "#1e8e3e" in content
    has_gold = "#f9ab00" in content
    assert has_blue and has_green and has_gold
