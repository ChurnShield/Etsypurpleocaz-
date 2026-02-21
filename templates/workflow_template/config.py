# =============================================================================
# templates/workflow_template/config.py
#
# All settings for this workflow live here.
# ✅ DO: Change WORKFLOW_NAME when you copy this template.
# ✅ DO: Tune thresholds here — never hardcode them inside other files.
# ❌ DON'T: Import from the project-root config.py for workflow-specific values.
# =============================================================================

# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------
# Give your workflow a unique snake_case name.
# This is the primary key used in the database to group executions + proposals.
# Example: "email_summariser", "invoice_processor", "lead_enricher"
WORKFLOW_NAME = "example_workflow"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
# Path to the SQLite database, relative to the project root.
# Keep this in sync with the root config.py and data/ directory.
DATABASE_PATH = "data/system.db"

# ---------------------------------------------------------------------------
# Orchestrator settings
# ---------------------------------------------------------------------------
# How many times the orchestrator retries a step when the validator rejects it.
# After MAX_RETRIES attempts the step is marked failed and execution continues.
MAX_RETRIES = 3

# ---------------------------------------------------------------------------
# SmallBrain settings
# ---------------------------------------------------------------------------
# SmallBrain will not generate proposals until this many executions exist.
# Too few runs = noise, not signal. 15 is a safe starting point.
PROPOSAL_THRESHOLD_RUNS = 15

# A tool call is flagged as "slow" when it exceeds this duration.
# Adjust based on your workflow's acceptable response times.
SLOW_TOOL_THRESHOLD_MS = 5000  # 5 seconds

# SmallBrain only saves a proposal when the pattern appears this often.
# 0.7 = the problem must occur in ≥70 % of observations.
MIN_PATTERN_CONFIDENCE = 0.7
