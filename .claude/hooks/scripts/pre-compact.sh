#!/usr/bin/env bash
# PurpleOcaz PreCompact hook
# Saves context state before compression so nothing critical is lost.

set -euo pipefail

PROJECT_ROOT="/root/NEW-AI-PROJECT"
STATE_DIR="$PROJECT_ROOT/.claude/state"
COMPACT_FILE="$STATE_DIR/pre_compact_state.md"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

mkdir -p "$STATE_DIR"

# Read the tool input from stdin
INPUT=$(cat)

cat > "$COMPACT_FILE" << EOF
---
compacted_at: $TIMESTAMP
---

# Pre-Compact State

Context was compacted at $TIMESTAMP.

## Active tasks at time of compaction
Check TaskList for current task state.

## Key context to preserve
- Always re-read SOUL.md after compaction
- Check .claude/state/session_state.md for session continuity
- Check STANDUP.md for today's progress
- Re-read any files you were actively editing

## Session state at compaction
$(cat "$STATE_DIR/session_state.md" 2>/dev/null || echo "(no session state file)")
EOF

echo "[pre-compact] State saved to $COMPACT_FILE before compaction"

# Pass through stdin for Claude Code
printf '%s' "$INPUT"
