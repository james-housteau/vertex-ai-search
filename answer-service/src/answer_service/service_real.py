"""Answer Service implementation using REAL Vertex AI Conversational Search."""

import time
import uuid
from typing import Any

try:
    from google.cloud import discoveryengine_v1 as discoveryengine

    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    discoveryengine: Any = None
    GOOGLE_CLOUD_AVAILABLE = False

from .models import ConversationResult


class RealAnswerService:
    """Real conversational search using Vertex AI Discovery Engine."""

    def __init__(self, project_id: str, data_store_id: str):
        """Initialize Answer Service with project and datastore configuration."""
        self.project_id = project_id
        self.data_store_id = data_store_id
        self.conversation_id = f"conv-{uuid.uuid4().hex[:8]}"
        self._conversation_history: list[ConversationResult] = []

        if not GOOGLE_CLOUD_AVAILABLE:
            raise ImportError(
                "google-cloud-discoveryengine is not installed. "
                "Install it with: pip install google-cloud-discoveryengine"
            )

        # Initialize the conversational search client
        self.client = discoveryengine.ConversationalSearchServiceClient()

        # Construct the serving config path
        self.serving_config = (
            f"projects/{project_id}/locations/global/collections/default_collection/"
            f"dataStores/{data_store_id}/servingConfigs/default_search"
        )

        # Construct the conversation resource name
        self.conversation_name = (
            f"projects/{project_id}/locations/global/collections/default_collection/"
            f"dataStores/{data_store_id}/conversations/-"
        )

    def _build_conversation_request(self, question: str) -> Any:
        """Build the conversation request for Vertex AI."""
        return discoveryengine.ConverseConversationRequest(
            name=self.conversation_name,
            query=discoveryengine.TextInput(input=question),
            serving_config=self.serving_config,
            # Configure summary generation
            summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                summary_result_count=5,  # Use top 5 results for summary
                include_citations=True,  # Include source citations
                language_code="en",
                model_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelSpec(
                    version="stable",  # Use stable model version
                ),
            ),
            # Add context if provided
            conversation=discoveryengine.Conversation(
                user_pseudo_id=self.conversation_id,
                messages=[],  # Could add conversation history here
            ),
        )

    def _extract_sources_from_metadata(self, metadata: Any) -> list[str]:
        """Extract source citations from metadata."""
        sources = []
        if hasattr(metadata, "citations"):
            for citation in metadata.citations:
                if hasattr(citation, "sources"):
                    for source in citation.sources:
                        sources.append(source.reference_id)
        return sources

    def _build_fallback_answer(self, search_results: Any) -> tuple[str, float]:
        """Build fallback answer from search results."""
        results_text = []
        for result in search_results[:3]:
            if hasattr(result.document, "derived_struct_data"):
                doc_data = dict(result.document.derived_struct_data)
                if "title" in doc_data:
                    results_text.append(doc_data["title"])

        if results_text:
            answer = f"Based on the search results: {', '.join(results_text)}"
            return answer, 0.6
        return "", 0.0

    def _extract_answer_from_response(
        self, response: Any
    ) -> tuple[str, list[str], float]:
        """Extract answer, sources, and confidence from the response."""
        answer = ""
        sources = []
        confidence_score = 0.0

        # Get the reply (generated answer)
        if response.reply and response.reply.summary:
            answer = response.reply.summary.summary_text
            confidence_score = 0.85 if answer else 0.3

            # Extract source citations
            if hasattr(response.reply.summary, "summary_with_metadata"):
                metadata = response.reply.summary.summary_with_metadata
                sources = self._extract_sources_from_metadata(metadata)

        # If no summary, try to get search results as fallback
        if not answer and response.search_results:
            answer, confidence_score = self._build_fallback_answer(
                response.search_results
            )

        return answer, sources, confidence_score

    def ask_question(
        self, question: str, context: str | None = None
    ) -> ConversationResult:
        """Execute conversational search query using Vertex AI."""
        start_time = time.time()

        try:
            # Build and execute the conversation request
            request = self._build_conversation_request(question)
            response = self.client.converse_conversation(request)

            # Extract the answer and metadata
            answer, sources, confidence_score = self._extract_answer_from_response(
                response
            )

            execution_time = (time.time() - start_time) * 1000

            # Create result
            result = ConversationResult(
                query=question,
                answer=answer if answer else "No answer generated",
                confidence_score=confidence_score,
                sources=sources[:5] if sources else [],
                conversation_id=self.conversation_id,
                response_time_ms=execution_time,
                success=bool(answer),
            )

            self._conversation_history.append(result)
            return result

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_msg = str(e)

            # Create error result
            result = ConversationResult(
                query=question,
                answer="",
                confidence_score=0.0,
                sources=[],
                conversation_id=self.conversation_id,
                response_time_ms=execution_time,
                success=False,
                error_message=f"Vertex AI error: {error_msg}",
            )

            self._conversation_history.append(result)
            return result

    def start_conversation(self) -> str:
        """Initialize new conversation session."""
        self.conversation_id = f"conv-{uuid.uuid4().hex[:8]}"
        self._conversation_history = []
        return self.conversation_id

    def end_conversation(self, conversation_id: str) -> bool:
        """End conversation session."""
        if conversation_id == self.conversation_id:
            self._conversation_history = []
            return True
        return False

    def get_conversation_history(
        self, conversation_id: str
    ) -> list[ConversationResult]:
        """Get conversation history for given conversation ID."""
        if conversation_id == self.conversation_id:
            return self._conversation_history.copy()
        return []
