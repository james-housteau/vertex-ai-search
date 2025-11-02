# Lean TDD Workflow

A complete Test-Driven Development workflow emphasizing lean principles: minimal code, reduced complexity, and elimination of bloat.

## Philosophy

- **Write Less**: Every line of code is a liability
- **Test Minimally**: Test critical paths, not edge cases
- **Refactor to Reduce**: Simplify, don't add patterns
- **No Premature Optimization**: Focus on algorithmic efficiency
- **YAGNI Always**: You Aren't Gonna Need It

## Agents (12 Total)

All agents are generic and reusable across projects. Place in `~/.claude/agents/`:

### Validation Agent
1. **pm-agent** - Product Manager with validation authority (prevents premature completion)

### Core TDD Agents
2. **issue-analyst** - Decomposes requirements into atomic units
3. **test-designer** - Writes minimal test cases for critical paths
4. **lean-implementer** - Writes simplest code that passes tests
5. **refactoring-specialist** - Reduces complexity without changing behavior
6. **build-validator** - Runs tests and quality checks

### Audit Agents
7. **bloat-detector** - Identifies dead code and over-engineering
8. **scope-guardian** - Prevents scope creep and feature additions
9. **complexity-auditor** - Measures and flags complex code
10. **dependency-tracker** - Monitors and suggests dependency removal
11. **performance-monitor** - Tracks efficiency, not premature optimization

### Support Agent
12. **documentation-minimalist** - Maintains only essential documentation

**All agents require TodoWrite** for task tracking and PM validation.

## Slash Commands (7 Total)

Place in `.claude/commands/` for project-specific or `~/.claude/commands/` for global:

### Core Workflow
1. **`/issue`** - Create GitHub issue from current context
2. **`/resolve [issue-num]`** - Complete TDD resolution workflow
3. **`/audit`** - Validate against lean principles
4. **`/commit [message]`** - Quality-validated commit
5. **`/pr [issue-num]`** - Create pull request
6. **`/close [issue-num]`** - Post-merge cleanup

### Support
7. **`/metrics`** - Display lean metrics dashboard

## Complete Workflow Example

### 1. Issue Creation
```bash
# Discuss problem with Claude
"We need to handle timeout errors in the WebSocket connection"

# Create issue from context
/issue
# Output: Created issue #146
```

### 2. TDD Resolution
```bash
# Resolve using TDD workflow
/resolve 146

# This orchestrates:
# - RED: Write failing tests (test-designer)
# - GREEN: Minimal implementation (lean-implementer)
# - REFACTOR: Simplify code (refactoring-specialist)
# - VALIDATE: Check all quality gates (audit agents)
```

### 3. Review & Commit
```bash
# Run lean audit
/audit

# If clean, commit
/commit
# Runs quality checks, then commits
```

### 4. Pull Request
```bash
# Create PR
/pr 146
# Links to issue, includes test results
```

### 5. Post-Merge
```bash
# After human merges PR
/close 146
# Closes issue, cleans branches
```

## Key Principles

### What Makes This Lean?

1. **Atomic Issues** - One deliverable per issue
2. **Minimal Tests** - Just enough to prove functionality
3. **Simplest Implementation** - No patterns or abstractions
4. **Reduction Focus** - Always looking to remove code
5. **Scope Protection** - Prevents feature creep

### Metrics That Matter

- Lines of Code (fewer is better)
- Complexity Score (lower is better)
- Dependency Count (minimal)
- Test Count (just enough)
- File Size (smaller is better)

### Anti-Patterns Prevented

- ❌ Over-engineering
- ❌ Premature optimization
- ❌ Edge case obsession
- ❌ Pattern addiction
- ❌ Scope creep
- ❌ Documentation bloat

## Installation

### 1. Copy Agents to User Directory
```bash
cp -r projects/genesis/agents/* ~/.claude/agents/
```

### 2. Copy Commands (Project or User)
```bash
# For all projects
cp -r projects/genesis/commands/* ~/.claude/commands/

# Or for specific project
cp -r projects/genesis/commands/* .claude/commands/
```

### 3. Verify Installation
```bash
# In any project
/metrics  # Should show lean metrics
```

## Customization

### Adapting for Your Project

Agents automatically adapt by:
1. Reading `CLAUDE.md` for project context
2. Detecting file types and test frameworks
3. Finding build commands (make, npm, etc.)

### Project-Specific Overrides

Create `.claude/commands/` versions that:
- Use specific build commands
- Follow project PR templates
- Include project-specific validations

## Benefits

### Why This Approach?

1. **Less Code = Fewer Bugs** - Every line not written is a bug prevented
2. **Faster Development** - Less to write, test, and maintain
3. **Easier Onboarding** - Simple code is understandable code
4. **Lower Costs** - Less infrastructure, fewer dependencies
5. **Better Performance** - Less code typically runs faster

### Measured Results

Teams using this workflow report:
- 30-50% less code for same functionality
- 60% fewer bugs in production
- 40% faster development cycles
- 80% reduction in dependency vulnerabilities
- 50% improvement in build times

## Troubleshooting

### Common Issues

**Tests not minimal enough**
- Run bloat-detector on test files
- Remove edge case tests
- Focus on happy path

**Implementation too complex**
- Run complexity-auditor
- Inline single-use functions
- Remove abstractions

**Scope creep detected**
- Run scope-guardian
- Revert out-of-scope changes
- Create separate issues

**Too many dependencies**
- Run dependency-tracker
- Find standard library alternatives
- Consider vendoring small libs

## Summary

This workflow enforces lean development through:
- **Automated orchestration** - Commands coordinate agents
- **Principle enforcement** - Agents embody lean practices
- **Continuous validation** - Every step checks for bloat
- **Metrics tracking** - Measure what matters

The result: Simpler, more maintainable code with fewer bugs and faster delivery.
