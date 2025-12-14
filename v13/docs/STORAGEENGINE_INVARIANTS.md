# StorageEngine Invariants (QFS V13)

## Scope

This document defines **hard invariants** for `v13/core/StorageEngine.py` and how each invariant is **checked**.

**Non-negotiable principle:** Storage state and all storage-derived economics must be **reconstructible** from deterministic configuration + ordered storage/EQM events (no wall-clock, no randomness, no heuristic placement).

## Definitions

- **StorageEngine**: Deterministic storage component providing content addressing, sharding, replication assignment, proofs, and deterministic storage metrics.
- **EQM / StorageEvent**: An ordered, append-only event record sufficient to replay StorageEngine state.
- **Deterministic timestamp**: A tick provided by deterministic time (not wall-clock), passed into consensus paths as data.

## Invariant format

Each invariant is defined as:

- **ID**
- **Statement**
- **Checkable conditions**
- **Test types** (unit, replay harness, zero-sim)

---

## I. Determinism & Zero‑Sim invariants

### SE-D1 — No wall-clock / random / nondeterministic ordering
- **Statement**: StorageEngine consensus paths must not depend on OS time, randomness, or nondeterministic iteration.
- **Checkable conditions**:
  - No `datetime.now()`, `time.time()`, `random.*`, `uuid.*` in StorageEngine deterministic methods.
  - Iteration over dicts must be via deterministic order (`sorted(...)`) when order affects results.
- **Test types**:
  - **Zero‑Sim AST scan** over `v13/core/StorageEngine.py`.
  - **Determinism unit tests** asserting same inputs → same outputs across multiple runs.

### SE-D2 — Hashing is canonical and stable
- **Statement**: `hash_commit` and `shard_id` must be stable functions of canonical inputs.
- **Checkable conditions**:
  - `hash_commit = SHA3-256(content_bytes || schema_version || canonical_json(metadata))`.
  - `shard_id = SHA3-256(f"{object_id}:{version}:{shard_index}")`.
  - Canonical JSON uses `sort_keys=True` and fixed separators.
- **Test types**:
  - Unit tests on `_compute_content_hash` and `_compute_shard_id`.

### SE-D3 — Placement depends only on eligible node set + shard_id
- **Statement**: Replica assignment must be a pure function of `shard_id` and the epoch’s eligible node list.
- **Checkable conditions**:
  - Eligible node list must be **sorted by node_id**.
  - Assignment uses deterministic start index (`H(shard_id) mod N`) and consecutive selection.
- **Test types**:
  - Unit tests for `_assign_nodes_to_shard` given fixed node sets.
  - Replay tests ensuring placements re-derive from event logs.

---

## II. Replay & audit invariants

### SE-R1 — Replay completeness from StorageEvents
- **Statement**: StorageEngine state must be reconstructible from ordered StorageEvents (and deterministic config/constants).
- **Checkable conditions**:
  - For each `STORE` (and later UPDATE/DELETE_MARKER), event contains at minimum:
    - `object_id`, `version`, `content_size`, `hash_commit`, `shard_ids`, `assigned_nodes`, `timestamp_tick`, `epoch`.
  - Replay does not require external data sources.
- **Test types**:
  - Replay harness (e.g. `v13/scripts/run_storage_replay_drill.py`), plus golden-hash comparisons.
  - Unit replay tests: `v13/tests/storage/test_storageengine_replay.py` (live vs replay snapshot + hash).

### SE-R2 — List operations are deterministically sorted
- **Statement**: `list_objects(filters)` output ordering must be deterministic.
- **Checkable conditions**:
  - Sorting by `(object_id, version)`.
  - Filter iteration uses deterministic ordering.
- **Test types**:
  - Unit tests: same state → identical list output across runs.

### SE-R3 — Proof generation is deterministic for same content chunk
- **Statement**: `merkle_root` and any generated shard proof must be deterministic for the same chunk bytes.
- **Checkable conditions**:
  - Same chunk yields same `merkle_root`.
  - Proof generation contains no wall-clock/random inputs.
- **Test types**:
  - Unit tests for `_generate_merkle_root` and `_generate_shard_proof`.

### SE-R4 — Proof events are logged and replay-accountable
- **Statement**: Proof requests must emit deterministic `PROOF_GENERATED`/`PROOF_FAILED` StorageEvents so proof accounting can be reconstructed from logs.
- **Checkable conditions**:
  - `get_storage_proof` emits `PROOF_GENERATED` on success with `replica_sets` including assigned nodes.
  - Missing shard emits `PROOF_FAILED` with a finite `error_code`.
  - Replay-derived proof counts match live proof calls.
- **Test types**:
  - Replay proof accounting tests: `v13/tests/storage/test_storageengine_replay.py`.
  - Replay-derived metrics tests: `v13/tests/test_storage_economic_views.py`.

## Replay helper (test-only)

- `v13/tests/storage/test_storageengine_replay.py::replay_storage_events` is the current pure replay helper used by tests.

---

## III. Boundary invariants (economics + safety)

### SE-E1 — StorageEngine does not mint/burn user tokens directly
- **Statement**: StorageEngine must not directly mutate user balances. It may only track deterministic metrics and compute deterministic fees/reward candidates.
- **Checkable conditions**:
  - StorageEngine does not call TreasuryEngine mint/burn paths.
  - StorageEngine exposes metrics to TokenStateBundle via `update_storage_metrics_in_token_bundle`.
- **Test types**:
  - Static scan test: no imports/calls to governance treasury mutation APIs.
  - Unit tests confirming TokenStateBundle update is a pure mapping from node metrics.

### SE-E2 — ATR fees computed deterministically
- **Statement**: Storage ATR fee calculations must be integer-only and deterministic.
- **Checkable conditions**:
  - Uses CertifiedMath/BigNum128.
  - Fee depends only on content size and deterministic metadata fields.
- **Test types**:
  - Unit tests on `_calculate_atr_storage_cost` with fixed inputs.

### SE-S1 — Error space is finite, enumerated
- **Statement**: StorageEngine interface errors must be mapped to a bounded set of error codes, not unstructured exceptions.
- **Checkable conditions**:
  - Public interface methods return `{ok: false, error_code: ...}` or raise only mapped exceptions at the API boundary.
- **Test types**:
  - API boundary tests validating 4xx/5xx mapping is deterministic.

---

## IV. AEGIS & epoch invariants

### SE-A1 — Eligibility changes only at epoch boundaries
- **Statement**: Node eligibility is evaluated at epoch transitions, not per-request.
- **Checkable conditions**:
  - `advance_epoch()` recomputes verification and invalidates caches.
  - `get_eligible_nodes()` uses cached, deterministic results.
- **Test types**:
  - Unit tests simulating epoch changes and verifying placement changes.

### SE-A2 — AEGIS integration cannot introduce nondeterminism
- **Statement**: AEGIS verification inputs must be replayable snapshots.
- **Checkable conditions**:
  - `set_aegis_context()` accepts snapshots; verification does not read live telemetry.
- **Test types**:
  - Unit tests with fixed registry/telemetry snapshots.

---

## Implementation alignment notes

- Current implementation provides:
  - `put_content`, `get_content`, `get_storage_proof`, `list_objects`, `advance_epoch`, `get_eligible_nodes`.
  - `storage_event_log` exists but is not yet a full StorageEvent schema (missing shard_ids/assigned_nodes in the event payload).

Next step after this invariants list is to define the authoritative StorageEvent schema and error-code mapping (see `STORAGEENGINE_INTERFACE_SPEC.md`).
