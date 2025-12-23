# QFS × ATLAS Documentation Index

**Last Updated**: 2025-12-18  
**Status**: Synchronized with v14.0 frozen baseline and v15 protocol spec

---

## Classification Legend

- **[v14 Baseline]** - Describes current frozen behavior and guarantees
- **[v15 Protocol]** - Describes planned parallel layer (not yet active)
- **[Evergreen]** - Cross-version documentation (architecture, security, process)
- **[Legacy]** - Superseded or archived documentation

---

## Root Documentation

| Document | Classification | Purpose | Status |
|----------|---------------|---------|--------|
| `README.md` | Evergreen | Project overview, quickstart, current status | ✅ Updated |
| `LICENSE.ATLAS.md` | Evergreen | License and legal | ✅ Current |
| `REGRESSION.md` | v14 Baseline | Regression hash and replay verification | ✅ Current |
| `SECURITY_NOTES.md` | Evergreen | Security assumptions and deviations | ✅ Current |
| `CI_IMPROVEMENTS.md` | Evergreen | CI/CD improvements and roadmap | ✅ Current |
| `REPO_STRUCTURE.md` | Evergreen | Repository organization | ✅ Current |
| `ROOT_CLEANUP_SUMMARY.md` | Evergreen | Root directory cleanup actions | ✅ Current |
| `CHANGELOG.md` | Evergreen | Version history and changes | 🔄 To create |

---

## v14 Documentation (Frozen Baseline)

| Document | Purpose | Status |
|----------|---------|--------|
| `v13/docs/v14-evidence-deck.md` | Audit readiness and compliance | ✅ Current |
| `v13/docs/V14_RELEASE_NOTES.md` | v14 release documentation | ✅ Current |
| `v13/docs/V14_PR_STABILIZATION_CHECKLIST.md` | v14 PR review checklist | ✅ Current |
| `v13/docs/V14_CONSOLIDATION_PLAN.md` | v14 consolidation strategy | ✅ Current |
| `v13/tests/regression/phase_v14_social_full.py` | Canonical v14 regression scenario | ✅ Current |
| `v14_regression_hash.txt` | Canonical v14 regression hash | ✅ Current |

---

## v15 Documentation (Protocol Spec)

| Document | Purpose | Status |
|----------|---------|--------|
| `v13/docs/V15_FULL_EXECUTION_PLAN.md` | Master v15 protocol spec | ✅ Current |
| `v13/docs/V15_GOVERNANCE_HSMF_ROADMAP.md` | v15 governance roadmap | ✅ Current |
| `v13/docs/V15_NON_GOALS.md` | v14 protected areas for v15 | ✅ Current |
| `v13/docs/DEVELOPER_REWARDS_GAP_ANALYSIS.md` | Developer rewards gap analysis | ✅ Current |
| `v13/docs/V15_EVENT_SCHEMAS.md` | Canonical v15 event registry | ✅ Current |
| `v13/docs/V15_LIVING_POSTS_SPEC.md` | Living Posts specification | ✅ Current |
| `v13/docs/V15_DEVELOPER_REWARDS_SPEC.md` | Developer Rewards specification | ✅ Current |
| `v13/docs/V15_GOVERNANCE_PARAMS.md` | Governable parameters | 🔄 To create |
| `v13/docs/V15_REGRESSION.md` | v15 regression scenarios | 🔄 To create |

---

## Governance & Policy

| Document | Purpose | Status |
|----------|---------|--------|
| `v13/docs/HSMF_INTEGRATION_PLAN.md` | HSMF integration strategy | ✅ Current |
| `BOUNTIES.md` | Bounty registry and process | 🔄 To create |
| `CONTRIBUTORS.md` | Contributor ATR tracking | 🔄 To create |

---

## HSMF Documentation (v13.5)

