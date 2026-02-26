# =============================================================================
# lib/big_brain/hooks.py
#
# One-line hooks for automatic BigBrain health checks.
#
# Usage in any workflow run.py (after SmallBrain):
#
#     from lib.big_brain.hooks import post_workflow_check
#     post_workflow_check(db)
#
# The function is internally safe -- it never raises.  If BigBrain hits an
# error the workflow result is not affected.
# =============================================================================

import os
import sys
from dataclasses import asdict

_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_here))

if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


def post_workflow_check(db, quiet: bool = False):
    """
    Run BigBrain health check after a workflow completes.

    This is designed to be called at the end of every run.py, right after
    SmallBrain.  It:

      1. Analyses system health (uses 5-min cache -- fast on repeated calls)
      2. If degraded/critical, auto-generates proposals via SystemProposer
      3. Prints a one-line summary (unless quiet=True)

    The function catches all exceptions internally so it NEVER affects the
    calling workflow's result.

    Args:
        db:    SQLiteClient instance (the same one the workflow uses).
        quiet: If True, only print when issues are found.
    """
    try:
        from lib.big_brain.brain import BigBrain

        brain = BigBrain(db_client=db)
        health = brain.analyze_system_health()

        if health.status == "healthy":
            if not quiet:
                print(
                    f"    BigBrain: System healthy "
                    f"({health.total_executions_24h} runs in 24h)"
                )
            return

        # System is degraded or critical -- generate proposals
        proposals = brain.proposer.generate_proposals_from_health(asdict(health))

        problem_count = len(health.problems)
        print(
            f"    BigBrain: System {health.status.upper()} -- "
            f"{problem_count} issue(s), "
            f"{len(proposals)} proposal(s) generated"
        )

        # Print top-severity problems (max 3)
        critical = [p for p in health.problems if p["severity"] == "critical"]
        high = [p for p in health.problems if p["severity"] == "high"]
        top = (critical + high)[:3]
        for p in top:
            print(f"      [{p['severity'].upper()}] {p['description'][:80]}")

    except Exception as exc:
        if not quiet:
            print(f"    BigBrain: Skipped ({exc})")
