# =============================================================================
# lib/big_brain/brain.py
#
# BigBrain -- the system-wide learning layer.
#
# What it does
# ------------
# Analyses execution logs across ALL workflows and detects:
#   1. System health problems (failure rates, crashes, resource issues)
#   2. Cross-workflow patterns (common errors, infrastructure issues)
#   3. Critical alerts that need immediate attention
#
# What it does NOT do
# -------------------
# It never modifies workflows automatically.
# It only reads logs and writes proposals (human-in-the-loop).
# Per-workflow analysis is SmallBrain's job -- BigBrain looks across workflows.
# =============================================================================

import os
import sys
import uuid
import json
import shutil
import time
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_here))

if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from lib.common_tools.sqlite_client import get_client
from lib.big_brain.system_proposer import SystemProposer
from config import (
    DATABASE_PATH,
    BIG_BRAIN_MIN_WORKFLOWS,
    BIG_BRAIN_MIN_RUNS_PER_WORKFLOW,
    BIG_BRAIN_CACHE_TTL_SECONDS,
    BIG_BRAIN_FAILURE_RATE_CRITICAL,
    BIG_BRAIN_FAILURE_RATE_DEGRADED,
    BIG_BRAIN_RECURRING_ERROR_THRESHOLD,
    BIG_BRAIN_TIMEOUT_THRESHOLD,
    BIG_BRAIN_DB_MAX_SIZE_MB,
    BIG_BRAIN_PERF_DEGRADATION_FACTOR,
)


# =============================================================================
# Data structures
# =============================================================================

@dataclass
class WorkflowInfo:
    """Metadata about a discovered workflow directory."""
    workflow_id: str
    workflow_dir: Path
    has_brain: bool
    has_orchestrator: bool
    version: str = "1.0.0"


@dataclass
class SystemHealth:
    """Result of analyze_system_health()."""
    status: str                                          # 'healthy', 'degraded', 'critical'
    timestamp: str                                       # ISO format
    total_executions_24h: int
    system_failure_rate: float                           # 0.0 - 1.0
    problems: List[Dict[str, Any]] = field(default_factory=list)
    workflow_stats: Dict[str, Dict] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Health metrics cache
# =============================================================================

class _HealthCache:
    """Simple timestamp-based cache for health metrics."""

    def __init__(self, ttl_seconds: int):
        self._ttl = ttl_seconds
        self._result: Optional[SystemHealth] = None
        self._timestamp: float = 0.0

    def get(self) -> Optional[SystemHealth]:
        if self._result is None:
            return None
        if (time.time() - self._timestamp) > self._ttl:
            self._result = None
            return None
        return self._result

    def set(self, result: SystemHealth):
        self._result = result
        self._timestamp = time.time()


# =============================================================================
# BigBrain
# =============================================================================

