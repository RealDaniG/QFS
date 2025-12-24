# QFS × ATLAS — Release Notes

> **Current Version:** v18.0.0-alpha-distributed-fabric
> **Theme:** Distributed Consensus, PQC Anchoring, and Multi-node EvidenceBus
> **Status:** Alpha (Backbone Core Complete)

---

## 🌐 v18.0.0-alpha (December 20, 2025)

**Major Milestone**: "Distributed Backbone". Transitioned from single-node governance to a multi-node PQC-anchored fabric.

### v18 New Features

#### 1. Distributed Consensus (`v18/consensus`)

- Deterministic Raft-style replication engine.
- Multi-node simulation harness with failover verification.
- Majority-based commitment for EvidenceBus events.

#### 2. PQC Batch Anchors (`v18/pqc`)

- Deterministic segment sealing for EvidenceBus.
- Environment-aware signing (MOCKQPC or real Dilithium).
- Distributed anchor verification.

#### 3. Fabric Governance

- Wiring EvidenceBus commits to Raft.
- Audit metadata (`v18_consensus_term`) for all consensus-driven events.

### Documentation

- [Cluster Operations Guide](docs/CLUSTER_OPERATIONS_GUIDE.md)
- [PQC Security Profile](docs/PQC_SECURITY_PROFILE.md)
- [Backbone Completion Report](docs/RELEASES/v18_BACKBONE_COMPLETE.md)

### v18 Verification

- **14/14 tests passing** in multi-node simulation.
- **Zero-Sim Compliance** verified across distributed layers.

---

## 🚀 v17.0.0-beta (December 20, 2025)

**Major Milestone**: "Compression and Reveal". The core F-Layer engine is now fully deterministic and surfaced via human-readable UI projections.

### v17 New Features

#### 1. Governance F-Layer (`v17/governance`)

- Deterministic Proposal Creation, Voting, and Execution.
- Quorum rules, Approval thresholds, and Tie-breaking logic.
- Full PoE logging to EvidenceBus.

#### 2. Bounty F-Layer (`v17/bounties`)

- Creation, Contribution Tracking, and Reward Allocation.
- Configurable reward caps and algorithms.

#### 3. Social Surface (`v17/social`)

- Threads bound to Governance/Bounties.
- Dispute lifecycle management.
- User Profiles with contribution history.

#### 4. Layer D Advisory (`v17/agents`)

- Non-authoritative agent signals overlaid on UI.
- Heuristics for:
  - **Governance**: High amounts, short descriptions, spam.
  - **Bounties**: Reference links, content quality.
  - **Social**: Urgency keywords ("scam", "fraud").

### v17 Verification

- **Zero-Sim**: 100% Deterministic execution enforced by CI.
- **Replay**: Full state reconstruction from EvidenceBus.

---

## 📜 v16.1.0 (Previous Stable)

**Theme**: Foundations (Auth, Admin, PoE)

### v16 Stable Features

## 🕰️ v15.5 (Legacy)

### v15 Legacy Prototypes
