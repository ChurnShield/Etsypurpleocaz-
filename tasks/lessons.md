# Lessons Learned

Track patterns from corrections and mistakes to prevent repeating them.

## Format

Each lesson follows this pattern:
- **Date**: When the lesson was learned
- **Trigger**: What went wrong or what correction was received
- **Rule**: The rule to prevent this in the future
- **Context**: Which part of the codebase was affected

---

## Lessons

### 2026-03-08 — Session URL is not an API error
- **Trigger**: Confused session reference URL in commit messages with an actual API error
- **Rule**: The `https://claude.ai/code/session_...` link appended to commits is metadata, not a functioning endpoint. Do not treat it as an API error.
- **Context**: Git commit messages

---

_Add new lessons above this line. Review at the start of every session._
