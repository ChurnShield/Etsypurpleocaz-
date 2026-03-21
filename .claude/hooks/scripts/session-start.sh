#!/usr/bin/env bash
# PurpleOcaz SessionStart hook
# Loads core context files and prior session state into the conversation.

set -euo pipefail

PROJECT_ROOT="/root/NEW-AI-PROJECT"

echo "=== PURPLEOCAZ SESSION START ==="
echo ""

# 1. Load SOUL.md
if [ -f "$PROJECT_ROOT/SOUL.md" ]; then
  echo "[session-start] SOUL.md loaded"
else
  echo "[session-start] WARNING: SOUL.md is MISSING — stop and restore it"
fi

# 2. Load STANDUP.md (last 30 lines = most recent standup)
if [ -f "$PROJECT_ROOT/STANDUP.md" ]; then
  echo "[session-start] STANDUP.md loaded (latest entry):"
  head -40 "$PROJECT_ROOT/STANDUP.md" | tail -35
  echo ""
fi

# 3. Load LESSONS.md (last entry)
if [ -f "$PROJECT_ROOT/LESSONS.md" ]; then
  echo "[session-start] LESSONS.md loaded (latest lesson):"
  # Show everything up to the second --- separator (= latest entry)
  awk '/^---$/{c++} c==2{exit} {print}' "$PROJECT_ROOT/LESSONS.md" | tail -20
  echo ""
fi

# 4. Load prior session state if it exists
STATE_FILE="$PROJECT_ROOT/.claude/state/session_state.md"
if [ -f "$STATE_FILE" ]; then
  echo "[session-start] Prior session state found:"
  cat "$STATE_FILE"
  echo ""
else
  echo "[session-start] No prior session state (fresh start)"
fi

# 5. Show what was learned in the last session
LEARNED_DIR="$PROJECT_ROOT/.claude/skills/learned"
if [ -d "$LEARNED_DIR" ]; then
  LATEST_LEARNED=$(ls -t "$LEARNED_DIR"/*.md 2>/dev/null | head -1)
  if [ -n "$LATEST_LEARNED" ]; then
    LEARNED_NAME=$(basename "$LATEST_LEARNED" .md)
    echo "[session-start] Last learned pattern: $LEARNED_NAME"
    # Show the frontmatter description and Problem/Solution sections
    awk '/^---$/{fm++; next} fm==1 && /^description:/{print "  " $0} fm>=2 && /^## (Problem|Solution)/{show=1; print "  " $0; next} fm>=2 && show && /^## /{show=0} show{print "  " $0}' "$LATEST_LEARNED"
    echo ""
  else
    echo "[session-start] No learned patterns yet"
    echo ""
  fi
fi

echo ""
echo "PurpleOcaz brain loaded"
echo "=== SESSION READY ==="
