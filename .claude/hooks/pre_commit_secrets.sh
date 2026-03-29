#!/usr/bin/env bash
# Blocks git commit if staged files contain secrets
set -euo pipefail
INPUT=$(cat)
COMMAND=$(printf '%s' "$INPUT" | python3 -c "
import sys,json
cmd = json.load(sys.stdin).get('tool_input',{}).get('command','')
print(cmd)
" 2>/dev/null || echo "")

if printf '%s' "$COMMAND" | grep -qE 'git\s+commit'; then
  SECRETS=$(cd /root/NEW-AI-PROJECT && git diff --cached --diff-filter=ACM 2>/dev/null | grep -iE '(sk-ant-api|gsk_[A-Za-z0-9]{20,}|AIzaSy[A-Za-z0-9_-]{30,}|ghp_[A-Za-z0-9]{30,}|PINTEREST_PASSWORD=)' | grep -v 'YOUR_\|REDACTED\|grep\|echo' | head -5)
  if [ -n "$SECRETS" ]; then
    echo "BLOCKED: Secrets detected in staged files:" >&2
    echo "$SECRETS" >&2
    exit 2
  fi
fi
exit 0