class BigBrain:
    """
    Analyses execution logs across ALL workflows and proposes system-wide
    improvements.

    Usage
    -----
    from lib.big_brain.brain import BigBrain
    from lib.common_tools.sqlite_client import get_client

    db = get_client()
    brain = BigBrain(workflows_dir="workflows", db_client=db)

    # Discover workflows
    print(f"Discovered {len(brain.workflows)} workflows")

    # Full analysis
    result = brain.analyze()
    print(f"Status: {result['status']}, {result['proposals_saved']} proposals")

    # Health check only
    health = brain.analyze_system_health()
    print(f"System: {health.status}, {health.total_executions_24h} executions")

    # Cross-workflow patterns only
    patterns = brain.detect_cross_workflow_patterns()
    print(f"Found {len(patterns)} cross-workflow patterns")
    """

    def __init__(self, workflows_dir: str = "workflows", db_client=None):
        self.workflows_dir = os.path.join(_project_root, workflows_dir)
        self.db = db_client or get_client()
        self._cache = _HealthCache(BIG_BRAIN_CACHE_TTL_SECONDS)
        self.proposer = SystemProposer(db_client=self.db)
        self._workflows: Dict[str, WorkflowInfo] = {}
        self._workflows = self.discover_workflows()

    @property
    def workflows(self) -> Dict[str, WorkflowInfo]:
        return self._workflows

    # -------------------------------------------------------------------------
    # Workflow discovery
    # -------------------------------------------------------------------------

    def discover_workflows(self) -> Dict[str, WorkflowInfo]:
        """
        Scan the workflows directory for valid workflow subdirectories.

        A valid workflow has a run.py file. Returns dict of workflow_id -> WorkflowInfo.
        """
        workflows = {}
        workflows_path = Path(self.workflows_dir)

        if not workflows_path.is_dir():
            print(f"BigBrain: Workflows directory not found: {self.workflows_dir}")
            return workflows

        for entry in sorted(workflows_path.iterdir()):
            if not entry.is_dir():
                continue
            if entry.name.startswith("_") or entry.name.startswith("."):
                continue

            run_py = entry / "run.py"
            if not run_py.exists():
                continue

            has_orchestrator = False
            try:
                run_content = run_py.read_text(encoding="utf-8")
                has_orchestrator = "SimpleOrchestrator" in run_content
            except Exception:
                pass

            workflows[entry.name] = WorkflowInfo(
                workflow_id=entry.name,
                workflow_dir=entry,
                has_brain=True,
                has_orchestrator=has_orchestrator,
                version="1.0.0",
            )

        return workflows

    # -------------------------------------------------------------------------
    # Main entry point
    # -------------------------------------------------------------------------

    def analyze(self) -> dict:
        """
        Run full system analysis and return a summary dict.

        Returns
        -------
        dict with:
            success, status, workflows_discovered, qualified_workflows,
            health (SystemHealth as dict), cross_workflow_patterns, alerts,
            proposals_saved
        """
        print(f"\nBigBrain: Starting system-wide analysis...")
        print(f"BigBrain: {len(self._workflows)} workflows discovered")

        qualified = self._get_qualified_workflows()
        if len(qualified) < BIG_BRAIN_MIN_WORKFLOWS:
            print(
                f"BigBrain: Only {len(qualified)}/{BIG_BRAIN_MIN_WORKFLOWS} "
                f"workflows have {BIG_BRAIN_MIN_RUNS_PER_WORKFLOW}+ runs. "
                f"Need more data before analysis."
            )
            return {
                "success": True,
                "status": "insufficient_data",
                "workflows_discovered": len(self._workflows),
                "qualified_workflows": len(qualified),
                "health": None,
                "cross_workflow_patterns": [],
                "alerts": [],
                "proposals_saved": 0,
            }

        health = self.analyze_system_health()
        patterns = self.detect_cross_workflow_patterns()
        alerts = self.generate_alerts()

        proposals = []
        for pattern in patterns:
            if pattern.get("severity") in ("high", "critical"):
                proposal = self._pattern_to_proposal(pattern)
                proposals.append(proposal)
                self._save_proposal(proposal)

        for alert in alerts:
            if alert.get("severity") == "critical":
                proposal = self._alert_to_proposal(alert)
                proposals.append(proposal)
                self._save_proposal(proposal)

        print(
            f"BigBrain: Status={health.status}, "
            f"{len(patterns)} patterns, "
            f"{len(alerts)} alerts, "
            f"{len(proposals)} proposals saved"
        )

        return {
            "success": True,
            "status": health.status,
            "workflows_discovered": len(self._workflows),
            "qualified_workflows": len(qualified),
            "health": asdict(health),
            "cross_workflow_patterns": patterns,
            "alerts": alerts,
            "proposals_saved": len(proposals),
        }

    def _get_qualified_workflows(self) -> List[str]:
        """Return workflow IDs that have enough runs for analysis."""
        qualified = []
        for wf_id in self._workflows:
            rows = (
                self.db.table("executions")
                .select("id")
                .eq("workflow_id", wf_id)
                .execute()
            )
            if len(rows) >= BIG_BRAIN_MIN_RUNS_PER_WORKFLOW:
                qualified.append(wf_id)
        return qualified

    # -------------------------------------------------------------------------
    # System health analysis
    # -------------------------------------------------------------------------

    def analyze_system_health(self) -> SystemHealth:
        """
        Analyze system health across all workflows for the last 24 hours.

        Uses 5-minute caching to avoid hammering the database.
        """
        cached = self._cache.get()
        if cached is not None:
            return cached

        cutoff_24h = (datetime.utcnow() - timedelta(hours=24)).isoformat()

        all_logs_24h = (
            self.db.table("execution_logs")
            .select("*")
            .gte("timestamp", cutoff_24h)
            .execute()
        )

        all_executions_24h = (
            self.db.table("executions")
            .select("*")
            .gte("started_at", cutoff_24h)
            .execute()
        )

        all_workflows = (
            self.db.table("workflows")
            .select("*")
            .execute()
        )

        total_exec = len(all_executions_24h)
        failed_exec = len([
            e for e in all_executions_24h if e.get("status") == "failed"
        ])
        system_failure_rate = (failed_exec / total_exec) if total_exec > 0 else 0.0

        workflow_stats = self._compute_workflow_stats(all_executions_24h, all_logs_24h)
        metrics = self._collect_resource_metrics()

        problems = []
        problems.extend(self._check_system_failure_rate(system_failure_rate, total_exec))
        problems.extend(self._check_multiple_workflows_failing(workflow_stats))
        problems.extend(self._check_performance_degradation(all_logs_24h, all_workflows))
        problems.extend(self._check_recurring_errors(all_logs_24h))
        problems.extend(self._check_database_size(metrics))
        problems.extend(self._check_api_key_failures(all_logs_24h))
        problems.extend(self._check_unauthorized_access(all_logs_24h))
        problems.extend(self._check_data_corruption(all_logs_24h))
        problems.extend(self._check_memory_usage(metrics))
        problems.extend(self._check_disk_space(metrics))
        problems.extend(self._check_database_connections(all_logs_24h))
        problems.extend(self._check_system_crashes(all_logs_24h))
        problems.extend(self._check_data_loss(all_logs_24h))
        problems.extend(self._check_validation_trends(all_logs_24h))
        problems.extend(self._check_timeout_patterns(all_logs_24h))

        status = self._determine_status(problems)

        result = SystemHealth(
            status=status,
            timestamp=datetime.utcnow().isoformat(),
            total_executions_24h=total_exec,
            system_failure_rate=round(system_failure_rate, 4),
            problems=problems,
            workflow_stats=workflow_stats,
            metrics=metrics,
        )

        self._cache.set(result)
        return result

    # -------------------------------------------------------------------------
    # Helpers: stats and resources
    # -------------------------------------------------------------------------

    def _compute_workflow_stats(self, executions: list, logs: list) -> Dict[str, Dict]:
        """Aggregate execution stats per workflow (in Python, no SQL GROUP BY)."""
        stats = defaultdict(lambda: {
            "total": 0, "failed": 0, "succeeded": 0,
            "failure_rate": 0.0, "errors": [], "avg_duration_ms": 0,
        })

        for exe in executions:
            wf_id = exe.get("workflow_id")
            if not wf_id:
                continue
            stats[wf_id]["total"] += 1
            if exe.get("status") == "failed":
                stats[wf_id]["failed"] += 1
                if exe.get("error_message"):
                    stats[wf_id]["errors"].append(exe["error_message"])
            elif exe.get("status") == "completed":
                stats[wf_id]["succeeded"] += 1

        durations = defaultdict(list)
        for log in logs:
            if log.get("event_type") == "tool_result" and log.get("duration_ms"):
                durations[log.get("workflow_id", "")].append(log["duration_ms"])

        for wf_id, s in stats.items():
            s["failure_rate"] = (s["failed"] / s["total"]) if s["total"] > 0 else 0.0
            if durations.get(wf_id):
                s["avg_duration_ms"] = int(
                    sum(durations[wf_id]) / len(durations[wf_id])
                )

        return dict(stats)

    def _collect_resource_metrics(self) -> Dict[str, Any]:
        """Collect OS-level resource metrics. Returns partial data if checks fail."""
        metrics = {
            "db_size_mb": None,
            "db_max_mb": BIG_BRAIN_DB_MAX_SIZE_MB,
            "disk_total_gb": None,
            "disk_used_gb": None,
            "disk_free_gb": None,
            "disk_usage_pct": None,
            "memory_total_mb": None,
            "memory_available_mb": None,
            "memory_usage_pct": None,
        }

        # -- Database size --
        try:
            db_path = os.path.join(_project_root, DATABASE_PATH)
            if os.path.exists(db_path):
                size_bytes = os.path.getsize(db_path)
                metrics["db_size_mb"] = round(size_bytes / (1024 * 1024), 2)
        except Exception:
            pass

        # -- Disk space --
        try:
            db_path = os.path.join(_project_root, DATABASE_PATH)
            drive = os.path.splitdrive(db_path)[0] or "/"
            if not drive.endswith(os.sep):
                drive += os.sep
            usage = shutil.disk_usage(drive)
            metrics["disk_total_gb"] = round(usage.total / (1024 ** 3), 2)
            metrics["disk_used_gb"] = round(usage.used / (1024 ** 3), 2)
            metrics["disk_free_gb"] = round(usage.free / (1024 ** 3), 2)
            metrics["disk_usage_pct"] = round((usage.used / usage.total) * 100, 1)
        except Exception:
            pass

        # -- Memory (Windows via ctypes, Linux via /proc/meminfo) --
        try:
            if sys.platform == "win32":
                import ctypes

                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]

                mem = MEMORYSTATUSEX()
                mem.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))

                metrics["memory_total_mb"] = round(mem.ullTotalPhys / (1024 ** 2))
                metrics["memory_available_mb"] = round(mem.ullAvailPhys / (1024 ** 2))
                metrics["memory_usage_pct"] = round(float(mem.dwMemoryLoad), 1)
            else:
                if os.path.exists("/proc/meminfo"):
                    with open("/proc/meminfo", "r") as f:
                        lines = f.readlines()
                    mem_info = {}
                    for line in lines:
                        parts = line.split(":")
                        if len(parts) == 2:
                            key = parts[0].strip()
                            val = parts[1].strip().split()[0]
                            mem_info[key] = int(val)
                    total_kb = mem_info.get("MemTotal", 0)
                    avail_kb = mem_info.get("MemAvailable", 0)
                    metrics["memory_total_mb"] = round(total_kb / 1024)
                    metrics["memory_available_mb"] = round(avail_kb / 1024)
                    if total_kb > 0:
                        used_pct = ((total_kb - avail_kb) / total_kb) * 100
                        metrics["memory_usage_pct"] = round(used_pct, 1)
        except Exception:
            pass

        return metrics

    # -------------------------------------------------------------------------
    # Health checks (15 checks)
    # -------------------------------------------------------------------------

    def _check_system_failure_rate(self, rate: float, total: int) -> List[Dict]:
        """Check 1: System-wide failure rate."""
        problems = []
        if total == 0:
            return problems
        if rate >= BIG_BRAIN_FAILURE_RATE_CRITICAL:
            problems.append({
                "severity": "critical",
                "category": "system_failure_rate",
                "description": (
                    f"System-wide failure rate is {rate:.0%} "
                    f"({int(rate * total)} of {total} executions failed in 24h)"
                ),
                "details": {"rate": rate, "total": total},
            })
        elif rate >= BIG_BRAIN_FAILURE_RATE_DEGRADED:
            problems.append({
                "severity": "high",
                "category": "system_failure_rate",
                "description": (
                    f"System-wide failure rate is elevated at {rate:.0%} "
                    f"({int(rate * total)} of {total} failed in 24h)"
                ),
                "details": {"rate": rate, "total": total},
            })
        return problems

    def _check_multiple_workflows_failing(self, workflow_stats: Dict) -> List[Dict]:
        """Check 2: Multiple workflows with high failure rates."""
        problems = []
        high_fail = [
            wf_id for wf_id, stats in workflow_stats.items()
            if stats["failure_rate"] >= 0.80 and stats["total"] >= 3
        ]
        if len(high_fail) >= 3:
            problems.append({
                "severity": "critical",
                "category": "multiple_workflow_failures",
                "description": (
                    f"{len(high_fail)} workflows have 80%+ failure rate: "
                    f"{', '.join(high_fail)}"
                ),
                "details": {"workflows": high_fail},
            })
        elif len(high_fail) >= 2:
            problems.append({
                "severity": "high",
                "category": "multiple_workflow_failures",
                "description": (
                    f"{len(high_fail)} workflows have 80%+ failure rate: "
                    f"{', '.join(high_fail)}"
                ),
                "details": {"workflows": high_fail},
            })
        return problems

    def _check_performance_degradation(self, logs: list, workflows: list) -> List[Dict]:
        """Check 3: Performance degradation vs historical baseline."""
        problems = []
        baselines = {}
        for wf in workflows:
            if wf.get("avg_duration_ms") and wf.get("id"):
                baselines[wf["id"]] = wf["avg_duration_ms"]

        current_durations = defaultdict(list)
        for log in logs:
            if log.get("event_type") == "tool_result" and log.get("duration_ms"):
                wf_id = log.get("workflow_id")
                if wf_id:
                    current_durations[wf_id].append(log["duration_ms"])

        for wf_id, durations in current_durations.items():
            if wf_id not in baselines or not baselines[wf_id]:
                continue
            current_avg = sum(durations) / len(durations)
            baseline = baselines[wf_id]
            if current_avg > baseline * BIG_BRAIN_PERF_DEGRADATION_FACTOR:
                problems.append({
                    "severity": "medium",
                    "category": "performance_degradation",
                    "description": (
                        f"{wf_id}: avg duration {current_avg:.0f}ms vs "
                        f"baseline {baseline}ms "
                        f"({current_avg / baseline:.1f}x slower)"
                    ),
                    "details": {
                        "workflow_id": wf_id,
                        "current_avg_ms": round(current_avg),
                        "baseline_ms": baseline,
                        "factor": round(current_avg / baseline, 2),
                    },
                })
        return problems

    def _check_recurring_errors(self, logs: list) -> List[Dict]:
        """Check 4: Same error message occurring repeatedly."""
        problems = []
        error_counts = defaultdict(lambda: {"count": 0, "workflows": set()})
        for log in logs:
            if log.get("event_type") == "error" and log.get("error_message"):
                msg = log["error_message"][:200]
                error_counts[msg]["count"] += 1
                if log.get("workflow_id"):
                    error_counts[msg]["workflows"].add(log["workflow_id"])

        for msg, info in error_counts.items():
            if info["count"] >= BIG_BRAIN_RECURRING_ERROR_THRESHOLD:
                problems.append({
                    "severity": "high",
                    "category": "recurring_error",
                    "description": (
                        f"Error occurred {info['count']} times in 24h "
                        f"across {len(info['workflows'])} workflow(s): "
                        f"{msg[:100]}"
                    ),
                    "details": {
                        "error_message": msg,
                        "count": info["count"],
                        "workflows": list(info["workflows"]),
                    },
                })
        return problems

    def _check_database_size(self, metrics: Dict) -> List[Dict]:
        """Check 5: Database approaching size limit."""
        problems = []
        db_size = metrics.get("db_size_mb")
        if db_size is None:
            return problems
        usage_pct = (db_size / BIG_BRAIN_DB_MAX_SIZE_MB) * 100
        if usage_pct >= 90:
            problems.append({
                "severity": "high",
                "category": "database_size",
                "description": (
                    f"Database is {db_size:.1f}MB of "
                    f"{BIG_BRAIN_DB_MAX_SIZE_MB}MB limit ({usage_pct:.0f}%)"
                ),
                "details": {"size_mb": db_size, "limit_mb": BIG_BRAIN_DB_MAX_SIZE_MB},
            })
        elif usage_pct >= 75:
            problems.append({
                "severity": "medium",
                "category": "database_size",
                "description": (
                    f"Database is {db_size:.1f}MB of "
                    f"{BIG_BRAIN_DB_MAX_SIZE_MB}MB limit ({usage_pct:.0f}%)"
                ),
                "details": {"size_mb": db_size, "limit_mb": BIG_BRAIN_DB_MAX_SIZE_MB},
            })
        return problems

    def _check_api_key_failures(self, logs: list) -> List[Dict]:
        """Check 6: API key / authentication failures."""
        problems = []
        api_errors = []
        for log in logs:
            if log.get("event_type") == "error":
                msg = (log.get("error_message") or "").lower()
                if any(kw in msg for kw in (
                    "401", "403", "api key", "unauthorized",
                    "forbidden", "authentication",
                )):
                    api_errors.append(log)

        if len(api_errors) > 3:
            affected = list(set(
                l.get("workflow_id") for l in api_errors if l.get("workflow_id")
            ))
            problems.append({
                "severity": "high",
                "category": "api_key_failure",
                "description": (
                    f"{len(api_errors)} API authentication errors in 24h "
                    f"affecting: {', '.join(affected)}"
                ),
                "details": {"count": len(api_errors), "workflows": affected},
            })
        return problems

    def _check_unauthorized_access(self, logs: list) -> List[Dict]:
        """Check 7: Unauthorized access attempts."""
        problems = []
        for log in logs:
            if log.get("event_type") == "error":
                msg = (log.get("error_message") or "").lower()
                if any(kw in msg for kw in (
                    "unauthorized access", "security violation",
                    "permission denied", "access denied",
                )):
                    problems.append({
                        "severity": "critical",
                        "category": "unauthorized_access",
                        "description": (
                            f"Security event in "
                            f"{log.get('workflow_id', 'unknown')}: "
                            f"{log.get('error_message', '')[:100]}"
                        ),
                        "details": {
                            "workflow_id": log.get("workflow_id"),
                            "timestamp": log.get("timestamp"),
                        },
                    })
                    break
        return problems

    def _check_data_corruption(self, logs: list) -> List[Dict]:
        """Check 8: Data corruption signals."""
        problems = []
        for log in logs:
            if log.get("event_type") == "error":
                msg = (log.get("error_message") or "").lower()
                if any(kw in msg for kw in (
                    "corrupt", "malformed", "integrity",
                    "database disk image",
                )):
                    problems.append({
                        "severity": "critical",
                        "category": "data_corruption",
                        "description": (
                            f"Possible data corruption in "
                            f"{log.get('workflow_id', 'unknown')}: "
                            f"{log.get('error_message', '')[:100]}"
                        ),
                        "details": {
                            "workflow_id": log.get("workflow_id"),
                            "timestamp": log.get("timestamp"),
                        },
                    })
                    break
        return problems

    def _check_memory_usage(self, metrics: Dict) -> List[Dict]:
        """Check 9: System memory usage."""
        problems = []
        pct = metrics.get("memory_usage_pct")
        if pct is None:
            return problems
        if pct >= 95:
            problems.append({
                "severity": "critical",
                "category": "memory_usage",
                "description": f"System memory usage is {pct}%",
                "details": {
                    "usage_pct": pct,
                    "total_mb": metrics.get("memory_total_mb"),
                    "available_mb": metrics.get("memory_available_mb"),
                },
            })
        elif pct >= 90:
            problems.append({
                "severity": "high",
                "category": "memory_usage",
                "description": f"System memory usage is {pct}%",
                "details": {
                    "usage_pct": pct,
                    "total_mb": metrics.get("memory_total_mb"),
                    "available_mb": metrics.get("memory_available_mb"),
                },
            })
        return problems

    def _check_disk_space(self, metrics: Dict) -> List[Dict]:
        """Check 10: Disk space usage."""
        problems = []
        pct = metrics.get("disk_usage_pct")
        if pct is None:
            return problems
        if pct >= 95:
            problems.append({
                "severity": "critical",
                "category": "disk_space",
                "description": (
                    f"Disk is {pct}% full "
                    f"({metrics.get('disk_free_gb', '?')}GB free)"
                ),
                "details": {
                    "usage_pct": pct,
                    "free_gb": metrics.get("disk_free_gb"),
                },
            })
        elif pct >= 90:
            problems.append({
                "severity": "high",
                "category": "disk_space",
                "description": (
                    f"Disk is {pct}% full "
                    f"({metrics.get('disk_free_gb', '?')}GB free)"
                ),
                "details": {
                    "usage_pct": pct,
                    "free_gb": metrics.get("disk_free_gb"),
                },
            })
        return problems

    def _check_database_connections(self, logs: list) -> List[Dict]:
        """Check 11: Database connection errors."""
        problems = []
        for log in logs:
            if log.get("event_type") == "error":
                msg = (log.get("error_message") or "").lower()
                if any(kw in msg for kw in (
                    "database is locked", "unable to open database",
                    "disk i/o error", "no such table",
                )):
                    problems.append({
                        "severity": "critical",
                        "category": "database_connection",
                        "description": (
                            f"Database error: "
                            f"{log.get('error_message', '')[:100]}"
                        ),
                        "details": {
                            "workflow_id": log.get("workflow_id"),
                            "timestamp": log.get("timestamp"),
                        },
                    })
                    break
        return problems

    def _check_system_crashes(self, logs: list) -> List[Dict]:
        """Check 12: Detect system crashes."""
        problems = []
        for log in logs:
            if log.get("event_type") == "error":
                msg = (log.get("error_message") or "").lower()
                if any(kw in msg for kw in (
                    "crash", "segfault", "fatal",
                    "unhandled exception", "traceback",
                )):
                    problems.append({
                        "severity": "critical",
                        "category": "system_crash",
                        "description": (
                            f"Crash detected in "
                            f"{log.get('workflow_id', 'unknown')}: "
                            f"{log.get('error_message', '')[:100]}"
                        ),
                        "details": {
                            "workflow_id": log.get("workflow_id"),
                            "timestamp": log.get("timestamp"),
                        },
                    })
                    break
        return problems

    def _check_data_loss(self, logs: list) -> List[Dict]:
        """Check 13: Signals of data loss."""
        problems = []
        for log in logs:
            if log.get("event_type") == "error":
                msg = (log.get("error_message") or "").lower()
                if any(kw in msg for kw in (
                    "data loss", "missing data", "truncated",
                    "file not found", "lost",
                )):
                    problems.append({
                        "severity": "critical",
                        "category": "data_loss",
                        "description": (
                            f"Possible data loss in "
                            f"{log.get('workflow_id', 'unknown')}: "
                            f"{log.get('error_message', '')[:100]}"
                        ),
                        "details": {
                            "workflow_id": log.get("workflow_id"),
                            "timestamp": log.get("timestamp"),
                        },
                    })
                    break
        return problems

    def _check_validation_trends(self, logs: list) -> List[Dict]:
        """Check 14: Increasing validation failure trends."""
        problems = []
        now = datetime.utcnow()
        midpoint = (now - timedelta(hours=12)).isoformat()

        recent = {"total": 0, "failed": 0}
        older = {"total": 0, "failed": 0}

        for log in logs:
            if log.get("event_type") != "validation":
                continue
            ts = log.get("timestamp", "")
            bucket = recent if ts >= midpoint else older
            bucket["total"] += 1
            if not log.get("success"):
                bucket["failed"] += 1

        if recent["total"] >= 5 and older["total"] >= 5:
            recent_rate = recent["failed"] / recent["total"]
            older_rate = older["failed"] / older["total"]

            if recent_rate > older_rate + 0.2:
                problems.append({
                    "severity": "medium",
                    "category": "validation_trend",
                    "description": (
                        f"Validation failures increasing: "
                        f"{older_rate:.0%} -> {recent_rate:.0%} "
                        f"(last 12h vs prior 12h)"
                    ),
                    "details": {
                        "recent_rate": round(recent_rate, 3),
                        "older_rate": round(older_rate, 3),
                    },
                })
        return problems

    def _check_timeout_patterns(self, logs: list) -> List[Dict]:
        """Check 15: Timeout patterns across workflows."""
        problems = []
        timeout_logs = []
        for log in logs:
            if log.get("event_type") == "error":
                msg = (log.get("error_message") or "").lower()
                if any(kw in msg for kw in (
                    "timeout", "timed out", "deadline exceeded",
                )):
                    timeout_logs.append(log)

        if len(timeout_logs) >= BIG_BRAIN_TIMEOUT_THRESHOLD:
            affected = list(set(
                l.get("workflow_id") for l in timeout_logs if l.get("workflow_id")
            ))
            problems.append({
                "severity": "medium",
                "category": "timeout_pattern",
                "description": (
                    f"{len(timeout_logs)} timeouts in 24h "
                    f"affecting: {', '.join(affected)}"
                ),
                "details": {"count": len(timeout_logs), "workflows": affected},
            })
        return problems

    # -------------------------------------------------------------------------
    # Status determination
    # -------------------------------------------------------------------------

    def _determine_status(self, problems: List[Dict]) -> str:
        """Determine overall system status from problems list."""
        severities = [p.get("severity") for p in problems]
        if "critical" in severities:
            return "critical"
        if "high" in severities:
            return "degraded"
        if "medium" in severities:
            return "degraded"
        return "healthy"

    # -------------------------------------------------------------------------
    # Cross-workflow pattern detection
    # -------------------------------------------------------------------------

    def detect_cross_workflow_patterns(self) -> List[Dict]:
        """
        Find patterns affecting 3+ workflows.

        Returns list of pattern dicts with:
            pattern_type, affected_workflows, severity, description, recommendation
        """
        cutoff_24h = (datetime.utcnow() - timedelta(hours=24)).isoformat()

        all_logs = (
            self.db.table("execution_logs")
            .select("*")
            .gte("timestamp", cutoff_24h)
            .execute()
        )

        patterns = []
        patterns.extend(self._detect_common_errors(all_logs))
        patterns.extend(self._detect_performance_patterns(all_logs))
        patterns.extend(self._detect_infrastructure_issues(all_logs))
        patterns.extend(self._detect_resource_contention(all_logs))
        patterns.extend(self._detect_security_patterns(all_logs))

        return patterns

    def _detect_common_errors(self, logs: list) -> List[Dict]:
        """Find error messages appearing in 3+ workflows."""
        error_workflows = defaultdict(set)
        for log in logs:
            if log.get("event_type") == "error" and log.get("error_message"):
                msg = log["error_message"][:100].lower().strip()
                wf_id = log.get("workflow_id")
                if wf_id:
                    error_workflows[msg].add(wf_id)

        patterns = []
        for msg, wf_set in error_workflows.items():
            if len(wf_set) >= 3:
                patterns.append({
                    "pattern_type": "common_error",
                    "affected_workflows": sorted(wf_set),
                    "severity": "high",
                    "description": (
                        f"Same error in {len(wf_set)} workflows: {msg}"
                    ),
                    "recommendation": (
                        "Investigate shared infrastructure or dependencies "
                        "that could cause this error across workflows."
                    ),
                })
        return patterns

    def _detect_performance_patterns(self, logs: list) -> List[Dict]:
        """Find performance issues in 3+ workflows."""
        slow_workflows = defaultdict(lambda: {"slow_count": 0, "total_count": 0})
        for log in logs:
            if log.get("event_type") == "tool_result" and log.get("duration_ms"):
                wf_id = log.get("workflow_id")
                if not wf_id:
                    continue
                slow_workflows[wf_id]["total_count"] += 1
                if log["duration_ms"] > 10000:
                    slow_workflows[wf_id]["slow_count"] += 1

        degraded = [
            wf_id for wf_id, s in slow_workflows.items()
            if s["total_count"] >= 5 and (s["slow_count"] / s["total_count"]) > 0.3
        ]

        patterns = []
        if len(degraded) >= 3:
            patterns.append({
                "pattern_type": "performance_degradation",
                "affected_workflows": sorted(degraded),
                "severity": "medium",
                "description": (
                    f"{len(degraded)} workflows showing slow performance "
                    f"(30%+ tool calls over 10s)"
                ),
                "recommendation": (
                    "Check shared resources (database, network, API rate limits) "
                    "that may be causing system-wide slowdowns."
                ),
            })
        return patterns

    def _detect_infrastructure_issues(self, logs: list) -> List[Dict]:
        """Find infrastructure errors in 3+ workflows."""
        infra_keywords = (
            "connection", "timeout", "dns", "ssl", "certificate",
            "network", "socket", "refused",
        )
        wf_with_infra = set()
        for log in logs:
            if log.get("event_type") == "error":
                msg = (log.get("error_message") or "").lower()
                if any(kw in msg for kw in infra_keywords):
                    if log.get("workflow_id"):
                        wf_with_infra.add(log["workflow_id"])

        patterns = []
        if len(wf_with_infra) >= 3:
            patterns.append({
                "pattern_type": "infrastructure_issue",
                "affected_workflows": sorted(wf_with_infra),
                "severity": "high",
                "description": (
                    f"Infrastructure errors in {len(wf_with_infra)} workflows"
                ),
                "recommendation": (
                    "Check network connectivity, DNS resolution, SSL certificates, "
                    "and external API availability."
                ),
            })
        return patterns

    def _detect_resource_contention(self, logs: list) -> List[Dict]:
        """Find resource contention signals in 3+ workflows."""
        contention_keywords = (
            "locked", "busy", "resource", "quota", "rate limit",
            "throttle", "too many requests", "429",
        )
        wf_with_contention = set()
        for log in logs:
            if log.get("event_type") == "error":
                msg = (log.get("error_message") or "").lower()
                if any(kw in msg for kw in contention_keywords):
                    if log.get("workflow_id"):
                        wf_with_contention.add(log["workflow_id"])

        patterns = []
        if len(wf_with_contention) >= 3:
            patterns.append({
                "pattern_type": "resource_contention",
                "affected_workflows": sorted(wf_with_contention),
                "severity": "high",
                "description": (
                    f"Resource contention in {len(wf_with_contention)} workflows "
                    f"(rate limits, locks, quotas)"
                ),
                "recommendation": (
                    "Stagger workflow execution times. Check API rate limits. "
                    "Consider adding delays between workflows."
                ),
            })
        return patterns

    def _detect_security_patterns(self, logs: list) -> List[Dict]:
        """Find security-related patterns in 3+ workflows."""
        security_keywords = (
            "401", "403", "unauthorized", "forbidden",
            "authentication failed", "invalid token", "expired token",
        )
        wf_with_security = set()
        for log in logs:
            if log.get("event_type") == "error":
                msg = (log.get("error_message") or "").lower()
                if any(kw in msg for kw in security_keywords):
                    if log.get("workflow_id"):
                        wf_with_security.add(log["workflow_id"])

        patterns = []
        if len(wf_with_security) >= 3:
            patterns.append({
                "pattern_type": "security_pattern",
                "affected_workflows": sorted(wf_with_security),
                "severity": "critical",
                "description": (
                    f"Authentication failures in {len(wf_with_security)} workflows"
                ),
                "recommendation": (
                    "Check API keys and OAuth tokens. Multiple workflows failing "
                    "auth suggests expired credentials or revoked access."
                ),
            })
        return patterns

    # -------------------------------------------------------------------------
    # Alert generation
    # -------------------------------------------------------------------------

    def generate_alerts(self) -> List[Dict]:
        """
        Generate immediate alerts for critical issues.

        Returns list of alert dicts with:
            severity, problem_type, affected_workflows, recommended_action, timestamp
        """
        health = self._cache.get()
        if health is None:
            health = self.analyze_system_health()

        alerts = []
        for problem in health.problems:
            if problem.get("severity") != "critical":
                continue

            affected = []
            details = problem.get("details", {})
            if "workflows" in details:
                affected = details["workflows"]
            elif "workflow_id" in details and details["workflow_id"]:
                affected = [details["workflow_id"]]

            alerts.append({
                "severity": "critical",
                "problem_type": problem["category"],
                "affected_workflows": affected,
                "recommended_action": self._get_recommendation(problem["category"]),
                "timestamp": datetime.utcnow().isoformat(),
            })

        return alerts

    def _get_recommendation(self, category: str) -> str:
        """Return a human-readable recommendation for a problem category."""
        recommendations = {
            "system_failure_rate": (
                "Investigate root cause of failures. Check logs for common errors. "
                "Consider pausing non-critical workflows."
            ),
            "multiple_workflow_failures": (
                "Multiple workflows failing suggests a shared dependency issue. "
                "Check database connectivity, API keys, and network."
            ),
            "data_corruption": (
                "IMMEDIATE: Back up data/system.db. "
                "Run integrity check. Consider restoring from backup."
            ),
            "unauthorized_access": (
                "IMMEDIATE: Review access logs. "
                "Rotate API keys and OAuth tokens."
            ),
            "system_crash": (
                "Review crash logs. Check for memory leaks or resource exhaustion."
            ),
            "database_connection": (
                "IMMEDIATE: Check database file integrity. "
                "Ensure no other process has locked the database."
            ),
            "data_loss": (
                "IMMEDIATE: Check backup availability. "
                "Investigate which data was lost and whether recovery is possible."
            ),
            "memory_usage": (
                "System memory is critically low. "
                "Close unnecessary applications. Check for memory leaks."
            ),
            "disk_space": (
                "Disk space critically low. "
                "Clean up old logs, exports, or temporary files."
            ),
        }
        return recommendations.get(category, "Investigate and resolve the issue.")

    # -------------------------------------------------------------------------
    # Proposal helpers
    # -------------------------------------------------------------------------

    def _pattern_to_proposal(self, pattern: dict) -> dict:
        """Convert a cross-workflow pattern to a proposal dict."""
        return {
            "proposal_type": f"cross_workflow_{pattern['pattern_type']}",
            "title": (
                f"Cross-workflow issue: "
                f"{pattern['pattern_type'].replace('_', ' ')}"
            ),
            "description": pattern["description"],
            "pattern_data": {
                "pattern_type": pattern["pattern_type"],
                "affected_workflows": pattern["affected_workflows"],
                "severity": pattern["severity"],
            },
            "proposed_changes": {
                "action": f"investigate_{pattern['pattern_type']}",
                "target": "system",
                "suggestion": pattern["recommendation"],
            },
        }

    def _alert_to_proposal(self, alert: dict) -> dict:
        """Convert a critical alert to a proposal dict."""
        return {
            "proposal_type": f"critical_alert_{alert['problem_type']}",
            "title": f"Critical: {alert['problem_type'].replace('_', ' ')}",
            "description": alert["recommended_action"],
            "pattern_data": {
                "problem_type": alert["problem_type"],
                "affected_workflows": alert["affected_workflows"],
                "severity": "critical",
            },
            "proposed_changes": {
                "action": f"resolve_{alert['problem_type']}",
                "target": "system",
                "suggestion": alert["recommended_action"],
            },
        }

    def _save_proposal(self, proposal: dict):
        """
        Write one proposal to the proposals table.

        System-wide proposals use workflow_id=None.
        Matches SmallBrain._save_proposal() pattern exactly.
        """
        self.db.table("proposals").insert({
            "id": str(uuid.uuid4()),
            "workflow_id": None,
            "generated_at": datetime.utcnow().isoformat(),
            "status": "pending",
            "proposal_type": proposal["proposal_type"],
            "title": proposal["title"],
            "description": proposal["description"],
            "pattern_data": json.dumps(proposal["pattern_data"]),
            "proposed_changes": json.dumps(proposal["proposed_changes"]),
            "applied_at": None,
            "applied_by": None,
        }).execute()
