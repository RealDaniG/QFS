"""
Logical time provider for Zero-Sim compliance.
In production: provides real wall-clock time.
In tests/replay: provides deterministic time.
"""

import time
from typing import Optional

# Global variable for test injection
_test_time: Optional[int] = None


def set_test_time(timestamp: int) -> None:
    """Inject deterministic time for testing/replay."""
    global _test_time
    _test_time = timestamp


def clear_test_time() -> None:
    """Clear test time injection."""
    global _test_time
    _test_time = None


def get_logical_time() -> int:
    """
    FastAPI dependency for logical timestamps.
    Returns:
        Current logical time (real or injected).
    """
    if _test_time is not None:
        return _test_time
    return int(time.time())
