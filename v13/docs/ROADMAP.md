# QFS × ATLAS Roadmap

**Status**: v15 Execution (Standing Workstreams)  
**Methodology**: Autonomous, Additive, Zero-Sim

---

## Overview

We operate in **standing workstreams** rather than rigid phases.

- **v14 is frozen** (Social Layer baseline).
- **v15 is active** (Parallel Layer: Living Posts + Developer Rewards).
- Workstreams are **unordered** and can proceed independently.

---

---

## Completed (v13.5 / v14)

- [x] **Social Layer v2**: Deterministic rewards, Sybil resistance, HSMF integration.
- [x] **Self-Identifying Code**: Build identity injected via CI and exposed at runtime.
- [x] **EvidenceBus Wiring**: Social rewards linked to code provenance.

## PQC / OQS Preparation

- [ ] **Mode Verification**: `QFS_PQC_MODE=mock` verified in staging.
- [ ] **Real OQS Provider Implementation**:
  - [ ] `liboqs` packaging and CI pipeline.
  - [ ] Performance benchmarks (mock vs real).
  - [ ] `QFS_PQC_MODE=real` switchover.

## Workstream A: Living Posts Layer

*Status: Protocol Planned*

- [ ] **Formalize \(f(H_p)\)**: Define exact integer-math scoring function.
- [ ] **State Persistence**: Schema for storing \(H_p\) vectors parallel to ledger.
- [ ] **PostRewardStateMachine**: Implement `NEW → ACTIVE → TAPERING` logic.
- [ ] **HSMF Engagement**: Wire ATR/AEGIS/Graph filters to engagement inputs.
- [ ] **Epoch Pools**: Implement pre-funded FLX pool logic per epoch.

---

## Workstream B: Developer Rewards Layer

*Status: Phase 1 Implemented*

- [x] **Foundation**: Schema, Events, Treasury (v14.1).
- [x] **Registry**: `BOUNTIES.md` and `CONTRIBUTORS.md` created.
- [ ] **ATR Integration**: Wire `atr_boost_applied` to `ContributorProfile` tracking.
- [ ] **BountyStateMachine**: Automate transitions (`OPEN` → `PAID`).
- [ ] **CI Verification**: Auto-verify CI status for bounty PRs.

---

## Workstream C: Governance Integration

*Status: Protocol Planned*

- [ ] **Proposal Types**: Define proposals for v15 parameters (pools, coefs).
- [ ] **Parameter Logging**: Emit immutable events for parameter changes.
- [ ] **Activation Logic**: Deterministic epoch-based activation for new params.

---

## Workstream D: Verification & Testing

*Status: Ongoing*

- [ ] **Living Posts Regression**: `[V15-LP]` multi-epoch scenario.
- [ ] **Dev Rewards Regression**: `[V15-DEV]` bounty lifecycle scenario.
- [ ] **Zero-Sim v1.5**: Formalize draft contract into active contract.
- [x] **v14 Invariance**: Enforce frozen baseline hash in CI.

---

## Non-Goals (v15)

| Feature | Reason | Target |
|---------|--------|--------|
| New Token Minting | Violates bounded economics | Never |
| Content Moderation | HSMF validates *engagement*, not content | Never |
| Semantic Changes to v14 | v14 is frozen/immutable | Never |
| NOD Validation | Requires significant infra work | v16.0 |

**Last Updated**: 2025-12-18
