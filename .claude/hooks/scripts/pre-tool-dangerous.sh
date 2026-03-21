#!/usr/bin/env bash
# PurpleOcaz PreToolUse hook — Dangerous command blocker
# Blocks rm -rf, --force, DROP TABLE, --no-verify on Bash tool calls.
# Exit 2 = block, exit 0 = allow.

set -euo pipefail

# Read tool input from stdin (JSON with tool_input.command)
INPUT=$(cat)

# Extract the command string
COMMAND=$(printf '%s' "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null || echo "")

# Skip if no command found
if [ -z "$COMMAND" ]; then
  exit 0
fi

# Check for dangerous patterns
if printf '%s' "$COMMAND" | grep -qE 'rm\s+-rf'; then
  echo "BLOCKED: dangerous command detected (rm -rf) — requires explicit confirmation" >&2
  exit 2
fi

if printf '%s' "$COMMAND" | grep -qF -- '--force'; then
  echo "BLOCKED: dangerous command detected (--force) — requires explicit confirmation" >&2
  exit 2
fi

if printf '%s' "$COMMAND" | grep -qiF 'DROP TABLE'; then
  echo "BLOCKED: dangerous command detected (DROP TABLE) — requires explicit confirmation" >&2
  exit 2
fi

if printf '%s' "$COMMAND" | grep -qF -- '--no-verify'; then
  echo "BLOCKED: dangerous command detected (--no-verify) — requires explicit confirmation" >&2
  exit 2
fi

# No match — allow
exit 0
