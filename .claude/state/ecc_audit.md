# Everything Claude Code (ECC) -- Full Repository Audit

**Date:** 2026-03-21
**Source:** https://github.com/affaan-m/everything-claude-code
**Version:** 1.9.0
**Author:** Affaan M
**Primary Language:** JavaScript
**Package Manager:** bun

---

## 1. Executive Summary

ECC is a production-ready Claude Code plugin providing 28 specialized agents, 116 skills, 59 commands, and automated hook workflows. It is designed as a comprehensive development toolkit that can be installed into any project via a selective install system with profile tiers (minimal, standard, strict, full/enterprise). It also ships adapters for Cursor, OpenCode (Codex), and Antigravity.

Key stats:
- 28 agents (code reviewers, build resolvers, planners, security, etc.)
- 116+ skills (language-specific patterns, testing, deployment, business domains)
- 59 slash commands
- 30+ hook scripts (pre/post tool use, session management, quality gates)
- 10 language-specific rule sets + common rules
- Multi-harness support (Claude Code, Cursor, Codex/OpenCode, Antigravity)
- Translations: Japanese (ja-JP), Korean (ko-KR), Chinese Simplified (zh-CN), Chinese Traditional (zh-TW)

---

## 2. Top-Level File Tree

```
.agents/                    -- Codex/OpenAI agent harness copies
.claude/                    -- Claude Code config (rules, skills, commands, identity)
.claude-plugin/             -- Plugin marketplace manifest
.codex/                     -- Codex harness config
.cursor/                    -- Cursor IDE harness (hooks, rules, skills)
.github/                    -- CI/CD workflows, issue/PR templates
.opencode/                  -- OpenCode harness (commands, prompts, tools, plugins)
agents/                     -- 28 agent definitions (markdown)
assets/                     -- Guide images and screenshots
commands/                   -- 59 slash command definitions (markdown)
contexts/                   -- 3 context mode files (dev, research, review)
docs/                       -- Architecture docs, translations, release notes, business docs
examples/                   -- Example CLAUDE.md files for various stacks
hooks/                      -- Hook config (hooks.json) + README
manifests/                  -- Install component/module/profile manifests
mcp-configs/                -- MCP server configurations
plugins/                    -- Plugin system README
rules/                      -- Language-specific + common rule sets
schemas/                    -- JSON schemas for config validation
scripts/                    -- Node.js utilities, hook scripts, CI validators, install system
skills/                     -- 116+ skill definitions
tests/                      -- Test suite (hooks, lib, CI, integration)
AGENTS.md                   -- Agent orchestration instructions
CHANGELOG.md                -- Release changelog
CLAUDE.md                   -- Entry point for Claude Code
CODE_OF_CONDUCT.md          -- Community guidelines
CONTRIBUTING.md             -- Contribution guide with formats
LICENSE                     -- License file
README.md                   -- Main README (English)
README.zh-CN.md             -- Chinese README
SECURITY.md                 -- Security policy
SPONSORING.md               -- Sponsorship info
SPONSORS.md                 -- Current sponsors
TROUBLESHOOTING.md          -- Common issues and fixes
VERSION                     -- Version number
the-longform-guide.md       -- Detailed usage guide
the-security-guide.md       -- Security deep-dive
the-shortform-guide.md      -- Quick reference guide
commitlint.config.js        -- Commit message linting
eslint.config.js            -- ESLint config
install.ps1                 -- Windows installer
install.sh                  -- Unix installer
package.json                -- NPM package config
```

---

## 3. Directory: agents/ (28 agents)

| File | Description |
|------|-------------|
| architect.md | System design and scalability decisions |
| build-error-resolver.md | Fix build/type errors generically |
| chief-of-staff.md | Communication triage (email, Slack, LINE, Messenger) |
| code-reviewer.md | Code quality and maintainability review |
| cpp-build-resolver.md | C++ build error resolution |
| cpp-reviewer.md | C++ code review |
| database-reviewer.md | PostgreSQL/Supabase schema and query specialist |
| doc-updater.md | Documentation and codemap updates |
| docs-lookup.md | Library/API documentation research |
| e2e-runner.md | End-to-end Playwright testing |
| flutter-reviewer.md | Flutter/Dart code review |
| go-build-resolver.md | Go build error resolution |
| go-reviewer.md | Go code review |
| harness-optimizer.md | Harness config tuning (reliability, cost, throughput) |
| java-build-resolver.md | Java/Maven/Gradle build errors |
| java-reviewer.md | Java and Spring Boot code review |
| kotlin-build-resolver.md | Kotlin/Gradle build errors |
| kotlin-reviewer.md | Kotlin/Android/KMP code review |
| loop-operator.md | Autonomous loop execution, monitoring, intervention |
| planner.md | Implementation planning for complex features |
| python-reviewer.md | Python code review |
| pytorch-build-resolver.md | PyTorch runtime/CUDA/training errors |
| refactor-cleaner.md | Dead code cleanup and refactoring |
| rust-build-resolver.md | Rust build error resolution |
| rust-reviewer.md | Rust code review |
| security-reviewer.md | Vulnerability detection and security review |
| tdd-guide.md | Test-driven development workflow |
| typescript-reviewer.md | TypeScript/JavaScript code review |

