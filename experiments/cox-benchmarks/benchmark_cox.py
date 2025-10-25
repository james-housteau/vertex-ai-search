#!/usr/bin/env python3
"""Cox Communications Oliver Service Benchmarking Tool.

This script benchmarks both pure search and conversational AI performance
to identify bottlenecks in the 2.5 second response time issue.

Usage:
    python benchmark_cox.py
"""

import statistics
import sys
import time
from pathlib import Path

# Add module paths relative to project root
_project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_project_root / "answer-service" / "src"))
sys.path.insert(0, str(_project_root / "search-engine" / "src"))
sys.path.insert(0, str(_project_root / "metrics-collector" / "src"))

from answer_service import AnswerService
from answer_service.models import ConversationResult
from metrics_collector import MetricsCollector
from search_engine import SearchEngine
from search_engine.models import SearchResult

# Configuration
PROJECT_ID = "admin-workstation"
DATASTORE_ID = "nq-html-docs-search"

# Cox-like realistic queries (customer service scenarios)
COX_QUERIES = [
    # Billing & Account
    "How do I pay my bill online?",
    "What payment methods do you accept?",
    "Why did my bill increase this month?",
    "How can I view my billing history?",
    "What is autopay and how do I set it up?",
    # Internet & Connectivity
    "My internet is slow, what should I do?",
    "How do I reset my modem?",
    "What internet speeds are available in my area?",
    "How do I change my WiFi password?",
    "Why is my internet connection dropping?",
    # Cable TV
    "How do I find what channel a show is on?",
    "Can I watch Cox TV on my mobile device?",
    "How do I set up parental controls?",
    "What's included in the basic cable package?",
    "How do I troubleshoot my cable box?",
    # Technical Support
    "How do I troubleshoot connection issues?",
    "My email isn't working, what should I check?",
    "How do I set up port forwarding?",
    "What are your DNS server addresses?",
    "How do I check for service outages in my area?",
]


def benchmark_search_only(engine: SearchEngine, queries: list[str]) -> dict:
    """Benchmark pure search performance (no LLM generation)."""
    print("\n" + "=" * 70)
    print("🔍 BENCHMARKING PURE SEARCH (Document Retrieval Only)")
    print("=" * 70)

    times = []
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Query: {query[:50]}...")

        start = time.time()
        result = engine.search(query, max_results=5)
        elapsed_ms = (time.time() - start) * 1000

        times.append(elapsed_ms)

        print(
            f"  ✓ Time: {elapsed_ms:.1f}ms | Found: {result.result_count} docs | Success: {result.success}"
        )

        # Show first result title if available
        if result.results and result.results[0].get("title"):
            print(f"  → Top result: {result.results[0]['title'][:60]}...")

    return {
        "type": "search",
        "count": len(times),
        "avg_ms": statistics.mean(times),
        "median_ms": statistics.median(times),
        "p95_ms": sorted(times)[int(0.95 * len(times))] if times else 0,
        "min_ms": min(times),
        "max_ms": max(times),
        "times": times,
    }


def benchmark_conversation(service: AnswerService, queries: list[str]) -> dict:
    """Benchmark conversational AI (search + LLM answer generation)."""
    print("\n" + "=" * 70)
    print("💬 BENCHMARKING CONVERSATIONAL AI (Search + Answer Generation)")
    print("=" * 70)

    times = []
    service.start_conversation()

    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Query: {query[:50]}...")

        start = time.time()
        result = service.ask_question(query)
        elapsed_ms = (time.time() - start) * 1000

        times.append(elapsed_ms)

        print(
            f"  ✓ Time: {elapsed_ms:.1f}ms | Confidence: {result.confidence_score:.2f} | Success: {result.success}"
        )

        # Show answer preview
        if result.answer:
            preview = result.answer[:80].replace("\n", " ")
            print(f"  → Answer: {preview}...")

    return {
        "type": "conversation",
        "count": len(times),
        "avg_ms": statistics.mean(times),
        "median_ms": statistics.median(times),
        "p95_ms": sorted(times)[int(0.95 * len(times))] if times else 0,
        "min_ms": min(times),
        "max_ms": max(times),
        "times": times,
    }


