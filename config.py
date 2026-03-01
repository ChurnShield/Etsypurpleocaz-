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

# ── Timeout & Safety Limits ──
PLAYWRIGHT_PAGE_TIMEOUT_MS = 30_000       # 30s max for page.set_content()
PAGINATION_MAX_PAGES = 50                 # Cap all while-True pagination loops
LLM_REQUEST_TIMEOUT_SECONDS = 120        # Timeout for LLM API calls
CANVA_POLL_MAX_ITERATIONS = 20           # Cap Canva export polling
CANVA_POLL_MAX_WAIT_SECONDS = 8          # Max per-iteration wait

# ── Small Brain Settings ──
PROPOSAL_THRESHOLD_RUNS = 15       # Generate proposals after N runs
MIN_PATTERN_CONFIDENCE = 0.7       # Only propose if 70%+ confidence

# ── Big Brain Settings ──
BIG_BRAIN_MIN_WORKFLOWS = 2        # Need at least 2 workflows to compare
BIG_BRAIN_MIN_RUNS_PER_WORKFLOW = 10  # Need enough data per workflow
BIG_BRAIN_CACHE_TTL_SECONDS = 300          # 5 min cache for health metrics
BIG_BRAIN_FAILURE_RATE_CRITICAL = 0.50     # 50% system-wide = critical
BIG_BRAIN_FAILURE_RATE_DEGRADED = 0.25     # 25% system-wide = degraded
BIG_BRAIN_RECURRING_ERROR_THRESHOLD = 10   # Same error 10+ times in 24h
BIG_BRAIN_TIMEOUT_THRESHOLD = 5            # 5+ timeouts in 24h
BIG_BRAIN_DB_MAX_SIZE_MB = 500             # Database size limit in MB
BIG_BRAIN_PERF_DEGRADATION_FACTOR = 1.5    # 50% slower = flagged