---

## 4. Directory: commands/ (59 slash commands)

| File | Description |
|------|-------------|
| aside.md | Side conversation / tangent |
| build-fix.md | Fix build errors |
| checkpoint.md | Save a checkpoint |
| claw.md | Claw utility command |
| code-review.md | Trigger code review |
| context-budget.md | Manage context window budget |
| cpp-build.md | C++ build command |
| cpp-review.md | C++ code review |
| cpp-test.md | C++ test runner |
| devfleet.md | Development fleet management |
| docs.md | Documentation command |
| e2e.md | End-to-end test generation/execution |
| eval.md | Evaluation harness |
| evolve.md | Skill evolution |
| go-build.md | Go build command |
| go-review.md | Go code review |
| go-test.md | Go test runner |
| gradle-build.md | Gradle build command |
| harness-audit.md | Audit harness configuration |
| instinct-export.md | Export learned instincts |
| instinct-import.md | Import instincts |
| instinct-status.md | View instinct status |
| kotlin-build.md | Kotlin build command |
| kotlin-review.md | Kotlin code review |
| kotlin-test.md | Kotlin test runner |
| learn-eval.md | Evaluate learning outcomes |
| learn.md | Extract patterns from sessions |
| loop-start.md | Start an autonomous loop |
| loop-status.md | Check loop status |
| model-route.md | Model routing configuration |
| multi-backend.md | Multi-agent backend workflow |
| multi-execute.md | Multi-agent execution |
| multi-frontend.md | Multi-agent frontend workflow |
| multi-plan.md | Multi-agent planning |
| multi-workflow.md | Multi-agent workflow orchestration |
| orchestrate.md | Orchestrate complex workflows |
| plan.md | Implementation planning |
| pm2.md | PM2 process management |
| projects.md | Project management |
| promote.md | Promote changes |
| prompt-optimize.md | Optimize prompts |
| python-review.md | Python code review |
| quality-gate.md | Run quality gate checks |
| refactor-clean.md | Refactor and clean code |
| resume-session.md | Resume a saved session |
| rules-distill.md | Distill rules from codebase |
| rust-build.md | Rust build command |
| rust-review.md | Rust code review |
| rust-test.md | Rust test runner |
| save-session.md | Save current session |
| sessions.md | Session management |
| setup-pm.md | Setup package manager |
| skill-create.md | Generate skills from git history |
| skill-health.md | Check skill health |
| tdd.md | Test-driven development |
| test-coverage.md | Check test coverage |
| update-codemaps.md | Update code maps |
| update-docs.md | Update documentation |
| verify.md | Verify changes |

---

## 5. Directory: contexts/ (3 context modes)

| File | Description |
|------|-------------|
| dev.md | Active development mode -- code first, explain after, run tests, atomic commits |
| research.md | Exploration mode -- read widely before concluding, document findings, no code until understanding clear |
| review.md | PR review mode -- read thoroughly, prioritize by severity, check security, suggest fixes |

---

## 6. Directory: .claude/ (Claude Code configuration)

### .claude/rules/
| File | Description |
|------|-------------|
| everything-claude-code-guardrails.md | Auto-generated guardrails: commit workflow, architecture, code style, detected workflows |

### .claude/skills/
| File | Description |
|------|-------------|
| everything-claude-code/SKILL.md | Auto-generated repo conventions skill (commit style, architecture, code patterns, testing, workflows) |

### .claude/commands/ (3 workflow commands)
| File | Description |
|------|-------------|
| add-language-rules.md | Workflow scaffold for adding new language rules |
| database-migration.md | Workflow scaffold for database migrations |
| feature-development.md | Standard feature implementation workflow |

