# Baseline Performance Metrics

## System Under Test
- **Technology**: Vertex AI Agent Builder (Discovery Engine API)
- **Datastore**: nq-html-docs-search
- **Documents**: 1,600 HTML files (368MB)
- **Date**: October 25, 2024

## Performance Baseline

### Search Latency (Current System)
| Metric | Value | Target (New) | Improvement Needed |
|--------|-------|--------------|-------------------|
| P50 | 546ms | <80ms | 6.8x |
| P95 | **628ms** | **<120ms** | **5.2x** |
| P99 | 650ms | <150ms | 4.3x |
| Average | 550ms | <100ms | 5.5x |

### Key Findings
1. **Search accounts for 22% of Cox's latency** (550ms of 2500ms)
2. **LLM generation accounts for 78%** (~1950ms estimated)
3. **Document retrieval averages 2.9 docs** per query

## Success Criteria for Vector Search

To successfully replace/augment the current system, Vector Search must:

### Performance Requirements
- [ ] P95 latency ≤120ms (5.2x improvement)
- [ ] P50 latency ≤80ms (6.8x improvement)
- [ ] Cache hit latency ≤10ms

### Quality Requirements
- [ ] Result relevance ≥70% of baseline
- [ ] Top-5 precision ≥0.7
- [ ] Zero failed queries (100% success rate)

### Operational Requirements
- [ ] Support 100 QPS minimum
- [ ] <1% error rate
- [ ] Auto-scaling capability

## Test Queries for Comparison

All benchmarks use the same Cox-representative queries:
```python
COX_QUERIES = [
    "How do I pay my bill online?",
    "What payment methods do you accept?",
    "Why did my bill increase this month?",
    "How can I view my billing history?",
    "What is autopay and how do I set it up?",
    "My internet is slow, what should I do?",
    "How do I reset my modem?",
    "What internet speeds are available in my area?",
    "How do I change my WiFi password?",
    "Why is my internet connection dropping?"
]
```

## Baseline System Characteristics

### Strengths (Preserve These)
- 100% query success rate
- Good result quality (full document retrieval)
- No infrastructure management needed
- Built-in ACL and security

### Weaknesses (Improve These)
- High latency (628ms P95)
- No caching layer
- Document-level retrieval (not chunk-level)
- No semantic understanding (keyword-based)

## Measurement Methodology

### Tools Available
- `metrics-collector/` - Performance tracking
- `search-engine/` - SearchResult API
- `benchmark_cox*.py` - Comparison scripts

### How to Compare
```python
# Run baseline
baseline = SearchEngine(PROJECT_ID, "nq-html-docs-search")
baseline_result = baseline.search(query)

# Run vector search
vector = VectorSearchEngine(PROJECT_ID, "vector-index")
vector_result = vector.search(query)

# Compare
improvement = (baseline_result.execution_time_ms -
               vector_result.execution_time_ms) /
               baseline_result.execution_time_ms * 100
```

## Next Steps

1. **Implement Vector Search** (Issue #1)
2. **Run A/B comparison** using this baseline
3. **Tune parameters** to meet targets
4. **Document improvements** vs baseline

---

*This baseline represents the current state before Vector Search implementation.*
*All improvements will be measured against these metrics.*
