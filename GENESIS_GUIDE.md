# Genesis Developer Guide

**Version:** 1.7.2
**Last Updated:** 2025-10-12

## What is Genesis?

Genesis is a lean development toolkit that enforces AI-safe project practices, quality gates, and automated workflows. It provides CLI commands for testing, formatting, smart commits, and worktree management while keeping your codebase focused and maintainable.

**Core Principles:**
- AI safety through file count limits and sparse worktrees
- Quality gates before every commit
- Minimal complexity, maximum value
- Template-driven project consistency

## Installation

Install the latest Genesis CLI from GitHub releases:

```bash
# Using curl (recommended)
curl -sSL https://raw.githubusercontent.com/jhousteau/genesis/main/.genesis/scripts/setup/install-genesis.sh | bash

# Or if you have a Makefile with install-latest target
make install-latest
```

Verify installation:
```bash
genesis --version
# Genesis CLI v1.7.2
```

[Content continues... Full file is 695 lines]
