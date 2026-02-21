import uuid
import json
from datetime import datetime


class ExecutionLogger:
    """Logs every step of workflow execution to database.

    CRITICAL: Always use in a try/finally block to ensure flush() is called.
    """

    def __init__(self, execution_id: str, workflow_id: str, db_client):
        self.execution_id = execution_id
        self.workflow_id = workflow_id
        self.db = db_client
        self._buffer = []
        self._current_phase = None

    def phase_start(self, phase_name: str):
        """Log when a phase begins."""
        self._current_phase = phase_name
        self._log_event(
            event_type="phase_start",
            phase=phase_name,
            success=True
        )

    def phase_end(self, phase_name: str, success: bool):
        """Log when a phase completes."""
        self._log_event(
            event_type="phase_end",
            phase=phase_name,
            success=success
        )
        self._current_phase = None

    def tool_call(self, tool_name: str, params: dict):
        """Log before calling a tool."""
        self._log_event(
            event_type="tool_call",
            tool_name=tool_name,
            metadata=params
        )

    def tool_result(self, tool_name: str, result: dict, success: bool, duration_ms: int):
        """Log after tool returns."""
        self._log_event(
            event_type="tool_result",
            tool_name=tool_name,
            success=success,
            duration_ms=duration_ms,
            metadata=result
        )

    def validation_event(self, validator_name: str, passed: bool, issues: list):
        """Log validator results."""
        self._log_event(
            event_type="validation",
            validator_name=validator_name,
            success=passed,
            metadata={"issues": issues}
        )

    def error(self, error_message: str, metadata: dict = None):
        """Log errors."""
        self._log_event(
            event_type="error",
            success=False,
            error_message=error_message,
            metadata=metadata or {}
        )

    def flush(self):
        """Write buffered logs to database. MUST be called in finally block."""
        for log_entry in self._buffer:
            self.db.table("execution_logs").insert(log_entry).execute()
        self._buffer = []

    def _log_event(self, event_type: str, phase: str = None,
                   tool_name: str = None, validator_name: str = None,
                   success: bool = None, duration_ms: int = None,
                   metadata: dict = None, error_message: str = None):
        """Internal: buffer a log event."""
        self._buffer.append({
            "id": str(uuid.uuid4()),
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "timestamp": datetime.utcnow().isoformat(),
            "phase": phase or self._current_phase,
            "event_type": event_type,
            "tool_name": tool_name,
            "validator_name": validator_name,
            "success": success,
            "duration_ms": duration_ms,
            "metadata": json.dumps(metadata) if metadata else None,
            "error_message": error_message
        })