### Other .claude files
| File | Description |
|------|-------------|
| ecc-tools.json | Full install manifest -- profiles, packages, dependencies, managed files, adapters |
| identity.json | Agent identity config (technical level, verbosity, domains) |
| package-manager.json | Package manager preference (bun, set 2026-01-23) |
| enterprise/controls.md | Enterprise governance scaffold (approvals, audit, escalation) |
| research/everything-claude-code-research-playbook.md | Research workflow defaults for docs-heavy tasks |
| team/everything-claude-code-team-config.json | Team config pointing collaborators at shared ECC bundle |
| homunculus/instincts/inherited/everything-claude-code-instincts.yaml | 8 curated instincts (commits, naming, testing, hooks, cross-platform sync, releases, learning) |

---

## 7. Directory: rules/ (10 languages + common)

Each language directory contains 5 files: coding-style.md, hooks.md, patterns.md, security.md, testing.md.

| Directory | Language |
|-----------|----------|
| rules/common/ | Cross-language rules (agents, coding-style, development-workflow, git-workflow, hooks, patterns, performance, security, testing) |
| rules/cpp/ | C++ |
| rules/csharp/ | C# |
| rules/golang/ | Go |
| rules/java/ | Java |
| rules/kotlin/ | Kotlin |
| rules/perl/ | Perl |
| rules/php/ | PHP |
| rules/python/ | Python |
| rules/rust/ | Rust |
| rules/swift/ | Swift |
| rules/typescript/ | TypeScript |

---

## 8. Directory: skills/ (116+ skills)

Listed alphabetically. Each skill has a SKILL.md file. Some have additional scripts/ or reference/ subdirectories.

