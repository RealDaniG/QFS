# v18 Backbone Complete: Consensus, PQC Anchors & EvidenceBus Wiring

> **Date:** 2025-12-20  
> **Status:** Phase 1-3 Verified (Multi-node Simulation)  
> **Baseline:** v17.0.0-beta F-Layer

The distributed Tier A backbone is now consensus-driven, PQC-anchored, and cleanly wired into the existing F-layer; next work should make it observable and extend it to Tier B/C edges.

## What v18 can do now

- **Consensus + EvidenceBus integration:**  
  - `ConsensusNode` now performs real Raft-style log replication and majority-based commit, not just term/vote handling.
  - `EvidenceBusConsensusAdapter` forwards only **committed** log entries into `EvidenceBus.emit`, tagging them with `v18_consensus_term` so auditors can see which term/cluster committed any given event.
  - Integration tests show that a governance action is visible in EvidenceBus only after consensus, preserving the deterministic, event-sourced model from v17.

- **PQC batch anchoring:**  
  - `PQCBatchAnchorService` computes deterministic batch roots over EvidenceBus segments and signs them via the environment-aware `sign_poe` adapter, aligning with the MOCKQPC → real PQC migration plan.
  - `verify_batch_signature` lets any node validate that a segment’s hash-chain and signature are intact, making log tampering detectible across the fabric.
  - `test_pqc_anchors.py` confirms deterministic signatures and rejects tampered batches, consistent with NIST-style transition guidance.

- **Determinism & CI:**  
  - 14/14 v18 tests now cover multi-node simulation, Raft+EvidenceBus integration, and PQC anchoring, all under Zero-Sim constraints (fixed seeds and message orders → identical cluster + EvidenceBus histories).

## Recommended Phase 4: Observability & Edge Expansion

- **Cluster & anchor observability:**  
  - Extend the admin dashboard to add:  
    - Cluster view (leaders, terms, node health, commit indices).  
    - PQC anchor timeline (which EvidenceBus ranges have anchors, with verification status).  
  - Add APIs to query: “Show all events covered by anchor X” or “Show latest verified anchor for this proposal/bounty space.”

- **Tier B & C wiring:**  
  - Tier B (edge UI/advisory) nodes:  
    - Consume EvidenceBus from the consensus-backed Tier A cluster instead of single-node logs.  
    - Run the minimal embedded agent pattern from v17 for advisory, unchanged, but now against a distributed backbone.  
  - Tier C (sensors/observers):  
    - Use gateways that submit telemetry as consensus proposals, so even sensor data becomes part of the anchored EvidenceBus when committed.

- **Operational simulations:**  
  - Use existing simulator plus the new PQC+EBus wiring to test:  
    - Node failures during heavy governance load.  
    - Anchor generation under stress.  
    - Replay of a full cluster history onto a fresh node, verifying both consensus state and anchors.

The system now has a deterministic, cryptographically anchored core suitable for real Tier A deployment experiments, with v17’s governance, bounty, social, and advisory layers riding on top without modification.
