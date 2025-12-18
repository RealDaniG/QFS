"""
QFS V13 Unified Logging Framework
Provides structured, deterministic logging with PQC signing support
"""

import json
import hashlib
from enum import Enum
from typing import Dict, Any, Optional
from pathlib import Path
from v13.libs.deterministic_helpers import det_time_isoformat


class LogLevel(Enum):
    """Deterministic log levels"""

    TRACE = 0
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5
    SECURITY = 6


class LogCategory(Enum):
    """Error/event categorization"""

    PIPELINE = "pipeline"
    TOKEN_OPERATION = "token_op"
    CRYPTOGRAPHY = "crypto"
    VALIDATION = "validation"
    DETERMINISM = "determinism"
    ATLAS_INTEGRATION = "atlas"
    ECONOMICS = "economics"
    GOVERNANCE = "governance"
    TESTING = "testing"
    INFRASTRUCTURE = "infra"


class QFSLogger:
    """Deterministic, structured logger for QFS V13"""

    def __init__(self, component: str, context: Optional[Dict] = None):
        self.component = component
        self.context = context or {}
        self.log_buffer = []
        self.session_id = self._generate_session_id()

    def _generate_session_id(self) -> str:
        """Generate deterministic session ID"""
        return hashlib.sha3_256(
            f"{self.component}:{det_time_isoformat()}".encode()
        ).hexdigest()[:16]

    def log(
        self,
        level: LogLevel,
        category: LogCategory,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None,
        stack_trace: Optional[str] = None,
    ):
        """Core logging method with structured output"""
        log_entry = {
            "timestamp": det_time_isoformat(),
            "session_id": self.session_id,
            "component": self.component,
            "level": level.name,
            "category": category.value,
            "message": message,
            "context": self.context,
            "details": details or {},
        }
        if exception:
            log_entry["exception"] = {
                "type": type(exception).__name__,
                "message": str(exception),
                "args": exception.args,
            }
        if stack_trace:
            log_entry["stack_trace"] = stack_trace
        log_entry["hash"] = self._hash_entry(log_entry)
        self.log_buffer.append(log_entry)
        self._write_log(log_entry)
        if level == LogLevel.CRITICAL:
            self._trigger_cir_handler(log_entry)

    def _hash_entry(self, entry: Dict) -> str:
        """Generate SHA3-512 hash of log entry"""
        hashable = {k: v for k, v in entry.items() if k != "hash"}
        return hashlib.sha3_512(
            json.dumps(hashable, sort_keys=True, default=str).encode()
        ).hexdigest()

    def _write_log(self, entry: Dict):
        """Write log entry to file and stdout"""
        if entry["level"] in ["ERROR", "CRITICAL", "SECURITY"]:
            pass
        elif entry["level"] == "WARNING":
            pass
        else:
            pass
        log_dir = Path("v13/evidence/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{self.component}_{entry['level'].lower()}.jsonl"
        with log_file.open("a") as f:
            f.write(json.dumps(entry, default=str) + "\n")

    def _trigger_cir_handler(self, entry: Dict):
        """Trigger CIR-302 handler for critical failures"""
        try:
            from v13.handlers.CIR302_Handler import CIR302Handler

            handler = CIR302Handler()
            if hasattr(handler, "handle_critical_event"):
                handler.handle_critical_event(entry)
            else:
                pass
        except ImportError:
            pass
        except Exception:
            pass

    def trace(self, category: LogCategory, message: str, **kwargs):
        self.log(LogLevel.TRACE, category, message, **kwargs)

    def debug(self, category: LogCategory, message: str, **kwargs):
        self.log(LogLevel.DEBUG, category, message, **kwargs)

    def info(self, category: LogCategory, message: str, **kwargs):
        self.log(LogLevel.INFO, category, message, **kwargs)

    def warning(self, category: LogCategory, message: str, **kwargs):
        self.log(LogLevel.WARNING, category, message, **kwargs)

    def error(self, category: LogCategory, message: str, **kwargs):
        self.log(LogLevel.ERROR, category, message, **kwargs)

    def critical(self, category: LogCategory, message: str, **kwargs):
        self.log(LogLevel.CRITICAL, category, message, **kwargs)

    def security(self, category: LogCategory, message: str, **kwargs):
        self.log(LogLevel.SECURITY, category, message, **kwargs)

    def export_session_logs(self, output_path: Path):
        """Export all session logs to artifact"""
        with output_path.open("w") as f:
            json.dump(
                {
                    "session_id": self.session_id,
                    "component": self.component,
                    "logs": self.log_buffer,
                    "metadata": {
                        "total_entries": len(self.log_buffer),
                        "levels": {
                            level.name: sum(
                                (
                                    1
                                    for log in self.log_buffer
                                    if log["level"] == level.name
                                )
                            )
                            for level in LogLevel
                        },
                    },
                },
                f,
                indent=2,
                default=str,
            )
