"""Unit tests for Answer Service implementation."""

from unittest.mock import Mock, patch

from answer_service.models import ConversationResult
from answer_service.service import AnswerService


class TestAnswerService:
    """Unit tests for AnswerService class."""

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_service_initialization(self, mock_client_class):
        """Test service initialization."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        service = AnswerService(project_id="test-project", conversation_id="test-conv")

        assert service.project_id == "test-project"
        assert service.conversation_id == "test-conv"
        assert service.client == mock_client
        assert service._conversation_history == []

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_service_initialization_client_error(self, mock_client_class):
        """Test service initialization with client error."""
        mock_client_class.side_effect = Exception("Client creation failed")

        service = AnswerService(project_id="test-project", conversation_id="test-conv")

        assert service.client is None
        assert hasattr(service, "_client_error")
        assert "Client creation failed" in service._client_error

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_ask_question_basic(self, mock_client_class):
        """Test basic question asking functionality."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        service = AnswerService(project_id="test-project", conversation_id="test-conv")
        result = service.ask_question("What is Python?")

        assert isinstance(result, ConversationResult)
        assert result.query == "What is Python?"
        assert result.success is True
        assert result.answer != ""
        assert result.conversation_id == "test-conv"
        assert result.response_time_ms > 0

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_ask_question_with_context(self, mock_client_class):
        """Test asking question with context."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        service = AnswerService(project_id="test-project", conversation_id="test-conv")
        result = service.ask_question(
            question="What are the benefits?", context="Programming languages"
        )

        assert result.success is True
        assert result.query == "What are the benefits?"

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_ask_question_client_error(self, mock_client_class):
        """Test question asking with client initialization error."""
        mock_client_class.side_effect = Exception("Client error")

        service = AnswerService(project_id="test-project", conversation_id="test-conv")
        result = service.ask_question("Test question")

        assert result.success is False
        assert result.error_message is not None
        assert "Client error" in result.error_message

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_start_conversation(self, mock_client_class):
        """Test starting a new conversation."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        service = AnswerService(project_id="test-project", conversation_id="")
        conversation_id = service.start_conversation()

        assert isinstance(conversation_id, str)
        assert len(conversation_id) > 0
        assert conversation_id.startswith("conv-")
        assert service.conversation_id == conversation_id
        assert service._conversation_history == []

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_end_conversation_success(self, mock_client_class):
        """Test successfully ending a conversation."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        service = AnswerService(project_id="test-project", conversation_id="test-conv")
        success = service.end_conversation("test-conv")

        assert success is True

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_end_conversation_wrong_id(self, mock_client_class):
        """Test ending conversation with wrong ID."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        service = AnswerService(project_id="test-project", conversation_id="test-conv")
        success = service.end_conversation("wrong-conv")

        assert success is False

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_get_conversation_history_empty(self, mock_client_class):
        """Test getting empty conversation history."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        service = AnswerService(project_id="test-project", conversation_id="test-conv")
        history = service.get_conversation_history("test-conv")

        assert isinstance(history, list)
        assert len(history) == 0

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_get_conversation_history_with_questions(self, mock_client_class):
        """Test getting conversation history after asking questions."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        service = AnswerService(project_id="test-project", conversation_id="test-conv")

        # Ask a couple of questions
        service.ask_question("First question")
        service.ask_question("Second question")

        history = service.get_conversation_history("test-conv")

        assert len(history) == 2
        assert history[0].query == "First question"
        assert history[1].query == "Second question"
        assert all(isinstance(item, ConversationResult) for item in history)

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_get_conversation_history_wrong_id(self, mock_client_class):
        """Test getting conversation history with wrong ID."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        service = AnswerService(project_id="test-project", conversation_id="test-conv")
        service.ask_question("Test question")

        history = service.get_conversation_history("wrong-conv")

        assert isinstance(history, list)
        assert len(history) == 0

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_mock_answer_generation(self, mock_client_class):
        """Test mock answer generation for different question types."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        service = AnswerService(project_id="test-project", conversation_id="test-conv")

        # Test machine learning question
        result_ml = service.ask_question("What is machine learning?")
        assert "machine learning" in result_ml.answer.lower()

        # Test Python question
        result_python = service.ask_question("What is Python?")
        assert "python" in result_python.answer.lower()

        # Test AI question
        result_ai = service.ask_question("What is artificial intelligence?")
        assert "artificial intelligence" in result_ai.answer.lower()

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_mock_confidence_calculation(self, mock_client_class):
        """Test mock confidence score calculation."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        service = AnswerService(project_id="test-project", conversation_id="test-conv")

        # Test long detailed question (should have high confidence)
        long_question = "What is machine learning and how does it differ from traditional programming approaches?"
        result_long = service.ask_question(long_question)
        assert result_long.confidence_score >= 0.9

        # Test proper question with question mark
        result_proper = service.ask_question("What is AI?")
        assert result_proper.confidence_score >= 0.8

        # Test very short question
        result_short = service.ask_question("AI?")
        assert result_short.confidence_score < 0.8

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_mock_sources_extraction(self, mock_client_class):
        """Test mock sources extraction for different question types."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        service = AnswerService(project_id="test-project", conversation_id="test-conv")

        # Test AI/ML question sources
        result_ai = service.ask_question("What is machine learning?")
        assert len(result_ai.sources) > 0
        assert any(
            "ai" in source.lower() or "ml" in source.lower()
            for source in result_ai.sources
        )

        # Test Python question sources
        result_python = service.ask_question("How to use Python?")
        assert len(result_python.sources) > 0
        assert any("python" in source.lower() for source in result_python.sources)

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_response_time_measurement(self, mock_client_class):
        """Test that response time is properly measured."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        service = AnswerService(project_id="test-project", conversation_id="test-conv")
        result = service.ask_question("Test question")

        assert result.response_time_ms > 0
        assert isinstance(result.response_time_ms, int | float)

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_conversation_history_isolation(self, mock_client_class):
        """Test that conversation histories are isolated by conversation ID."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Create two services with different conversation IDs
        service1 = AnswerService(project_id="test-project", conversation_id="conv-1")
        service2 = AnswerService(project_id="test-project", conversation_id="conv-2")

        # Ask questions in each service
        service1.ask_question("Question in conv-1")
        service2.ask_question("Question in conv-2")

        # Check that histories are isolated
        history1 = service1.get_conversation_history("conv-1")
        history2 = service2.get_conversation_history("conv-2")

        assert len(history1) == 1
        assert len(history2) == 1
        assert history1[0].query == "Question in conv-1"
        assert history2[0].query == "Question in conv-2"

        # Check cross-conversation access returns empty
        assert service1.get_conversation_history("conv-2") == []
        assert service2.get_conversation_history("conv-1") == []
