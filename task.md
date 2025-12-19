# QFS × ATLAS v16 Operationalization Plan

> **Goal:** Operationalize the v16 baseline by encoding governance rules, maintainer workflows, and onboarding clarity.

## 1. Governance & PR Process Enforcement

- [x] Update `docs/PR_TEMPLATE_v16.md` (and `v15.5`) with "Core Invariant" checklist
- [x] Requirements:
  - State touched invariants (MOCKQPC, EvidenceBus, Determinism, Cost)
  - Reference capability area (Governance, Wallet, Agents, Bounties, UI)

## 2. Maintainer Workflow & Labels

- [x] Add "Maintainer Guide" section to `docs/QFS_ATLAS_PRODUCTION_READINESS.md`
- [x] Define standard labels: `area:governance`, `area:wallet-auth`, `area:evidencebus`, `area:agent-advisory`, `area:bounties`, `area:ui`, `type:cost`, `type:determinism`
- [x] Document triage process

## 3. Onboarding and FAQ

- [x] Create `docs/FAQ_MOCKQPC_AND_AGENTS.md`
- [x] Content:
  - Why MOCKQPC? Safety?
  - Real PQC timeline?
  - "Advisory-only" definition?
  - How to avoid breaking Zero-Sim?
- [x] Link from `README.md` and `CONTRIBUTING.md`

## 4. Release Tagging

- [x] Create `docs/RELEASES/v16_EVERGREEN_BASELINE.md`
- [x] Content:
  - Summary
  - Links to Canon (State of Union, Cost Arch, Readiness)

## 5. Branch Protection & Maintenance

- [x] Create `docs/MAINTAINERS_GUIDE.md`
- [x] Document required checks:
  - `ci.yml` pass (Zero-Sim)
  - Review requirements for `v15/crypto`, EvidenceBus, Governance

## 6. Final Verification

- [x] Verify all new docs are linked
- [x] Commit with message: "docs: v16 operationalization complete"