| Skill | Domain |
|-------|--------|
| agent-eval | Agent evaluation |
| agent-harness-construction | Building agent harnesses |
| agentic-engineering | Agentic engineering patterns |
| ai-first-engineering | AI-first development approach |
| ai-regression-testing | AI regression testing |
| android-clean-architecture | Android clean architecture |
| api-design | API design patterns |
| architecture-decision-records | ADR documentation |
| article-writing | Content/article writing |
| autonomous-loops | Autonomous agent loop patterns |
| backend-patterns | Backend development patterns |
| blueprint | Project blueprinting |
| bun-runtime | Bun runtime usage |
| carrier-relationship-management | Logistics: carrier relationships |
| claude-api | Claude API usage |
| claude-devfleet | Claude development fleet |
| clickhouse-io | ClickHouse database patterns |
| codebase-onboarding | Onboarding to new codebases |
| coding-standards | Coding standards enforcement |
| compose-multiplatform-patterns | Kotlin Compose Multiplatform |
| configure-ecc | ECC configuration |
| content-engine | Content creation engine |
| content-hash-cache-pattern | Content hash caching |
| context-budget | Context window budget management |
| continuous-agent-loop | Continuous agent loops |
| continuous-learning | Continuous learning (v1) |
| continuous-learning-v2 | Continuous learning (v2, with observer agent, hooks, scripts) |
| cost-aware-llm-pipeline | Cost-aware LLM pipeline design |
| cpp-coding-standards | C++ coding standards |
| cpp-testing | C++ testing |
| crosspost | Cross-platform posting |
| customs-trade-compliance | Logistics: customs compliance |
| data-scraper-agent | Data scraping agent |
| database-migrations | Database migration patterns |
| deep-research | Deep research workflows |
| deployment-patterns | Deployment patterns |
| django-patterns | Django patterns |
| django-security | Django security |
| django-tdd | Django TDD |
| django-verification | Django verification |
| dmux-workflows | Dmux workflow orchestration |
| docker-patterns | Docker patterns |
| documentation-lookup | Documentation/API lookup |
| e2e-testing | End-to-end testing |
| energy-procurement | Energy procurement domain |
| enterprise-agent-ops | Enterprise agent operations |
| eval-harness | Evaluation harness |
| exa-search | Exa search integration |
| fal-ai-media | fal.ai media generation |
| flutter-dart-code-review | Flutter/Dart review |
| foundation-models-on-device | On-device foundation models |
| frontend-patterns | Frontend development patterns |
| frontend-slides | Frontend slide generation |
| golang-patterns | Go patterns |
| golang-testing | Go testing |
| inventory-demand-planning | Logistics: inventory planning |
| investor-materials | Investor materials creation |
| investor-outreach | Investor outreach workflows |
| iterative-retrieval | Iterative retrieval patterns |
| java-coding-standards | Java coding standards |
| jpa-patterns | JPA patterns |
| kotlin-coroutines-flows | Kotlin coroutines and flows |
| kotlin-exposed-patterns | Kotlin Exposed ORM |
| kotlin-ktor-patterns | Kotlin Ktor patterns |
| kotlin-patterns | Kotlin patterns |
| kotlin-testing | Kotlin testing |
| laravel-patterns | Laravel patterns |
| laravel-security | Laravel security |
| laravel-tdd | Laravel TDD |
| laravel-verification | Laravel verification |
| liquid-glass-design | Liquid glass design patterns |
| logistics-exception-management | Logistics: exception management |
| market-research | Market research |
| mcp-server-patterns | MCP server patterns |
| nanoclaw-repl | NanoClaw REPL |
| nextjs-turbopack | Next.js with Turbopack |
| nutrient-document-processing | Nutrient document processing |
| nuxt4-patterns | Nuxt 4 patterns |
| perl-patterns | Perl patterns |
| perl-security | Perl security |
| perl-testing | Perl testing |
| plankton-code-quality | Plankton code quality |
| postgres-patterns | PostgreSQL patterns |
| production-scheduling | Production scheduling domain |
| project-guidelines-example | Example project guidelines |
| prompt-optimizer | Prompt optimization |
| python-patterns | Python patterns |
| python-testing | Python testing |
| pytorch-patterns | PyTorch patterns |
| quality-nonconformance | Quality non-conformance domain |
| ralphinho-rfc-pipeline | RFC pipeline |
| regex-vs-llm-structured-text | Regex vs LLM for structured text |
| returns-reverse-logistics | Returns/reverse logistics domain |
| rules-distill | Distill rules from codebases (with scripts) |
| rust-patterns | Rust patterns |
| rust-testing | Rust testing |
| search-first | Search-first development |
| security-review | Security review (with cloud infrastructure security) |
| security-scan | Security scanning |
| skill-stocktake | Skill inventory audit (with scripts) |
| springboot-patterns | Spring Boot patterns |
| springboot-security | Spring Boot security |
| springboot-tdd | Spring Boot TDD |
| springboot-verification | Spring Boot verification |
| strategic-compact | Strategic context compaction (with suggest-compact.sh) |
| swift-actor-persistence | Swift actor persistence |
| swift-concurrency-6-2 | Swift concurrency 6.2 |
| swift-protocol-di-testing | Swift protocol DI testing |
| swiftui-patterns | SwiftUI patterns |
| tdd-workflow | TDD workflow |
| team-builder | Team building |
| verification-loop | Verification loop patterns |
| video-editing | Video editing |
| videodb | VideoDB integration (with reference docs and scripts) |
| visa-doc-translate | Visa document translation |
| x-api | X (Twitter) API |

---

## 9. Directory: hooks/ (Hook System)

The hook system is defined in `hooks/hooks.json` and implemented via scripts in `scripts/hooks/`.

### Hook Events and Scripts

**PreToolUse hooks:**
| Hook | Matcher | Description |
|------|---------|-------------|
| block-no-verify | Bash | Block git --no-verify flag bypass |
| auto-tmux-dev | Bash | Auto-start dev servers in tmux |
| tmux-reminder | Bash | Remind to use tmux for long-running commands |
| git-push-reminder | Bash | Remind before git push to review |
| doc-file-warning | Write | Warn about non-standard doc files |
| suggest-compact | Edit/Write | Suggest manual compaction at intervals |
| observe (CL v2) | * | Capture tool use for continuous learning |
| insaits-security | Bash/Write/Edit/MultiEdit | Optional AI security monitor |
| governance-capture | Bash/Write/Edit/MultiEdit | Capture governance events |
| mcp-health-check | * | Check MCP server health before calls |

**PostToolUse hooks:**
| Hook | Matcher | Description |
|------|---------|-------------|
| pr-created | Bash | Log PR URL after creation |
| build-complete | Bash | Async build analysis |
| quality-gate | Edit/Write/MultiEdit | Quality gate checks after edits |
| format | Edit | Auto-format JS/TS (Biome or Prettier) |
| typecheck | Edit | TypeScript check on .ts/.tsx |
| console-warn | Edit | Warn about console.log |
| governance-capture | Bash/Write/Edit/MultiEdit | Capture governance events |
| observe (CL v2) | * | Capture tool results for learning |

