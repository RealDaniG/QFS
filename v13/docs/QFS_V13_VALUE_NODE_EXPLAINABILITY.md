# QFS V13 Value Node Explainability

## 1. The "Explain-This" Philosophy

Every value displayed in the ATLAS UI must be traceable back to its origin events in the `CoherenceLedger`. "Value Node Explainability" is the technical implementation of this requirement.

## 2. Architecture

1. **Ledger Event**: A `ReferralRewarded` or `ContentCoherenceScored` event is written to the ledger.
2. **Storage Engine**: The event is indexed deterministically in the `StorageEngine`.
3. **Explanation Service**: When a user queries a balance (e.g. "Why do I have 50 FLX?"), the service:
    * Replays the ledger log for that wallet.
    * Aggregates the specific `amount_scaled` deltas.
    * Generates a cryptographic proof (PQC signature) of the replay result.

## 3. Implementation Interfaces

* **Backend**: `v13/ATLAS/src/signals/explainability.py` (and related services).
* **Frontend**: `StorageExplainPanel.tsx` renders the visual trace.

## 4. Zero-Sim Compliance

The explanation pipeline is strictly read-only and deterministic. It does **not** use heuristics. If the ledger cannot prove a value, the value is invalid (`CIR-302`).

## 5. Audit Trails

All explanation requests are logged with a `pqc_cid` to ensure that even the act of explaining is auditable.
