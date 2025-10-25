# Repository Cleanup Plan

## Current Issues

### 1. Root Directory Clutter (29 loose files)
- Multiple benchmark scripts (benchmark_cox*.py)
- Test scripts (test_*.py)
- LLM setup scripts (enable_llm*.py, create_*.py)
- Documentation files mixed with config

### 2. Non-Module Directories
- `src/` - Should not exist at root (modules have their own src/)
- `tests/` - Should not exist at root (modules have their own tests/)
- `config/` - Configuration files
- `data/` - Data files
- `scripts/` - Utility scripts

### 3. Documentation Scattered
- Cox-specific docs in root (cox_*.md)
- Architecture docs in docs/
- Summary files in root

## Proposed Structure

```
vertex-ai-search/
├── # EXISTING MODULES (keep as-is)
├── answer-service/
├── cli-orchestrator/
├── config-manager/
├── document-uploader/
├── filename-sanitizer/
├── gcs-manager/
├── html-extractor/
├── load-tester/
├── metrics-collector/
├── nq-downloader/
├── search-engine/
├── vertex-datastore/
│
├── # ORGANIZED DIRECTORIES
├── experiments/              # NEW - for test scripts
│   ├── cox-benchmarks/      # Cox-specific benchmarking
│   │   ├── benchmark_cox.py
│   │   ├── benchmark_cox_hybrid.py
│   │   ├── benchmark_cox_real.py
│   │   └── README.md
│   │
│   ├── llm-testing/         # LLM add-on experiments
│   │   ├── enable_llm.py
│   │   ├── create_chat_datastore.py
│   │   ├── import_to_chat_datastore.py
│   │   ├── test_conversation.py
│   │   └── test_real_chat.py
│   │
│   └── baseline-snapshot/   # Current system metrics
│       ├── discovery_engine_baseline.json
│       └── performance_baseline.md
│
├── docs/
│   ├── architecture/        # Keep existing
│   ├── benchmarks/          # NEW
│   │   ├── cox_insights_report.md
│   │   ├── cox_executive_summary.md
│   │   └── FINAL_SUMMARY.md
│   │
│   └── setup/               # NEW
│       ├── ENABLE_LLM_NOW.md
│       ├── ENABLE_LLM_STEPS.md
│       └── enable_llm_addon.md
│
├── # ROOT FILES (keep minimal)
├── .gitignore
├── .gitattributes
├── .gitleaks.toml
├── .markdownlint.json
├── .mcp.json
├── .pre-commit-config.yaml
├── CLAUDE.md                # Keep - AI context
├── Dockerfile
├── docker-compose.yml
├── Makefile                 # Root orchestration
├── mypy.ini
├── poetry.lock              # Remove if not used at root
├── pyproject.toml           # Remove if not used at root
├── README.md
└── issue_body.md            # Can delete after issue created
```

## Cleanup Commands

```bash
# 1. Create new directories
mkdir -p experiments/cox-benchmarks
mkdir -p experiments/llm-testing
mkdir -p experiments/baseline-snapshot
mkdir -p docs/benchmarks
mkdir -p docs/setup

# 2. Move Cox benchmarking scripts
mv benchmark_cox*.py experiments/cox-benchmarks/
mv cox_*.md docs/benchmarks/

# 3. Move LLM testing scripts
mv enable_llm.py create_chat_datastore.py import_to_chat_datastore.py experiments/llm-testing/
mv test_conversation.py test_real_chat.py experiments/llm-testing/

# 4. Move setup documentation
mv ENABLE_LLM*.md enable_llm_addon.md docs/setup/

# 5. Move FINAL_SUMMARY to benchmarks
mv FINAL_SUMMARY.md docs/benchmarks/

# 6. Remove unnecessary root directories
rm -rf src/ tests/  # If empty or redundant

# 7. Clean up temporary files
rm issue_body.md  # Already used

# 8. Remove root poetry files if not needed
# Check if root pyproject.toml is used
```

## Why This Matters for Pure Module Isolation

1. **Clean root = Clear module boundaries**
   - Each module stands alone
   - No confusion about what's a module vs utility

2. **Experiments directory**
   - Clearly marked as non-production
   - AI agents know these are test/exploration scripts
   - Not modules, don't need isolation

3. **Documentation organization**
   - All docs in docs/
   - Easier to exclude from AI context
   - Clear separation of concerns

## Benefits

- **Before**: 29 loose files + mixed directories = confusion
- **After**: Clean root with only modules + organized experiments
- **AI Safety**: Clear distinction between modules and utilities
- **Developer UX**: Easy to find modules vs experiments