| Document | Purpose | Status |
|----------|---------|--------|
| `v13/docs/HSMF_API.md` | API surface, classes, methods | ✅ Updated v13.5 |
| `v13/docs/HSMF_MathContracts.md` | Invariants, formulas, test specifications | ✅ Current |
| `v13/docs/hsmf_harmonic_design.md` | Theoretical grounding, flow diagrams | ✅ Current |
| `v13/tests/HSMF/test_hsmf_math_contracts.py` | 13 invariant tests | ✅ Current |
| `v13/tests/HSMF/test_hsmf_replay.py` | 9 replay/PoE tests | ✅ Current |
| `v13/tests/atlas/test_hsmf_wall_integration.py` | 8 wall integration tests | ✅ Current |
| `v13/tools/explain_hsmf_action.py` | CLI explainer for action costs | ✅ Current |
| `v13/services/hsmf_integration.py` | AEGIS→HSMF→RewardAllocator service | ✅ Current |
| `v13/atlas/wall/hsmf_wall_service.py` | HSMF-scored wall posts | ✅ Current |

## Zero-Sim & Compliance

| Document | Purpose | Status |
|----------|---------|--------|
| `v13/docs/ZERO_SIM_QFS_ATLAS_CONTRACT.md` | Zero-Sim Contract v1.4 | ✅ Current |
| `v13/docs/ZERO_SIM_QFS_ATLAS_CONTRACT_v1.5_draft.md` | Zero-Sim Contract v1.5 (draft) | 🔄 To create |
| `zero_sim_architectural_exceptions.md` | Architectural exceptions | ✅ Archived |
| `zero_sim_manual_review.md` | Manual review notes | ✅ Archived |

---

## Monitoring & Observability

| Document | Purpose | Status |
|----------|---------|--------|
| `monitoring/MONITORING_FRAMEWORK.md` | Monitoring framework spec | ✅ Current |

---

## Changelogs & History

| Document | Purpose | Status |
|----------|---------|--------|
| `docs/changelogs/CHANGELOG_P0.md` | Phase 0 changelog | ✅ Archived |
| `docs/changelogs/CHANGELOG_P3.md` | Phase 3 changelog | ✅ Archived |
| `docs/changelogs/CHANGELOG_SESSIONS.md` | Session changelog | ✅ Archived |
| `CHANGELOG.md` | Unified changelog (Keep a Changelog format) | 🔄 To create |

---

## Transmissions (Public Communications)

| Document | Purpose | Status |
|----------|---------|--------|
| `v13/docs/transmissions/TRANSMISSION_006_V15_PLAN_LOCKED.md` | v15 plan announcement | 🔄 To create |

---

## Roadmap & Planning

| Document | Purpose | Status |
|----------|---------|--------|
| `v13/docs/ROADMAP.md` | Standing workstreams roadmap | 🔄 To create |

---

## Archived Documentation

| Document | Original Purpose | Archive Location |
|----------|------------------|------------------|
| Phase 0-3 completion docs | Historical milestones | `docs/changelogs/` |
| Compliance reports | Historical audits | `archive/compliance_reports/` |
| Phase 3 artifacts | Phase 3 completion | `archive/phase3_complete/` |

---

## Update Rules

### When Changing v14 Behavior

1. Update tests and `REGRESSION.md`
2. Update `CHANGELOG.md`
3. Consider Zero-Sim contract update (v1.4 → v1.5)
4. Update v14 evidence deck if needed

### When Adding/Modifying v15 Behavior

1. Update appropriate v15 spec (protocol, living posts, or developer rewards)
2. Update governance parameter docs if parameters change
3. Add or adjust regression docs
4. Update `CHANGELOG.md` with v15 tag

### When Changing CI Only

1. Update `CI_IMPROVEMENTS.md`
2. Only touch v14/v15 docs if CI changes protocol guarantees

---

## Completion Criteria

Documentation is synchronized when:

- ✅ v14 frozen baseline status is clear in README, CHANGELOG, REGRESSION
- ✅ v15 protocol spec is captured in dedicated docs
- ✅ Transmissions, roadmap, and registries reflect current reality
- ✅ Autonomous executor can determine what to update from docs alone

---

**Status**: Synchronization in progress  
**Next**: Create missing docs and update existing
