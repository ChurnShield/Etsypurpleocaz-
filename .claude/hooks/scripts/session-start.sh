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

echo ""
echo "PurpleOcaz brain loaded"
echo "=== SESSION READY ==="
