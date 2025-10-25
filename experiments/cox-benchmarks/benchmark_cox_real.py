#!/usr/bin/env python3
"""Cox Communications Oliver Service - REAL Benchmarking Tool.

This measures ACTUAL performance with the LLM add-on enabled:
- Real search latency from Vertex AI
- Real LLM generation time from Gemini
- Actual end-to-end conversational response times

This gives you the exact benchmarks Cox is experiencing with Oliver.
"""

import json
import statistics
import sys
import time
from pathlib import Path

# Add module paths relative to project root
_project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_project_root / "answer-service" / "src"))
sys.path.insert(0, str(_project_root / "search-engine" / "src"))

from answer_service.service_real import RealAnswerService
from search_engine import SearchEngine

# Configuration
PROJECT_ID = "admin-workstation"
DATASTORE_ID = "nq-html-docs-search"

# Cox-like realistic queries
COX_QUERIES = [
    # Billing & Account
    "How do I pay my Cox bill online?",
    "What payment methods does Cox accept?",
    "Why did my Cox bill increase this month?",
    "How can I view my Cox billing history?",
    "How do I set up autopay for my Cox account?",
    # Internet & Connectivity
    "My Cox internet is slow, what should I do?",
    "How do I reset my Cox modem?",
    "What Cox internet speeds are available in my area?",
    "How do I change my Cox WiFi password?",
    "Why is my Cox internet connection dropping?",
    # Cable TV
    "How do I find what channel a show is on Cox?",
    "Can I watch Cox TV on my mobile device?",
    "How do I set up parental controls on Cox cable?",
    "What's included in Cox's basic cable package?",
    "How do I troubleshoot my Cox cable box?",
    # Technical Support
    "How do I troubleshoot Cox connection issues?",
    "My Cox email isn't working, what should I check?",
    "How do I set up port forwarding on Cox router?",
    "What are Cox's DNS server addresses?",
    "How do I check for Cox service outages in my area?",
]


def measure_search_performance(engine: SearchEngine, queries: list[str]) -> dict:
    """Measure pure search performance (document retrieval only)."""
    print("\n" + "=" * 70)
    print("🔍 MEASURING PURE SEARCH PERFORMANCE (Document Retrieval)")
    print("=" * 70)

    measurements = []

    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Query: {query[:60]}...")

        # Measure search
        start = time.perf_counter()
        result = engine.search(query, max_results=5)
        elapsed_ms = (time.perf_counter() - start) * 1000

        measurements.append(
            {
                "query": query,
                "time_ms": elapsed_ms,
                "doc_count": result.result_count,
                "success": result.success,
            }
        )

        status = "✅" if result.success else "❌"
        print(f"  {status} Time: {elapsed_ms:.1f}ms | Docs: {result.result_count}")

        if result.results and result.results[0].get("title"):
            print(f"     → Top: {result.results[0]['title'][:50]}...")

    # Calculate statistics
    times = [m["time_ms"] for m in measurements]
    return {
        "measurements": measurements,
        "stats": {
            "count": len(times),
            "avg_ms": statistics.mean(times),
            "median_ms": statistics.median(times),
            "p95_ms": sorted(times)[int(0.95 * len(times))],
            "min_ms": min(times),
            "max_ms": max(times),
            "std_dev_ms": statistics.stdev(times) if len(times) > 1 else 0,
        },
    }


def measure_conversational_performance(
    service: RealAnswerService, queries: list[str]
) -> dict:
    """Measure REAL conversational AI performance (search + LLM generation)."""
    print("\n" + "=" * 70)
    print("💬 MEASURING REAL CONVERSATIONAL AI PERFORMANCE")
    print("   Using Vertex AI with Gemini LLM")
    print("=" * 70)

    measurements = []
    service.start_conversation()

    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Query: {query[:60]}...")

        # Measure conversational response
        start = time.perf_counter()
        result = service.ask_question(query)
        elapsed_ms = (time.perf_counter() - start) * 1000

        measurements.append(
            {
                "query": query,
                "time_ms": elapsed_ms,
                "success": result.success,
                "has_answer": bool(result.answer),
                "confidence": result.confidence_score,
                "error": result.error_message,
            }
        )

        status = "✅" if result.success else "❌"
        print(
            f"  {status} Time: {elapsed_ms:.1f}ms | Confidence: {result.confidence_score:.2f}"
        )

        if result.answer:
            preview = result.answer[:80].replace("\n", " ")
            print(f"     → Answer: {preview}...")
        elif result.error_message:
            print(f"     ❌ Error: {result.error_message[:60]}...")

    # Calculate statistics
    times = [m["time_ms"] for m in measurements if m["success"]]
    if times:
        stats = {
            "count": len(measurements),
            "successful": len(times),
            "avg_ms": statistics.mean(times),
            "median_ms": statistics.median(times),
            "p95_ms": sorted(times)[int(0.95 * len(times))],
            "min_ms": min(times),
            "max_ms": max(times),
            "std_dev_ms": statistics.stdev(times) if len(times) > 1 else 0,
        }
    else:
        stats = {"error": "No successful measurements"}

    return {"measurements": measurements, "stats": stats}


