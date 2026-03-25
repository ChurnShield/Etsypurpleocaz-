#!/usr/bin/env python3
"""
Refresh Canva OAuth access token using the stored refresh token.
Reads credentials from purpleocaz-canva-mcp/.env
Updates both .env and canva_tokens.json with the new access token.
"""

import os
import json
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv, set_key

ENV_PATH = Path("/root/NEW-AI-PROJECT/purpleocaz-canva-mcp/.env")
TOKENS_PATH = Path("/root/NEW-AI-PROJECT/workflows/auto_listing_creator/canva_tokens.json")

load_dotenv(ENV_PATH, override=True)

CLIENT_ID     = os.getenv("CANVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("CANVA_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("CANVA_REFRESH_TOKEN")

if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
    raise SystemExit("ERROR: CANVA_CLIENT_ID / CANVA_CLIENT_SECRET / CANVA_REFRESH_TOKEN missing from .env")

credentials = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

resp = requests.post(
    "https://api.canva.com/rest/v1/oauth/token",
    headers={
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    },
    data={
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
    },
    timeout=30,
)

if resp.status_code != 200:
    raise SystemExit(f"ERROR: Token refresh failed — HTTP {resp.status_code}: {resp.text}")

data = resp.json()
new_access  = data["access_token"]
expires_in  = data.get("expires_in", 14400)
# Canva may or may not rotate the refresh token
new_refresh = data.get("refresh_token", REFRESH_TOKEN)

# Update .env
set_key(str(ENV_PATH), "CANVA_ACCESS_TOKEN", new_access)
if new_refresh != REFRESH_TOKEN:
    set_key(str(ENV_PATH), "CANVA_REFRESH_TOKEN", new_refresh)

# Update canva_tokens.json
if TOKENS_PATH.exists():
    with open(TOKENS_PATH) as f:
        tokens = json.load(f)
else:
    tokens = {}

tokens["access_token"]  = new_access
tokens["expires_in"]    = expires_in
tokens["token_type"]    = data.get("token_type", "Bearer")
if new_refresh != REFRESH_TOKEN:
    tokens["refresh_token"] = new_refresh

with open(TOKENS_PATH, "w") as f:
    json.dump(tokens, f, indent=2)

print(f"Token refreshed. Expires: {expires_in}s")