**PostToolUseFailure hooks:**
| Hook | Matcher | Description |
|------|---------|-------------|
| mcp-health-check | * | Track failed MCP calls, mark unhealthy, reconnect |

**PreCompact hooks:**
| Hook | Matcher | Description |
|------|---------|-------------|
| pre-compact | * | Save state before context compaction |

**SessionStart hooks:**
| Hook | Matcher | Description |
|------|---------|-------------|
| session-start | * | Load previous context, detect package manager |

**Stop hooks:**
| Hook | Matcher | Description |
|------|---------|-------------|
| check-console-log | * | Check for console.log in modified files |
| session-end | * | Persist session state (async) |
| evaluate-session | * | Evaluate session for extractable patterns (async) |
| cost-tracker | * | Track token and cost metrics (async) |

**SessionEnd hooks:**
| Hook | Matcher | Description |
|------|---------|-------------|
| session-end-marker | * | Session end lifecycle marker (async) |

---

## 10. Directory: .agents/ (Codex/OpenAI Harness)

Skills mirrored for the OpenAI Codex agent harness. Each skill has a SKILL.md and an agents/openai.yaml.

Skills included: api-design, article-writing, backend-patterns, bun-runtime, claude-api, coding-standards, content-engine, crosspost, deep-research, dmux-workflows, documentation-lookup, e2e-testing, eval-harness, everything-claude-code, exa-search, fal-ai-media, frontend-patterns, frontend-slides, investor-materials, investor-outreach, market-research, mcp-server-patterns, nextjs-turbopack, security-review, strategic-compact, tdd-workflow, verification-loop, video-editing, x-api.

---

## 11. Directory: .cursor/ (Cursor IDE Harness)

### .cursor/hooks/ (14 hook scripts)
| File | Description |
|------|-------------|
| adapter.js | Hook adapter for Cursor |
| after-file-edit.js | Post-edit hook |
| after-mcp-execution.js | Post-MCP hook |
| after-shell-execution.js | Post-shell hook |
| after-tab-file-edit.js | Post-tab-edit hook |
| before-mcp-execution.js | Pre-MCP hook |
| before-read-file.js | Pre-read hook |
| before-shell-execution.js | Pre-shell hook |
| before-submit-prompt.js | Pre-prompt hook |
| before-tab-file-read.js | Pre-tab-read hook |
| pre-compact.js | Pre-compact hook |
| session-end.js | Session end hook |
| session-start.js | Session start hook |
| stop.js | Stop hook |
| subagent-start.js | Subagent start hook |
| subagent-stop.js | Subagent stop hook |

### .cursor/rules/ (30 rule files)
Common rules (9): agents, coding-style, development-workflow, git-workflow, hooks, patterns, performance, security, testing.
Language-specific rules (5 each for golang, kotlin, php, python, swift, typescript): coding-style, hooks, patterns, security, testing.

### .cursor/skills/ (10 skills)
article-writing, bun-runtime, content-engine, documentation-lookup, frontend-slides, investor-materials, investor-outreach, market-research, mcp-server-patterns, nextjs-turbopack.

---

## 12. Directory: .opencode/ (OpenCode Harness)

| Path | Description |
|------|-------------|
| MIGRATION.md | Migration guide |
| README.md | OpenCode adapter docs |
| commands/ (30 commands) | Mirrored command set |
| index.ts | Entry point |
| instructions/INSTRUCTIONS.md | OpenCode instructions |
| opencode.json | Config |
| package.json / tsconfig.json | Build config |
| plugins/ecc-hooks.ts | Hook plugin |
| plugins/index.ts | Plugin entry |
| prompts/agents/ (14 agent prompts) | architect, build-error-resolver, code-reviewer, database-reviewer, doc-updater, e2e-runner, go-build-resolver, go-reviewer, planner, refactor-cleaner, rust-build-resolver, rust-reviewer, security-reviewer, tdd-guide |
| tools/ (7 tools) | check-coverage, format-code, git-summary, index, lint-check, run-tests, security-audit |

---

## 13. Install System

ECC uses a selective install system with profiles, packages, and components.

### Profiles
- **minimal** -- Core essentials only
- **standard** -- Common development tools
- **strict** -- Standard + enforcement
- **full/enterprise** -- Everything including governance

