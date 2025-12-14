# ATLAS V13.8 Release Notes

**Release Date:** 2025-12-14
**Version:** V13.8-RC1
**Status:** Production Ready
**Codename:** "Zero-Sim Absolute"

## 🌟 Highlights

ATLAS V13.8 marks the completion of the "Zero-Simulation" initiative. It integrates the QFS Coherence Ledger directly into the explanation loop, ensuring that every user-facing number, ranking, and reward is mathematically provable.

### 🚀 Key Features

* **Live Ledger Replay**: `LiveLedgerReplaySource` allows ATLAS to hydrate state directly from immutable `.jsonl` ledger artifacts, eliminating database drift risks.
* **Time-Travel Debugging**: Operators and policies can now query state *as it existed* at any specific epoch via `PolicyRegistry`.
* **Cryptographic Storage Audits**: `StorageEngine` now emits full Merkle Proofs. The new `storage_explainability` module enables verifying `RF=3` placement and data integrity without trusting the node.
* **Operational Drift Detection**: The new `DriftDetector` tool and `replay-drill` CI workflow automate the detection of non-deterministic behavior.

### 🔒 Security & Compliance

* **Zero-Simulation**: 100% compliant. No external I/O or RNG allowed in explanation paths.
* **Audit Trails**: `PROOF_GENERATED` events are now unredacted to support transparent auditing.
* **MockPQC**: System currently uses SHA-256 for mock post-quantum signatures (Staging only); `liboqs` required for Production.

## 🛠️ Components Updated

* `v13.core.StorageEngine`: Merkle Proofs added.
* `v13.core.QFSReplaySource`: Live Ledger support added.
* `v13.ATLAS.src.api.routes.explain`: New endpoints for storage and historical queries.
* `v13.policy`: Added `storage_explainability` and `PolicyRegistry`.
* `v13.ops`: Added `DriftDetector`.

## 📚 New Documentation

* `v13/docs/STORAGE_AUDIT.md`: Guide for auditing storage proofs.
* `v13/docs/OPERATOR_RUNBOOK_V13.8.md`: Operating procedures for Zero-Sim mode.
* `v13/docs/STAGING_VALIDATION_REPORT.md`: Outcome of the V13.8 Staging Drill.

## ⚠️ Known Issues

* **liboqs dependency**: The `DriftDetector` prints a warning if `liboqs` is not installed. This is expected in environments without PQC hardware support.
