import os
from dotenv import load_dotenv

load_dotenv()

# ── API Configuration ──
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

# ── Database ──
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/system.db")

# ── Execution Settings ──
DEFAULT_TIMEOUT_SECONDS = 120
MAX_RETRIES = 3

# ── Small Brain Settings ──
PROPOSAL_THRESHOLD_RUNS = 15       # Generate proposals after N runs
MIN_PATTERN_CONFIDENCE = 0.7       # Only propose if 70%+ confidence

# ── Big Brain Settings ──
BIG_BRAIN_MIN_WORKFLOWS = 2        # Need at least 2 workflows to compare
BIG_BRAIN_MIN_RUNS_PER_WORKFLOW = 10  # Need enough data per workflow
