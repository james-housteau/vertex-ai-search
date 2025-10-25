"""Integration tests for Answer Service."""

from unittest.mock import Mock, patch

from answer_service.service import AnswerService


class TestAnswerServiceIntegration:
    """Integration tests for Answer Service with mocked Google Cloud services."""

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_complete_conversation_flow(self, mock_client_class):
        """Test complete conversation flow from start to finish."""
        # Mock the client
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Initialize service
        service = AnswerService(project_id="integration-test", conversation_id="")

        # Start conversation
        conversation_id = service.start_conversation()
        assert conversation_id.startswith("conv-")

        # Ask multiple questions
        result1 = service.ask_question("What is machine learning?")
        result2 = service.ask_question("How does it work?")
        result3 = service.ask_question("What are the applications?")

        # Verify all questions succeeded
        assert result1.success is True
        assert result2.success is True
        assert result3.success is True

        # Verify conversation ID consistency
        assert result1.conversation_id == conversation_id
        assert result2.conversation_id == conversation_id
        assert result3.conversation_id == conversation_id

        # Get conversation history
        history = service.get_conversation_history(conversation_id)
        assert len(history) == 3
        assert history[0].query == "What is machine learning?"
        assert history[1].query == "How does it work?"
        assert history[2].query == "What are the applications?"

        # End conversation
        success = service.end_conversation(conversation_id)
        assert success is True

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_parallel_conversations(self, mock_client_class):
        """Test handling multiple parallel conversations."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Create two separate services
        service1 = AnswerService(project_id="test-project", conversation_id="")
        service2 = AnswerService(project_id="test-project", conversation_id="")

        # Start separate conversations
        conv_id1 = service1.start_conversation()
        conv_id2 = service2.start_conversation()

        assert conv_id1 != conv_id2

        # Ask questions in each conversation
        result1 = service1.ask_question("Question in conversation 1")
        result2 = service2.ask_question("Question in conversation 2")

        # Verify isolation
        assert result1.conversation_id == conv_id1
        assert result2.conversation_id == conv_id2

        # Verify history isolation
        history1 = service1.get_conversation_history(conv_id1)
        history2 = service2.get_conversation_history(conv_id2)

        assert len(history1) == 1
        assert len(history2) == 1
        assert history1[0].query == "Question in conversation 1"
        assert history2[0].query == "Question in conversation 2"

        # Verify cross-conversation access fails
        assert service1.get_conversation_history(conv_id2) == []
        assert service2.get_conversation_history(conv_id1) == []

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_conversation_context_handling(self, mock_client_class):
        """Test that conversation context is properly maintained."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        service = AnswerService(project_id="context-test", conversation_id="")
        conversation_id = service.start_conversation()

        # First question establishes context
        result1 = service.ask_question(
            "Tell me about Python", context="Programming languages"
        )

        # Follow-up question should maintain context
        result2 = service.ask_question("What are its main features?")

        # Third question with different context
        result3 = service.ask_question(
            "How fast is it?", context="Performance comparison"
        )

        assert result1.success is True
        assert result2.success is True
        assert result3.success is True

        # All should be in same conversation
        assert result1.conversation_id == conversation_id
        assert result2.conversation_id == conversation_id
        assert result3.conversation_id == conversation_id

        # History should show all questions
        history = service.get_conversation_history(conversation_id)
        assert len(history) == 3

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_error_recovery_and_continuation(self, mock_client_class):
        """Test conversation continues after an error."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        service = AnswerService(project_id="error-test", conversation_id="")
        conversation_id = service.start_conversation()

        # First question succeeds
        result1 = service.ask_question("Good question")
        assert result1.success is True

        # Simulate an error in service for next question
        with patch.object(
            service, "_generate_answer", side_effect=Exception("Mock error")
        ):
            result2 = service.ask_question("Question that will fail")

        assert result2.success is False
        assert "Mock error" in result2.error_message

        # Third question should work again
        result3 = service.ask_question("Recovery question")
        assert result3.success is True

        # History should include all attempts
        history = service.get_conversation_history(conversation_id)
        assert len(history) == 3
        assert history[0].success is True
        assert history[1].success is False
        assert history[2].success is True

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_conversation_metrics_consistency(self, mock_client_class):
        """Test that conversation metrics are consistent and realistic."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        service = AnswerService(project_id="metrics-test", conversation_id="")
        conversation_id = service.start_conversation()

        # Ask multiple questions and check metrics
        questions = [
            "Short?",
            "What is a medium length question about technology?",
            "This is a very long and detailed question that should demonstrate how the system handles complex queries with multiple components and clauses that require comprehensive analysis and processing time measurements?",
        ]

        results = []
        for question in questions:
            result = service.ask_question(question)
            results.append(result)

        # Verify metrics consistency
        for result in results:
            assert result.response_time_ms > 0
            assert 0.0 <= result.confidence_score <= 1.0
            assert isinstance(result.sources, list)
            assert result.conversation_id == conversation_id

        # Verify confidence trends (longer questions should have higher confidence)
        short_confidence = results[0].confidence_score
        medium_confidence = results[1].confidence_score
        long_confidence = results[2].confidence_score

        assert (
            long_confidence >= medium_confidence >= short_confidence
        )  # Detailed question should have high confidence

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_conversation_cleanup_on_end(self, mock_client_class):
        """Test that conversation is properly cleaned up when ended."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        service = AnswerService(project_id="cleanup-test", conversation_id="")
        conversation_id = service.start_conversation()

        # Add some conversation history
        service.ask_question("Question 1")
        service.ask_question("Question 2")

        # Verify history exists
        history_before = service.get_conversation_history(conversation_id)
        assert len(history_before) == 2

        # End conversation
        success = service.end_conversation(conversation_id)
        assert success is True

        # History should still be accessible after ending
        history_after = service.get_conversation_history(conversation_id)
        assert len(history_after) == 2  # History preserved

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_large_conversation_handling(self, mock_client_class):
        """Test handling of conversations with many questions."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        service = AnswerService(project_id="large-test", conversation_id="")
        conversation_id = service.start_conversation()

        # Ask many questions
        num_questions = 20
        for i in range(num_questions):
            result = service.ask_question(f"Question number {i + 1}")
            assert result.success is True
            assert result.conversation_id == conversation_id

        # Verify complete history
        history = service.get_conversation_history(conversation_id)
        assert len(history) == num_questions

        # Verify order preservation
        for i, result in enumerate(history):
            assert result.query == f"Question number {i + 1}"

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_google_cloud_error_simulation(self, mock_client_class):
        """Test handling of Google Cloud specific errors."""
        # Use a generic Exception since google.cloud.exceptions is not available
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        service = AnswerService(project_id="error-sim", conversation_id="test-conv")

        # Simulate Google Cloud error during question processing
        with patch.object(
            service, "_generate_answer", side_effect=Exception("Quota exceeded")
        ):
            result = service.ask_question("Question that triggers GCP error")

        assert result.success is False
        # Update expectation since we're using a generic exception
        assert "error" in result.error_message.lower()
        assert "Quota exceeded" in result.error_message
        assert result.response_time_ms > 0  # Time should still be measured

    @patch("answer_service.service.ConversationalSearchServiceClient")
    def test_unicode_and_special_characters(self, mock_client_class):
        """Test handling of unicode and special characters."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        service = AnswerService(project_id="unicode-test", conversation_id="")
        conversation_id = service.start_conversation()

        # Test various unicode questions
        unicode_questions = [
            "¿Qué es la inteligencia artificial?",
            "什么是机器学习?",
            "Что такое нейронные сети?",
            "How about émojis 🤖 and spëcial çhars?",
        ]

        for question in unicode_questions:
            result = service.ask_question(question)
            assert result.success is True
            assert result.query == question
            assert result.conversation_id == conversation_id

        # Verify history preserves unicode
        history = service.get_conversation_history(conversation_id)
        assert len(history) == len(unicode_questions)
        for i, result in enumerate(history):
            assert result.query == unicode_questions[i]
