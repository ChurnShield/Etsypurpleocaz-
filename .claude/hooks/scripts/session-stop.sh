#!/usr/bin/env bash
# PurpleOcaz Stop hook
# Persists session state after each response so nothing is lost.

set -euo pipefail

PROJECT_ROOT="/root/NEW-AI-PROJECT"
STATE_DIR="$PROJECT_ROOT/.claude/state"
STATE_FILE="$STATE_DIR/session_state.md"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATE_SHORT=$(date +"%Y-%m-%d")

mkdir -p "$STATE_DIR"

# Read tool input from stdin (Claude Code passes JSON with transcript info)
INPUT=$(cat)

# Write session state file
cat > "$STATE_FILE" << EOF
---
saved_at: $TIMESTAMP
---

# Session State

**Last active:** $TIMESTAMP

## What was being worked on
(Updated automatically by Stop hook — Claude should update this via the command)

## What was accomplished
(Populated by session activity)

## What's next
(Carry forward to next session)
EOF

echo "[session-stop] Session state saved to $STATE_FILE"

# Ensure learned skills directory exists
LEARNED_DIR="$PROJECT_ROOT/.claude/skills/learned"
mkdir -p "$LEARNED_DIR"

# Count learned patterns saved this session (modified today)
TODAY=$(date +"%Y-%m-%d")
LEARNED_TODAY=$(find "$LEARNED_DIR" -name "${TODAY}-*.md" -type f 2>/dev/null | wc -l)

echo "Session saved"
echo ""
echo "=== AUTO-LEARN TRIGGER ==="
echo "INSTRUCTION: Before ending this session, run /learn to extract reusable patterns."
echo "Save any new patterns to .claude/skills/learned/ following the format in .claude/commands/learn.md."
echo "Patterns already saved today: $LEARNED_TODAY"
echo "After extracting patterns, print: Patterns extracted and saved"
echo "=== END AUTO-LEARN ==="
