# v14 Monitoring & Observability Framework

**Version**: v14.0-social-layer  
**Purpose**: Production observability for ATLAS social modules  
**Status**: Framework Definition

## Metrics Schema

### Module-Level Metrics

#### Spaces Module

```json
{
  "module": "spaces",
  "metrics": {
    "events": {
      "space_created": {
        "count": 0,
        "success_rate": 1.0,
        "avg_latency_ms": 0,
        "chr_emitted": "0.0"
      },
      "space_joined": {
        "count": 0,
        "success_rate": 1.0,
        "avg_latency_ms": 0,
        "chr_emitted": "0.0"
      },
      "space_spoke": {
        "count": 0,
        "success_rate": 1.0,
        "avg_latency_ms": 0,
        "chr_emitted": "0.0"
      },
      "space_ended": {
        "count": 0,
        "success_rate": 1.0,
        "avg_latency_ms": 0,
        "chr_emitted": "0.0"
      }
    },
    "health": {
      "active_spaces": 0,
      "total_participants": 0,
      "avg_participants_per_space": 0.0
    }
  }
}
```

#### Wall Posts Module

```json
{
  "module": "wall",
  "metrics": {
    "events": {
      "post_created": {
        "count": 0,
        "success_rate": 1.0,
        "avg_latency_ms": 0,
        "chr_emitted": "0.0"
      },
      "post_quoted": {
        "count": 0,
        "success_rate": 1.0,
        "avg_latency_ms": 0,
        "chr_emitted": "0.0"
      },
      "post_pinned": {
        "count": 0,
        "success_rate": 1.0,
        "avg_latency_ms": 0,
        "chr_emitted": "0.0"
      },
      "post_reacted": {
        "count": 0,
        "success_rate": 1.0,
        "avg_latency_ms": 0,
        "flx_emitted": "0.0"
      }
    },
    "health": {
      "total_posts": 0,
      "pinned_posts": 0,
      "total_reactions": 0
    }
  }
}
```

#### Chat Module

```json
{
  "module": "chat",
  "metrics": {
    "events": {
      "conversation_created": {
        "count": 0,
        "success_rate": 1.0,
        "avg_latency_ms": 0,
        "chr_emitted": "0.0"
      },
      "message_sent": {
        "count": 0,
        "success_rate": 1.0,
        "avg_latency_ms": 0,
        "chr_emitted": "0.0"
      },
      "message_read": {
        "count": 0,
        "success_rate": 1.0,
        "avg_latency_ms": 0,
        "flx_emitted": "0.0"
      }
    },
    "health": {
      "active_conversations": 0,
      "total_messages": 0,
      "avg_messages_per_conversation": 0.0
    }
  }
}
```

### Economic Health Metrics

```json
{
  "economics": {
    "chr": {
      "total_emitted": "0.0",
      "by_module": {
        "spaces": "0.0",
        "wall": "0.0",
        "chat": "0.0"
      },
      "by_event_type": {
        "space_created": "0.0",
        "space_joined": "0.0",
        "space_spoke": "0.0",
        "space_ended": "0.0",
        "post_created": "0.0",
        "post_quoted": "0.0",
        "post_pinned": "0.0",
        "conversation_created": "0.0",
        "message_sent": "0.0"
      }
    },
    "flx": {
      "total_emitted": "0.0",
      "by_module": {
        "wall": "0.0",
        "chat": "0.0"
      },
      "by_event_type": {
        "post_reacted": "0.0",
        "message_read": "0.0"
      }
    }
  }
}
```

### Zero-Sim Compliance Metrics

```json
{
  "zero_sim": {
    "violations": {
      "total": 0,
      "by_severity": {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
      },
      "by_type": {
        "time_dependency": 0,
        "randomness": 0,
        "float_arithmetic": 0,
        "external_io": 0,
        "unsorted_iteration": 0
      }
    },
    "replay": {
      "success_rate": 1.0,
      "total_replays": 0,
      "failed_replays": 0,
      "avg_replay_time_ms": 0
    }
  }
}
```

## Structured Event Logs

### Log Format

```json
{
  "timestamp": "2025-12-18T18:00:00Z",
  "module": "spaces",
  "actor": "wallet_alice",
  "event_type": "space_created",
  "event_id": "space_created_space_123",
  "tx_hash": "0x...",
  "state_root_before": "0x...",
  "state_root_after": "0x...",
  "regression_hash_id": "v14_social_full",
  "trace_id": "trace_001",
  "metadata": {
    "space_id": "space_123",
    "title": "Tech Talk",
    "reward_chr": "0.5"
  }
}
```

### Trace IDs

**Live Path**: `trace_live_{timestamp}_{module}_{event_id}`  
**Replay Path**: `trace_replay_{scenario_id}_{module}_{event_id}`

Comparison: `diff trace_live_* trace_replay_*` should be empty

## Dashboard Definitions

### Real-Time Dashboard

**Location**: `monitoring/dashboards/realtime.json`