### Packages (dependency order)
1. **runtime-core** -- Skills, identity, instincts, Codex config
2. **workflow-pack** -- Workflow commands (depends on runtime-core)
3. **agentshield-pack** -- Guardrails (depends on workflow-pack)
4. **research-pack** -- Research playbook (depends on workflow-pack)
5. **team-config-sync** -- Team config (depends on runtime-core)
6. **enterprise-controls** -- Governance (depends on team-config-sync)

### Components
repo-baseline, workflow-automation, security-audits, research-tooling, team-rollout, governance-controls

---

## 14. Key File Contents

### 14a. CLAUDE.md (full content)

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Claude Code plugin** - a collection of production-ready agents, skills, hooks, commands, rules, and MCP configurations. The project provides battle-tested workflows for software development using Claude Code.

## Running Tests

node tests/run-all.js
node tests/lib/utils.test.js
node tests/lib/package-manager.test.js
node tests/hooks/hooks.test.js

## Architecture

- agents/ - Specialized subagents for delegation
- skills/ - Workflow definitions and domain knowledge
- commands/ - Slash commands invoked by users
- hooks/ - Trigger-based automations
- rules/ - Always-follow guidelines
- mcp-configs/ - MCP server configurations
- scripts/ - Cross-platform Node.js utilities
- tests/ - Test suite

## Key Commands

/tdd, /plan, /e2e, /code-review, /build-fix, /learn, /skill-create

## Development Notes

- Package manager detection: npm, pnpm, yarn, bun
- Cross-platform: Windows, macOS, Linux via Node.js
- Agent format: Markdown with YAML frontmatter
- Skill format: Markdown with sections
- Hook format: JSON with matcher conditions

## Contributing

- Agents: Markdown with frontmatter (name, description, tools, model)
- Skills: Clear sections (When to Use, How It Works, Examples)
- Commands: Markdown with description frontmatter
- Hooks: JSON with matcher and hooks array
- File naming: lowercase with hyphens
```

### 14b. contexts/dev.md (full content)

```markdown
# Development Context

Mode: Active development
Focus: Implementation, coding, building features

## Behavior
- Write code first, explain after
- Prefer working solutions over perfect solutions
- Run tests after changes
- Keep commits atomic

## Priorities
1. Get it working
2. Get it right
3. Get it clean

## Tools to favor
- Edit, Write for code changes
- Bash for running tests/builds
- Grep, Glob for finding code
```

### 14c. contexts/research.md (full content)

```markdown
# Research Context

Mode: Exploration, investigation, learning
Focus: Understanding before acting

## Behavior
- Read widely before concluding
- Ask clarifying questions
- Document findings as you go
- Don't write code until understanding is clear

## Research Process
1. Understand the question
2. Explore relevant code/docs
3. Form hypothesis
4. Verify with evidence
5. Summarize findings

## Tools to favor
- Read for understanding code
- Grep, Glob for finding patterns
- WebSearch, WebFetch for external docs
- Task with Explore agent for codebase questions

## Output
Findings first, recommendations second
```

### 14d. contexts/review.md (full content)

```markdown
# Code Review Context

Mode: PR review, code analysis
Focus: Quality, security, maintainability

## Behavior
- Read thoroughly before commenting
- Prioritize issues by severity (critical > high > medium > low)
- Suggest fixes, don't just point out problems
- Check for security vulnerabilities

## Review Checklist
- [ ] Logic errors
- [ ] Edge cases
- [ ] Error handling
- [ ] Security (injection, auth, secrets)
- [ ] Performance
- [ ] Readability
- [ ] Test coverage

## Output Format
Group findings by file, severity first
```

### 14e. .claude/identity.json (full content)

```json
{
  "version": "2.0",
  "technicalLevel": "technical",
  "preferredStyle": {
    "verbosity": "minimal",
    "codeComments": true,
    "explanations": true
  },
  "domains": [
    "javascript"
  ],
  "suggestedBy": "ecc-tools-repo-analysis",
  "createdAt": "2026-03-20T12:07:57.119Z"
}
```

### 14f. .claude/rules/everything-claude-code-guardrails.md (full content)

```markdown
# Everything Claude Code Guardrails

## Commit Workflow
- Prefer conventional commit messaging with prefixes: fix, test, feat, docs.
- Keep new changes aligned with existing PR and review flow.

## Architecture
- Preserve the current hybrid module organization.
- Respect current test layout: separate.

## Code Style
- Use camelCase file naming.
- Prefer relative imports and mixed exports.

## ECC Defaults
- Current recommended install profile: full.
- Validate risky config changes in PRs.

