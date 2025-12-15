
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

## 6. Implementation Status (V13.8)

### E-001: Backend Endpoint

The endpoint `GET /explain/reward/{tx_id}` serves canonical explanations derived exclusively from `CoherenceLedger`.
It returns a `zero_sim_proof` containing:

* `input_state_hash`: Hash of the previous ledger state.
* `output_state_hash`: Hash of the current entry (guaranteed by ledger integrity).
* `entry_data_snapshot`: The raw data used to compute the hash (Client-side verifiable).
* `pqc_cid`: Correlation ID for Post-Quantum Cryptography audit.

### E-003: Verification Tooling

A CLI tool `v13/scripts/verify_reward_proof.py` is provided to independently verify the Zero-Sim Proof.
Usage:

```bash
python v13/scripts/verify_reward_proof.py <response_json_file>
```

It re-computes the SHA-256 hash of the snapshot and compares it against the `output_state_hash`, proving data has not been tampered with since finalization in the ledger.