**Panels**:

1. Event Rate (events/sec by module)
2. Success Rate (% successful events)
3. Economic Flow (CHR/FLX emitted per minute)
4. Active Entities (spaces, conversations, posts)
5. Zero-Sim Violations (should be 0)
6. Replay Success Rate (should be 100%)

### Economic Dashboard

**Location**: `monitoring/dashboards/economics.json`

**Panels**:

1. Total CHR/FLX Emitted (cumulative)
2. Distribution by Module (pie chart)
3. Distribution by Event Type (bar chart)
4. Top Earners (wallets with most rewards)
5. Anomaly Detection (spikes, unusual patterns)

### Compliance Dashboard

**Location**: `monitoring/dashboards/compliance.json`

**Panels**:

1. Zero-Sim Violation Trend (over time)
2. Violation Types Breakdown
3. Replay Verification Status
4. Regression Hash Stability
5. Determinism Score (100% = fully deterministic)

## Alerting Rules

### Critical Alerts

```yaml
alerts:
  - name: zero_sim_violation_detected
    condition: zero_sim.violations.total > 0
    severity: critical
    action: page_on_call
    
  - name: replay_failure
    condition: zero_sim.replay.success_rate < 1.0
    severity: critical
    action: page_on_call
    
  - name: regression_hash_mismatch
    condition: regression_hash != expected_hash
    severity: critical
    action: block_deployment
```

### Warning Alerts

```yaml
alerts:
  - name: high_event_failure_rate
    condition: event.success_rate < 0.95
    severity: warning
    action: notify_team
    
  - name: economic_anomaly
    condition: chr_emitted_rate > 2 * avg_rate
    severity: warning
    action: investigate
    
  - name: slow_event_processing
    condition: avg_latency_ms > 1000
    severity: warning
    action: performance_review
```

## Collection & Export

### Metrics Collection

```python
# monitoring/collectors/metrics_collector.py

from dataclasses import dataclass
from typing import Dict, List
import json

@dataclass
class MetricPoint:
    timestamp: int
    module: str
    event_type: str
    count: int
    success_rate: float
    latency_ms: float
    token_emitted: str

class MetricsCollector:
    def __init__(self):
        self.metrics: List[MetricPoint] = []
    
    def record_event(
        self,
        module: str,
        event_type: str,
        success: bool,
        latency_ms: float,
        token_amount: str,
        timestamp: int
    ):
        """Record a single event metric"""
        # Implementation
        pass
    
    def export_json(self, filepath: str):
        """Export metrics to JSON"""
        with open(filepath, 'w') as f:
            json.dump([m.__dict__ for m in self.metrics], f, indent=2)
    
    def export_prometheus(self, filepath: str):
        """Export metrics in Prometheus format"""
        # Implementation
        pass
```

### Log Aggregation

```python
# monitoring/collectors/log_aggregator.py

class LogAggregator:
    def __init__(self):
        self.logs: List[Dict] = []
    
    def append_log(self, log_entry: Dict):
        """Append structured log entry"""
        self.logs.append(log_entry)
    
    def query(self, filters: Dict) -> List[Dict]:
        """Query logs with filters"""
        # Implementation
        pass
    
    def export_timeline(self, filepath: str):
        """Export human-readable timeline"""
        # Implementation
        pass
```

## Integration Points

### CI Integration

Add to `.github/workflows/ci.yml`:

```yaml
- name: Collect Metrics
  run: |
    python monitoring/collectors/metrics_collector.py \
      --input test-results.xml \
      --output metrics.json

- name: Upload Metrics
  uses: actions/upload-artifact@v4
  with:
    name: metrics
    path: metrics.json
```

### Production Integration

```python
# In each module's event emission

from monitoring.collectors import MetricsCollector

metrics = MetricsCollector()

def emit_space_created(space, cm, log_list, pqc_cid=""):
    start_time = time.perf_counter()
    
    # Emit event
    event = _create_event(...)
    
    # Record metric
    latency_ms = (time.perf_counter() - start_time) * 1000
    metrics.record_event(
        module="spaces",
        event_type="space_created",
        success=True,
        latency_ms=latency_ms,
        token_amount=event.amount,
        timestamp=space.created_at
    )
    
    return event
```

## Usage

### Start Monitoring

```bash
# Start metrics collector
python monitoring/collectors/metrics_collector.py --daemon

# Start log aggregator
python monitoring/collectors/log_aggregator.py --daemon

# Start dashboard server
python monitoring/dashboard_server.py --port 8080
```

### View Dashboards

```bash
# Open in browser
http://localhost:8080/dashboards/realtime
http://localhost:8080/dashboards/economics
http://localhost:8080/dashboards/compliance
```

### Export Reports

```bash
# Export metrics
python monitoring/export_metrics.py --format json --output metrics_report.json

# Export logs
python monitoring/export_logs.py --format markdown --output logs_timeline.md
```

---

**Status**: Framework defined  
**Next**: Implement collectors and dashboards
