#!/usr/bin/env python3
"""Cox Communications Oliver Service - HYBRID Benchmarking Tool.

Since the LLM add-on isn't enabled on your test datastore, this tool:
1. Measures REAL search performance from your Vertex AI datastore
2. Simulates LLM response times based on Vertex AI's typical performance
3. Provides actionable insights for Cox's 2.5-second latency issue

This gives you accurate benchmarks without paying for the LLM add-on.
"""

import random
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path

# Add module path relative to project root
_project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_project_root / "search-engine" / "src"))

from search_engine import SearchEngine

# Configuration
PROJECT_ID = "admin-workstation"
DATASTORE_ID = "nq-html-docs-search"

# Cox-like realistic queries (customer service scenarios)
COX_QUERIES = [
    # Billing & Account (Simple queries - faster LLM response)
    "How do I pay my bill online?",
    "What payment methods do you accept?",
    "Why did my bill increase this month?",
    "How can I view my billing history?",
    "What is autopay and how do I set it up?",
    # Internet & Connectivity (Technical - medium LLM response)
    "My internet is slow, what should I do?",
    "How do I reset my modem?",
    "What internet speeds are available in my area?",
    "How do I change my WiFi password?",
    "Why is my internet connection dropping?",
    # Cable TV (Product info - medium LLM response)
    "How do I find what channel a show is on?",
    "Can I watch Cox TV on my mobile device?",
    "How do I set up parental controls?",
    "What's included in the basic cable package?",
    "How do I troubleshoot my cable box?",
    # Technical Support (Complex - slower LLM response)
    "How do I troubleshoot connection issues?",
    "My email isn't working, what should I check?",
    "How do I set up port forwarding?",
    "What are your DNS server addresses?",
    "How do I check for service outages in my area?",
]


@dataclass
class LLMSimulation:
    """Simulated LLM performance based on Vertex AI's typical behavior."""

    @staticmethod
    def estimate_llm_time(query: str, num_docs: int) -> float:
        """
        Estimate LLM response time based on:
        - Query complexity (length, technical terms)
        - Number of documents to process
        - Vertex AI's typical performance

        Based on real-world Vertex AI benchmarks:
        - Gemini Pro: 800-1500ms for short answers
        - Gemini Flash: 400-800ms for short answers
        - Additional 100-200ms per document processed
        """
        # Base latency for model initialization
        base_latency_ms = 300

        # Query complexity factor
        query_length = len(query)
        if query_length < 30:  # Simple question
            query_factor = 400
        elif query_length < 60:  # Medium question
            query_factor = 600
        else:  # Complex question
            query_factor = 800

        # Document processing time (100-200ms per doc)
        doc_processing = num_docs * random.uniform(100, 200)

        # Answer generation time (varies by model)
        # Cox likely uses Gemini Pro for quality
        generation_time = random.uniform(500, 1000)

        # Network overhead
        network_overhead = random.uniform(50, 150)

        # Add some realistic variance
        variance = random.uniform(0.9, 1.1)

        total_ms = (
            base_latency_ms
            + query_factor
            + doc_processing
            + generation_time
            + network_overhead
        ) * variance

        return total_ms


def benchmark_search_only(engine: SearchEngine, queries: list[str]) -> dict:
    """Benchmark pure search performance (document retrieval only)."""
    print("\n" + "=" * 70)
    print("🔍 PHASE 1: PURE SEARCH PERFORMANCE (Document Retrieval)")
    print("=" * 70)

    times = []
    doc_counts = []

    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Query: {query[:50]}...")

        start = time.time()
        result = engine.search(query, max_results=5)
        elapsed_ms = (time.time() - start) * 1000

        times.append(elapsed_ms)
        doc_counts.append(result.result_count)

        status = "✅" if result.success else "❌"
        print(
            f"  {status} Search time: {elapsed_ms:.1f}ms | Found: {result.result_count} docs"
        )

        # Show first result title if available
        if result.results and result.results[0].get("title"):
            print(f"     → Top result: {result.results[0]['title'][:50]}...")

    return {
        "type": "search",
        "count": len(times),
        "times": times,
        "doc_counts": doc_counts,
        "avg_ms": statistics.mean(times),
        "median_ms": statistics.median(times),
        "p95_ms": sorted(times)[int(0.95 * len(times))] if times else 0,
        "min_ms": min(times),
        "max_ms": max(times),
        "avg_docs": statistics.mean(doc_counts),
    }


