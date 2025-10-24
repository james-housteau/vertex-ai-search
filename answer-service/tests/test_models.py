"""Tests for Answer Service data models."""

from answer_service.models import ConversationResult


class TestConversationResult:
    """Test ConversationResult data model."""

    def test_conversation_result_creation(self):
        """Test basic ConversationResult creation."""
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
        """Test ConversationResult with error message."""
        result = ConversationResult(
            query="failed query",
            answer="",
            confidence_score=0.0,
            sources=[],
            conversation_id="conv-456",
            response_time_ms=25.0,
            success=False,
            error_message="API connection failed",
        )

        assert result.query == "failed query"
        assert result.answer == ""
        assert result.confidence_score == 0.0
        assert result.sources == []
        assert result.conversation_id == "conv-456"
        assert result.response_time_ms == 25.0
        assert result.success is False
        assert result.error_message == "API connection failed"

    def test_conversation_result_empty_sources(self):
        """Test ConversationResult with empty sources list."""
        result = ConversationResult(
            query="query without sources",
            answer="answer without sources",
            confidence_score=0.70,
            sources=[],
            conversation_id="conv-789",
            response_time_ms=100.0,
            success=True,
        )

        assert result.sources == []
        assert result.success is True

    def test_conversation_result_multiple_sources(self):
        """Test ConversationResult with multiple sources."""
        sources = [
            "https://example.com/doc1",
            "https://example.com/doc2",
            "https://example.com/doc3",
        ]

        result = ConversationResult(
            query="query with multiple sources",
            answer="comprehensive answer",
            confidence_score=0.92,
            sources=sources,
            conversation_id="conv-multi",
            response_time_ms=200.0,
            success=True,
        )

        assert len(result.sources) == 3
        assert "https://example.com/doc1" in result.sources
        assert "https://example.com/doc2" in result.sources
        assert "https://example.com/doc3" in result.sources

    def test_conversation_result_confidence_boundaries(self):
        """Test ConversationResult with boundary confidence values."""
        # Test minimum confidence
        result_min = ConversationResult(
            query="min confidence",
            answer="answer",
            confidence_score=0.0,
            sources=[],
            conversation_id="conv-min",
            response_time_ms=50.0,
            success=True,
        )
        assert result_min.confidence_score == 0.0

        # Test maximum confidence
        result_max = ConversationResult(
            query="max confidence",
            answer="answer",
            confidence_score=1.0,
            sources=[],
            conversation_id="conv-max",
            response_time_ms=50.0,
            success=True,
        )
        assert result_max.confidence_score == 1.0

    def test_conversation_result_response_time_types(self):
        """Test ConversationResult with different response time types."""
        # Test integer response time
        result_int = ConversationResult(
            query="integer time",
            answer="answer",
            confidence_score=0.8,
            sources=[],
            conversation_id="conv-int",
            response_time_ms=100,
            success=True,
        )
        assert result_int.response_time_ms == 100
        assert isinstance(result_int.response_time_ms, int)

        # Test float response time
        result_float = ConversationResult(
            query="float time",
            answer="answer",
            confidence_score=0.8,
            sources=[],
            conversation_id="conv-float",
            response_time_ms=123.456,
            success=True,
        )
        assert result_float.response_time_ms == 123.456
        assert isinstance(result_float.response_time_ms, float)

    def test_conversation_result_string_types(self):
        """Test ConversationResult with various string content."""
        # Test with unicode characters
        result = ConversationResult(
            query="¿Qué es la inteligencia artificial?",
            answer="La inteligencia artificial es...",
            confidence_score=0.88,
            sources=["https://ejemplo.com/ia"],
            conversation_id="conv-unicode",
            response_time_ms=150.0,
            success=True,
        )

        assert "¿" in result.query
        assert "La inteligencia" in result.answer

    def test_conversation_result_immutability(self):
        """Test that ConversationResult behaves as expected with dataclass."""
        result1 = ConversationResult(
            query="test",
            answer="answer",
            confidence_score=0.8,
            sources=["source1"],
            conversation_id="conv-1",
            response_time_ms=100.0,
            success=True,
        )

        result2 = ConversationResult(
            query="test",
            answer="answer",
            confidence_score=0.8,
            sources=["source1"],
            conversation_id="conv-1",
            response_time_ms=100.0,
            success=True,
        )

        # Test equality (dataclass should provide __eq__)
        assert result1 == result2

        # Test that modifying sources list doesn't affect equality
        result1.sources.append("source2")
        assert result1 != result2
