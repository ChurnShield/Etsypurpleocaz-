"""
PurpleOcaz AI Dashboard — Server Entry Point

Run locally:
    python server.py

Or with uvicorn directly:
    uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload

Access from any device on the same network:
    http://<your-ip>:8000
"""

import os
import sys
import uvicorn

# Ensure project root is on sys.path
_project_root = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Initialise the database if it doesn't exist yet
from config import DATABASE_PATH

db_path = os.path.join(_project_root, DATABASE_PATH)
if not os.path.exists(db_path):
    print("Database not found — initialising...")
    from scripts.init_db import init_db
    init_db()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"\n  PurpleOcaz AI Dashboard")
    print(f"  Local:   http://localhost:{port}")
    print(f"  Network: http://0.0.0.0:{port}")
    print(f"  (Access from phone on same WiFi using your computer's IP)\n")

    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    )
