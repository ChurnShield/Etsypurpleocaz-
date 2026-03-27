---
name: stop-slop
description: "Etsy listing copy quality gate. Score titles, descriptions, and tag copy
              against stop-slop rules before publishing. Must reach 35/50. Loads
              automatically when writing or reviewing any Etsy listing copy."
user-invocable: false
---

# Stop Slop — Etsy Listing Copy Quality Gate

External skill by Hardik Pandya. Full rules live in:
- `skills/stop-slop/references/phrases.md` — banned phrases to remove
- `skills/stop-slop/references/structures.md` — structural patterns to avoid
- `skills/stop-slop/references/examples.md` — before/after transformations

Read those files before reviewing any listing copy.

---

## When This Applies

Before writing or submitting any Etsy listing **title**, **description**, or tag group.

CLAUDE.md hard rule: *"NEVER write Etsy listing copy without scoring at 35/50 first."*

---

## Core Rules (Summary)

1. **Cut filler phrases.** No throat-clearing openers, emphasis crutches, adverbs. See `phrases.md`.
2. **Break formulaic structures.** No binary contrasts, negative listings, dramatic fragmentation. See `structures.md`.
3. **Active voice only.** Every sentence needs a human subject doing something.
4. **Be specific.** No vague declaratives. Name the specific thing.
5. **No em dashes.** No Wh- sentence starters. No staccato fragmentation.
6. **Trust the buyer.** State facts directly. Skip softening and hand-holding.

---

## Etsy-Specific Checks

Before submitting listing copy, verify:

- [ ] Title: no "Here's what you get", no "Perfect for", no "Amazing"
- [ ] Title: leads with the product, not an adjective
- [ ] Description: first sentence states the product and buyer outcome — no preamble
- [ ] Description: bullet points list specific items, not vague benefits
- [ ] Description: no "you'll love", "game-changer", "take your business to the next level"
- [ ] Tags: plain keywords, not mini-sentences

---

## Scoring

Rate 1–10 on each dimension:

| Dimension | Question |
|-----------|----------|
| Directness | Statements or announcements? |
| Rhythm | Varied or metronomic? |
| Trust | Respects reader intelligence? |
| Authenticity | Sounds human? |
| Density | Anything cuttable? |

**Below 35/50: revise before publishing.** Flag the specific lines that dragged the score.

---

## When Exact Copy Is Provided

If Andy provides the listing copy verbatim — skip scoring and use it exactly as written.
The score gate applies only to copy you draft yourself.