def benchmark_simulated_conversation(engine: SearchEngine, queries: list[str]) -> dict:
    """Benchmark search + simulated LLM response times."""
    print("\n" + "=" * 70)
    print("💬 PHASE 2: SIMULATED CONVERSATIONAL AI (Search + LLM Generation)")
    print("=" * 70)
    print("   Note: LLM times are simulated based on Vertex AI benchmarks")
    print("=" * 70)

    search_times = []
    llm_times = []
    total_times = []

    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Query: {query[:50]}...")

        # Real search
        start = time.time()
        result = engine.search(query, max_results=5)
        search_ms = (time.time() - start) * 1000

        # Simulated LLM generation
        llm_ms = LLMSimulation.estimate_llm_time(query, result.result_count)
        total_ms = search_ms + llm_ms

        search_times.append(search_ms)
        llm_times.append(llm_ms)
        total_times.append(total_ms)

        print(
            f"  ✅ Search: {search_ms:.1f}ms | LLM (sim): {llm_ms:.1f}ms | Total: {total_ms:.1f}ms"
        )

    return {
        "type": "conversation",
        "count": len(total_times),
        "search_times": search_times,
        "llm_times": llm_times,
        "total_times": total_times,
        "avg_search_ms": statistics.mean(search_times),
        "avg_llm_ms": statistics.mean(llm_times),
        "avg_total_ms": statistics.mean(total_times),
        "median_total_ms": statistics.median(total_times),
        "p95_total_ms": sorted(total_times)[int(0.95 * len(total_times))],
        "min_total_ms": min(total_times),
        "max_total_ms": max(total_times),
    }


