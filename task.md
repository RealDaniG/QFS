# QFS V13.8 Integration & Cleanup Tracker

**Objective:** Finalize QFS V13.8 "Zero-Sim Absolute" integration with ATLAS, ensuring strict zero-simulation compliance, legacy cleanup, and functional production readiness.

## Phase 1: Legacy Cleanup & Structure Consolidation [Priority: High]

- [ ] **Audit Legacy `src/` Directory**
  - [ ] Compare `src/core` with `v13/core` to ensure no lost logic.
  - [ ] Archive or remove `src/` to prevent "Split Brain" confusion.
- [ ] **Verify `v13` Imports**
  - [ ] Ensure all internal imports reference `v13.*` or relative paths correctly, not legacy `src.*`.

## Phase 2: ATLAS P0 Critical Integration Gaps [Priority: Critical]

*Ref: ATLAS-P0-001 to ATLAS-P0-008*

- [ ] **ATLAS-P0-001: Unified ATLAS API Contracts**
  - [ ] Define shared Pydantic models/Typescript interfaces for critical QFS<->ATLAS boundaries.
- [ ] **ATLAS-P0-002: Coherence-Based Feed Ranking**
  - [ ] Implement ranking logic sourced from `CoherenceLedger`.
- [ ] **ATLAS-P0-003: QFS Event Bridge**
  - [ ] Create event bridge for real-time frontend updates from QFS ledger events.
- [ ] **ATLAS-P0-007: Explain-This System Backend**
  - [x] Backend Routes (`/explain/*`) - *Implemented & Audited*
  - [ ] Frontend Integration (Connect UI to new routes).

## Phase 3: AEGIS & Security Production Readiness [Priority: High]

*Ref: ATLAS-P1-009*

- [ ] **Deploy AEGIS Guard Service**
  - [ ] Move from "Staged" to "Active" in production configuration.
  - [ ] Verify PQC Identity bootstrap in live environment.
- [ ] **Production Configuration Hardening**
  - [ ] Ensure all `localhost` fallbacks are strictly disabled in prod env vars.

## Phase 4: Continuous Validation [Priority: Medium]

- [ ] **Maintain Green Pipeline**
  - [ ] Monitor strictly for regressions in `security-scan` and `zero-sim` workflows.
