#!/usr/bin/env python3
"""
Test REAL conversational AI with the chat-enabled datastore.
No mocks, no simulations - actual Vertex AI performance.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "answer-service" / "src"))
from answer_service.service_real import RealAnswerService  # type: ignore[import]

PROJECT_ID = "admin-workstation"
DATASTORE_ID = "nq-chat-benchmark"  # New chat-enabled datastore


def test_real_conversational_ai() -> None:
    """Test real Vertex AI conversational search - no mocks!"""
    print("=" * 70)
    print("🚀 TESTING REAL VERTEX AI CONVERSATIONAL SEARCH")
    print("   Using chat-enabled datastore with Gemini LLM")
    print("=" * 70)

    service = RealAnswerService(PROJECT_ID, DATASTORE_ID)
    service.start_conversation()

    # Cox-like customer service queries
    queries = [
        "How do I reset my modem?",
        "Why is my internet slow?",
        "What payment methods are accepted?",
    ]

    print("\n📊 Configuration:")
    print(f"   • Project: {PROJECT_ID}")
    print(f"   • Datastore: {DATASTORE_ID}")
    print("   • Model: Gemini (auto-selected by Vertex)")

    for query in queries:
        print(f"\n{'='*70}")
        print(f"🔍 Query: {query}")
        print("-" * 70)

        start = time.perf_counter()
        result = service.ask_question(query)
        elapsed_ms = (time.perf_counter() - start) * 1000

        if result.success:
            print("✅ SUCCESS")
            print(f"⏱️  Response time: {elapsed_ms:.1f}ms")
            print(f"📊 Confidence: {result.confidence_score:.2f}")

            if result.answer:
                print("\n💬 Answer:")
                import textwrap

                wrapped = textwrap.wrap(result.answer, width=65)
                for line in wrapped[:3]:
                    print(f"   {line}")
                if len(wrapped) > 3:
                    print(f"   ... ({len(wrapped)-3} more lines)")
        else:
            print("❌ FAILED")
            print(f"⏱️  Time: {elapsed_ms:.1f}ms")
            print(f"Error: {result.error_message}")

            if "not ready" in str(result.error_message).lower():
                print("\n⚠️  Datastore import still in progress!")
                print("   Wait 10-30 minutes for import to complete")
                break

    print("\n" + "=" * 70)
    print("✅ Test complete!")


if __name__ == "__main__":
    test_real_conversational_ai()
