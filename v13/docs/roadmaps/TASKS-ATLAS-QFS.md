# TASKS: ATLAS x QFS Integration

**Version:** 1.0  
**Date:** 2025-12-13  
**Status:** ACTIVE

---

## Derived from Gap Analysis 2025-12-13

### 🔴 P0 Priority Items

- [x] **System Creator Wallet (Bootstrap)**
  - [x] Spec doc (Clarified & Finalized)
  - [x] Deterministic Derivation (`crypto/derivation.py`)
  - [x] Keystore Abstraction (`libs/keystore/`)
  - [x] Ledger Writer (`ledger/writer.py`)
  - [x] Policy Authorization (`policy/authorization.py`)
  - [x] CLI Command (`cli/init_creator.py`)
  - [x] Tests & Verification (7/7 passing)
  - [x] Evidence (`v13/evidence/SYSTEM_CREATOR_WALLET_EVIDENCE.json`)

- [x] **Unified ATLAS API contracts**
  - [x] Spec doc
  - [x] API/architecture
  - [x] Implementation
  - [x] Tests
  - [x] Evidence
  - [x] Stub APIs available

- [x] **Coherence-based feed ranking**
  - [x] Spec doc
  - [x] API/architecture
  - [x] Implementation
  - [x] Tests
  - [x] Evidence
  - [x] Stub APIs available
  - _Feed/Interactions now integrated with QFS and covered by deterministic tests._

- [x] **QFS event bridge for interactions**
  - [x] Spec doc
  - [x] API/architecture
  - [x] Implementation
  - [x] Tests
  - [x] Evidence
  - [x] Stub APIs available
  - _Feed/Interactions now integrated with QFS and covered by deterministic tests._

- [x] **Direct messaging system**
  - [x] Spec doc (`v13/docs/DIRECT_MESSAGING_SYSTEM_SPEC.md`)
  - [x] API/architecture (`v13/docs/DIRECT_MESSAGING_API.md`)
  - [x] Implementation (`v13/services/dm/`)
  - [x] Open-AGI Integration (`v13/integrations/openagi_dm_adapter.py`)
  - [x] Tests (13/13 passing: 4 core + 9 Open-AGI)
  - [x] Evidence (`v13/evidence/DIRECT_MESSAGING_OPENAGI_EVIDENCE.json`)

- [x] **Community model & tools**
  - [x] Spec doc (`v13/docs/COMMUNITY_MODEL_SPEC.md`)
  - [x] API/architecture (`v13/docs/COMMUNITY_MODEL_API.md`)
  - [x] Implementation (`v13/services/community/`)
  - [x] Tests (2/2 passing)
  - [x] Evidence (`v13/evidence/COMMUNITY_MODEL_EVIDENCE.json`)

- [x] **Appeals workflow**
  - [x] Spec doc (`v13/docs/APPEALS_WORKFLOW_SPEC.md`)
  - [x] API/architecture (`v13/docs/APPEALS_WORKFLOW_API.md`)
  - [x] Implementation (`v13/services/appeals/`)
  - [x] Tests (4/4 passing)
  - [x] Evidence (`v13/evidence/APPEALS_WORKFLOW_EVIDENCE.json`)

- [x] **Explain-This system**
  - [x] Spec doc (`v13/docs/EXPLAIN_THIS_SYSTEM_SPEC.md`)
  - [x] API/architecture (`v13/docs/EXPLAIN_THIS_API.md`)
  - [x] Implementation (`v13/services/explainer/`)
  - [x] Tests (6/6 passing)
  - [x] Evidence (`v13/evidence/EXPLAIN_THIS_EVIDENCE.json`)

- [x] **QFS Onboarding tours**
  - [x] Spec doc (`v13/docs/ONBOARDING_TOURS_SPEC.md`)
  - [x] API/architecture (`v13/docs/ONBOARDING_TOURS_API.md`)
  - [x] Implementation (`v13/services/onboarding/`)
  - [x] Tests (4/4 passing)
  - [x] Evidence (`v13/evidence/ONBOARDING_TOURS_EVIDENCE.json`)

### 🟢 UI Integration (In Progress)

- [ ] **ATLAS Frontend Integration**
  - [x] P0 API Client (`v13/ATLAS/src/lib/p0-api-client.ts`)
  - [x] React Hooks (`v13/ATLAS/src/hooks/useP0Services.ts`)
  - [x] Integration Plan (`v13/ATLAS/ATLAS_UI_INTEGRATION_PLAN.md`)
  - [ ] Explain-This UI Components (Week 2)
  - [ ] Onboarding Tour Overlay (Week 3)
  - [ ] Guild Dashboard (Week 4)
  - [ ] Agent Visibility Indicators (Week 5)

### 🟡 P1 Priority Items

- [x] **AEGIS guard integration**
  - [x] Spec doc
  - [x] API/architecture
  - [x] Implementation
  - [x] Tests
  - [x] Evidence

- [x] **Event ledger explorer backend**
  - [x] Spec doc
  - [x] API/architecture
  - [x] Implementation
  - [x] Tests
  - [x] Evidence

- [x] **Segmented notifications**
  - [x] Spec doc
  - [x] API/architecture
  - [x] Implementation
  - [x] Tests
  - [x] Evidence

- [x] **OPEN-AGI simulation-only role**
  - [x] Spec doc
  - [x] API/architecture
  - [x] Implementation
  - [x] Tests
  - [x] Evidence

---
