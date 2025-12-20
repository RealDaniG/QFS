# Observability Specification (V18)

## 1. Backend Logging Standards

All API services must adhere to the following structured logging format (JSON preferred in production, Text in dev):

**Format:**
`[TIMESTAMP] [LEVEL] [MODULE] [REQUEST_ID] Message {metadata}`

**Events to Log:**

- **Auth**:
  - `INFO`: Session created (Wallet: `...1234`).
  - `WARN`: Invalid signature attempt.
  - `ERROR`: Token generation failure.
- **Governance**:
  - `INFO`: Proposal created, Vote cast.
  - `WARN`: Vote rejected (eligibility).
- **Content**:
  - `INFO`: Content published (CID: `...`).
  - `ERROR`: Replication failure.

**HTTP Access Logs:**

- Must include: `Method`, `Path`, `Status Code`, `Latency (ms)`, `User-Agent`.

## 2. Metrics (Prometheus/OpenTelemetry)

- **Counters**:
  - `http_requests_total{method, status, route}`
  - `proposals_created_total`
  - `votes_cast_total`
- **Gauges**:
  - `active_sessions`
  - `connected_peers`

## 3. Frontend Telemetry

- **Client-side Errors**: Capture uncaught expectations and send to `/api/v1/telemetry/error` (to be implemented).
- **Performance**: Track "Time to First Byte" and "Time to Interactive" for Dashboard.

## 4. Dashboard

Logs should be shipped to a centralized aggregator (e.g., ELK Stack, Loki) for visualization.
