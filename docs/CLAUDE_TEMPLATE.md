**For AI Assistants**: Read this file first before working with this codebase. It contains critical rules, patterns, and the reasoning behind them.

---

## Contents

1. [Purpose & Overview](#purpose--overview)  
2. [Critical Rules (Must Follow)](#critical-rules-must-follow)  
3. [Architecture & Structure](#architecture--structure)  
4. [Project Conventions](#project-conventions)  
5. [Development Workflow](#development-workflow)  
6. [Common Commands](#common-commands)  
7. [The WHY (Important Context)](#the-why-important-context)  
8. [Boundaries & Constraints](#boundaries--constraints)  
9. [Reference Files](#reference-files)  
10. [Out of Scope](#out-of-scope)  
11. [Emergency Procedures](#emergency-procedures)

---

## Purpose & Overview

**What this project does**: \[Brief description of core functionality\]

**Tech Stack**:

- Language: \[e.g., Python 3.10+, Node.js 18+, Go 1.21+\]  
- Database: \[e.g., PostgreSQL, MongoDB, SQLite\]  
- Framework: \[e.g., FastAPI, Express, Django\]  
- External Services: \[e.g., Stripe, SendGrid, OpenAI API\]

**Key Innovation**: \[What's the most important/unique aspect of this project?\]

---

## Critical Rules (Must Follow)

### 🚫 DO NOT Modify or Delete

**Critical Files** (never modify without explicit user permission):

- `[path/to/critical/file]` → \[Why it's critical\]  
- `[path/to/another/critical/file]` → \[Why it's critical\]  
- `[directory/]` → \[What breaks if this is modified\]

**WHY**: \[Explain the consequences of modifying these files\]

### ✅ ALWAYS Do

**\[Pattern Name 1\]**:

```
# Example of correct pattern
[code example]
```

**WHY**: \[Explain why this pattern is mandatory\]

**\[Pattern Name 2\]**:

```
# Example of correct pattern
[code example]
```

**WHY**: \[Explain why this pattern is mandatory\]

### ❌ NEVER Do

**\[Anti-pattern 1\]**:

```
# WRONG
[bad code example]

# RIGHT
[correct code example]
```

**WHY**: \[Explain the consequences of this mistake\]

**\[Anti-pattern 2\]**:

```
# WRONG
[bad code example]

# RIGHT
[correct code example]
```

**WHY**: \[Explain the consequences of this mistake\]

---

## Architecture & Structure

**Main Language**: \[Primary programming language\]

**Key Directories**:

```
/[directory_name]    → [What this directory contains]
  ├── [subdirectory] → [What this subdirectory contains]
  └── [subdirectory] → [What this subdirectory contains]

/[directory_name]    → [What this directory contains]
  ├── [subdirectory] → [What this subdirectory contains]
  └── [subdirectory] → [What this subdirectory contains]
```

**Entry Points**:

- Main application: `[command to start app]`  
- Tests: `[command to run tests]`  
- Development mode: `[command for dev mode]`

**Data Flow**:

```
[Input Source] → [Processing Step 1] → [Processing Step 2] → [Output/Storage]
```

---

## Project Conventions

**Naming Style**:

- Files: `[naming_convention]` (e.g., snake\_case.py, kebab-case.ts)  
- Classes: `[naming_convention]` (e.g., PascalCase)  
- Functions/variables: `[naming_convention]` (e.g., camelCase, snake\_case)  
- Constants: `[naming_convention]` (e.g., UPPER\_SNAKE\_CASE)

**File Organization**:

- \[Convention 1: e.g., "One class per file"\]  
- \[Convention 2: e.g., "Tests in **tests** directory"\]  
- \[Convention 3: e.g., "Index files export all public APIs"\]

**Error Handling**:

```
# Standard error handling pattern
[code example showing how to handle errors]
```

**Configuration**:

- Configuration file: `[path to config file]`  
- Environment variables: `[where .env is loaded, required vars]`  
- Never hardcode: `[what should never be hardcoded]`

**Database/Storage Access**:

```
# How to access database/storage correctly
[code example]
```

---

## Development Workflow

### Test-Driven Development (TDD)

**When to write tests first**:

- ✅ \[Scenario 1: e.g., "New features"\]  
- ✅ \[Scenario 2: e.g., "Bug fixes"\]  
- ✅ \[Scenario 3: e.g., "API changes"\]

**Test Structure**:

```
tests/
├── [test_directory_1]/
│   ├── test_[feature_1].py
│   └── test_[feature_2].py
└── [test_directory_2]/
    └── test_[feature_3].py
```

**Run tests**:

```shell
[command to run all tests]
[command to run specific test file]
[command to run with coverage]
```

### Git Workflow

**Branch naming**:

- Features: `[naming pattern, e.g., feature/description]`  
- Bugs: `[naming pattern, e.g., fix/description]`  
- Main branch: `[branch name, e.g., main, master]`

**Commit message format**:

```
[format, e.g., "type: description"]

Examples:
- feat: add user authentication
- fix: resolve database connection timeout
- docs: update API documentation
```

**Before committing**:

- [ ] \[Requirement 1: e.g., "Run tests"\]  
- [ ] \[Requirement 2: e.g., "Run linter"\]  
- [ ] \[Requirement 3: e.g., "Update documentation"\]

---

## Common Commands

**Development**:

```shell
# Start development server
[command]

# Run tests
[command]

# Run linter
[command]

# Format code
[command]
```

**Database/Storage**:

```shell
# Run migrations
[command]

# Seed database
[command]

# Reset database
[command]
```

**Deployment**:

```shell
# Build for production
[command]

# Deploy to [environment]
[command]
```

---

## The WHY (Important Context)

### Why \[Important Pattern/Rule\]

**We \[do/require\] this because**:

- \[Reason 1\]  
- \[Reason 2\]  
- \[Reason 3\]

**What happens without it**:

- ❌ \[Consequence 1\]  
- ❌ \[Consequence 2\]

**Example**:

```
[code example demonstrating the pattern]
```

### Why \[Another Important Pattern/Rule\]

**We \[do/require\] this because**:

- \[Reason 1\]  
- \[Reason 2\]

**What happens without it**:

- ❌ \[Consequence 1\]  
- ❌ \[Consequence 2\]

---

## Boundaries & Constraints

### Never Access Directly

- \[Resource 1\] → Use \[proper method\] instead  
- \[Resource 2\] → Use \[proper method\] instead

### Avoid These Patterns

**\[Anti-pattern name\]**:

```
# ❌ WRONG
[bad example]

# ✅ RIGHT
[correct example]
```

### Required Patterns

**All \[component type\] MUST**:

1. \[Requirement 1\]  
2. \[Requirement 2\]  
3. \[Requirement 3\]

**Example**:

```
[code example showing all requirements]
```

---

## Reference Files

### Documentation

- `[path/to/doc1.md]` → \[What this document covers\]  
- `[path/to/doc2.md]` → \[What this document covers\]

### Code Examples

- `[path/to/example1]` → \[What this example demonstrates\]  
- `[path/to/example2]` → \[What this example demonstrates\]

### Configuration Files

- `[path/to/config1]` → \[What this configures\]  
- `[path/to/config2]` → \[What this configures\]

---

## Out of Scope

Claude should NOT:

- **\[Action 1\]** unless explicitly requested  
    
  - Example: "Refactor unrelated files"  
  - Why: \[Reason\]


- **\[Action 2\]** without approval  
    
  - Example: "Add new dependencies"  
  - Why: \[Reason\]


- **\[Action 3\]**  
    
  - Example: "Change database schema"  
  - Why: \[Reason\]

### How Claude Should Behave Here

- **Prefer small, safe changes** over large refactors  
- **Match existing code style** (don't impose preferences)  
- **Ask before structural changes** (new directories, moving files)  
- **Explain reasoning** when suggesting non-obvious changes  
- **Run tests** before claiming code is complete

---

## Emergency Procedures

### \[Common Issue 1\]

**Problem**: \[Description of the problem\]

**Solution**:

```shell
[command to fix]
```

**Prevention**: \[How to avoid this issue\]

### \[Common Issue 2\]

**Problem**: \[Description of the problem\]

**Solution**:

```shell
[command to fix]
```

**Prevention**: \[How to avoid this issue\]

### \[Common Issue 3\]

**Problem**: \[Description of the problem\]

**Solution**:

```shell
[command to fix]
```

**Prevention**: \[How to avoid this issue\]

---

## Quick Start for AI Assistants

1. **Read this file** (CLAUDE.md) \- 5-10 minutes  
2. **Check \[key directory\]** for \[important context\]  
3. **Always \[required pattern\]**  
4. **Never \[forbidden action\]**  
5. **Run tests** before claiming completion

**Most Common Mistakes**:

- \[Mistake 1: Description\]  
- \[Mistake 2: Description\]  
- \[Mistake 3: Description\]

---

*This file is the single source of truth for AI assistants working with this codebase. When in doubt, refer to this file first.*  
