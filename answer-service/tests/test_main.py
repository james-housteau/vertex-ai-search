"""Tests for Answer Service CLI main module."""

from click.testing import CliRunner
from unittest.mock import patch, Mock

from answer_service.main import main, ask, status
from answer_service.models import ConversationResult


class TestMainCLI:
    """Test the main CLI commands."""

    def test_main_group(self):
        """Test main CLI group is accessible."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Answer Service CLI" in result.output

    def test_status_command(self):
        """Test status command."""
        runner = CliRunner()
        result = runner.invoke(status)

        assert result.exit_code == 0
        assert "Answer Service v0.1.0" in result.output
        assert "Ready for conversation testing" in result.output

    @patch("answer_service.service.AnswerService")
    def test_ask_command_success(self, mock_service_class):
        """Test ask command with successful response."""
        # Mock service and methods
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.start_conversation.return_value = "conv-123"
        mock_service.end_conversation.return_value = True

        # Mock successful result
        mock_result = ConversationResult(
            query="What is Python?",
            answer="Python is a programming language.",
            confidence_score=0.85,
            sources=["https://python.org"],
            conversation_id="conv-123",
            response_time_ms=150.0,
            success=True,
        )
        mock_service.ask_question.return_value = mock_result

        runner = CliRunner()
        result = runner.invoke(
            ask, ["--project-id", "test-project", "--question", "What is Python?"]
        )

        assert result.exit_code == 0
        assert "What is Python?" in result.output
        assert "Python is a programming language." in result.output
        assert "0.85" in result.output
        assert "150.00ms" in result.output
        assert "https://python.org" in result.output

        # Verify service calls
        mock_service_class.assert_called_once_with(
            project_id="test-project", conversation_id=""
        )
        mock_service.start_conversation.assert_called_once()
        mock_service.ask_question.assert_called_once_with(
            question="What is Python?", context=None
        )
        mock_service.end_conversation.assert_called_once_with("conv-123")

    @patch("answer_service.service.AnswerService")
    def test_ask_command_with_context(self, mock_service_class):
        """Test ask command with context parameter."""
        # Mock service and methods
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.start_conversation.return_value = "conv-456"
        mock_service.end_conversation.return_value = True

        # Mock successful result
        mock_result = ConversationResult(
            query="What are the benefits?",
            answer="Benefits include simplicity and readability.",
            confidence_score=0.90,
            sources=["https://example.com/benefits"],
            conversation_id="conv-456",
            response_time_ms=200.0,
            success=True,
        )
        mock_service.ask_question.return_value = mock_result

        runner = CliRunner()
        result = runner.invoke(
            ask,
            [
                "--project-id",
                "test-project",
                "--question",
                "What are the benefits?",
                "--context",
                "Programming languages",
            ],
        )

        assert result.exit_code == 0
        assert "What are the benefits?" in result.output
        assert "Benefits include simplicity" in result.output

        # Verify context was passed
        mock_service.ask_question.assert_called_once_with(
            question="What are the benefits?", context="Programming languages"
        )

    @patch("answer_service.service.AnswerService")
    def test_ask_command_error(self, mock_service_class):
        """Test ask command with error response."""
        # Mock service and methods
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.start_conversation.return_value = "conv-error"
        mock_service.end_conversation.return_value = True

        # Mock error result
        mock_result = ConversationResult(
            query="Failed question",
            answer="",
            confidence_score=0.0,
            sources=[],
            conversation_id="conv-error",
            response_time_ms=50.0,
            success=False,
            error_message="API connection failed",
        )
        mock_service.ask_question.return_value = mock_result

        runner = CliRunner()
        result = runner.invoke(
            ask, ["--project-id", "test-project", "--question", "Failed question"]
        )

        assert result.exit_code == 0
        assert "API connection failed" in result.output

    def test_ask_command_missing_project_id(self):
        """Test ask command with missing required project-id."""
        runner = CliRunner()
        result = runner.invoke(ask, ["--question", "What is Python?"])

        assert result.exit_code != 0
        assert "Missing option" in result.output or "Error" in result.output

    def test_ask_command_missing_question(self):
        """Test ask command with missing required question."""
        runner = CliRunner()
        result = runner.invoke(ask, ["--project-id", "test-project"])

        assert result.exit_code != 0
        assert "Missing option" in result.output or "Error" in result.output

    @patch("answer_service.service.AnswerService")
    def test_ask_command_no_sources(self, mock_service_class):
        """Test ask command when result has no sources."""
        # Mock service and methods
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.start_conversation.return_value = "conv-nosrc"
        mock_service.end_conversation.return_value = True

        # Mock result without sources
        mock_result = ConversationResult(
            query="Simple question",
            answer="Simple answer",
            confidence_score=0.75,
            sources=[],
            conversation_id="conv-nosrc",
            response_time_ms=100.0,
            success=True,
        )
        mock_service.ask_question.return_value = mock_result

        runner = CliRunner()
        result = runner.invoke(
            ask, ["--project-id", "test-project", "--question", "Simple question"]
        )

        assert result.exit_code == 0
        assert "Simple question" in result.output
        assert "Simple answer" in result.output
        assert "0.75" in result.output
        # Sources section should not appear when empty
        assert "Sources:" not in result.output

    @patch("answer_service.service.AnswerService")
    def test_ask_command_multiple_sources(self, mock_service_class):
        """Test ask command with multiple sources."""
        # Mock service and methods
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.start_conversation.return_value = "conv-multi"
        mock_service.end_conversation.return_value = True

        # Mock result with multiple sources
        mock_result = ConversationResult(
            query="Complex question",
            answer="Detailed answer",
            confidence_score=0.95,
            sources=[
                "https://example.com/doc1",
                "https://example.com/doc2",
                "https://example.com/doc3",
            ],
            conversation_id="conv-multi",
            response_time_ms=300.0,
            success=True,
        )
        mock_service.ask_question.return_value = mock_result

        runner = CliRunner()
        result = runner.invoke(
            ask, ["--project-id", "test-project", "--question", "Complex question"]
        )

        assert result.exit_code == 0
        assert "Complex question" in result.output
        assert "Detailed answer" in result.output
        assert "Sources:" in result.output
        assert "https://example.com/doc1" in result.output
        assert "https://example.com/doc2" in result.output
        assert "https://example.com/doc3" in result.output

    def test_main_command_version(self):
        """Test main command version option."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output

    @patch("answer_service.service.AnswerService")
    def test_conversation_lifecycle(self, mock_service_class):
        """Test complete conversation lifecycle in ask command."""
        # Mock service and methods
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.start_conversation.return_value = "conv-lifecycle"
        mock_service.end_conversation.return_value = True

        # Mock successful result
        mock_result = ConversationResult(
            query="Lifecycle test",
            answer="Lifecycle response",
            confidence_score=0.80,
            sources=[],
            conversation_id="conv-lifecycle",
            response_time_ms=120.0,
            success=True,
        )
        mock_service.ask_question.return_value = mock_result

        runner = CliRunner()
        result = runner.invoke(
            ask, ["--project-id", "lifecycle-project", "--question", "Lifecycle test"]
        )

        assert result.exit_code == 0

        # Verify complete lifecycle
        mock_service.start_conversation.assert_called_once()
        mock_service.ask_question.assert_called_once()
        mock_service.end_conversation.assert_called_once_with("conv-lifecycle")
