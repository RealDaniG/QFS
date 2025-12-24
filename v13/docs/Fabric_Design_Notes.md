# Fabric Design Notes (Post-HSMF)

> **Goal**: Scale QFS from a single verified node to a Raft-based consensus cluster without rewriting the deterministic core (HSMF/Governance).

## 1. Architecture Separation

We follow the **State Machine Replication (SMR)** pattern:

```
[ Clients ] -> [ Gateway (API) ] -> [ Consensus Transport (Raft) ] -> [ Replicated Log ]
                                                                             |
      +----------------------------------------------------------------------+
      v
[ Deterministic State Machine (QFS Core) ]
   |-- HSMF.py (Economics)
   |-- ProposalEngine.py (Governance)
   |-- EvidenceBus (PoE)
```

## 2. The Apply Loop

Use a single entry point for all state mutations:

```python
def apply_log_entry(entry: LogEntry):
    if entry.type == "HSMF_ACTION":
        HSMF.apply(...)
    elif entry.type == "GOV_PROPOSAL":
        ProposalEngine.create_proposal(...)
    elif entry.type == "GOV_VOTE":
        VoteEngine.cast_vote(...)
```

**Zero-Sim Advantage**: Because QFS Core is 100% deterministic (no `time`, no `random`, no `floats`), every Raft node that applies the same log will reach the exact same state hash.

## 3. Storage Abstraction

* **Current**: local file system or SQLite.
* **Future (Fabric)**: `RaftLog` (append-only) + `MerkleTree` (State Snapshot).
* **Action**: Ensure `StorageEngine.py` accepts a `transaction_context` to allow atomic commits driven by Raft.

## 4. Node Identity & PQC

* **Identity**: Each Raft node must sign its vote messages with Dilithium (`PQCProvider`).
* **Election**: Leader election must respect `Reputation` scores (Proof-of-Authority/Reputation variant of Raft).

## 5. Fabric Readiness Checklist

* [x] **Deterministic Core**: HSMF & Governance are repeatable (Zero-Sim).
* [ ] **Unified Apply Loop**: Single entry point `apply_log_entry` fully implemented.
* [ ] **State Snapshots**: Ability to hash complete state for Raft log compaction.
* [ ] **Storage Isolation**: No side-effect writes outside the apply loop.

## 6. Phase 1 Raft Prototype Plan

1. **Local Log (Implemented in `QFSReplaySource`)**: Simulation of Raft log locally.
2. **Fake Raft (Planned)**: Networked nodes sending log entries but using a central coordinator (no leader election complex logic yet).
3. **Real Raft (Planned)**: Drop in `PySyncObj` or custom Raft lib for leader election + log replication.
