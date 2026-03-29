#!/usr/bin/env bash
# PurpleOcaz PreToolUse hook — Anti-deletion safety guard
# Blocks rm -rf, git clean -fd, git reset --hard.
# Input: JSON on stdin with tool_input.command
# Exit 2 = block and show error, exit 0 = allow.

set -euo pipefail

INPUT=$(cat)
COMMAND=$(printf '%s' "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null || echo "")

if [ -z "$COMMAND" ]; then
  exit 0
fi

if printf '%s' "$COMMAND" | grep -qE 'rm\s+-rf|rm\s+.*-[a-zA-Z]*r[a-zA-Z]*f'; then
  echo "BLOCKED: rm -rf detected — confirm with Andy before deleting recursively" >&2
  exit 2
fi

if printf '%s' "$COMMAND" | grep -qE 'git\s+(clean\s+.*-[a-zA-Z]*f|clean\s+-f)'; then
  echo "BLOCKED: git clean -f* detected — this deletes untracked files permanently" >&2
  exit 2
fi

if printf '%s' "$COMMAND" | grep -qE 'git\s+reset\s+--hard'; then
  echo "BLOCKED: git reset --hard detected — this discards uncommitted changes permanently" >&2
  exit 2
fi

exit 0
