#!/usr/bin/env python3
"""Test the REAL Vertex AI Conversational Search API."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "answer-service" / "src"))

# Import the REAL service
from answer_service.service_real import RealAnswerService

PROJECT_ID = "admin-workstation"
DATASTORE_ID = "nq-html-docs-search"


def test_real_conversation() -> None:
    """Test real conversational search."""
    print("=" * 70)
    print("🧪 TESTING REAL VERTEX AI CONVERSATIONAL SEARCH")
    print("=" * 70)

    # Initialize the real service
    service = RealAnswerService(PROJECT_ID, DATASTORE_ID)
    service.start_conversation()

    # Test queries
    test_queries = [
        "What is photosynthesis and how does it work?",
        "Tell me about the Olympic Games",
        "Explain World War II",
    ]

    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        print("-" * 70)

        result = service.ask_question(query)

        print(f"✅ Success: {result.success}")
        print(f"⏱️  Response time: {result.response_time_ms:.1f}ms")
        print(f"📊 Confidence: {result.confidence_score:.2f}")

        if result.answer:
            print("\n💬 Answer:")
            # Wrap long answers
            import textwrap

            wrapped = textwrap.wrap(result.answer, width=70)
            for line in wrapped[:5]:  # Show first 5 lines
                print(f"   {line}")
            if len(wrapped) > 5:
                print(f"   ... ({len(wrapped)-5} more lines)")
        else:
            print("❌ No answer generated")

        if result.sources:
            print(f"\n📚 Sources: {result.sources}")

        if result.error_message:
            print(f"\n❌ Error: {result.error_message}")

    print("\n" + "=" * 70)
    print("✅ Test complete!")


if __name__ == "__main__":
    test_real_conversation()