def analyze_cox_bottleneck(search_stats: dict, conv_stats: dict) -> None:
    """Analyze where Cox's performance bottleneck likely is."""
    print("\n" + "=" * 70)
    print("📊 PERFORMANCE ANALYSIS FOR COX COMMUNICATIONS OLIVER SERVICE")
    print("=" * 70)

    # Search performance
    print("\n🔍 SEARCH PERFORMANCE (Document Retrieval):")
    print(f"  • Average:    {search_stats['avg_ms']:.1f}ms")
    print(f"  • Median:     {search_stats['median_ms']:.1f}ms")
    print(f"  • P95:        {search_stats['p95_ms']:.1f}ms")
    print(
        f"  • Min/Max:    {search_stats['min_ms']:.1f}ms / {search_stats['max_ms']:.1f}ms"
    )
    print(f"  • Avg docs:   {search_stats['avg_docs']:.1f} documents retrieved")

    # Conversational performance
    print("\n💬 CONVERSATIONAL AI PERFORMANCE (Search + LLM):")
    print(f"  • Search avg:     {conv_stats['avg_search_ms']:.1f}ms")
    print(f"  • LLM gen avg:    {conv_stats['avg_llm_ms']:.1f}ms (simulated)")
    print(f"  • Total avg:      {conv_stats['avg_total_ms']:.1f}ms")
    print(f"  • Total median:   {conv_stats['median_total_ms']:.1f}ms")
    print(f"  • Total P95:      {conv_stats['p95_total_ms']:.1f}ms")

    # Cox target analysis
    cox_target_ms = 2500
    print("\n🎯 COX'S 2500ms TARGET ANALYSIS:")
    print(f"  • Simulated total: {conv_stats['avg_total_ms']:.1f}ms")

    if conv_stats["avg_total_ms"] > cox_target_ms:
        over_by = conv_stats["avg_total_ms"] - cox_target_ms
        print(f"  ⚠️  OVER TARGET by {over_by:.1f}ms ({over_by/cox_target_ms*100:.1f}%)")
    else:
        under_by = cox_target_ms - conv_stats["avg_total_ms"]
        print(f"  ✅ UNDER TARGET by {under_by:.1f}ms (good!)")

    # Breakdown analysis
    search_pct = (conv_stats["avg_search_ms"] / conv_stats["avg_total_ms"]) * 100
    llm_pct = (conv_stats["avg_llm_ms"] / conv_stats["avg_total_ms"]) * 100

    print("\n🔬 BOTTLENECK BREAKDOWN:")
    print(f"  • Search accounts for:     {search_pct:.1f}% of total time")
    print(f"  • LLM generation:          {llm_pct:.1f}% of total time")

    # Optimization recommendations
    print("\n💡 OPTIMIZATION RECOMMENDATIONS FOR COX:")

    recommendations = []

    # Search optimizations
    if conv_stats["avg_search_ms"] > 1000:
        recommendations.append(
            {
                "priority": "HIGH",
                "area": "Search Performance",
                "issue": f"Search is slow ({conv_stats['avg_search_ms']:.0f}ms > 1000ms)",
                "solutions": [
                    "Reduce max_results from 5 to 3 documents",
                    "Enable search result caching for common queries",
                    "Use search filters to narrow scope",
                    "Consider regional deployment to reduce network latency",
                ],
            }
        )
    elif conv_stats["avg_search_ms"] > 500:
        recommendations.append(
            {
                "priority": "MEDIUM",
                "area": "Search Performance",
                "issue": f"Search could be faster ({conv_stats['avg_search_ms']:.0f}ms)",
                "solutions": [
                    "Implement connection pooling",
                    "Use batch search for multiple queries",
                    "Add query preprocessing to simplify searches",
                ],
            }
        )

    # LLM optimizations
    if conv_stats["avg_llm_ms"] > 1500:
        recommendations.append(
            {
                "priority": "HIGH",
                "area": "LLM Generation",
                "issue": f"LLM generation is slow ({conv_stats['avg_llm_ms']:.0f}ms > 1500ms)",
                "solutions": [
                    "Switch from Gemini Pro to Gemini Flash (2-3x faster)",
                    "Reduce answer length (max_tokens parameter)",
                    "Implement streaming responses for perceived speed",
                    "Cache common Q&A pairs (FAQ caching)",
                    "Use answer templates for common queries",
                ],
            }
        )

    # Variance issues
    if search_stats["p95_ms"] > search_stats["avg_ms"] * 2:
        recommendations.append(
            {
                "priority": "MEDIUM",
                "area": "Stability",
                "issue": "High variance in search times (P95 >> avg)",
                "solutions": [
                    "Implement retry logic with exponential backoff",
                    "Add circuit breaker pattern",
                    "Monitor for cold starts",
                    "Check network stability to GCP",
                ],
            }
        )

    # Display recommendations
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"\n  {i}. [{rec['priority']}] {rec['area']}")
            print(f"     Issue: {rec['issue']}")
            print("     Solutions:")
            for solution in rec["solutions"]:
                print(f"       • {solution}")
    else:
        print("\n  ✅ Performance looks good! Minor optimizations possible:")
        print("     • Consider response caching for common queries")
        print("     • Implement query batching for multiple simultaneous users")
        print("     • Use streaming for better perceived performance")

    # Model comparison
    print("\n🤖 LLM MODEL COMPARISON (for Cox's consideration):")
    print("  ┌─────────────────┬──────────────┬─────────────┬──────────┐")
    print("  │ Model           │ Avg Latency  │ Quality     │ Cost     │")
    print("  ├─────────────────┼──────────────┼─────────────┼──────────┤")
    print("  │ Gemini Pro      │ 800-1500ms   │ High        │ $$       │")
    print("  │ Gemini Flash    │ 300-600ms    │ Good        │ $        │")
    print("  │ Claude Haiku    │ 500-1000ms   │ High        │ $$       │")
    print("  │ GPT-3.5 Turbo   │ 600-1200ms   │ Good        │ $        │")
    print("  └─────────────────┴──────────────┴─────────────┴──────────┘")

    print("\n" + "=" * 70)


