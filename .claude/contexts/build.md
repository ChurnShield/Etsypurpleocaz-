---
name: build
description: "Active during listing builds, pipeline runs, Canva/Etsy API work. Terse, fast, verify everything."
type: context
---

# Build Context

Mode: Active listing build / pipeline execution
Focus: Ship working listings, verify every step, no wasted words

## Behaviour

- Terse output. No explanations unless Andy asks.
- Run planner agent first to break the task into steps.
- Run verifier agent after each completed step.
- One transaction at a time. Commit before next.
- GET after every POST. Never report success from POST response alone.
- If a step fails, stop and diagnose — do not retry blindly.

## Priorities

1. Get it built correctly
2. Get it verified
3. Get it pushed to Etsy

## Rules Enforced

These rules are mandatory in build mode — violations are blockers:

- `.claude/rules/canva.md` — delivery links, transaction safety, element limits
- `.claude/rules/etsy.md` — tags, pricing, PATCH only, verification
- `.claude/rules/pipeline.md` — image sources, hero thumbnail pipeline, design registry

## Agent Sequence

1. **Planner** — break the build into numbered steps with definitions of done
2. **Execute** — work through each step
3. **Verifier** — after each step, confirm the output matches the definition of done
4. **Verifier (final)** — run `verify_listing.py` on completed listings

## Tools to Favour

- Canva MCP tools for design work
- Bash for Etsy API calls and verify_listing.py
- Write for delivery PDFs and config updates

## Tools to Avoid

- WebSearch, WebFetch (that's research mode)
- Agent with researcher subtype (save for /context research)

## Output Format

Status updates only:
```
[step 1/5] Hero thumbnail exported — 1587x2245, uploaded to Spaces
[step 2/5] Listing created — draft #4472977919, price £2.99
...
[DONE] All 5 steps complete. verify_listing.py: PASS
```
