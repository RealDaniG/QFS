"""
Structured Logger & Trace Context
=================================

Provides JSON-based structured logging with mandatory trace ID propagation.
Integrates with CertifiedMath to link mathematical proofs to API requests.

Contracts:
- Output: Single-line JSON to stdout.
- Fields: timestamp (ISO8601), level, message, trace_id, span_id, component, data.
- Zero-Sim: Timestamp must be passed in if deterministic execution is required,
  otherwise defaults to system time (ONLY for Observability, NOT for Consensus).
"""

import sys
import json
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional
from v13.libs.deterministic_helpers import DeterministicID


@dataclass
class TraceContext:
    """Carries trace identifiers across the call stack."""

    trace_id: str
    span_id: str
    parent_id: Optional[str] = None

    @staticmethod
    def new_trace() -> "TraceContext":
        """Generate a new trace context (non-deterministic entry point)."""
        return TraceContext(
            trace_id=DeterministicID.next(), span_id=DeterministicID.next()
        )

    @staticmethod
    def from_headers(headers: Dict[str, str]) -> "TraceContext":
        """Extract trace context from headers (e.g., W3C Trace Context)."""
        # Simplified for P0
        tid = headers.get("x-trace-id") or DeterministicID.next()
        sid = headers.get("x-span-id") or DeterministicID.next()
        pid = headers.get("x-parent-id")
        return TraceContext(trace_id=tid, span_id=sid, parent_id=pid)


class StructuredLogger:
    """
    JSON Logger that enforces structured output.
    """

    def __init__(self, service_name: str = "qfs-core"):
        self.service_name = service_name

    def log(
        self,
        level: str,
        message: str,
        ctx: Optional[TraceContext] = None,
        data: Optional[Dict[str, Any]] = None,
        deterministic_timestamp: Optional[str] = None,
    ):
        """
        Emit a structured log line.

        Args:
            level: INFO, WARN, ERROR, DEBUG
            message: Human readable event description
            ctx: TraceContext for correlation
            data: Structured payload
            deterministic_timestamp: Optional ISO string for Zero-Sim replays.
        """
        # Zero-Sim Compliance Note:
        # If deterministic_timestamp is provided, use it.
        # If not, use Zero-Sim epoch placeholder.
        # If inside Consensus, caller MUST provide deterministic_timestamp.

        timestamp = deterministic_timestamp or "1970-01-01T00:00:00Z"

        payload = {
            "timestamp": timestamp,
            "level": level.upper(),
            "service": self.service_name,
            "message": message,
            "data": data or {},
        }

        if ctx:
            payload["trace_id"] = ctx.trace_id
            payload["span_id"] = ctx.span_id
            if ctx.parent_id:
                payload["parent_id"] = ctx.parent_id

        # Zero-Sim requires we don't assume stdout is safe if we were in strict logic,
        # but logger is strictly an effect.
        # In a real rigorous Zero-Sim, logs are outputs of the transition function.
        # Here we write to sys.stdout as the observability sink.

        try:
            # ensure_ascii=True to avoid encoding issues in generic log aggregators
            json_line = json.dumps(payload, ensure_ascii=True)
            sys.stdout.write(json_line + "\n")
            sys.stdout.flush()
        except Exception:
            # Fallback for critical logging failure
            pass

    def info(self, msg: str, ctx=None, **kwargs):
        self.log("INFO", msg, ctx, data=kwargs)

    def error(self, msg: str, ctx=None, **kwargs):
        self.log("ERROR", msg, ctx, data=kwargs)

    def warn(self, msg: str, ctx=None, **kwargs):
        self.log("WARN", msg, ctx, data=kwargs)


# Singleton instance
logger = StructuredLogger()
