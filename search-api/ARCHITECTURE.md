# Search API - Architecture Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Cloud Run                                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   Search API Service                       │  │
│  │                                                             │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐  │  │
│  │  │   FastAPI   │  │   Cache      │  │  VectorQuery    │  │  │
│  │  │   Uvicorn   │──│  TTLCache    │──│    Client       │  │  │
│  │  │             │  │  (1000/300s) │  │                 │  │  │
│  │  └─────────────┘  └──────────────┘  └─────────────────┘  │  │
│  │         │                                     │            │  │
│  │         │                                     │            │  │
│  │         ▼                                     ▼            │  │
│  │  ┌─────────────┐                    ┌─────────────────┐  │  │
│  │  │   Gemini    │                    │  Vertex AI      │  │  │
│  │  │   Flash     │                    │  Vector Search  │  │  │
│  │  │  (Stream)   │                    │                 │  │  │
│  │  └─────────────┘                    └─────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                        search-api/                            │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                     api.py                              │  │
│  │                                                          │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │  │
│  │  │  /health     │  │  /search     │  │  /summarize  │ │  │
│  │  │  endpoint    │  │  endpoint    │  │  endpoint    │ │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │  │
│  │                           │                  │          │  │
│  │                           ▼                  ▼          │  │
│  │  ┌──────────────────────────┐  ┌──────────────────┐   │  │
│  │  │   search_cache           │  │  generate_sse()  │   │  │
│  │  │   (TTLCache)             │  │  (async gen)     │   │  │
│  │  └──────────────────────────┘  └──────────────────┘   │  │
│  │                                                          │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  Dependencies:                                                │
│  ┌────────────────────┐  ┌───────────────────────────────┐  │
│  │ vector-query-client│  │    shared-contracts            │  │
│  │                    │  │                                │  │
│  │ - VectorQueryClient│  │ - SearchMatch                 │  │
│  │ - query()          │  │ - TextChunk                   │  │
│  │ - latency tracking │  │ - Vector768                   │  │
│  └────────────────────┘  └───────────────────────────────┘  │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## Request Flow Diagrams

### GET /search (Cache Miss)

```
Client Request
    │
    ▼
┌─────────────────┐
│ GET /search     │
│ ?q=query        │
│ &top_k=10       │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ Generate cache key  │
│ MD5(query:top_k)    │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐      No
│ Check cache?        ├─────────┐
└────────┬────────────┘         │
         │ Yes                  │
         │                      ▼
         │              ┌──────────────────┐
         │              │ VectorQueryClient│
         │              │ .query()         │
         │              └────────┬─────────┘
         │                       │
         │                       ▼
         │              ┌──────────────────┐
         │              │ Vertex AI Vector │
         │              │ Search           │
         │              └────────┬─────────┘
         │                       │
         │                       ▼
         │              ┌──────────────────┐
         │              │ Store in cache   │
         │              └────────┬─────────┘
         │                       │
         ▼                       ▼
┌──────────────────────────────────┐
│ Return SearchResponse            │
│ - results: List[SearchMatch]     │
│ - latency_ms: float              │
│ - cache_hit: bool                │
└──────────────────────────────────┘
```

### GET /search (Cache Hit)

```
Client Request
    │
    ▼
┌─────────────────┐
│ GET /search     │
│ ?q=query        │
│ &top_k=10       │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ Generate cache key  │
│ MD5(query:top_k)    │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐      Yes (< 10ms)
│ Check cache?        ├──────────────┐
└─────────────────────┘              │
                                     ▼
                            ┌──────────────────┐
                            │ Return from cache│
                            └────────┬─────────┘
                                     │
                                     ▼
                            ┌──────────────────────────────────┐
                            │ Return SearchResponse            │
                            │ - results: List[SearchMatch]     │
                            │ - latency_ms: <10ms              │
                            │ - cache_hit: true                │
                            └──────────────────────────────────┘
```

### POST /summarize

```
Client Request
    │
    ▼
┌─────────────────────┐
│ POST /summarize     │
│ {                   │
│   "content": "...", │
│   "max_tokens": 100 │
│ }                   │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Validate request    │
│ (Pydantic model)    │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Initialize Gemini   │
│ GenerativeModel     │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ generate_content()  │
│ stream=True         │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Stream SSE tokens   │
│                     │
│ data: Token1        │
│                     │
│ data: Token2        │
│                     │
│ data: Token3        │
│                     │
└─────────────────────┘
```

## Data Flow

### Search Match Object Flow

