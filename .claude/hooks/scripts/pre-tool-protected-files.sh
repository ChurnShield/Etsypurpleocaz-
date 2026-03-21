#!/usr/bin/env bash
# PurpleOcaz PreToolUse hook — Protected file warning
# Warns when Write or Edit targets a protected file.
# Always exits 0 (warning only, never blocks).

set -euo pipefail

# Read tool input from stdin (JSON with tool_input.file_path)
INPUT=$(cat)

# Extract the file path
FILE_PATH=$(printf '%s' "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))" 2>/dev/null || echo "")

# Skip if no file path found
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Extract just the filename for matching
FILENAME=$(basename "$FILE_PATH")

# Check for protected file patterns
PROTECTED=false

case "$FILENAME" in
  SOUL.md)        PROTECTED=true ;;
  CLAUDE.md)      PROTECTED=true ;;
  .env)           PROTECTED=true ;;
  .env.*)         PROTECTED=true ;;
esac

# Check for token/credential files by pattern
if printf '%s' "$FILENAME" | grep -qiE 'tokens\.json$'; then
  PROTECTED=true
fi

if printf '%s' "$FILENAME" | grep -qiE 'credentials'; then
  PROTECTED=true
fi

# Also catch .env files in subdirectories
if printf '%s' "$FILE_PATH" | grep -qE '/\.env$|/\.env\.'; then
  PROTECTED=true
fi

if [ "$PROTECTED" = true ]; then
  echo "WARNING: editing protected file ($FILENAME) — confirm this is intentional"
fi

# Always allow — this is a warning, not a blocker
exit 0
