#!/usr/bin/env bash
# PurpleOcaz Stop hook — Session cost tracker
# Logs session duration and approximate tool call count.
# Always exits 0.

set -euo pipefail

PROJECT_ROOT="/root/NEW-AI-PROJECT"
STATE_DIR="$PROJECT_ROOT/.claude/state"
LOG_FILE="$STATE_DIR/session_costs.log"
START_FILE="$STATE_DIR/session_start_ts"
STATE_FILE="$STATE_DIR/session_state.md"

mkdir -p "$STATE_DIR"

# Read tool input from stdin
INPUT=$(cat)

# --- Session start time ---
# Use session_start_ts if it exists (set by first cost-tracker run or session-start)
# Otherwise snapshot current time as start and return (first call of session)
if [ ! -f "$START_FILE" ]; then
  date -u +"%Y-%m-%dT%H:%M:%SZ" > "$START_FILE"
  # First stop of this session — just record start, skip logging
  exit 0
fi

START_TS=$(cat "$START_FILE" 2>/dev/null || echo "")
if [ -z "$START_TS" ]; then
  exit 0
fi

# --- Duration ---
NOW_EPOCH=$(date +%s)
START_EPOCH=$(date -d "$START_TS" +%s 2>/dev/null || echo "$NOW_EPOCH")
DURATION_SECS=$((NOW_EPOCH - START_EPOCH))
DURATION_MINS=$((DURATION_SECS / 60))

# --- Tool call count (approximate) ---
# Count lines with common tool-use markers in session state
TOOL_CALLS=0
if [ -f "$STATE_FILE" ]; then
  TOOL_CALLS=$(grep -cE '^\s*\*|tool_|Tool |Bash|Read|Write|Edit|Glob|Grep|mcp__|WebFetch' "$STATE_FILE" 2>/dev/null || echo "0")
fi

# Fall back to counting stop hook invocations as a proxy
# Each stop = one Claude response = ~1-3 tool calls
if [ "$TOOL_CALLS" -eq 0 ] && [ -f "$LOG_FILE" ]; then
  # Use line count as rough session counter
  TOOL_CALLS="n/a"
fi

# --- Session number ---
if [ -f "$LOG_FILE" ]; then
  PREV_SESSIONS=$(wc -l < "$LOG_FILE" 2>/dev/null || echo "0")
else
  PREV_SESSIONS=0
fi
SESSION_NUM=$((PREV_SESSIONS + 1))

# --- Log entry ---
DATE_SHORT=$(date +"%Y-%m-%d %H:%M")
echo "${DATE_SHORT} | DURATION: ${DURATION_MINS}m | TOOL_CALLS: ${TOOL_CALLS} | SESSION: #${SESSION_NUM}" >> "$LOG_FILE"

# --- Output ---
echo "Session #${SESSION_NUM} | Duration: ${DURATION_MINS}m | Tool calls: ~${TOOL_CALLS}"

exit 0
