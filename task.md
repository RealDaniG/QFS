# QFS × ATLAS Task Tracker

> **Current Version:** v18.0.0-alpha (Distributed Backbone)  
> **Status:** Consensus driven & PQC anchored (Tier A backbone complete)  
> **Last Updated:** 2025-12-20

---

## v16 Operationalization Plan ✅ COMPLETE

> **Goal:** Operationalize the v16 baseline by encoding governance rules, maintainer workflows, and onboarding clarity.

### 1. Governance & PR Process Enforcement ✅

- [x] Update `docs/PR_TEMPLATE_v16.md` with "Core Invariant" checklist
- [x] Requirements: State invariants, reference capability areas

### 2. Maintainer Workflow & Labels ✅

- [x] Add "Maintainer Guide" to `docs/QFS_ATLAS_PRODUCTION_READINESS.md`
- [x] Define standard labels (area:*, type:*)
- [x] Document triage process

### 3. Onboarding and FAQ ✅

- [x] Create `docs/FAQ_MOCKQPC_AND_AGENTS.md`
- [x] Link from `README.md` and `CONTRIBUTING.md`

### 4. Release Tagging ✅

- [x] Create `docs/RELEASES/v16_EVERGREEN_BASELINE.md`

### 5. Branch Protection & Maintenance ✅

- [x] Create `docs/MAINTAINERS_GUIDE.md`
- [x] Document required checks

### 6. Final Verification ✅

- [x] All docs linked
- [x] Committed: "docs: v16 operationalization complete"

---

## v16 Integration Plan ✅ COMPLETE

> **Goal:** Build user-facing and admin-facing layers on v16 baseline.

### 1. Wallet Authentication ✅

- [x] Implement `v15/auth/wallet_connect.py` (EIP-191)
- [x] Connect to `SessionManager`
- [x] Emit `auth_event` to EvidenceBus

### 2. Admin Panel & Observability ✅

- [x] Create `v15/ui/admin_dashboard.py`
- [x] Implement "Evidence Chain Viewer"
- [x] Connect `CostProfile` metrics

### 3. Agent Advisory Migration ✅

- [x] Audit `v14` agents for write-access violations
- [x] Refactor into `AdvisorySignal` emitters
- [x] Enforce read-only permissions

---

## v16 Health Check & Hardening ✅ COMPLETE

> **Goal:** Full pipeline preflight before v17 development.

### Health Check Execution ✅

- [x] Baseline confirmation (v16.1.0-integration-complete)
- [x] Full test & determinism sweep
- [x] Zero-Sim compliance (0 critical violations)
- [x] Issues identified and fixed (dict access safety)
- [x] All tests passing
- [x] Tagged: `v16.1.1-pre-v17-ready`

### CI Wiring Fixes ✅

- [x] Updated artifact actions (v3 → v4)
- [x] Created `notify_discord.py` stub
- [x] Verified CI operational
- [x] Documentation complete

---

## v17 Governance & Bounty F-Layer ✅ ENGINE COMPLETE

> **Goal:** Deterministic governance and bounty management with full PoE logging.

### Phase 1: Engine Implementation ✅

#### Governance F-Layer ✅

- [x] `v17/governance/schemas.py` - Pydantic models
- [x] `v17/governance/f_proposals.py` - Proposal creation & state reconstruction
- [x] `v17/governance/f_voting.py` - Vote casting & validation
- [x] `v17/governance/f_execution.py` - Outcome computation & finalization
- [x] All functions pure (state from events only)
- [x] Full PoE logging to EvidenceBus

#### Bounty F-Layer ✅

- [x] `v17/bounties/schemas.py` - Pydantic models
- [x] `v17/bounties/f_bounties.py` - Bounty lifecycle & reward computation
- [x] Deterministic reward allocation
- [x] Advisory signal integration
- [x] Full PoE logging to EvidenceBus

#### Testing ✅

- [x] `v17/tests/test_governance_f_layer.py` - All tests passing
- [x] `v17/tests/test_bounties_f_layer.py` - All tests passing
- [x] Determinism verified
- [x] PoE logging verified
- [x] Zero-Sim compliance (0 critical violations)

### Phase 2: UI/UX Layer (Compression & Reveal) 🔄 IN PROGRESS

> **Constraint:** Engine frozen - no new mechanisms, only visibility

#### Layer B: Authority Visibility (Admin & Steward) ✅

- [x] Extend `v15/ui/admin_dashboard.py` with Governance Timeline
  - [x] Proposal → votes → outcome → execution
  - [x] "View evidence" links to PoE events
  - [x] Tests for timeline rendering
