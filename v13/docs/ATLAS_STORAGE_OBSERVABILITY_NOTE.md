# ATLAS ↔ Storage Observability (Read-only, Replay-derived)

## Purpose

This note describes how ATLAS can safely surface storage observability without violating QFS/ATLAS invariants:

- QFS is the source of truth
- UI is read-only for economics
- all metrics are deterministic and replayable

## Source of truth

ATLAS should consume storage observability as **replay-derived views** computed from StorageEvents, not by polling live node performance.

Recommended source module:

- `v13/core/storage_economic_views.py` (pure function over StorageEvents)

## Suggested UI panels (read-only)

- **Storage Health Panel**
  - Current epoch
  - eligible node count (AEGIS-verified)
  - bytes stored per node (bucketable)
  - proof generated counts per node
  - proof failure counts (global + per shard if added later)

- **Replay Assurance Panel**
  - last replay test hash
  - deterministic replay pass/fail status (evidence artifact)

## Non-goals

- No client-side inference of “fastest node” or adaptive shard placement.
- No UI-driven economic mutations.

## Next implementation step (optional)

Once a stable storage API surface exists, ATLAS can add a read-only endpoint such as:

- `GET /api/v1/metrics/storage/economics` (already exists in ATLAS backend)

…provided it is backed by replay-derived metrics and does not read wall-clock telemetry.
