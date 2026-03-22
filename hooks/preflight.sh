#!/usr/bin/env bash
# Pre-flight session summary — reads SOUL.md, STANDUP.md, LESSONS.md
# and outputs a condensed session brief.
#
# Usage: bash hooks/preflight.sh
# Add to CLAUDE.md as required first step every session.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "========================================="
echo "  PRE-FLIGHT SESSION SUMMARY"
echo "  $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "========================================="
echo ""

# ── SOUL.md: Mission reminder ──
if [[ -f "$PROJECT_ROOT/SOUL.md" ]]; then
    echo "--- MISSION (SOUL.md) ---"
    # Extract the mission and what-good-looks-like sections
    sed -n '/^## The Mission$/,/^---$/p' "$PROJECT_ROOT/SOUL.md" | head -8
    echo ""
else
    echo "!!! SOUL.md IS MISSING — STOP AND RESTORE IT !!!"
    exit 1
fi

# ── STANDUP.md: Latest standup ──
if [[ -f "$PROJECT_ROOT/STANDUP.md" ]]; then
    echo "--- LATEST STANDUP (STANDUP.md) ---"
    # Extract the most recent standup entry (first ## block after the header)
    awk '/^## [0-9]/{if(found) exit; found=1} found{print}' "$PROJECT_ROOT/STANDUP.md"
    echo ""
else
    echo "(No STANDUP.md found)"
fi

# ── LESSONS.md: Last 3 lessons ──
if [[ -f "$PROJECT_ROOT/LESSONS.md" ]]; then
    echo "--- RECENT LESSONS (LESSONS.md) ---"
    # Show the 3 most recent lesson headers with their Rule line
    awk '/^### [0-9]/{count++; if(count>3) exit; print} /^\*\*Rule:\*\*/{if(count<=3) print}' "$PROJECT_ROOT/LESSONS.md"
    echo ""
else
    echo "(No LESSONS.md found)"
fi

# ── Git status snapshot ──
echo "--- GIT STATUS ---"
cd "$PROJECT_ROOT"
echo "Branch: $(git branch --show-current 2>/dev/null || echo 'unknown')"
echo "Uncommitted changes: $(git status --porcelain 2>/dev/null | wc -l) files"
echo ""

echo "========================================="
echo "  Pre-flight complete. Let's build."
echo "========================================="
