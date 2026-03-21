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
echo "Session saved"
