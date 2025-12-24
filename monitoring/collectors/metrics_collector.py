"""
metrics_collector.py - v14 Metrics Collection

Collects metrics from v14 social modules for observability.
Supports JSON and Prometheus export formats.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import json
from pathlib import Path
from v13.libs.BigNum128 import BigNum128


@dataclass
class MetricPoint:
    """Single metric data point"""

    timestamp: int
    module: str
    event_type: str
    count: int
    success_rate: float
    latency_ms: float
    token_emitted: str
    token_type: str  # CHR or FLX


class MetricsCollector:
    """
    Collects and aggregates metrics from social modules.

    Thread-safe for concurrent event recording.
    Supports multiple export formats.
    """

    def __init__(self):
        self.metrics: List[MetricPoint] = []
        self.aggregated: Dict[str, Dict] = {"spaces": {}, "wall": {}, "chat": {}}

    def record_event(
        self,
        module: str,
        event_type: str,
        success: bool,
        latency_ms: float,
        token_amount: str,
        token_type: str,
        timestamp: Optional[int] = None,
    ):
        """
        Record a single event metric.

        Args:
            module: Module name (spaces, wall, chat)
            event_type: Event type (e.g., space_created)
            success: Whether event succeeded
            latency_ms: Processing latency in milliseconds
            token_amount: Token amount emitted (as string)
            token_type: CHR or FLX
            timestamp: Event timestamp (defaults to 0 for Zero-Sim)
        """
        if timestamp is None:
            # Zero-Sim requires deterministic timestamp entry.
            # Default to 0 if not provided. Use logical clocks in production.
            timestamp = 0

        # Create metric point
        metric = MetricPoint(
            timestamp=timestamp,
            module=module,
            event_type=event_type,
            count=1,
            success_rate=1.0 if success else 0.0,
            latency_ms=latency_ms,
            token_emitted=token_amount,
            token_type=token_type,
        )

        self.metrics.append(metric)

        # Update aggregated metrics
        if event_type not in self.aggregated[module]:
            self.aggregated[module][event_type] = {
                "count": 0,
                "success_count": 0,
                "total_latency_ms": 0.0,
                "token_emitted": "0.0",
            }

        agg = self.aggregated[module][event_type]
        agg["count"] += 1
        if success:
            agg["success_count"] += 1
        agg["total_latency_ms"] += latency_ms

        # Add token amounts (simplified - would use BigNum128 in production)
        try:
            current = BigNum128.from_string(agg["token_emitted"])
            new = BigNum128.from_string(token_amount)
            agg["token_emitted"] = str(current + new)
        except ValueError:
            pass

    def get_summary(self) -> Dict:
        """Get summary statistics"""
        summary = {}

        for module, events in self.aggregated.items():
            summary[module] = {}
            for event_type, agg in events.items():
                count = agg["count"]
                success_rate = agg["success_count"] / count if count > 0 else 0.0
                avg_latency = agg["total_latency_ms"] / count if count > 0 else 0.0

                summary[module][event_type] = {
                    "count": count,
                    "success_rate": success_rate,
                    "avg_latency_ms": avg_latency,
                    "token_emitted": agg["token_emitted"],
                }

        return summary

    def export_json(self, filepath: str):
        """Export metrics to JSON file"""
        output = {
            "summary": self.get_summary(),
            "raw_metrics": [asdict(m) for m in self.metrics],
        }

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(output, f, indent=2)

    def export_prometheus(self, filepath: str):
        """Export metrics in Prometheus format"""
        lines = []

        # Event counts
        lines.append(
            "# HELP qfs_events_total Total number of events by module and type"
        )
        lines.append("# TYPE qfs_events_total counter")

        for module, events in self.aggregated.items():
            for event_type, agg in events.items():
                lines.append(
                    f'qfs_events_total{{module="{module}",event_type="{event_type}"}} {agg["count"]}'
                )

        # Success rates
        lines.append("\n# HELP qfs_events_success_rate Success rate of events")
        lines.append("# TYPE qfs_events_success_rate gauge")

        for module, events in self.aggregated.items():
            for event_type, agg in events.items():
                count = agg["count"]
                success_rate = agg["success_count"] / count if count > 0 else 0.0
                lines.append(
                    f'qfs_events_success_rate{{module="{module}",event_type="{event_type}"}} {success_rate}'
                )

        # Latencies
        lines.append("\n# HELP qfs_events_latency_ms Average event processing latency")
        lines.append("# TYPE qfs_events_latency_ms gauge")

        for module, events in self.aggregated.items():
            for event_type, agg in events.items():
                count = agg["count"]
                avg_latency = agg["total_latency_ms"] / count if count > 0 else 0.0
                lines.append(
                    f'qfs_events_latency_ms{{module="{module}",event_type="{event_type}"}} {avg_latency}'
                )

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            f.write("\n".join(lines))


# Global collector instance
_collector = MetricsCollector()


def get_collector() -> MetricsCollector:
    """Get global metrics collector instance"""
    return _collector


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="QFS v14 Metrics Collector")
    parser.add_argument("--input", help="Input test results XML")
    parser.add_argument("--output", default="metrics.json", help="Output metrics file")
    parser.add_argument("--format", choices=["json", "prometheus"], default="json")

    args = parser.parse_args()

    # For now, just create empty metrics file
    # In production, would parse test results and collect metrics
    collector = get_collector()

    if args.format == "json":
        collector.export_json(args.output)
    else:
        collector.export_prometheus(args.output)

    print(f"✅ Metrics exported to {args.output}")
