#!/usr/bin/env bash
# Quick environment check — called by session start hook
# Returns non-zero if critical keys are missing

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

MISSING=0
WARN=""

# Check .env exists
if [ ! -f "$REPO_ROOT/.env" ]; then
    echo "WARNING: No .env file found. Run: cp .env.example .env && edit with your API keys"
    exit 1
fi

# Source .env
set -a
source "$REPO_ROOT/.env"
set +a

# Required keys
check_required() {
    local key="$1"
    local placeholder="$2"
    local val="${!key:-}"
    if [ -z "$val" ] || [ "$val" = "$placeholder" ]; then
        echo "MISSING: $key"
        MISSING=$((MISSING + 1))
    fi
}

check_required "ANTHROPIC_API_KEY" "sk-ant-your-key-here"
check_required "ETSY_API_KEYSTRING" "your-etsy-keystring-here"
check_required "ETSY_SHARED_SECRET" "your-etsy-secret-here"
check_required "ETSY_SHOP_ID" "your-shop-id-here"
check_required "GOOGLE_SPREADSHEET_ID" "your-spreadsheet-id-here"

# Check Google credentials file
CREDS="${GOOGLE_CREDENTIALS_FILE:-google-credentials.json}"
if [ ! -f "$REPO_ROOT/$CREDS" ] && [ ! -f "$CREDS" ]; then
    echo "MISSING: Google credentials file ($CREDS)"
    MISSING=$((MISSING + 1))
fi

# Optional warnings
if [ -z "${GEMINI_API_KEY:-}" ] || [ "${GEMINI_API_KEY:-}" = "your-gemini-api-key-here" ]; then
    WARN="$WARN  - GEMINI_API_KEY not set (optional — needed for AI image generation)\n"
fi

if [ ! -f "$REPO_ROOT/workflows/etsy_analytics/etsy_tokens.json" ]; then
    WARN="$WARN  - Etsy OAuth not configured (optional — needed for auto-draft creation)\n"
fi

# Summary
if [ $MISSING -gt 0 ]; then
    echo ""
    echo "$MISSING required key(s) missing. See TOMORROW_PLAN.md for setup steps."
    exit 1
fi

echo "All required API keys configured."
if [ -n "$WARN" ]; then
    echo "Optional:"
    echo -e "$WARN"
fi
exit 0
