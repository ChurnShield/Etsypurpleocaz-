#!/usr/bin/env bash
# Learning loop: log a failure + fix to LESSONS.md
#
# Called by CC after every significant task that fails or hits a gotcha.
# Usage: bash hooks/on_task_fail.sh "Task name" "What failed" "Root cause" "Fix applied"
#
# Example:
#   bash hooks/on_task_fail.sh \
#     "Etsy image upload" \
#     "POST returned 400 on tag field" \
#     "Tags passed as JSON array instead of comma-separated string" \
#     "Changed to comma-separated string in request body"

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LESSONS_FILE="$PROJECT_ROOT/LESSONS.md"

TASK_NAME="${1:?Usage: on_task_fail.sh \"Task name\" \"What failed\" \"Root cause\" \"Fix applied\"}"
WHAT_FAILED="${2:?Usage: on_task_fail.sh \"Task name\" \"What failed\" \"Root cause\" \"Fix applied\"}"
ROOT_CAUSE="${3:?Usage: on_task_fail.sh \"Task name\" \"What failed\" \"Root cause\" \"Fix applied\"}"
FIX_APPLIED="${4:?Usage: on_task_fail.sh \"Task name\" \"What failed\" \"Root cause\" \"Fix applied\"}"
DATE="$(date '+%Y-%m-%d')"
TIME="$(date '+%H:%M')"

# Create LESSONS.md if somehow missing
if [[ ! -f "$LESSONS_FILE" ]]; then
    cat > "$LESSONS_FILE" <<'HEADER'
# Lessons Learned

A living document updated every session. Most recent entries first.

---
HEADER
fi

# Build the entry
ENTRY="\n### ${DATE} ${TIME} — ${TASK_NAME}\n\n**Rule:** ${WHAT_FAILED}\n\n**Why:** ${ROOT_CAUSE}\n\n**How to apply:** ${FIX_APPLIED}\n\n---"

# Insert after the first --- (the header separator)
sed -i "0,/^---$/{ /^---$/a\\${ENTRY}
}" "$LESSONS_FILE"

echo "[learn] Lesson logged: ${TASK_NAME}"