- [x] Add Bounty Timeline view
  - [x] Bounty → contributions → advisory → rewards
  - [x] Show advisory vs F-layer distinction
  - [x] Tests for bounty timeline
- [x] Implement Decision Explanation panels
  - [x] Governance outcomes
  - [x] Bounty rewards
  - [x] Dispute resolutions
  - [x] "Show record" to Evidence View
- [x] Implement Dispute Resolution panel
  - [x] Steward-facing interface
  - [x] Evidence chain preview
  - [x] Mandatory PoE reference

#### Layer C: Social Surface (User-Facing) ✅

- [x] Wire conversations to governance/bounty events
  - [x] Inline indicators
  - [x] Links to explanation panels
- [x] Implement "Explanation First" flow
  - [x] Summary → Click → Evidence Graph
  - [x] User-accessible verification
- [x] Tests for social/user timeline flows
- [x] Implement Contribution History view
  - [x] Per-user activity log
  - [x] Plain language summaries
  - [ ] "Show record" for each item
- [ ] Implement Escalation/Dispute flow
  - [ ] Clear lifecycle
  - [ ] Evidence links
  - [ ] Guardrails

#### Layer D: Agent Advisory (User-Facing) ✅

- [x] Implement Advisory Interpreters (v17/agents/)
  - [x] Governance Heuristics
  - [x] Bounty Heuristics
  - [x] Social Heuristics
- [x] Wire to UI Projections
  - [x] Governance Overlay
  - [x] Bounty Overlay
  - [x] Social Overlay
- [x] Verification
  - [x] Deterministic Tests
  - [x] Zero-Sim Compliance

#### Layer E: Progressive Disclosure 🔄

- [ ] Level 1: Summary (human explanation)
- [ ] Level 2: Evidence View (PoE events)
- [ ] Level 3: Replay/Technical (deterministic reconstruction)

### Phase 3: Documentation & Testing 🔄

- [ ] Update `MAINTAINERS_GUIDE.md` with v17 layers
- [ ] Create user-facing docs
- [ ] Add diagrams (Outcome → Explanation → Evidence → Replay)
- [ ] End-to-end tests
- [ ] CI integration

### Phase 4: Release 🔄

- [ ] Open PR: `feat/v17-governance-bounty-f-layer` → `main`
- [ ] CI verification (all tests green)
- [ ] Tag: `v17.0.0-beta-governance-bounties`
- [ ] Release summary

## v18 Distributed Fabric ✅ BACKBONE COMPLETE

> **Goal:** Transform v17's single-node deterministic core into a distributed, PQC-anchored mesh.

### Phase 1: Multi-Node Core (Tier A) ✅

- [x] Raft/PBFT Consensus Implementation (v18/consensus/)
- [x] Multi-node Simulation Harness (v18/consensus/simulator.py)
- [x] Election & Failover Logic
- [x] Log Replication & Majority Commitment
- [x] Determinism Verified (Zero-Sim)

### Phase 2: PQC Anchors (Tier A) ✅

- [x] PQC Batch Anchor Service (v18/pqc/anchors.py)
- [x] Environment-Aware Batch Signing (MOCKQPC or liboqs)
- [x] Batch Verification Logic
- [x] Deterministic Signature Tests

### Phase 3: Consensus & Bus integration ✅

- [x] EvidenceBusConsensusAdapter Implementation
- [x] Consensus Commit -> EvidenceBus.emit Wiring
- [x] Integration Test (Propose -> Replicate -> Commit -> Append)

### Phase 4: Observability & Edge Expansion 🔄

- [ ] Cluster Status Dashboard (Leader, Term, Indices)
- [ ] PQC Anchor Timeline & Verification API
- [ ] Tier B Edge Node Config (UI+Advisory)
- [ ] Tier C Sensor Gateways

---

## Current Status Summary

**Completed:**

- ✅ v16 Operationalization
- ✅ v16 Integration (wallet auth, admin panel, agent advisory)
- ✅ v16 Health Check & Hardening
- ✅ v17 Engine Implementation (governance + bounties)
- ✅ v17 UI/UX (Timelines, Explanations, Advisory Overlays)
- ✅ v18 Phase 1: Multi-Node Core
- ✅ v18 Phase 2: PQC Anchors
- ✅ v18 Phase 3: Consensus & Bus Integration

**In Progress:**

- 🔄 v18 Phase 4: Observability & Edge Expansion

**Next Steps:**

1. Implement Cluster Dashboards
2. Wire Tier B Edge Nodes to Distributed Bus
3. Implement Tier C Gateways

---

**Branch:** `feat/v18-distributed-fabric`
**Foundation:** v17.0.0-beta-governance-bounties
**Target:** v18 Observability Phase
**Contract:** Deterministic Core Preserved
