#!/usr/bin/env bash
# .claude/hooks/stop.sh — Session end checklist reminder
#
# Runs on every Stop event. Only outputs a reminder when it detects
# uncommitted session-end tasks (CHANGELOG, LESSONS, SESSION_START).
# Silent when everything looks up to date — no noise.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_ROOT"

missing=()

# Check if CHANGELOG.md has uncommitted changes (staged or unstaged)
if ! git diff --name-only HEAD -- CHANGELOG.md 2>/dev/null | grep -q .; then
    if ! git diff --cached --name-only -- CHANGELOG.md 2>/dev/null | grep -q .; then
        missing+=("CHANGELOG.md")
    fi
fi

# Check if LESSONS.md has uncommitted changes
if ! git diff --name-only HEAD -- LESSONS.md 2>/dev/null | grep -q .; then
    if ! git diff --cached --name-only -- LESSONS.md 2>/dev/null | grep -q .; then
        missing+=("LESSONS.md")
    fi
fi

# Check if SESSION_START.md has uncommitted changes
if ! git diff --name-only HEAD -- SESSION_START.md 2>/dev/null | grep -q .; then
    if ! git diff --cached --name-only -- SESSION_START.md 2>/dev/null | grep -q .; then
        missing+=("SESSION_START.md")
    fi
fi

# Check for any unpushed commits
unpushed=$(git log --oneline @{upstream}..HEAD 2>/dev/null | wc -l || echo "0")

# Only output if something needs attention
if [ ${#missing[@]} -gt 0 ] || [ "$unpushed" -gt 0 ]; then
    echo "SESSION END CHECKLIST — items need attention:"
    for file in "${missing[@]}"; do
        echo "  [ ] Update $file"
    done
    if [ "$unpushed" -gt 0 ]; then
        echo "  [ ] Push $unpushed unpushed commit(s) to remote"
    fi
    echo "  [ ] Verify Google Sheet queue is up to date"
fi
