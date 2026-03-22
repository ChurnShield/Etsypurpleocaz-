#!/usr/bin/env bash
# Learning loop: log a successful pattern to WINS.md
#
# Called by CC after every significant task that succeeds.
# Usage: bash hooks/on_task_complete.sh "Task name" "What worked and why"
#
# Example:
#   bash hooks/on_task_complete.sh \
#     "Hero thumbnail swap" \
#     "One Canva transaction per card side, commit between. Verified export visually before upload."

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WINS_FILE="$PROJECT_ROOT/WINS.md"

TASK_NAME="${1:?Usage: on_task_complete.sh \"Task name\" \"What worked and why\"}"
PATTERN="${2:?Usage: on_task_complete.sh \"Task name\" \"What worked and why\"}"
DATE="$(date '+%Y-%m-%d')"
TIME="$(date '+%H:%M')"

# Create WINS.md if somehow missing
if [[ ! -f "$WINS_FILE" ]]; then
    cat > "$WINS_FILE" <<'HEADER'
# Wins

Successful patterns captured automatically after each significant task.
Most recent first. Read this to repeat what works.

---
HEADER
fi

# Insert new entry after the --- header line (line 6)
ENTRY="\n### ${DATE} ${TIME} — ${TASK_NAME}\n\n**Pattern:** ${PATTERN}\n\n---"

# Use sed to append after the first --- (the header separator)
sed -i "0,/^---$/{ /^---$/a\\${ENTRY}
}" "$WINS_FILE"

echo "[learn] Win logged: ${TASK_NAME}"
