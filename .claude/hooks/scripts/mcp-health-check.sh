#!/usr/bin/env bash
# PurpleOcaz PreToolUse hook — MCP health check
# Warns before MCP calls if Canva MCP has consecutive failures.
# Always exits 0 (warning only, never blocks).

set -euo pipefail

# Read tool input from stdin (JSON with tool_name)
INPUT=$(cat)

# Extract tool name
TOOL_NAME=$(printf '%s' "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_name',''))" 2>/dev/null || echo "")

# Only care about MCP/Canva tool calls
case "$TOOL_NAME" in
  *mcp*|*canva*|*Canva*) ;;
  *) exit 0 ;;
esac

PROJECT_ROOT="/root/NEW-AI-PROJECT"
HEALTH_FILE="$PROJECT_ROOT/.claude/state/mcp_health.json"

# Create health file if missing
if [ ! -f "$HEALTH_FILE" ]; then
  mkdir -p "$(dirname "$HEALTH_FILE")"
  printf '{"failures":0,"status":"healthy","last_failure":""}' > "$HEALTH_FILE"
  exit 0
fi

# Check current status
STATUS=$(python3 -c "import json; print(json.load(open('$HEALTH_FILE')).get('status','healthy'))" 2>/dev/null || echo "healthy")

if [ "$STATUS" = "unhealthy" ]; then
  echo "MCP HEALTH WARNING: Canva MCP had consecutive failures — restart CC if calls keep failing"
fi

exit 0