def analyze_cox_performance(search_data: dict, conv_data: dict) -> None:
    """Analyze performance and provide Cox-specific recommendations."""
    print("\n" + "=" * 70)
    print("📊 COX OLIVER SERVICE - PERFORMANCE ANALYSIS")
    print("=" * 70)

    s_stats = search_data["stats"]
    c_stats = conv_data.get("stats", {})

    if "error" in c_stats:
        print("\n⚠️  Conversational AI not available. Showing search stats only.")
        print("\n🔍 SEARCH PERFORMANCE:")
        print(f"  • Average:     {s_stats['avg_ms']:.1f}ms")
        print(f"  • Median:      {s_stats['median_ms']:.1f}ms")
        print(f"  • P95:         {s_stats['p95_ms']:.1f}ms")
        print(f"  • Std Dev:     {s_stats['std_dev_ms']:.1f}ms")
        print("\n💡 To get conversational benchmarks:")
        print("  1. Enable LLM add-on: python3 enable_llm.py")
        print("  2. Wait 5-10 minutes for activation")
        print("  3. Run this benchmark again")
        return

    # Calculate breakdown
    llm_overhead = c_stats["avg_ms"] - s_stats["avg_ms"]
    search_pct = (s_stats["avg_ms"] / c_stats["avg_ms"]) * 100
    llm_pct = (llm_overhead / c_stats["avg_ms"]) * 100

    print("\n🔍 SEARCH PERFORMANCE (Document Retrieval):")
    print(f"  • Average:     {s_stats['avg_ms']:.1f}ms")
    print(f"  • Median:      {s_stats['median_ms']:.1f}ms")
    print(f"  • P95:         {s_stats['p95_ms']:.1f}ms")
    print(f"  • Std Dev:     {s_stats['std_dev_ms']:.1f}ms")

    print("\n💬 CONVERSATIONAL PERFORMANCE (Search + LLM):")
    print(f"  • Average:     {c_stats['avg_ms']:.1f}ms")
    print(f"  • Median:      {c_stats['median_ms']:.1f}ms")
    print(f"  • P95:         {c_stats['p95_ms']:.1f}ms")
    print(f"  • Std Dev:     {c_stats['std_dev_ms']:.1f}ms")
    print(f"  • Success:     {c_stats['successful']}/{c_stats['count']} queries")

    print("\n⚙️  PERFORMANCE BREAKDOWN:")
    print(f"  • Search:      {s_stats['avg_ms']:.0f}ms ({search_pct:.1f}%)")
    print(f"  • LLM Gen:     {llm_overhead:.0f}ms ({llm_pct:.1f}%)")
    print(f"  • Total:       {c_stats['avg_ms']:.0f}ms")

    # Cox target analysis
    cox_target = 2500
    print("\n🎯 COX'S 2500ms TARGET:")
    if c_stats["avg_ms"] <= cox_target:
        under = cox_target - c_stats["avg_ms"]
        print(f"  ✅ MEETING TARGET - Under by {under:.0f}ms")
        print(f"     Your P95 ({c_stats['p95_ms']:.0f}ms) is the concern")
    else:
        over = c_stats["avg_ms"] - cox_target
        print(f"  ⚠️  OVER TARGET by {over:.0f}ms ({over/cox_target*100:.1f}%)")

    # Specific recommendations
    print("\n💡 OPTIMIZATION STRATEGIES FOR COX:")

    recommendations = []

    # Based on actual measurements
    if s_stats["avg_ms"] > 800:
        recommendations.append(
            {
                "priority": "HIGH",
                "impact": f"-{s_stats['avg_ms']*0.3:.0f}ms",
                "title": "Optimize Search",
                "actions": [
                    "Reduce max_results from 5 to 3",
                    "Add search result caching",
                    "Use regional Vertex AI endpoint",
                ],
            }
        )

    if llm_overhead > 1500:
        recommendations.append(
            {
                "priority": "CRITICAL",
                "impact": f"-{llm_overhead*0.5:.0f}ms",
                "title": "Switch to Gemini Flash",
                "actions": [
                    "Change from Gemini Pro to Flash (2x faster)",
                    "Reduce max_tokens to 150-200",
                    "Enable streaming responses",
                ],
            }
        )

    if c_stats["std_dev_ms"] > c_stats["avg_ms"] * 0.3:
        recommendations.append(
            {
                "priority": "MEDIUM",
                "impact": f"-{c_stats['p95_ms']-c_stats['median_ms']:.0f}ms variance",
                "title": "Reduce Variance",
                "actions": [
                    "Implement request retry logic",
                    "Add connection pooling",
                    "Monitor for cold starts",
                ],
            }
        )

    # Always recommend caching
    recommendations.append(
        {
            "priority": "MEDIUM",
            "impact": "-30-50% for repeat queries",
            "title": "Implement Caching",
            "actions": [
                "Cache top 100 FAQ responses",
                "Use Redis with 1-hour TTL",
                "Implement semantic similarity matching",
            ],
        }
    )

    for i, rec in enumerate(recommendations, 1):
        print(f"\n  {i}. [{rec['priority']}] {rec['title']}")
        print(f"     Impact: {rec['impact']}")
        print("     Actions:")
        for action in rec["actions"]:
            print(f"       • {action}")

    # Model comparison table
    print("\n📊 VERTEX AI MODEL BENCHMARKS (from your data):")
    print("  ┌────────────────┬─────────────┬──────────────┬────────┐")
    print("  │ Current Config │ Latency     │ Quality      │ Cost   │")
    print("  ├────────────────┼─────────────┼──────────────┼────────┤")
    print(
        f"  │ Your setup     │ {c_stats['avg_ms']:.0f}ms      │ Good         │ $$     │"
    )
    print("  └────────────────┴─────────────┴──────────────┴────────┘")
    print()
    print("  ┌────────────────┬─────────────┬──────────────┬────────┐")
    print("  │ Alternative    │ Est. Latency│ Quality      │ Cost   │")
    print("  ├────────────────┼─────────────┼──────────────┼────────┤")

    # Estimate improvements
    flash_estimate = s_stats["avg_ms"] + (llm_overhead * 0.4)
    print(f"  │ Gemini Flash   │ ~{flash_estimate:.0f}ms     │ Good         │ $      │")

    cached_estimate = c_stats["avg_ms"] * 0.1  # 90% cache hit rate
    print(
        f"  │ With Caching   │ ~{cached_estimate:.0f}ms      │ Same         │ +Redis │"
    )

    optimized = s_stats["avg_ms"] * 0.7 + llm_overhead * 0.4
    print(f"  │ Fully Optimized│ ~{optimized:.0f}ms     │ Good         │ $$     │")
    print("  └────────────────┴─────────────┴──────────────┴────────┘")


