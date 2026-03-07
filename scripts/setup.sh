#!/usr/bin/env bash
# One-command project bootstrap
# Usage: bash scripts/setup.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== PurpleOcaz Setup ==="

# 1. Python venv
if [ ! -d ".venv" ]; then
    echo "[1/4] Creating virtual environment..."
    python3 -m venv .venv
else
    echo "[1/4] Virtual environment already exists"
fi

source .venv/bin/activate

# 2. Dependencies
echo "[2/4] Installing Python dependencies..."
pip install -q -r requirements.txt

# 3. Environment file
if [ ! -f ".env" ]; then
    echo "[3/4] Creating .env from template..."
    cp .env.example .env
    echo "  -> Edit .env with your API keys before running workflows"
else
    echo "[3/4] .env already exists"
fi

# 4. Database
echo "[4/4] Initialising database..."
python scripts/init_db.py

echo ""
echo "=== Setup complete ==="
echo "Activate the venv:  source .venv/bin/activate"
echo "Run tests:          pytest tests/ -v"
echo "Run a workflow:     python workflows/<name>/run.py"
