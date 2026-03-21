# /learn - Extract Reusable Patterns from This Session

Analyse the current session and extract any patterns worth saving as skills.

## Trigger

Run `/learn` at any point during a session when you've solved a non-trivial problem or discovered something reusable.

## What to Extract

Look for these pattern types in the current session:

1. **Error Resolution Patterns**
   - What error occurred?
   - What was the root cause?
   - What fixed it?
   - Is this reusable for similar errors?

2. **API Workarounds**
   - Etsy API quirks (tag limits, price patching, auth refresh)
   - Canva MCP limitations (element types, transaction safety)
   - DO Spaces gotchas (ACL, credential paths)

3. **Pipeline Patterns**
   - New listing build steps that worked
   - Image generation techniques (Pillow, Ideogram, compositing)
   - Delivery PDF structure that converted

4. **Tool Combinations**
   - Multi-tool workflows that solved a problem efficiently
   - MCP tool sequences that worked first time

5. **Business Insights**
   - Pricing discoveries, competitor patterns
   - SEO/tag strategies that drove impressions
   - Niche-specific learnings

## Process

1. Review the current session for extractable patterns
2. For each pattern found, create a skill file
3. Append a summary line to LESSONS.md
4. Report what was learned

## Output Format

For each pattern, create a dated skill file at `.claude/skills/learned/YYYY-MM-DD-[pattern-name].md`:

```markdown
---
name: [pattern-name]
description: "[One-line description of when this pattern applies]"
type: learned
extracted: [YYYY-MM-DD]
source_session: "[Brief description of what triggered this learning]"
---

# [Descriptive Pattern Name]

## Problem
[What problem this solves - be specific]

## Solution
[The pattern/technique/workaround - include exact commands, parameters, or code]

## Example
[Concrete example from this session]

## When to Apply
[Trigger conditions - what should activate this pattern in future sessions]

## Why This Matters for PurpleOcaz
[How this connects to the mission: listings, revenue, automation, scale]
```

## After Saving

1. Append a one-line summary to `LESSONS.md` under today's date heading:
   ```
   ### YYYY-MM-DD — [Pattern Name]
   **Rule:** [one-sentence rule]
   **Why:** [one-sentence reason]
   **How to apply:** [one-sentence instruction]
   ```

2. Confirm to the user:
   ```
   Learned: [pattern name]
   Saved to: .claude/skills/learned/[filename]
   Added to: LESSONS.md
   ```

## Rules

- Don't extract trivial fixes (typos, simple syntax errors)
- Don't extract one-time issues (specific API outages, temporary state)
- Focus on patterns that will save time in future sessions
- Keep skills focused — one pattern per skill file
- Always include concrete values (hex codes, pixel sizes, API endpoints) not vague descriptions
- If a pattern already exists in LESSONS.md, update it rather than duplicating
- PurpleOcaz context matters — frame everything in terms of the pipeline and business