## Detected Workflows
- database-migration
- feature-development
- add-language-rules

## Review Reminder
- Regenerate when repository conventions materially change.
- Keep suppressions narrow and auditable.
```

### 14g. .claude/enterprise/controls.md (full content)

```markdown
# Enterprise Controls

## Baseline
- Repository: https://github.com/affaan-m/everything-claude-code
- Recommended profile: full
- Keep install manifests, audit allowlists, and Codex baselines under review.

## Approval Expectations
- Security-sensitive workflow changes require explicit reviewer acknowledgement.
- Audit suppressions must include a reason and the narrowest viable matcher.
- Generated skills should be reviewed before broad rollout to teams.
```

### 14h. .claude/homunculus/instincts (8 instincts)

1. **conventional-commits** -- Use feat:, fix:, docs:, test:, chore:, refactor: prefixes
2. **commit-length** -- Keep subjects ~70 characters
3. **js-file-naming** -- camelCase for JS/TS modules, kebab-case for skill/command directories
4. **test-runner** -- Use *.test.js pattern, node tests/run-all.js for verification
5. **hooks-change-set** -- Update hook script + config + tests + docs together
6. **cross-platform-sync** -- Root repo is source of truth, mirror to .cursor/.codex/.opencode/.agents/
7. **release-sync** -- Synchronize package versions, plugin manifests, release docs
8. **learning-curation** -- Prefer small set of accurate instincts over bulk-generated ones

---

## 15. Schemas

| File | Description |
|------|-------------|
| ecc-install-config.schema.json | Install configuration validation |
| hooks.schema.json | Hook definition validation |
| install-components.schema.json | Component manifest validation |
| install-modules.schema.json | Module manifest validation |
| install-profiles.schema.json | Profile manifest validation |
| install-state.schema.json | Install state tracking |
| package-manager.schema.json | Package manager config validation |
| plugin.schema.json | Plugin manifest validation |
| state-store.schema.json | State store schema |

---

## 16. Scripts

### scripts/ci/ (CI validators)
validate-agents.js, validate-commands.js, validate-hooks.js, validate-install-manifests.js, validate-no-personal-paths.js, validate-rules.js, validate-skills.js, catalog.js

### scripts/hooks/ (30 hook implementations)
auto-tmux-dev.js, check-console-log.js, check-hook-enabled.js, cost-tracker.js, doc-file-warning.js, evaluate-session.js, governance-capture.js, insaits-security-monitor.py, insaits-security-wrapper.js, mcp-health-check.js, post-bash-build-complete.js, post-bash-pr-created.js, post-edit-console-warn.js, post-edit-format.js, post-edit-typecheck.js, pre-bash-dev-server-block.js, pre-bash-git-push-reminder.js, pre-bash-tmux-reminder.js, pre-compact.js, pre-write-doc-warn.js, quality-gate.js, run-with-flags-shell.sh, run-with-flags.js, session-end-marker.js, session-end.js, session-start.js, suggest-compact.js

### scripts/lib/ (core libraries)
agent-compress.js, hook-flags.js, inspection.js, install-executor.js, install-lifecycle.js, install-manifests.js, install-state.js, orchestration-session.js, package-manager.js, project-detect.js, resolve-ecc-root.js, resolve-formatter.js, session-manager.js, session-aliases.js, shell-split.js, tmux-worktree-orchestrator.js, utils.js

#### scripts/lib/install-targets/ (harness-specific installers)
antigravity-project.js, claude-home.js, codex-home.js, cursor-project.js, helpers.js, opencode-home.js, registry.js

#### scripts/lib/install/ (install pipeline)
apply.js, config.js, request.js, runtime.js

#### scripts/lib/session-adapters/
canonical-session.js, claude-history.js, dmux-tmux.js, registry.js

#### scripts/lib/skill-evolution/
dashboard.js, health.js, index.js, provenance.js, tracker.js, versioning.js

#### scripts/lib/skill-improvement/
amendify.js, evaluate.js, health.js, observations.js

#### scripts/lib/state-store/
index.js, migrations.js, queries.js, schema.js

### Top-level scripts
claw.js, doctor.js, ecc.js, harness-audit.js, install-apply.js, install-plan.js, list-installed.js, orchestrate-codex-worker.sh, orchestrate-worktrees.js, orchestration-status.js, release.sh, repair.js, session-inspect.js, sessions-cli.js, setup-package-manager.js, skill-create-output.js, skills-health.js, status.js, sync-ecc-to-codex.sh, uninstall.js

---

## 17. Tests

| Path | Description |
|------|-------------|
| tests/ci/validators.test.js | CI validator tests |
| tests/codex-config.test.js | Codex configuration tests |
| tests/hooks/ (16 test files) | Hook unit tests |
| tests/integration/hooks.test.js | Hook integration tests |
| tests/lib/ (20 test files) | Library unit tests |

---

## 18. Examples

| File | Description |
|------|-------------|
| examples/CLAUDE.md | Generic example CLAUDE.md |
| examples/django-api-CLAUDE.md | Django API project example |
| examples/go-microservice-CLAUDE.md | Go microservice example |
| examples/laravel-api-CLAUDE.md | Laravel API example |
| examples/rust-api-CLAUDE.md | Rust API example |
| examples/saas-nextjs-CLAUDE.md | SaaS Next.js example |
| examples/statusline.json | Statusline config example |
| examples/user-CLAUDE.md | User-level CLAUDE.md example |

---

## 19. Docs

| File | Description |
|------|-------------|
| docs/ANTIGRAVITY-GUIDE.md | Antigravity setup guide |
| docs/ARCHITECTURE-IMPROVEMENTS.md | Architecture improvement notes |
| docs/COMMAND-AGENT-MAP.md | Command to agent mapping |
| docs/ECC-2.0-SESSION-ADAPTER-DISCOVERY.md | Session adapter architecture |
| docs/MEGA-PLAN-REPO-PROMPTS-2026-03-12.md | Planning document |
| docs/PHASE1-ISSUE-BUNDLE-2026-03-12.md | Phase 1 issues |
| docs/PR-399-REVIEW-2026-03-12.md | PR review notes |
| docs/PR-QUEUE-TRIAGE-2026-03-13.md | PR queue triage |
| docs/SELECTIVE-INSTALL-ARCHITECTURE.md | Selective install architecture |
| docs/SELECTIVE-INSTALL-DESIGN.md | Selective install design |
| docs/SESSION-ADAPTER-CONTRACT.md | Session adapter contract |
| docs/business/metrics-and-sponsorship.md | Business metrics |
| docs/business/social-launch-copy.md | Social media copy |
| docs/continuous-learning-v2-spec.md | CL v2 specification |
| docs/releases/1.8.0/ | Release 1.8.0 notes and social copy |
| docs/token-optimization.md | Token optimization guide |
| docs/ja-JP/ | Japanese translations (full mirror) |
| docs/ko-KR/ | Korean translations (partial mirror) |
| docs/zh-CN/ | Chinese Simplified translations (full mirror) |
| docs/zh-TW/ | Chinese Traditional translations (partial mirror) |

---

## 20. Files That Did NOT Exist at Requested URLs

The following URLs from the original request do not correspond to actual files in the repo:

- `contexts/security-sops.md` -- Does NOT exist. The contexts/ directory only has dev.md, research.md, review.md.
- `contexts/tech-stack.md` -- Does NOT exist. Same reason.
- `.claude/settings.json` -- Does NOT exist. The closest file is `.claude/identity.json`.

There is no `.claude/agents/` directory. Agents live in the top-level `agents/` directory.

---

## 21. Relevance to PurpleOcaz

### Ideas worth adopting:

1. **Context modes (dev/research/review)** -- We could add context modes to our agents to switch between listing-building, research, and verification mindsets.

2. **Hook system** -- Their hooks.json pattern for PreToolUse/PostToolUse/Stop/SessionStart is well-structured. We already have a stop hook; could expand to session-start for auto-loading SOUL.md and latest digest.

3. **Instincts (continuous learning)** -- Their YAML-based instinct system captures repo-specific patterns with confidence scores and triggers. Could formalize our LESSONS.md into a similar structured format.

4. **Strategic compact** -- Their suggest-compact hook tracks context usage and suggests compaction. Could prevent our sessions from hitting context limits.

5. **Skill evolution tracking** -- Their skill-evolution/ library tracks skill health, provenance, and versioning. Could be adapted for tracking which listing templates perform well.

6. **Multi-harness support** -- Not immediately relevant, but the pattern of maintaining a source-of-truth root with mirrors to platform-specific dirs is clean architecture.

7. **Quality gate hooks** -- Post-edit quality gates could auto-run verify_listing.py after listing builds.

8. **Cost tracker** -- Token/cost tracking per session would help us understand the economics of automated listing creation.
