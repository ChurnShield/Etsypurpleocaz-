#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# sync.sh — Single command to sync this repo across devices
#
# Usage:
#   ./scripts/sync.sh          Pull latest, show status
#   ./scripts/sync.sh push     Add all, commit, push
#   ./scripts/sync.sh status   Show what's changed + roadmap
# ──────────────────────────────────────────────────────────────

set -euo pipefail

PURPLE='\033[0;35m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'

cd "$(git rev-parse --show-toplevel)"

# ── Helpers ──────────────────────────────────────────────────

print_header() {
    echo ""
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${PURPLE}  $1${NC}"
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

retry_with_backoff() {
    local cmd="$1"
    local max_retries=4
    local delay=2

    for ((i=1; i<=max_retries; i++)); do
        if eval "$cmd"; then
            return 0
        fi
        if [ $i -lt $max_retries ]; then
            echo -e "${YELLOW}  Retry $i/$max_retries in ${delay}s...${NC}"
            sleep $delay
            delay=$((delay * 2))
        fi
    done
    echo -e "${RED}  Failed after $max_retries attempts${NC}"
    return 1
}

show_status() {
    print_header "Repo Status"

    local branch
    branch=$(git branch --show-current)
    echo -e "  Branch: ${BOLD}$branch${NC}"

    local behind ahead
    behind=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "?")
    ahead=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "?")
    echo -e "  Behind main: ${behind}  |  Ahead of main: ${ahead}"

    local changed
    changed=$(git status --short | wc -l)
    if [ "$changed" -gt 0 ]; then
        echo -e "  ${YELLOW}Uncommitted changes: $changed files${NC}"
        git status --short | head -10
        if [ "$changed" -gt 10 ]; then
            echo "  ... and $((changed - 10)) more"
        fi
    else
        echo -e "  ${GREEN}Working tree clean${NC}"
    fi

    echo ""
    echo -e "  ${BOLD}Last 5 commits:${NC}"
    git log --oneline -5 | sed 's/^/    /'

    # Show roadmap summary if it exists
    if [ -f "ROADMAP.md" ]; then
        echo ""
        print_header "Roadmap"
        # Count tasks by status
        local done pending in_progress
        done=$(grep -c '\- \[x\]' ROADMAP.md 2>/dev/null || echo 0)
        pending=$(grep -c '\- \[ \]' ROADMAP.md 2>/dev/null || echo 0)
        in_progress=$(grep -c '\- \[~\]' ROADMAP.md 2>/dev/null || echo 0)
        echo -e "  ${GREEN}Done: $done${NC}  |  ${YELLOW}In Progress: $in_progress${NC}  |  Pending: $pending"

        # Show in-progress items
        if [ "$in_progress" -gt 0 ]; then
            echo ""
            echo -e "  ${BOLD}Currently working on:${NC}"
            grep '\- \[~\]' ROADMAP.md | sed 's/^/    /'
        fi

        # Show next pending items
        if [ "$pending" -gt 0 ]; then
            echo ""
            echo -e "  ${BOLD}Up next:${NC}"
            grep '\- \[ \]' ROADMAP.md | head -3 | sed 's/^/    /'
        fi
    fi
    echo ""
}

# ── Commands ─────────────────────────────────────────────────

cmd_pull() {
    print_header "Syncing from remote"
    retry_with_backoff "git fetch origin main"

    # Check if we need to merge
    local behind
    behind=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo 0)

    if [ "$behind" -gt 0 ]; then
        echo -e "  ${YELLOW}$behind new commits from remote — merging...${NC}"
        git merge origin/main --no-edit
        echo -e "  ${GREEN}Merged successfully${NC}"
    else
        echo -e "  ${GREEN}Already up to date${NC}"
    fi

    show_status
}

cmd_push() {
    print_header "Pushing to remote"

    # Check for changes
    local changed
    changed=$(git status --short | wc -l)
    if [ "$changed" -eq 0 ]; then
        echo -e "  ${GREEN}Nothing to push — working tree clean${NC}"
        return 0
    fi

    # Pull first to avoid conflicts
    echo -e "  ${YELLOW}Pulling latest before push...${NC}"
    retry_with_backoff "git fetch origin main"

    local behind
    behind=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo 0)
    if [ "$behind" -gt 0 ]; then
        git merge origin/main --no-edit
    fi

    # Stage and commit
    git add -A
    echo ""
    echo -e "  ${BOLD}Changes to commit:${NC}"
    git diff --cached --stat | sed 's/^/    /'
    echo ""

    # Auto-generate commit message from changed files
    local msg
    msg="Sync: $(git diff --cached --name-only | head -5 | tr '\n' ', ' | sed 's/,$//')"

    read -p "  Commit message [$msg]: " custom_msg
    msg="${custom_msg:-$msg}"

    git commit -m "$msg"
    retry_with_backoff "git push -u origin main"

    echo -e "  ${GREEN}Pushed successfully${NC}"
    echo ""
}

# ── Main ─────────────────────────────────────────────────────

case "${1:-pull}" in
    pull|sync)
        cmd_pull
        ;;
    push)
        cmd_push
        ;;
    status|s)
        git fetch origin main 2>/dev/null
        show_status
        ;;
    *)
        echo "Usage: ./scripts/sync.sh [pull|push|status]"
        echo ""
        echo "  pull     Fetch + merge latest from main (default)"
        echo "  push     Stage all, commit, push to main"
        echo "  status   Show repo status + roadmap progress"
        exit 1
        ;;
esac
