# Documentation Index

This directory contains comprehensive documentation for the Vertex AI Search and Conversation Testing System.

## Directory Structure

### `/architecture` - System Design
- **pure-module-isolation.md** - Core architectural principle documentation
- **REPO_CLEANUP_PLAN.md** - Repository organization strategy

### `/benchmarks` - Performance Analysis
- **cox_executive_summary.md** - High-level performance summary
- **cox_insights_report.md** - Detailed performance insights
- **FINAL_SUMMARY.md** - Comprehensive benchmark results

### `/guides` - Usage Documentation
- **VECTOR_SEARCH_QUICKSTART.md** - Complete vector search pipeline guide
- **genesis-how-to/** - Genesis framework usage guides
  - AI_SAFETY.md - AI safety constraints and guidelines
  - CLI_REFERENCE.md - Genesis CLI command reference
  - PACKAGING.md - Package distribution guide
  - TROUBLESHOOTING.md - Common issues and solutions
  - VERSION_MANAGEMENT.md - Version control best practices
  - WORKTREE_GUIDE.md - AI-safe worktree development

### `/reference` - Technical Reference
- **genesis-principles.md** - Genesis framework core principles
- **genesis-shared-core.md** - Shared utilities documentation
- **quick-start.md** - Quick start guide

### `/setup` - Configuration Guides
- **enable_llm_addon.md** - LLM addon setup
- **ENABLE_LLM_NOW.md** - Quick LLM enablement
- **ENABLE_LLM_STEPS.md** - Detailed LLM setup steps

## Quick Navigation

### Getting Started
1. Read the root [README.md](../README.md) for project overview
2. Review [CLAUDE.md](../CLAUDE.md) for development guidelines
3. Follow [guides/VECTOR_SEARCH_QUICKSTART.md](guides/VECTOR_SEARCH_QUICKSTART.md) for vector search setup
4. Check [reference/quick-start.md](reference/quick-start.md) for basic operations

### Module-Specific Documentation
Each module has its own documentation:
- README.md - Module overview and usage
- CLAUDE.md - AI assistant development guidelines
- Additional guides specific to module functionality

### Genesis Framework
- [genesis-how-to/](guides/genesis-how-to/) - Complete Genesis usage guides
- [genesis-principles.md](reference/genesis-principles.md) - Framework philosophy
- [genesis-shared-core.md](reference/genesis-shared-core.md) - Shared utilities

## Documentation Standards

### File Placement
- **Root README.md** - Project overview and quick start
- **Root CLAUDE.md** - AI assistant instructions
- **docs/** - All other documentation
- **Module README.md** - Module-specific documentation
- **Module CLAUDE.md** - Module-specific AI guidelines

### Markdown Style
- Use ATX-style headers (`#`, `##`, `###`)
- Include code fences with language identifiers
- Provide working examples with expected output
- Keep line length reasonable (recommend 120 chars)
- Use relative links for internal documentation

### Code Examples
- All code examples should be tested and working
- Include comments for complex operations
- Show both successful and error cases where relevant
- Provide context (before and after state)

## Contributing to Documentation

When adding or updating documentation:
1. Place files in appropriate subdirectories
2. Update this index if adding new sections
3. Use consistent formatting and style
4. Test all code examples
5. Validate all links
6. Run `/update-docs` to check alignment with code

## Last Updated
2025-10-26