```
┌────────────────────────────────────────────────────────┐
│                  Vertex AI Vector Search                │
│                                                          │
│  Returns: List[Neighbor]                                │
│  - id: str                                              │
│  - distance: float                                      │
└───────────────────────┬────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────┐
│              VectorQueryClient.query()                  │
│                                                          │
│  Converts to: List[SearchMatch]                        │
│  - chunk_id = neighbor.id                              │
│  - score = 1 / (1 + distance)                          │
│  - content = "" (fetched separately)                   │
│  - metadata = {}                                       │
└───────────────────────┬────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────┐
│                  search_cache                           │
│                                                          │
│  Key: MD5(query:top_k)                                 │
│  Value: (List[SearchMatch], timestamp)                 │
│  TTL: 300 seconds                                      │
│  Max: 1000 entries                                     │
└───────────────────────┬────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────┐
│               SearchResponse                            │
│                                                          │
│  {                                                      │
│    "results": List[SearchMatch],                       │
│    "latency_ms": float,                                │
│    "cache_hit": bool                                   │
│  }                                                      │
└────────────────────────────────────────────────────────┘
```

## Performance Architecture

### Caching Strategy

```
┌─────────────────────────────────────────────────────────┐
│                    TTLCache                              │
│                                                           │
│  Parameters:                                             │
│  ├─ maxsize: 1000 entries                               │
│  ├─ ttl: 300 seconds (5 minutes)                        │
│  └─ eviction: LRU when at capacity                      │
│                                                           │
│  Cache Key Strategy:                                     │
│  ├─ Input: query_text + top_k                           │
│  ├─ Hash: MD5                                            │
│  └─ Output: 32-char hex string                          │
│                                                           │
│  Performance:                                            │
│  ├─ Cache hit: <10ms                                    │
│  ├─ Cache miss: <120ms p95 (depends on VectorQuery)    │
│  └─ Memory: ~100KB per entry (estimate)                │
└─────────────────────────────────────────────────────────┘
```

### Latency Breakdown

```
Search Request Latency Components:

Cache Hit Path:
┌──────────────────────────────────────┐
│ Total: <10ms                          │
├──────────────────────────────────────┤
│ 1. Request parsing:      <1ms        │
│ 2. Cache key generation: <1ms        │
│ 3. Cache lookup:         <1ms        │
│ 4. Response serialize:   <5ms        │
│ 5. Network:              ~2ms        │
└──────────────────────────────────────┘

Cache Miss Path:
┌──────────────────────────────────────┐
│ Total: <120ms (p95 target)           │
├──────────────────────────────────────┤
│ 1. Request parsing:      <1ms        │
│ 2. Cache key generation: <1ms        │
│ 3. Cache lookup:         <1ms        │
│ 4. VectorQuery call:     ~100ms      │
│    ├─ Embedding gen:     ~30ms       │
│    └─ Vector search:     ~70ms       │
│ 5. Cache store:          <1ms        │
│ 6. Response serialize:   <5ms        │
│ 7. Network:              ~2ms        │
└──────────────────────────────────────┘
```

## Deployment Architecture

### Cloud Run Configuration

```
┌─────────────────────────────────────────────────────────┐
│                   Cloud Run Service                      │
│                                                           │
│  Name: search-api                                        │
│  Region: us-central1                                     │
│                                                           │
│  Resources:                                              │
│  ├─ CPU: 1 vCPU                                         │
│  ├─ Memory: 512 MiB                                     │
│  └─ Timeout: 300s                                       │
│                                                           │
│  Scaling:                                                │
│  ├─ Min instances: 0 (scale to zero)                   │
│  ├─ Max instances: 10                                   │
│  └─ Concurrency: 80 requests/instance                  │
│                                                           │
│  Health Check:                                           │
│  ├─ Endpoint: GET /health                               │
│  ├─ Initial delay: 10s                                  │
│  ├─ Timeout: 5s                                         │
│  └─ Failure threshold: 3                                │
│                                                           │
│  Environment:                                            │
│  ├─ GCP_PROJECT_ID                                      │
│  ├─ GCP_LOCATION                                        │
│  ├─ INDEX_ENDPOINT_ID                                   │
│  ├─ DEPLOYED_INDEX_ID                                   │
│  └─ GEMINI_API_KEY (Secret Manager)                    │
└─────────────────────────────────────────────────────────┘
```

### External Dependencies

