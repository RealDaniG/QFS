# PQC Anchoring Plan (v13.5)

> **Status**: Draft / Stub Implementation
> **Goal**: Anchor deterministic QFS state to a post-quantum secure medium (e.g., Dilithium-signed log or fast PQC chain).

## 1. Anchoring Hierarchy

To balance auditability with performance, we use a 3-tier structure:

1. **Event (Fast)**:
    * PoE log entries (e.g., `hsmf_proof`, `proposal_proof`).
    * Emitted at ~100ms-1s scale.
    * Protection: SHA-256 Chaining in `EvidenceBus`.

2. **Batch (Medium)**:
    * Aggregated segment of N events (e.g., 100 events or 1 minute).
    * Result: `MerkleRoot` of the batch.
    * Protection: PQC Signature (Dilithium5) by the Validator Node.
    * *Implementation*: `PQCAnchorService` (in-memory aggregation).

3. **Global Anchor (Slow/Hard)**:
    * Periodic submission of Batch Roots to a public ledger or timestamp authority.
    * Frequency: ~1 Hour.
    * Protection: Distributed Consensus / Public Blockchain.

## 2. PQC Interface Definition

The `PQCAnchorStub` provides the interface that `RealPQCAnchor` will later fulfill.

```python
class AnchorProof:
    batch_id: str
    merkle_root: str
    pqc_signature: str # "MOCK_SIG..." in stub
    timestamp: int
```

## 3. Transition Plan

1. **Phase 1 (Current)**:
    * Use `PQCAnchorStub`.
    * Signature = `MOCK_SIG_{Hash}`.
1. **Phase 1 (Current)**:
    * Use `PQCAnchorStub`.
    * Signature = `MOCK_SIG_{Hash}`.
    * Verify integration point in `EvidenceBus`.

1. **Phase 2 (Next)**:
    * Swap `Stub` for `liboqs` wrapper (Dilithium3/5).
    * Key management via `KeyLedger`.

## 4. Threat Model & Stub Status

> **IMPORTANT**: In v13.5, PQC anchoring is **STUBBED**.
>
> * Signatures are `MOCK_DILITHIUM_SIG...`.
> * These allow us to verify the `EvidenceBus` -> `Batch` -> `Proof` pipeline integration.
> * They provide **NO** cryptographic security until the `RealPQCAnchor` module is swapped in (Phase 2).

* **Long-Range Attacks**: Mitigated by hourly Global Anchors.
* **Key Compromise**: Validator keys are rotated (design TBD).
* **Quantum Decryption**: All historic anchors are PQC-signed, future-proof.

## 5. Implementation Roadmap

### Phase 1: Stub (Completed v13.5)

* **Signature**: `MOCK_DILITHIUM_SIG...`
* **Output**: Valid `AnchorProof` structure emitted to log.

### Phase 2: Real PQC Integration (Next)

* **Library**: `liboqs-python` (Dilithium5).

* **Wrapper**: Create `v13/core/pqc/RealPQCAnchor.py` implementing the `sign_batch(root)` interface.
* **Key Management**: Keys loaded from `KeyLedger` (encrypted at rest).

### Phase 3: Global Anchoring

* **Target**: Public Timestamp Server or QFS Mainnet (when ready).

* **Frequency**: Every 1 Hour (Global Anchor) vs Every 100 Events (Batch Anchor).