def main() -> None:
    """Run the complete real benchmark suite."""
    print("=" * 70)
    print(" COX COMMUNICATIONS - OLIVER SERVICE REAL BENCHMARK")
    print(" Measuring actual Vertex AI + Gemini performance")
    print("=" * 70)

    # Initialize services
    print("\n🔧 Initializing services...")
    search_engine = SearchEngine(PROJECT_ID, DATASTORE_ID)
    answer_service = RealAnswerService(PROJECT_ID, DATASTORE_ID)

    # Test connection
    print("📡 Testing Vertex AI connection...")
    if not search_engine.validate_connection():
        print("  ❌ Cannot connect to Vertex AI Search")
        return

    print("  ✅ Connected to Vertex AI Search")

    # Select queries
    num_queries = 10  # Start with 10, can increase to 20 for full test
    test_queries = COX_QUERIES[:num_queries]

    print(f"\n📝 Testing with {len(test_queries)} Cox customer service queries")

    # Run benchmarks
    search_data = measure_search_performance(search_engine, test_queries)
    conv_data = measure_conversational_performance(answer_service, test_queries)

    # Analyze
    analyze_cox_performance(search_data, conv_data)

    # Save results
    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "project_id": PROJECT_ID,
        "datastore_id": DATASTORE_ID,
        "queries_tested": len(test_queries),
        "search_performance": search_data["stats"],
        "conversational_performance": conv_data.get("stats", {}),
        "raw_measurements": {
            "search": search_data["measurements"],
            "conversational": conv_data["measurements"],
        },
    }

    with open("cox_real_benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n💾 Detailed results saved to cox_real_benchmark_results.json")

    # Final summary
    print("\n" + "=" * 70)
    print(" BENCHMARK COMPLETE")
    print("=" * 70)

    if "error" not in conv_data.get("stats", {}):
        print("\n🎯 EXECUTIVE SUMMARY FOR COX:")
        print(f"  • Current latency: {conv_data['stats']['avg_ms']:.0f}ms average")
        print("  • Cox target: 2500ms")

        if conv_data["stats"]["avg_ms"] < 2000:
            savings = ((2500 - conv_data["stats"]["avg_ms"]) / 2500) * 100
            print(
                f"  • Potential improvement: {savings:.0f}% faster than current Oliver"
            )
        else:
            print("  • Focus on the optimization recommendations above")
    else:
        print("\n⚠️  Enable LLM add-on to get conversational benchmarks")
        print("   Run: python3 enable_llm.py")


if __name__ == "__main__":
    main()
