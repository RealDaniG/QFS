"""
Metrics Adapter Stub
====================

Provides a unified interface for emitting metrics (counters, histograms).
Currently prints to logger logic or no-op.
"""

from typing import Dict, Any, Optional


class Metrics:
    @staticmethod
    def counter(name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """Increment a counter."""
        pass  # Stub: In prod, would push to Prometheus/StatsD

    @staticmethod
    def gauge(name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Set a gauge value."""
        pass  # Stub

    @staticmethod
    def histogram(name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a histogram observation."""
        pass  # Stub
