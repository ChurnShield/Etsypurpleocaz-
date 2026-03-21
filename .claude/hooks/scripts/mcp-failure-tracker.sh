#!/usr/bin/env bash
# PurpleOcaz PostToolUse hook — MCP failure tracker
# Tracks consecutive MCP failures and marks status unhealthy after 2+.
# Resets on success. Always exits 0.

set -euo pipefail

# Read tool input from stdin (JSON with tool_name, tool_response)
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
fi

# Detect success or failure from tool_response
# PostToolUse stdin includes tool_response — check for error indicators
FAILED=$(printf '%s' "$INPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
resp = data.get('tool_response', {})
# Check multiple failure signals
if isinstance(resp, str) and ('error' in resp.lower() or 'failed' in resp.lower()):
    print('true')
elif isinstance(resp, dict):
    if resp.get('error') or resp.get('is_error') or not resp.get('success', True):
        print('true')
    else:
        print('false')
else:
    print('false')
" 2>/dev/null || echo "false")

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

if [ "$FAILED" = "true" ]; then
  # Increment failures, mark unhealthy if >= 2
  python3 -c "
import json
with open('$HEALTH_FILE') as f:
    h = json.load(f)
h['failures'] = h.get('failures', 0) + 1
h['last_failure'] = '$TIMESTAMP'
if h['failures'] >= 2:
    h['status'] = 'unhealthy'
with open('$HEALTH_FILE', 'w') as f:
    json.dump(h, f)
print(h['failures'])
" 2>/dev/null | while read -r COUNT; do
    echo "MCP failure #${COUNT} recorded"
  done
else
  # Success — reset to healthy
  printf '{"failures":0,"status":"healthy","last_failure":""}' > "$HEALTH_FILE"
fi

exit 0
