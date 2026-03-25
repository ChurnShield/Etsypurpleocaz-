#!/usr/bin/env bash
# session_start.sh — run at the top of every session
set -euo pipefail

python3 /root/NEW-AI-PROJECT/scripts/refresh_canva_token.py
