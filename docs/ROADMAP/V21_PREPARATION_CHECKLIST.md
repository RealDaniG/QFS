# v21 Preparation Checklist

**Goal:** Prepare for offline auth semantics and replicated sessions.

## Offline Auth Semantics

- [ ] **Offline Session Counters:** Design Lamport-style `local_seq` for sessions.
- [ ] **Access Token Caching:** Define strict max offline duration policies.
- [ ] **Delayed Events:** Design EvidenceBus support for out-of-order events.

## SessionStore Replication Surface

- [ ] **Append-Only Log:** Define `SessionStore` log format.
- [ ] **Raft/BFT API:** Design APIs (`append`, `getById`, `scan`) to be consensus-ready.
- [ ] **Correlation:** Specify how session mutations map to PoE IDs.

## Offline Action Queue

- [ ] **Queue Architecture:** Design client-side queue (Action, session_id, seq, sigs).
- [ ] **Backend Replay:** Plan verification logic for offline logs.
- [ ] **Reconnection:** define reconciliation flow.

## Trust & Policy

- [ ] **Offline Context:** Extend `resolveTrustContext()` for offline windows.
- [ ] **Degraded Trust:** Mark sessions as `offline_degraded`.
- [ ] **Reconnection Policy:** Define actions requiring fresh MFA/online check.

## Dependencies

- [ ] **Schema Freeze:** Ensure v20 schemas are immutable.
- [ ] **EvidenceBus:** Verify out-of-order event handling capabilities.
- [ ] **Raft Library:** Select/Verify Raft implementation for future integration.
