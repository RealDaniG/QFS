# P2 Auth Integration Pattern

**Concept:** Apply the "Vertical Slice" + "Golden Trace" pattern from P2 to Authentication.

## Vertical Slice: AuthService

- **Core:** `AuthService` module.
- **Extension Points:**
  - `set_wallet_verifier()`
  - `set_mock_pqc_verifier()`
  - `set_session_store()`

## Golden Trace

- **Replayability:** Every auth action sequence (Login -> Refresh -> Revoke) must be replayable bit-for-bit.
- **Tests:** `tests/replay/auth_golden_trace.py` verifies this property.

## Observability

- **AuthObservation:** Events for anomalies (e.g., suspicious IP, device mismatch).
- **Correlation:** Link `AuthObservation` to `AGIObservation` for governance advisory.