```
┌────────────────────────────────────────────────────────┐
│                  External Services                      │
└────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Vertex AI  │ │  Gemini API │ │   Secret    │
│   Vector    │ │   (Flash)   │ │   Manager   │
│   Search    │ │             │ │             │
│             │ │             │ │             │
│ - Embedding │ │ - Summary   │ │ - API Keys  │
│ - ANN Query │ │ - Streaming │ │             │
└─────────────┘ └─────────────┘ └─────────────┘
```

## Module Dependencies

```
search-api
    │
    ├─── FastAPI (web framework)
    │     └─── Pydantic (validation)
    │
    ├─── Uvicorn (ASGI server)
    │
    ├─── cachetools (in-memory cache)
    │     └─── TTLCache
    │
    ├─── google-cloud-aiplatform
    │     └─── Vertex AI SDK
    │
    ├─── google-generativeai
    │     └─── Gemini API
    │
    ├─── shared-contracts (local)
    │     ├─── SearchMatch
    │     ├─── TextChunk
    │     └─── Vector768
    │
    └─── vector-query-client (local)
          └─── VectorQueryClient
```

## Security Architecture

```
┌────────────────────────────────────────────────────────┐
│                    Security Layers                      │
├────────────────────────────────────────────────────────┤
│                                                          │
│  1. Network Layer:                                      │
│     ├─ Cloud Run ingress: Internal only               │
│     ├─ HTTPS only                                      │
│     └─ VPC Service Controls                            │
│                                                          │
│  2. Authentication:                                     │
│     ├─ Cloud Run service account                       │
│     ├─ Workload Identity for GCP APIs                 │
│     └─ API key for Gemini (from Secret Manager)       │
│                                                          │
│  3. Authorization:                                      │
│     ├─ IAM roles for Vertex AI                        │
│     ├─ IAM roles for Secret Manager                   │
│     └─ Least privilege principle                       │
│                                                          │
│  4. Data Protection:                                    │
│     ├─ No sensitive data in cache                     │
│     ├─ Secrets in Secret Manager                      │
│     └─ Encrypted at rest/transit                       │
│                                                          │
│  5. Input Validation:                                   │
│     ├─ Pydantic models                                 │
│     ├─ FastAPI parameter validation                   │
│     └─ SQL injection not applicable (no DB)           │
└────────────────────────────────────────────────────────┘
```

## Monitoring Architecture

```
┌────────────────────────────────────────────────────────┐
│                 Observability Stack                     │
├────────────────────────────────────────────────────────┤
│                                                          │
│  Metrics (Cloud Monitoring):                            │
│  ├─ Request count                                       │
│  ├─ Request latency (p50, p95, p99)                   │
│  ├─ Cache hit rate                                      │
│  ├─ Error rate                                          │
│  └─ Active instances                                    │
│                                                          │
│  Logs (Cloud Logging):                                  │
│  ├─ Request logs                                        │
│  ├─ Error logs                                          │
│  ├─ Cache logs                                          │
│  └─ API call logs                                       │
│                                                          │
│  Traces (Cloud Trace):                                  │
│  ├─ Request traces                                      │
│  ├─ API call spans                                      │
│  └─ Cache operation spans                               │
│                                                          │
│  Alerts:                                                 │
│  ├─ Latency > 200ms (p95)                              │
│  ├─ Error rate > 1%                                     │
│  ├─ Cache hit rate < 50%                               │
│  └─ Instance scaling failures                           │
└────────────────────────────────────────────────────────┘
```

---

## Design Decisions

### Why TTLCache?
- **Simple**: Built-in Python library, no external dependencies
- **Fast**: O(1) lookup, perfect for latency-sensitive API
- **Memory-efficient**: Fixed size limit prevents runaway memory usage
- **TTL**: Automatic expiration ensures data freshness

### Why Gemini Flash?
- **Speed**: Faster than Pro for summaries
- **Cost**: More economical for high-volume usage
- **Streaming**: Native SSE support
- **Quality**: Sufficient for concise summaries

### Why FastAPI?
- **Performance**: Async/await support for high concurrency
- **Developer Experience**: Automatic OpenAPI docs, type hints
- **Validation**: Built-in Pydantic validation
- **Testing**: Excellent test client support

### Why Pure Module Isolation?
- **Independent Testing**: Each module tests in isolation
- **Parallel Development**: Teams work independently
- **Clear Dependencies**: Explicit dependency declarations
- **AI-Safe**: Modules stay small (<60 files)

---

**Module**: search-api
**Architecture Version**: 1.0
**Last Updated**: 2025-10-25
