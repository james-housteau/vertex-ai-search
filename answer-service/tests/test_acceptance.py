"""
TDD RED PHASE - Acceptance tests for Answer Service API contract.

These tests define the expected behavior and will initially fail.
They serve as the specification for the Answer Service implementation.
"""

from unittest.mock import patch

import pytest

# Import the API contract types that we need to implement
from answer_service.models import ConversationResult
from answer_service.service import AnswerService


class TestAnswerServiceAcceptance:
    """Acceptance tests defining the complete API contract."""

    def test_ask_question_success(self):
        """Test successful question asking with proper response."""
        with patch("answer_service.service.ConversationalSearchServiceClient"):
            service = AnswerService(
                project_id="test-project", conversation_id="test-conv"
            )

            result = service.ask_question(
                question="What is machine learning?", context="Technical documentation"
            )

            # Verify expected behavior
            assert isinstance(result, ConversationResult)
            assert result.query == "What is machine learning?"
            assert result.answer != ""
            assert 0.0 <= result.confidence_score <= 1.0
            assert isinstance(result.sources, list)
            assert result.conversation_id == "test-conv"
            assert result.response_time_ms > 0
            assert result.success is True
            assert result.error_message is None

    def test_ask_question_without_context(self):
        """Test question asking without additional context."""
        with patch("answer_service.service.ConversationalSearchServiceClient"):
            service = AnswerService(
                project_id="test-project", conversation_id="test-conv"
            )

            result = service.ask_question(question="What is AI?")

            assert result.success is True
            assert result.query == "What is AI?"
            assert result.answer != ""

    def test_start_conversation(self):
        """Test starting a new conversation session."""
        with patch("answer_service.service.ConversationalSearchServiceClient"):
            service = AnswerService(project_id="test-project", conversation_id="")

            conversation_id = service.start_conversation()

            assert conversation_id != ""
            assert isinstance(conversation_id, str)
            assert len(conversation_id) > 0

    def test_end_conversation(self):
        """Test ending a conversation session."""
        with patch("answer_service.service.ConversationalSearchServiceClient"):
            service = AnswerService(
                project_id="test-project", conversation_id="test-conv"
            )

            success = service.end_conversation("test-conv")

            assert success is True

    def test_get_conversation_history(self):
        """Test retrieving conversation history."""
        with patch("answer_service.service.ConversationalSearchServiceClient"):
            service = AnswerService(
                project_id="test-project", conversation_id="test-conv"
            )

            # Ask a question first
            service.ask_question("What is Python?")

            history = service.get_conversation_history("test-conv")

            assert isinstance(history, list)
            assert len(history) >= 0
            if history:
                assert isinstance(history[0], ConversationResult)

    def test_conversation_result_data_structure(self):
        """Test that ConversationResult has all required fields."""
        result = ConversationResult(
            query="test query",
            answer="test answer",
            confidence_score=0.85,
            sources=["source1", "source2"],
            conversation_id="conv-123",
            response_time_ms=150.5,
            success=True,
        )

        assert result.query == "test query"
        assert result.answer == "test answer"
        assert result.confidence_score == 0.85
        assert result.sources == ["source1", "source2"]
        assert result.conversation_id == "conv-123"
        assert result.response_time_ms == 150.5
        assert result.success is True
        assert result.error_message is None

    def test_conversation_result_with_error(self):
        """Test ConversationResult with error state."""
        result = ConversationResult(
            query="test query",
            answer="",
            confidence_score=0.0,
            sources=[],
            conversation_id="conv-123",
            response_time_ms=50.0,
            success=False,
            error_message="Connection failed",
        )

        assert result.success is False
        assert result.error_message == "Connection failed"

    def test_service_initialization(self):
        """Test AnswerService initialization with required parameters."""
        with patch("answer_service.service.ConversationalSearchServiceClient"):
            service = AnswerService(
                project_id="test-project", conversation_id="test-conv"
            )

            assert hasattr(service, "ask_question")
            assert hasattr(service, "start_conversation")
            assert hasattr(service, "end_conversation")
            assert hasattr(service, "get_conversation_history")

    def test_multiple_questions_in_conversation(self):
        """Test asking multiple questions in the same conversation."""
        with patch("answer_service.service.ConversationalSearchServiceClient"):
            service = AnswerService(
                project_id="test-project", conversation_id="test-conv"
            )

            result1 = service.ask_question("What is AI?")
            result2 = service.ask_question("How does machine learning work?")

            assert result1.success is True
            assert result2.success is True
            assert result1.conversation_id == result2.conversation_id

    def test_conversation_context_persistence(self):
        """Test that conversation context is maintained across questions."""
        with patch("answer_service.service.ConversationalSearchServiceClient"):
            service = AnswerService(
                project_id="test-project", conversation_id="test-conv"
            )

            # First question establishes context
            result1 = service.ask_question("What is Python?")

            # Second question should use context from first
            result2 = service.ask_question("What are its main features?")

            assert result1.success is True
            assert result2.success is True
            assert result1.conversation_id == result2.conversation_id

    def test_error_handling_invalid_project(self):
        """Test error handling for invalid project ID."""
        with patch(
            "answer_service.service.ConversationalSearchServiceClient"
        ) as mock_client:
            mock_client.side_effect = Exception("Invalid project")

            service = AnswerService(
                project_id="invalid-project", conversation_id="test-conv"
            )
            result = service.ask_question("test question")

            assert result.success is False
            assert result.error_message is not None
            assert (
                "Invalid project" in result.error_message or result.error_message != ""
            )

    def test_confidence_score_range(self):
        """Test that confidence scores are within valid range."""
        with patch("answer_service.service.ConversationalSearchServiceClient"):
            service = AnswerService(
                project_id="test-project", conversation_id="test-conv"
            )

            result = service.ask_question("What is the weather?")

            if result.success:
                assert 0.0 <= result.confidence_score <= 1.0

    def test_response_time_measurement(self):
        """Test that response time is properly measured."""
        with patch("answer_service.service.ConversationalSearchServiceClient"):
            service = AnswerService(
                project_id="test-project", conversation_id="test-conv"
            )

            result = service.ask_question("Quick question")

            if result.success:
                assert result.response_time_ms > 0
                assert isinstance(result.response_time_ms, int | float)

    def test_sources_list_format(self):
        """Test that sources are returned as a proper list."""
        with patch("answer_service.service.ConversationalSearchServiceClient"):
            service = AnswerService(
                project_id="test-project", conversation_id="test-conv"
            )

            result = service.ask_question("Question with sources")

            assert isinstance(result.sources, list)
            if result.sources:
                assert all(isinstance(source, str) for source in result.sources)
