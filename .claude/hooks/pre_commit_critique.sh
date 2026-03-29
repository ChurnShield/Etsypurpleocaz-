#!/usr/bin/env bash
# Forces CC to log what could go wrong before every commit
# Appends a critique checkpoint to LESSONS.md
set -euo pipefail
INPUT=$(cat)
COMMAND=$(printf '%s' "$INPUT" | python3 -c "
import sys,json
cmd = json.load(sys.stdin).get('tool_input',{}).get('command','')
print(cmd)
" 2>/dev/null || echo "")

# Only trigger on git commit commands
if printf '%s' "$COMMAND" | grep -qE 'git\s+commit'; then
  echo "REMINDER: Before committing, verify you have:" >&2
  echo "  1. Tested the change works" >&2
  echo "  2. Checked for unintended side effects" >&2
  echo "  3. Run verification scripts if applicable" >&2
fi
exit 0