def main() -> None:
    """Run the hybrid benchmark suite."""
    print("=" * 70)
    print(" COX COMMUNICATIONS - OLIVER SERVICE HYBRID BENCHMARK")
    print(" Simulating ~1,600 HTML knowledge base documents")
    print("=" * 70)
    print("\n⚠️  Note: Since LLM add-on isn't enabled on this datastore,")
    print("   we're using REAL search times + SIMULATED LLM times")
    print("   based on Vertex AI's typical performance metrics.")
    print("=" * 70)

    # Initialize search engine
    print("\n🔧 Initializing services...")
    search_engine = SearchEngine(PROJECT_ID, DATASTORE_ID)

    # Test connection
    print("📡 Testing connection to Vertex AI...")
    if search_engine.validate_connection():
        print("  ✅ Connected to Vertex AI Search")
    else:
        print("  ❌ Failed to connect to Vertex AI Search")
        return

    # Select queries for testing
    num_queries = 10  # Use 10 for good sample, or len(COX_QUERIES) for all
    test_queries = COX_QUERIES[:num_queries]

    print(f"\n📝 Testing with {len(test_queries)} Cox-like customer queries")
    print("   (billing, internet, cable, tech support)")

    # Run benchmarks
    search_stats = benchmark_search_only(search_engine, test_queries)
    conv_stats = benchmark_simulated_conversation(search_engine, test_queries)

    # Analyze results
    analyze_cox_bottleneck(search_stats, conv_stats)

    # Export results
    import json

    results = {
        "benchmark_type": "hybrid",
        "queries_tested": len(test_queries),
        "search_performance": {
            "avg_ms": search_stats["avg_ms"],
            "median_ms": search_stats["median_ms"],
            "p95_ms": search_stats["p95_ms"],
        },
        "conversational_performance": {
            "search_avg_ms": conv_stats["avg_search_ms"],
            "llm_avg_ms": conv_stats["avg_llm_ms"],
            "total_avg_ms": conv_stats["avg_total_ms"],
            "total_p95_ms": conv_stats["p95_total_ms"],
        },
        "cox_target_analysis": {
            "target_ms": 2500,
            "simulated_ms": conv_stats["avg_total_ms"],
            "meets_target": conv_stats["avg_total_ms"] < 2500,
        },
    }

    with open("cox_hybrid_benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n💾 Results saved to cox_hybrid_benchmark_results.json")

    # Final summary
    print("\n" + "=" * 70)
    print(" BENCHMARK COMPLETE")
    print("=" * 70)
    print("\n🎯 KEY FINDINGS:")
    print(f"  • Your search takes ~{search_stats['avg_ms']:.0f}ms (real measurement)")
    print(
        f"  • LLM generation likely adds ~{conv_stats['avg_llm_ms']:.0f}ms (simulated)"
    )
    print(f"  • Total estimated: ~{conv_stats['avg_total_ms']:.0f}ms")
    print("  • Cox's Oliver target: 2500ms")

    if conv_stats["avg_total_ms"] < 2000:
        print("\n✅ Good news! Based on these benchmarks, Cox's 2.5s latency")
        print("   seems HIGH. They likely have optimization opportunities.")
    else:
        print("\n⚠️  The simulated times are close to Cox's 2.5s target.")
        print("   Focus on the optimization recommendations above.")


if __name__ == "__main__":
    main()
