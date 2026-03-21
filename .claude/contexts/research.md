---
name: research
description: "Active during niche analysis, competitor research, keyword research. Thorough, cite sources, structured reports."
type: context
---

# Research Context

Mode: Exploration, investigation, market analysis
Focus: Understand before acting — never mix research with build work

## Behaviour

- Read widely before drawing conclusions.
- Cite every source (URL, listing ID, search query).
- Output structured reports to `research/{niche}/report.md`.
- Ask clarifying questions if the research scope is unclear.
- Do NOT write code, create listings, or edit designs in this mode.
- Do NOT start building until research is complete and Andy approves the findings.

## Priorities

1. Understand the niche / keyword / competitor landscape
2. Document findings with evidence
3. Recommend actions (but don't execute them)

## Rules Enforced

No pipeline or API rules apply — this is read-only mode.

## Agent Sequence

1. **Researcher** — the only agent used in this mode
2. No planner, verifier, or debug agents unless Andy explicitly asks

## Research Process

1. Define the question (what are we trying to learn?)
2. Search Etsy, Google, competitor shops
3. Collect data: prices, tags, reviews, sales counts, listing quality
4. Analyse patterns and gaps
5. Write report with recommendations
6. Wait for Andy's decision before switching to build mode

## Output Format

All research outputs follow this structure:

```markdown
# Research Report: {Niche/Topic}

**Date:** YYYY-MM-DD
**Query:** {what we searched for}

## Key Findings
1. Finding with evidence
2. Finding with evidence

## Competitor Analysis
| Shop | Listing | Price | Sales | Quality |
|------|---------|-------|-------|---------|

## Keyword Opportunities
| Keyword | Competition | Search Volume | Gap |
|---------|------------|---------------|-----|

## Recommendations
- Action 1 (with reasoning)
- Action 2 (with reasoning)

## Sources
- [source 1](url)
- [source 2](url)
```

## Tools to Favour

- WebSearch, WebFetch for market data
- Bash for Etsy API search queries
- Read, Grep for analysing existing listings and transcripts

## Tools to Avoid

- Canva MCP tools (that's build mode)
- Write for listing content (save for build mode)
- Edit on any pipeline or config files
