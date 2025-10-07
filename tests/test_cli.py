"""Tests for CLI commands."""

import pytest
from click.testing import CliRunner

from vertex_ai_search.cli import cli

@pytest.fixture
def runner() -> CliRunner:
    """Create CLI test runner."""
    return CliRunner()

def test_cli_help(runner: CliRunner) -> None:
    """Test CLI help command."""
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'A vertex-ai-search project created with Genesis' in result.output

def test_hello_command(runner: CliRunner) -> None:
    """Test hello command."""
    result = runner.invoke(cli, ['hello'])
    assert result.exit_code == 0
    assert 'Hello World!' in result.output

def test_hello_with_name(runner: CliRunner) -> None:
    """Test hello command with custom name."""
    result = runner.invoke(cli, ['hello', '--name', 'Alice'])
    assert result.exit_code == 0
    assert 'Hello Alice!' in result.output

def test_hello_with_count(runner: CliRunner) -> None:
    """Test hello command with count option."""
    result = runner.invoke(cli, ['hello', '--count', '3'])
    assert result.exit_code == 0
    assert result.output.count('Hello World!') == 3

def test_display_command(runner: CliRunner) -> None:
    """Test display command."""
    result = runner.invoke(cli, ['display', 'Test message'])
    assert result.exit_code == 0
    assert 'Test message' in result.output

def test_display_with_style(runner: CliRunner) -> None:
    """Test display command with different styles."""
    styles = ['info', 'success', 'warning', 'error']

    for style in styles:
        result = runner.invoke(cli, ['display', 'Test', '--style', style])
        assert result.exit_code == 0
        assert 'Test' in result.output

def test_status_command(runner: CliRunner) -> None:
    """Test status command."""
    result = runner.invoke(cli, ['status'])
    assert result.exit_code == 0
    assert 'vertex-ai-search is running!' in result.output
    assert 'Version: 0.1.0' in result.output

def test_invalid_command(runner: CliRunner) -> None:
    """Test invalid command returns error."""
    result = runner.invoke(cli, ['invalid'])
    assert result.exit_code != 0
