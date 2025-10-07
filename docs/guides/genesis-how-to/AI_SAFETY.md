# AI Safety Best Practices

## Overview

Genesis enforces AI safety through structured patterns, file limits, and automated safeguards that ensure reliable AI-assisted development.

## Core AI Safety Principles

### 1. Context Limitation
**Rule:** Keep development contexts under 30-60 files (configurable via AI_MAX_FILES environment variable).

**Why:** AI assistants have context windows that become unreliable with too many files.

**Implementation:**
- Sparse worktrees automatically enforce file limits
- `genesis worktree validate` checks file counts
- Warnings appear when approaching limits

### 2. Deterministic Environment
**Rule:** All development environments must be reproducible.

**Why:** Non-deterministic environments lead to AI confusion and inconsistent results.

**Implementation:**
- Container-based development with fixed versions
- Pinned dependencies in `pyproject.toml`/`package.json`
- Documented setup procedures

### 3. Fail-Fast Configuration
**Rule:** No hardcoded defaults; explicit configuration required.

**Why:** Hidden defaults create unpredictable behavior that AI cannot reason about.

**Implementation:**
- Required environment variables
- Configuration validation on startup
- Clear error messages for missing config

## File Organization Safety

### Directory Structure Standards
```
vertex-ai-search/
├── src/              # Source code (AI-focused)
├── tests/            # Test files (AI-validated)
├── docs/             # Documentation (AI-readable)
├── scripts/          # Automation (AI-auditable)
└── config/           # Configuration (AI-parseable)
```

### File Naming Conventions
- **Descriptive names**: `user_authentication.py` not `auth.py`
- **Consistent patterns**: `test_*.py`, `*_config.yml`
- **No abbreviations**: Full words for AI comprehension

### Content Organization
```python
# Good: Clear, AI-readable structure
class UserAuthenticationService:
    """Handles user authentication and session management."""

    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user with username and password."""
        pass

# Bad: Abbreviated, unclear for AI
class AuthSvc:
    def auth(self, u, p):
        pass
```

## AI-Safe Development Workflows

### 1. Worktree-Based Development
```bash
# Create focused context for AI
genesis worktree create user-auth src/auth/

# Validate file count
genesis worktree validate  # Must be ≤ 30 files

# Develop with AI assistance
cd ../vertex-ai-search-user-auth
```

### 2. Incremental Changes
- **Small commits**: One logical change per commit
- **Clear messages**: AI-readable commit messages
- **Staged rollbacks**: Easy to undo AI-assisted changes

### 3. Quality Gates
```bash
# Run before AI development session
make security          # Security scans
make lint             # Code quality
make test             # Functionality validation
```

## AI Assistant Configuration

### Claude Code Settings
Configure Claude Code for optimal safety in `.claude/settings.json`:

```json
{
  "file_limit": 30,
  "auto_validate": true,
  "safety_mode": "strict",
  "context_tracking": "enabled"
}
```

### Agent Container Isolation
For AI agent development, use isolated containers:

```bash
# Start agent container
genesis container run --profile agent

# Verify isolation
scripts/audit-agent.sh
```

**Agent Safety Features:**
- Read-only root filesystem
- Workspace-only write access
- Capability dropping (no CAP_SYS_ADMIN, etc.)
- Seccomp profiles blocking dangerous syscalls

## Risk Mitigation Strategies

### 1. Code Review Protocols
**Human oversight required for:**
- Security-sensitive code
- Database schema changes
- API contract modifications
- Configuration changes

**AI-safe review process:**
```bash
# Create review branch in focused worktree
genesis worktree create review-auth-changes src/auth/

# Review with limited context
git diff main..feature-branch

# Validate changes
make validate-changes
```

### 2. Rollback Procedures
**Immediate rollback triggers:**
- Test failures after AI changes
- Security scan failures
- Configuration validation errors

**Rollback commands:**
```bash
# Quick rollback
git reset --hard HEAD~1

# Selective rollback
git checkout HEAD~1 -- src/problematic_file.py

# Worktree rollback
rm -rf problematic-worktree/
genesis worktree create clean-start src/component/
```

### 3. Validation Gates
**Automated checks before deployment:**
- Unit test coverage ≥ 80%
- Security scan passes
- Type checking passes
- Documentation updated

## AI Safety Metrics

### Monitoring
Track these metrics for AI safety compliance:

```bash
# File count per worktree
genesis worktree stats

# Change complexity
git log --stat --since="1 day ago"

# Quality metrics
make quality-report
```

### Alerts
Set up alerts for:
- File count exceeding 25 (warning at 30)
- Large commits (>500 lines changed)
- Failed quality gates
- Security scan failures

## Container Security for AI Agents

### Agent Isolation
When developing AI agents, use the professional agent isolation:

```bash
# Build agent container
docker compose --profile agent build

# Run security audit
scripts/audit-agent.sh
```

**Security checklist:**
- ✅ Non-root user (UID 1000)
- ✅ Read-only root filesystem
- ✅ Workspace-only write access
- ✅ Dropped capabilities
- ✅ Seccomp profile active
- ✅ Resource limits enforced

### Agent Development Safety
```bash
# Verify agent cannot escape workspace
docker exec vertex-ai-search-agent ls /etc  # Should fail
docker exec vertex-ai-search-agent touch /usr/test  # Should fail
docker exec vertex-ai-search-agent touch /workspace/test  # Should succeed
```

## Emergency Procedures

### AI System Malfunction
1. **Stop AI processes immediately**
   ```bash
   kill -9 $(pgrep -f "ai-assistant")
   ```

2. **Preserve state for analysis**
   ```bash
   cp -r current-worktree/ incident-$(date +%Y%m%d_%H%M%S)/
   git stash push -m "AI incident state preservation"
   ```

3. **Rollback to known good state**
   ```bash
   git reset --hard last-known-good-commit
   make validate-bootstrap
   ```

### Data Integrity Issues
1. **Check for AI-introduced inconsistencies**
   ```bash
   make validate-data-integrity
   git log --since="last AI session" --stat
   ```

2. **Restore from backup if needed**
   ```bash
   git checkout HEAD~n -- path/to/corrupted/files
   ```

## Training and Education

### Developer Onboarding
- Complete AI safety training before using Genesis
- Understand worktree concepts and limitations
- Practice emergency procedures

### Ongoing Education
- Monthly AI safety reviews
- Update procedures as AI tools evolve
- Share lessons learned from incidents

## Compliance and Auditing

### Safety Audits
Regular audits should verify:
- File count compliance in all worktrees
- Security scan results
- Quality gate effectiveness
- Emergency procedure readiness

### Documentation Requirements
- All AI interactions documented
- Change rationales recorded
- Safety exceptions approved by lead

### Reporting
Generate safety reports:
```bash
# Weekly safety report
genesis safety-report --week

# Incident analysis
genesis incident-report --date 2024-01-15
```

## Related Documentation

- [Worktree Management Guide](./WORKTREE_GUIDE.md)
- [Genesis CLI Reference](./CLI_REFERENCE.md)
- [Troubleshooting Guide](./TROUBLESHOOTING.md)
