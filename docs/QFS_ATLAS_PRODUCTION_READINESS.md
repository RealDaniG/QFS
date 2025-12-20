# QFS × ATLAS Production Readiness – Evergreen v16 Baseline

> **Status:** Production-Ready (v16 Baseline)  
> **Foundation:** MOCKQPC-First, Zero-Sim Enforced, AGPL-3.0 Licensed  
> **Previous Target:** "v14.0 Final" (Superseded by v16 Baseline)

---

## 🏛️ Executive Summary

This roadmap tracks the production readiness of QFS × ATLAS based on **capabilities**, not temporal phases. The system has achieved its **v16 Baseline**, defined by:

1. **Deterministic Core**: 100% replayable economic and governance logic.
2. **MOCKQPC-First**: Zero-cost crypto in dev/beta, batched PQC anchors in mainnet.
3. **EvidenceBus-Centric**: All actions (governance, moderation, bounties) emitted as hash-chained evidence.
4. **Advisory Agents**: AI agents are read-only oracles, never authorities.

---

## 1. Core Determinism & Crypto (✅ Achieved)

**Capability:** The system runs physically deterministic logic (MOCKQPC) and enforces it via CI.

- [x] **Zero-Sim v1.4 Enforcement**: CI fails on any non-deterministic code (time, random, floats) via `scripts/check_zero_sim.py`.
- [x] **MOCKQPC Architecture**: Dev/Beta environments use purely deterministic crypto stubs ($0 cost).
- [x] **Crypto Abstraction**: `sign_poe`/`verify_poe` handle environment switching (MOCKQPC ↔ Real PQC).
- [x] **BigNum128 Integrity**: All economic math uses certified integer arithmetic.

## 2. EvidenceBus & Moderation (✅ Achieved)

**Capability:** Every significant action leaves a verifiable, hash-chained trail.

- [x] **EvidenceBus**: Central event spine emitting `governance_decision`, `moderation_decision`, `bounty_event`.
- [x] **PoE Anchoring**: Events are hash-chained and batch-signed (MOCKQPC/PQC).
- [x] **Deterministic Moderation**: Function `F(content, scores, rules)` decides outcomes based on inputs.
- [x] **Admin/Mod Panel**: Scope-based UI (`mod:act`, `admin:override`) powered by EvidenceBus.

## 3. Agent Advisory Layer (🔄 Active)

**Capability:** Agents provide insights (scoring, labeling) without holding authority.

- [x] **Advisory-Only Model**: Replaced "Open-AGI Authority" with "Agent as Oracle".
- [x] **Deterministic Adapters**: Agent outputs are sanitized and hashed before entering QFS.
- [ ] **CrewAI/LangGraph Integration**: Replacing legacy Open-AGI harnesses with efficient OSS stacks.
- [ ] **Sampling Strategy**: Enforce 10-20% sampling to reduce compute costs <$0.2/decision.

## 4. Governance & Monetization (⏭ implemented)

**Capability:** Community-driven upgrades and transparent value distribution.

- [x] **Wallet Auth**: EIP-191 signatures + Token-based sessions.
- [ ] **Governance Portal**: On-chain voting via PQC-signed batches.
- [ ] **NOD Token Distribution**: Automated issuance based on contribution evidence.
- [ ] **Contribution Indexer**: Dual-proof linking (Wallet ↔ GitHub) for verified rewards.

## 5. Deployment & Observability (🔄 Active)

**Capability:** Cost-efficient, single-node default deployment that scales.

- [x] **Single-Node Stack**: Next.js + FastAPI + Postgres + MOCKQPC Service.
- [x] **CI/CD Pipeline**: Automated testing, linting, and Zero-Sim checks.
- [ ] **Observability Dashboards**: Grafana/Prometheus tracking PQC/Agent costs per decision.
- [ ] **BetaNet Deployment**: `ENV=beta` nodes running MOCKQPC validation.

---

## 🔐 Crypto Modes & Threat Model

### MOCKQPC (Dev/Beta/CI)

- **Role**: Functional verification, determinism checks, high-speed replay.
- **Security**: None (keys are widely known/deterministic).
- **Cost**: $0.
- **Enforcement**: Mandatory in CI and local dev.

### Real PQC (Mainnet Anchors)

- **Role**: Immutable finality, long-term security.
- **Security**: CRYSTALS-Dilithium (or generally accepted PQC standard).
- **Cost**: Batched (LOW). Signatures applied to Merkle roots of event batches, not individual events.
- **Activation**: Via governance proposal and config switch (`ENV=mainnet`).

---

## 🛠️ Maintainer Guide

### Workflow & Triage

We use **capabilities** to organize work, not phases.

**Triage Process:**

1. **Label by Area**: Assign `area:*` based on module.
2. **Label by Requirements**: Assign `type:cost` or `type:determinism` if the PR touches these invariants.
3. **Verify Checklist**: Ensure PR description has the [Core Invariant Checklist](docs/PR_TEMPLATE_v15.5.md).

### Standard Labels

| Label | Usage |
| :--- | :--- |
| `area:governance` | Rules, voting, treasure logic |
| `area:evidencebus` | PoE schemas, event emitters, hash chains |
| `area:wallet-auth` | Signing, sessions, scopes (EIP-191) |
| `area:agent-advisory` | Agent signals, adapters (no write access) |
| `area:bounties` | Bounty logic, dashboard, payments |
| `area:ui` | Frontend components, Admin Panel |
| `area:infrastructure` | CI, Docker, MOCKQPC service |
| `type:determinism` | Changes to `F`, math, or sort order |
| `type:cost` | Changes affecting PQC/Agent call volume |

## 📚 Appendix: Historical Phases (Legacy)

*Reference for mapping old documentation to the new v16 Baseline.*

- **Phase 0 (Foundation)**: Now "Core Determinism".
- **Phase I (Canonical Alignment)**: Completed via Semantic Types & Schemas.
- **Phase II (Open-AGI Integration)**: Refactored to "Agent Advisory Layer".
- **Phase III (Monetization)**: Now "Governance & Monetization".
- **Phase IV (Decentralization)**: Deferred; focus is on "Deployment & Observability" (Single-Node focus).
- **AEGIS**: Legacy term for the validation/guard layer, now `F_moderation_v1`.
