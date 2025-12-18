# Open-A.G.I Read-Only Integration Contract (v1.0)

**Version:** 1.0.0
**Status:** DRAFT
**Last Updated:** 2025-12-17

## Overview

Open-A.G.I acts as an external advisory system. It provides high-intelligence signals (e.g., content quality assessment, risk analysis) but **HAS NO WRITE AUTHORITY** over the QFS ledger.

## Trust Boundary

- **Read Access:** Full transparency (Ledger, Metrics, Content).
- **Write Access:** **BLOCKED**. Can only submit "Signals" to a holding area.
- **Influence:** Signals are inputs to the `PolicyEngine`. They do not mutate state directly.

## Signal Protocol

All signals must match the `AdvisorySignal` canonical schema and be PQC-signed.

### 1. Submit Advisory Signal

**POST /v1/advisory/submit**

- **Request:** `AdvisorySignal` (JSON)
- **Response:**

  ```json
  {
    "status": "RECEIVED",
    "signal_hash": "sha256..."
  }
  ```

- **Processing:**
  1. QFS validates PQC signature.
  2. QFS verifies `source_ai_id` is a registered oracle.
  3. Signal is logged to `SignalLedger` (Immutable).
  4. Signal is forwarded to `PolicyEngine` for the next epoch.

### 2. Read Public State

**GET /v1/ledger/public/latest**

- **Response:** Snapshot of current block header and state roots.

**GET /v1/metrics/network**

- **Response:**

  ```json
  {
    "tps": 1500,
    "coherence_score": 0.99,
    "active_nodes": 50
  }
  ```

## Rate Limiting

- **Global:** 1000 requests/second.
- **Per Oracle:** 100 requests/second.
- **Violation:** IP Ban + 429 Too Many Requests.

## Security

- **Authentication:** API Key (Read) + PQC (Write Signal).
- **Telemetry:** All requests are logged for audit.
- **Isolation:** Open-A.G.I API runs on a separate gateway port (default: 8081).