def analyze_bottleneck(search_stats: dict, conv_stats: dict) -> None:
    """Analyze where the performance bottleneck is."""
    print("\n" + "=" * 70)
    print("📊 PERFORMANCE ANALYSIS FOR COX COMMUNICATIONS")
    print("=" * 70)

    # Calculate the overhead
    overhead_avg = conv_stats["avg_ms"] - search_stats["avg_ms"]
    overhead_median = conv_stats["median_ms"] - search_stats["median_ms"]
    overhead_p95 = conv_stats["p95_ms"] - search_stats["p95_ms"]

    print("\n📈 SEARCH PERFORMANCE (Document Retrieval):")
    print(f"  • Average:    {search_stats['avg_ms']:.1f}ms")
    print(f"  • Median:     {search_stats['median_ms']:.1f}ms")
    print(f"  • P95:        {search_stats['p95_ms']:.1f}ms")
    print(
        f"  • Min/Max:    {search_stats['min_ms']:.1f}ms / {search_stats['max_ms']:.1f}ms"
    )

    print("\n💬 CONVERSATION PERFORMANCE (Search + LLM):")
    print(f"  • Average:    {conv_stats['avg_ms']:.1f}ms")
    print(f"  • Median:     {conv_stats['median_ms']:.1f}ms")
    print(f"  • P95:        {conv_stats['p95_ms']:.1f}ms")
    print(
        f"  • Min/Max:    {conv_stats['min_ms']:.1f}ms / {conv_stats['max_ms']:.1f}ms"
    )

    print("\n🎯 LLM GENERATION OVERHEAD:")
    print(f"  • Average:    +{overhead_avg:.1f}ms")
    print(f"  • Median:     +{overhead_median:.1f}ms")
    print(f"  • P95:        +{overhead_p95:.1f}ms")

    # Breakdown analysis
    print("\n🔬 BOTTLENECK ANALYSIS:")
    search_pct = (search_stats["avg_ms"] / conv_stats["avg_ms"]) * 100
    llm_pct = (overhead_avg / conv_stats["avg_ms"]) * 100

    print(f"  • Search accounts for:     {search_pct:.1f}% of total time")
    print(f"  • LLM generation adds:     {llm_pct:.1f}% of total time")

    # Cox's 2500ms target analysis
    target_ms = 2500
    print("\n🎯 COX TARGET ANALYSIS (2500ms goal):")
    print(f"  • Current conversation avg: {conv_stats['avg_ms']:.1f}ms")

    if conv_stats["avg_ms"] > target_ms:
        print(f"  ⚠️  OVER TARGET by {conv_stats['avg_ms'] - target_ms:.1f}ms")
    else:
        print(f"  ✅ UNDER TARGET by {target_ms - conv_stats['avg_ms']:.1f}ms")

    # Optimization recommendations
    print("\n💡 OPTIMIZATION RECOMMENDATIONS:")

    if search_stats["avg_ms"] > 1000:
        print("  1. ⚠️  Search is slow (>1s). Consider:")
        print("     • Reduce number of retrieved documents")
        print("     • Optimize search query preprocessing")
        print("     • Enable search result caching")
    else:
        print("  1. ✅ Search performance is good (<1s)")

    if overhead_avg > 1500:
        print("  2. ⚠️  LLM generation is slow (>1.5s). Consider:")
        print("     • Use a faster model (e.g., gemini-flash)")
        print("     • Reduce answer length/complexity")
        print("     • Implement streaming responses")
        print("     • Cache common questions")
    else:
        print("  2. ✅ LLM generation time is acceptable")

    if search_stats["p95_ms"] > search_stats["avg_ms"] * 2:
        print("  3. ⚠️  High search variance (P95 >> avg). Consider:")
        print("     • Implement connection pooling")
        print("     • Add retry logic with exponential backoff")
        print("     • Check network latency to Vertex AI")

    print("\n" + "=" * 70)


def main() -> None:
    """Run the complete benchmark suite."""
    print("=" * 70)
    print(" COX COMMUNICATIONS - OLIVER SERVICE BENCHMARK")
    print(" Simulating ~1600 HTML knowledge base documents")
    print("=" * 70)

    # Initialize services
    print("\n🔧 Initializing services...")
    search_engine = SearchEngine(PROJECT_ID, DATASTORE_ID)
    answer_service = AnswerService(PROJECT_ID, "benchmark-session")
    metrics = MetricsCollector(Path("./cox_benchmark_metrics"))

    # Test connection
    print("📡 Testing connection to Vertex AI...")
    if search_engine.validate_connection():
        print("  ✅ Connected to Vertex AI Search")
    else:
        print("  ❌ Failed to connect to Vertex AI Search")
        return

    # Use a subset for quick testing (use all 20 for full benchmark)
    test_queries = COX_QUERIES[:5]  # Start with 5 queries for quick test

    print(f"\n📝 Testing with {len(test_queries)} Cox-like customer queries")

    # Run benchmarks
    search_stats = benchmark_search_only(search_engine, test_queries)
    conv_stats = benchmark_conversation(answer_service, test_queries)

    # Analyze results
    analyze_bottleneck(search_stats, conv_stats)

    # Save detailed metrics
    print("\n💾 Saving detailed metrics...")

    # Record in metrics collector
    for i, query in enumerate(test_queries):
        # Record search metric
        metrics.record_search_metric(
            SearchResult(
                query=query,
                results=[],
                result_count=5,
                execution_time_ms=search_stats["times"][i],
                relevance_scores=[],
                success=True,
            )
        )

        # Record conversation metric
        metrics.record_conversation_metric(
            ConversationResult(
                query=query,
                answer="",
                confidence_score=0.85,
                sources=[],
                conversation_id="benchmark",
                response_time_ms=conv_stats["times"][i],
                success=True,
            )
        )

    # Export results
    metrics.export_to_json(Path("cox_benchmark_results.json"))
    metrics.export_to_csv(Path("cox_benchmark_results.csv"))

    print("  ✅ Results saved to cox_benchmark_results.json/csv")

    # Final summary
    print("\n" + "=" * 70)
    print(" BENCHMARK COMPLETE")
    print("=" * 70)
    print("\n🎯 KEY FINDING:")
    if conv_stats["avg_ms"] < 2500:
        print(
            f"  Your setup ({conv_stats['avg_ms']:.0f}ms) is FASTER than Cox's Oliver (2500ms)"
        )
        print("  This gives you a baseline to compare optimization strategies.")
    else:
        print(
            f"  Your setup ({conv_stats['avg_ms']:.0f}ms) shows similar performance to Cox's Oliver"
        )
        print(
            "  The bottleneck analysis above shows where to focus optimization efforts."
        )


if __name__ == "__main__":
    main()
