# StorageEngine Decentralization Rollout — Risk Register

## Scope

This register captures risks for the decentralized storage rollout (Phases 0–5) with mitigations and required tests/evidence.

## Risk format

- **ID**
- **Risk**
- **Impact**
- **Likelihood**
- **Mitigation**
- **Required tests / evidence**

---

## R1 — Epoch churn breaks placement assumptions
- **Risk**: Node join/leave/revocation near epoch boundaries changes eligible_nodes; placement must remain replayable.
- **Impact**: Replica sets diverge between nodes; missing shards or inconsistent expected obligations.
- **Likelihood**: Medium
- **Mitigation**:
  - Eligibility changes only via `advance_epoch(epoch, snapshots)`.
  - StorageEvents must record `epoch` used for placement.
- **Required tests / evidence**:
  - Unit tests: placements stable within epoch; deterministic change across epoch.
  - Replay drill evidence: identical state hash given same log + constants.

## R2 — Proof failures and unverifiable shards
- **Risk**: Proof generation/verification is incomplete or inconsistent; `get_proof` returns unverifiable data.
- **Impact**: Cannot enforce NOD incentives; cannot audit shard health.
- **Likelihood**: Medium
- **Mitigation**:
  - Deterministic proof algorithm and canonical proof encoding.
  - Proofs recorded as events (or derivable) and counted deterministically.
- **Required tests / evidence**:
  - Unit tests: proof determinism per shard.
  - API tests: bad request vs success behavior.

## R3 — Dual-write divergence (Postgres vs StorageEngine)
- **Risk**: Dual-write phase produces mismatched content IDs, versions, or commit hashes.
- **Impact**: UI and audit surfaces become untrustworthy; replay mismatch.
- **Likelihood**: High (during migration)
- **Mitigation**:
  - Deterministic consistency checker.
  - Declare Postgres as non-authoritative cache/snapshot only.
- **Required tests / evidence**:
  - Dual-write verification tests.
  - Evidence artifacts comparing hashes across stores.

## R4 — Non-determinism introduced via telemetry or performance heuristics
- **Risk**: Placement or rewards accidentally depend on live metrics (latency, fastest node).
- **Impact**: Breaks replay and zero-simulation guarantees.
- **Likelihood**: Medium
- **Mitigation**:
  - Telemetry treated as observation-only and aggregated per epoch with deterministic rules.
  - Static Zero‑Sim checks and determinism tests on placement.
- **Required tests / evidence**:
  - AST scan evidence.
  - Replay harness for placement.

## R5 — Error semantics drift (infinite/unbounded exceptions)
- **Risk**: Interfaces leak runtime exceptions or non-enumerated error strings.
- **Impact**: Non-deterministic client behavior; unstable UI/API and audit incompatibility.
- **Likelihood**: Medium
- **Mitigation**:
  - Enforce finite error-code enum at API boundary.
  - Add tests ensuring 4xx/5xx mapping is stable.
- **Required tests / evidence**:
  - API boundary tests for all storage endpoints.

## R6 — OpenAGI misconfiguration leaks into consensus
- **Risk**: OpenAGI scoring becomes non-deterministic or influences placement/reward directly.
- **Impact**: Violates invariants; may create hidden economic manipulation surface.
- **Likelihood**: Medium
- **Mitigation**:
  - OpenAGI outputs are advisory metadata only.
  - All economic effects route through PolicyRegistry → TreasuryEngine.
  - Scores are bounded integers, recorded in metadata.
- **Required tests / evidence**:
  - Unit tests: scoring deterministic for fixed content.
  - Guardrail tests: no direct balance mutation from scoring path.

## R7 — Privacy regression (content or PII leaks into logs)
- **Risk**: StorageEvents/EQM logs accidentally contain plaintext content or identifying fields.
- **Impact**: Permanent privacy breach.
- **Likelihood**: Medium
- **Mitigation**:
  - Logs store hashes/IDs only; content remains ciphertext.
  - Add lint/test checks against prohibited fields.
- **Required tests / evidence**:
  - Log schema tests.
  - Negative tests asserting no plaintext fields present.

## R8 — Governance misconfiguration (constants drift without recording)
- **Risk**: Constants such as replication factor or block size change without being recorded for replay.
- **Impact**: Replay mismatch across versions.
- **Likelihood**: Medium
- **Mitigation**:
  - Treat constants as governed configuration; include in replay context.
  - Include constant version identifiers in StorageEvents.
- **Required tests / evidence**:
  - Replay tests with explicit config snapshots.

---

## Immediate next action

After this register, implement the StorageEvent schema and add deterministic tests that exercise:
- placement within epoch
- epoch advancement
- replay reconstruction
- finite error codes at API boundary
