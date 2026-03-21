#!/usr/bin/env bash
# PurpleOcaz PostToolUse hook — Auto-verify after Etsy API calls
# Reminds to GET-verify after any POST/PUT to Etsy endpoints.
# Always exits 0.

set -euo pipefail

# Read tool input from stdin (JSON with tool_input.command)
INPUT=$(cat)

# Extract the command string
COMMAND=$(printf '%s' "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null || echo "")

# Skip if no command found
if [ -z "$COMMAND" ]; then
  exit 0
fi

# Check if command involves Etsy/listings AND a mutating method
HAS_ETSY=false
HAS_MUTATE=false

if printf '%s' "$COMMAND" | grep -qiE 'etsy|listings'; then
  HAS_ETSY=true
fi

if printf '%s' "$COMMAND" | grep -qiE '\bPOST\b|\bPUT\b|\bPATCH\b'; then
  HAS_MUTATE=true
fi

if [ "$HAS_ETSY" = true ] && [ "$HAS_MUTATE" = true ]; then
  echo "VERIFY REQUIRED: run GET to confirm this change took effect"
fi

# Always allow
exit 0
