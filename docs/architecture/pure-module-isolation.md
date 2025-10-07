# Pure Module Isolation: vertex-ai-search Design Principle

## The Principle

**Each module must be capable of existing, building, testing, and running in complete isolation, with dependencies explicitly declared and dynamically resolved.**

This is a core Genesis design principle that vertex-ai-search inherits and must adhere to.

## What Pure Module Isolation Means for vertex-ai-search

Your modules should be designed as a **constellation of independent components** that can:
- Build independently (`cd module && make build`)
- Test independently (`cd module && make test`)
- Run independently (each has its own entry point if needed)
- Be developed in isolation (AI-safe worktrees with <60 files)
- Connect dynamically when needed (orchestration, not compilation)

## Why This Design Principle Exists

### 1. Cognitive Load Reduction
```
Monolith:        All files → Brain overload
Pure Isolation:  <60 files → Manageable chunks
```
When working on one component, you don't need to understand others.

### 2. AI-Safe Development
```python
# AI sees only what's needed for focused, accurate work
context_files = 30   # Focused, efficient development
```

### 3. True Parallel Development
```bash
# Multiple developers/AIs can work without conflicts
Developer A: cd component-a && make test  # No interference
Developer B: cd component-b && make test  # No interference
AI Agent 1:  cd module-x && ...           # No interference
```

### 4. Failure Isolation
```python
# Failures are contained, not cascading
if component_x_broken:
    other_components = still_work  # ✅
```

### 5. Deployment Flexibility
```bash
# Install/deploy only what you need
# No forced bundling of unused components
```

## Core Tenets for vertex-ai-search

1. **If you can't `cd` into it and `make test`, it's not a module**
2. **If removing it breaks other modules, it's not isolated**
3. **If an AI can't understand it with <60 files, it's not focused**
4. **If it imports from `../`, it's not independent**

## Implementation Requirements

### Module Structure
Every isolated module in vertex-ai-search MUST have:
```
module-name/
├── Makefile              # Standard targets: test, lint, build, clean
├── pyproject.toml        # Independent packaging (Python projects)
├── src/module_name/      # Source code
├── tests/               # Independent test suite
└── README.md            # Module-specific documentation
```

### Dependency Rules for vertex-ai-search
- **Allowed:** Imports from declared dependencies
- **Allowed:** Imports from standard library
- **Forbidden:** Imports from `../` (parent directories)
- **Forbidden:** Imports from sibling modules without declaration
- **Required:** All external dependencies explicitly declared

### Build Requirements
- `make test` - Must work in isolation
- `make build` - Must produce independent artifact
- `make lint` - Must validate without external dependencies
- `make clean` - Must clean only module artifacts

### AI Safety Requirements
- Module workspace must be <60 files for AI development
- Context must be comprehensible without broader codebase knowledge
- Use `genesis worktree create` for focused development

## The Anti-Pattern to Avoid

**"False Modularity"** - Directories that look modular but are intertwined:
```python
# Don't do this ❌
modules/
├── component-a/    # imports from ../shared/utils
├── component-b/    # imports from ../core/logger
└── component-c/    # imports from ../component-a/helpers
```

## The Pattern to Implement

**"Pure Module Isolation"** - True independence:
```python
# Do this ✅
modules/
├── component-a/    # imports only from: declared dependencies
├── component-b/    # imports only from: declared dependencies
└── component-c/    # imports only from: declared dependencies
```

## Benefits for vertex-ai-search

**Traditional Approach:**
- Change one line → test everything
- Understand everything → modify anything
- One bug → entire system affected

**Pure Module Isolation:**
- Change one line → test one module
- Understand one module → modify that module
- One bug → isolated impact

## The Philosophy

> "A module should be like a space station module - fully self-contained with its own life support (tests, build, dependencies), connecting to others through well-defined airlocks (APIs), and capable of being jettisoned without destroying the station."

## Enforcement in vertex-ai-search

This principle should be enforced through:
1. **Build validation** - Modules must build in isolation
2. **AI safety practices** - Use worktrees for focused development
3. **Code review** - Validate dependencies and imports
4. **Testing** - Each module has independent test suite

Pure Module Isolation isn't about process - it's about **cognitive isolation**, **failure isolation**, and **development isolation**.

**The isolation is the feature.**
