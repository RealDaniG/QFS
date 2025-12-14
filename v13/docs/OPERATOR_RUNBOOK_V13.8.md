# ATLAS V13.8 Operator Runbook

## 1. System Overview

ATLAS V13.8 runs in **"Zero-Simulation Mode"**, meaning all explanations and storage proofs are derived deterministically from the immutable QFS Coherence Ledger.

### Key Components

- **ATLAS API**: Serves `/explain/reward/{id}` and `/explain/storage/{id}`.
- **Replay Engine**: Reconstructs state from `LiveLedgerReplaySource`.
- **Drift Detector**: `v13.ops.DriftDetector` verifies consistency.

## 2. Monitoring & Alerts

### "Drift Detected" Alert

**Severity:** CRITICAL
**Meaning:** The code running in production produces a different result than what is recorded in the immutable ledger.
**Action:**

1. Isolate the node.
2. Run `DriftDetector` locally against the latest ledger artifact:

    ```bash
    python -m v13.ops.DriftDetector --ledger-path /var/data/qfs/ledger_v13.jsonl
    ```

3. If drift is confirmed, **ROLLBACK** the deployment immediately to the last known good commit.
4. Do not restart until the source of non-determinism (randomness, time dependency, library change) is identified.

## 3. Configuration

### Environment Variables

- `EXPLAIN_THIS_SOURCE`: Must be set to `live_ledger` in production.
- `QFS_LEDGER_PATH`: Absolute path to the `.jsonl` ledger file.
- `QFS_STORAGE_PATH`: Path to decentralized storage persistence.

## 4. Routine Maintenance

### Daily Replay Drill

The `replay-drill` CI/CD job runs nightly.

- **Success:** Codebase is mathematically consistent with history.
- **Failure:** A recent commit introduced a breaking change to the deterministic policy logic.

### Ledger Rotation

Archived ledger files should be moved to cold storage. Update `QFS_LEDGER_PATH` to point to the active hot ledger segment.
