# Architecture Documentation -- Index

**Read this first.** This folder contains the complete technical documentation for the 3-Layer Dual Learning Agentic AI System.

Each file covers one focused component or system.

CLAUDE.md at the project root is the main entry point for AI assistants.

## Quick-Find Table

| Topic | File | What's inside |
|-------|------|---------------|
| Navigation hub | [00-index.md](00-index.md) | This file -- all docs and reading paths |
| System overview | [01-overview.md](01-overview.md) | Architecture, tech stack, directory structure |
| Orchestrator & Logger | [02-orchestrator.md](02-orchestrator.md) | SimpleOrchestrator, ExecutionLogger, _run_phase |
| Tool patterns | [03-tool-patterns.md](03-tool-patterns.md) | BaseTool contract, return format, all tools |
| Validator patterns | [04-validator-patterns.md](04-validator-patterns.md) | BaseValidator contract, return format, all validators |
| Database layer | [05-database.md](05-database.md) | SQLiteClient, schema, queries, init_db |
| Brain system | [06-brain.md](06-brain.md) | SmallBrain analysis, proposals, thresholds |
| Workflows | [07-workflows.md](07-workflows.md) | All 5 workflows, structure, adding new ones |
| Configuration | [08-configuration.md](08-configuration.md) | Config pattern, env vars, LLM client |
| Testing | [09-testing.md](09-testing.md) | pytest patterns, running tests, coverage |
| Operations | [10-operations.md](10-operations.md) | Running, debugging, show_logs, troubleshooting |

## Reading Paths

**Understanding the system for the first time:**
01-overview -> 02-orchestrator -> 07-workflows -> 05-database

**Adding a new workflow:**
07-workflows -> 03-tool-patterns -> 04-validator-patterns -> 08-configuration

**Adding a new tool to an existing workflow:**
03-tool-patterns -> 04-validator-patterns -> 09-testing

**Debugging a failed workflow run:**
10-operations -> 02-orchestrator -> 05-database

**Understanding the learning system:**
06-brain -> 02-orchestrator -> 05-database

**Setting up the project from scratch:**
08-configuration -> 10-operations -> 01-overview

**Running tests or adding test coverage:**
09-testing -> 03-tool-patterns -> 04-validator-patterns

## What's Here vs. What's in CLAUDE.md

| Content | Location |
|---------|----------|
| Project-wide critical rules | CLAUDE.md |
| Quick task reading paths | CLAUDE.md |
| Detailed component implementation | docs/architecture/ |
| Code examples and patterns | docs/architecture/ |
| Schema, SQL, API details | docs/architecture/ |
