# QFS × ATLAS — Master Prompt

## Determinism First, MOCKQPC-First, PQC/Agents When Needed

> **Version:** Master Reference  
> **Date:** December 19, 2025  
> **Status:** Authoritative - All Future Work Must Follow This Prompt

---

You are helping design, implement, and document **QFS × ATLAS**. The system is a sovereign, deterministic governance and execution stack with PoE-backed verification and post-quantum security. The goals are:

- Deliver a **deterministic, PoE-backed Admin/Moderator Panel** (v15.5)
- Roll out a **cost-efficient, layered PQC architecture**, with MOCKQPC in dev/beta and batched PoE in mainnet
- Ship a **full web-app** (ATLAS dashboard: wallet auth, bounties, Admin/Mod Panel, GitHub linking) that is cheap to run but mainnet-ready

**All new features MUST follow the cost-efficient architecture and MOCKQPC-first rules below.**

---

## 1. Current Baseline

### v15.3 — Governance + PoE

- **Governance + PoE fully wired**:
  - Proposals → votes → finalize → execute → PoE artifact → index → deterministic replay
- **PoE artifacts**:
  - PQC-signed
  - Stored in a hash-chained governance index
  - Replayable via CLI tools (e.g., `verify_poe`, `replay_gov_cycle`)

### v15.4 — Wallet & Bounties

- **Wallet auth (Phases 1–2)**:
  - `NonceManager`, `WalletAuth` (EIP-191), `SessionManager` for wallet sessions
  - Frontend `useWalletAuth` hook and `WalletConnectButton` integrated into ATLAS

- **Phase 3 (frontend) implemented**:
  - `BountyList`: browse & claim bounties with `bounty:read` / `bounty:claim` scopes
  - `MyBounties`: view bounties by connected wallet
  - `BountyDashboard`: unified bounty view with tabs
  - E2E flow: Connect Wallet → sign nonce → get session → list bounties → claim → view in "My Bounties"

### v15.5 — Admin/Mod + Lean PQC

- **Planning complete**:
  - Admin/Moderator Panel spec (rules, decisions, RBAC, PoE log)
  - Lean PQC architecture: MOCKQPC-first, lazy batched PQC anchors

- **Hard requirements**:
  - All v15.5 work starts on **MOCKQPC** and goes through a **closed beta** (5–10 moderators, 4–6 weeks) before any mainnet deployment

---

## 2. Cost-Efficient Architecture

### 2.1 Cost Drivers

You must treat these as primary cost sources to minimize:

1. **Crypto (PQC/PoE)**:
   - Per-action PQC signatures and verifications
   - Key management (HSM/KMS), audits, compliance

2. **Infrastructure**:
   - Multi-node HA clusters, DB replication, load balancing, multi-region

3. **Agent/LLM usage**:
   - Hosted SaaS, proprietary models, always-on scoring

4. **Observability/Security**:
   - Enterprise tracing, SIEM, early HSM/SIEM before product-market fit

**Observation**: Most cost comes from **compute-heavy or always-on systems**. Determinism and replayability do not require real PQC/LLM at early stages.

---

### 2.2 Cost-Reduction Strategies

#### A. Crypto & PoE Optimizations

**MOCKQPC-first**:

- All dev, test, and closed beta use MOCKQPC:
  - Hash-chained logs
  - Simulated PQC signatures with test keys
- Real PQC only for:
  - Treasury/NOD allocation
  - Final governance anchors and PoE batches

**Batched PQC**:

- Hash-chain every event (moderation, admin, agent outputs)
- PQC-sign only **batches** (hundreds–thousands of events) in all environments
- This yields ~99%+ reduction in PQC calls while preserving replayability

**Crypto-agile abstraction**:

- All signing/verification via:

  ```python
  sign_poe(payload_hash, env)
  verify_poe(payload_hash, signature, env)
  ```

- `env=dev/beta` → MOCKQPC keys
- `env=mainnet` → production PQC (e.g., Dilithium) in HSM/KMS
- **Application logic must never depend on specific algorithms**—only on hashes and verified outcomes

---

#### B. Infrastructure Efficiency

**Monolithic-but-modular early**:

- One stack:
  - Web frontend (Next.js)
  - Backend APIs (FastAPI/Starlette)
  - One DB (Postgres) for auth/bounties/mod decisions
  - One PoE/MOCKQPC service
- Add microservices only when traffic/load clearly demand separation

**Stateless agent layers**:

- Agent services (moderation, scoring) must be stateless:
  - Horizontally scalable on mid-tier VMs or containers
- PQC/PoE/governance services remain small, stateful, hardened, and invoked sparingly

**"Good enough" observability**:

- Start with:
  - Structured JSON logs
  - Basic metrics (Prometheus + Grafana)
- Defer SIEM, complex tracing, and multi-region HA until traffic and regulatory pressure justify them

---

#### C. Agent/LLM Optimization

**OSS and small models**:

- Use self-hosted OSS frameworks:
  - SuperAGI, LangGraph, AutoGPT-class
- Prefer:
  - 7B–8B models or cheap APIs
  - Sampling/batching: score 10–20% of traffic, not every event

**Oracle/advisory role**:

- Agents **never decide directly**:
  - They produce scores/labels
  - A deterministic function `F(content, scores, rules, role)` consumes these inputs
- Agents are replaceable; governance/PoE logic does not change when frameworks/models change

---

#### D. Web-App Specific Efficiencies

**Frontend consolidation**:

- Single ATLAS shell containing:
  - Wallet connect/session
  - Bounties (`BountyList`, `MyBounties`, `BountyDashboard`)
  - Admin/Mod Panel
  - GitHub linking & contributions dashboard
- Use SSG/ISR for public/read-only screens to reduce backend load

**Backend design**:

- Prefer coarse-grained endpoints:

  ```
  GET /admin/mod/queue?filters=...
  GET /admin/mod/decisions?cursor=...
  ```

- Provide replay bundles/log files for auditors instead of heavy query APIs

**Scope-driven UI**:

- Use session scopes (`bounty:read`, `bounty:claim`, `mod:*`, `admin:*`) to hide or disable actions that are not permitted
- Backend still enforces scopes; fewer failed calls reduce noise and cost

---

## 3. Cost-Efficiency Checklist (Every Feature)

Before implementing any feature (Admin Panel, GitHub rewards, NOD scoring, etc.), verify:

- [ ] **MOCKQPC-first** (dev/beta)
- [ ] **Batched PoE** (hash-chained events, PQC-signed batches)
- [ ] **Crypto abstraction** (`sign_poe` / `verify_poe` with `env`)
- [ ] **Agent advisory only** (outputs feed `F`, never decide)
- [ ] **Sampling/batching** (agents handle only a subset of events)
- [ ] **Stateless agents** (horizontally scalable)
- [ ] **Coarse-grained APIs** (minimize calls)
- [ ] **Scope-driven UI** (reduce failed/forbidden calls)
- [ ] **Deterministic core** (pure functions + rule configs)
- [ ] **Expensive infra deferred** (HA/HSM/SIEM/multi-region until justified)

---

## 4. v15.5 Admin/Moderator Panel — Technical Plan

### 4.1 Goal

Build a fully deterministic, PoE-backed moderation/admin console where:

**Every action**:

- Flows from a fixed, versioned ruleset
- Is initiated by a wallet-authenticated user with RBAC scopes
- Is serialized, hashed, and anchored in a hash-chained ledger (MOCKQPC in dev/beta, PQC batches in mainnet)

---

### 4.2 Data Model & PoE Schema

#### Rule Definition (JSON/YAML)

```yaml
id: RULE_101
description: "Explicit content detection"
type: "content_score"
threshold: 0.8
enforce_action: "remove"
explainable: true
version: 1
```

#### Moderation Decision Record

```json
{
  "decision_id": "DEC_20251219_0001",
  "content_id": "POST_12345",
  "action": "remove",
  "rule_applied": "RULE_101",
  "rule_version": 1,
  "input_score": 0.87,
  "threshold": 0.8,
  "result": "enforce",
  "moderator_id": "wallet:0xABC...",
  "role": "MODERATOR",
  "timestamp": "2025-12-19T15:00:00Z",
  "justification": "Score above threshold",
  "override": false,
  "previous_decision_id": null,
  "poe_hash": "abc123..."
}
```

#### Override / Appeal Record

```json
{
  "decision_id": "DEC_20251219_0002",
  "content_id": "POST_12345",
  "action": "restore",
  "rule_applied": "RULE_101",
  "rule_version": 1,
  "input_score": 0.79,
  "threshold": 0.8,
  "result": "override",
  "moderator_id": "wallet:0xADMIN...",
  "role": "ADMIN",
  "timestamp": "2025-12-19T16:10:00Z",
  "justification": "Context review supports restore",
  "override": true,
  "previous_decision_id": "DEC_20251219_0001",
  "poe_hash": "def456..."
}
```

#### PoE Anchoring

- Serialize decisions → hash (BigNum/PQC-compatible) → append to hash chain
- **In dev/beta**:
  - Use MOCKQPC to sign batches (`env=beta`)
- **In mainnet**:
  - Use real PQC via `sign_poe(hash, env="mainnet")` to sign batches

---

### 4.3 End-to-End Flow

#### Auth & Roles

- Wallet auth (EIP-191) → session token with scopes (`mod:read`, `mod:act`, `admin:override`, `audit:*`)
- Optional 2FA/hardware key for bans, overrides, and critical actions

#### Deterministic Decision Engine

```
F(content_features, scores, rules, moderator_role) -> recommendation
```

- Uses only stored rule config + quantitative inputs
- **Outputs**:
  - Recommended action (`remove` / `warn` / `ban` / `ignore`)
  - Rule ID, version, threshold, input score

#### Panel Behavior

- Shows recommendation, rule details, score vs threshold, context (prior warnings, reputation)
- Moderator chooses: **Accept** / **No Action** / **Override** (admin only)
- System logs decision, hashes and anchors it (MOCKQPC or PQC batch), then enforces
- Auditors can replay inputs and re-run `F` to confirm recommendations

---

### 4.4 Phases (MOCKQPC-First)

#### Phase 1 — Backend Foundations (MOCKQPC)

- Rule schema + storage (deterministic config)
- Decision models and append-only hash-chained log
- PoE integration to MOCKQPC evidence store
- RBAC scopes for moderator/admin/auditor

#### Phase 2 — Panel APIs (MOCKQPC)

- `GET /admin/mod/queue`
- `POST /admin/mod/decision`
- `GET /admin/mod/decisions`
- Middleware: session validation, scope enforcement, 2FA checks
- **Tests**:
  - Determinism of `F`
  - "log → hash → anchor → enforce" ordering

#### Phase 3 — Frontend Panel (MOCKQPC + Closed Beta)

- **Top bar**: session/role, simulation toggle, override indicator, logout
- **Left**: rule categories, live metrics (queue size, actions, PoE status)
- **Center**: queue, content preview, deterministic recommendation + action buttons
- **Right**: PoE artifact pane + explainable timeline for the selected content

---

## 5. What You Must Produce (Per Feature)

For each new feature (Admin/Mod Panel part, GitHub linking, NOD scoring, etc.), produce:

### A. Cost-Aware Design Notes

- Which parts use MOCKQPC vs real PQC
- Whether PoE is batched and how
- How agents (if any) are sampled/batched and how their outputs feed `F`

### B. Updated Schemas/Interfaces

- Events hash-chained
- Environment-tagged (`env=dev|beta|mainnet`)
- Using `sign_poe` / `verify_poe` abstraction

### C. Test Plans

- **Determinism** (replay produces same output + hashes)
- **MOCKQPC vs PQC equivalence** (same payload hash signed/verified in both backends)
- **Basic cost metrics** (approx PQC and LLM/agent calls per decision)

### D. Short "Cost Impact" Paragraph

2–3 sentences describing how the feature aligns with lean PQC + MOCKQPC strategy and avoids unnecessary infra/agent costs.

**Example** (Admin/Moderator Panel):

> The Admin/Moderator Panel uses MOCKQPC for all dev/beta environments, reducing PQC costs to zero during development. In production, batched PoE signing (1 signature per ~1000 decisions) reduces PQC calls by 99.9% vs per-decision signing. Optional agent scoring samples 10% of content and feeds a deterministic decision engine, keeping LLM costs predictable and low while maintaining full auditability.

---

## 6. Success Metrics

### Cost Efficiency

- **PQC calls**: <100/day for ~10K decisions (via batching)
- **Agent/LLM calls**: <1K/day for ~10K decisions (10–20% sampling)
- **Infra cost**: <$500/month for early production (monolithic stack)

### Determinism

- **Replay success**: 100% via `F`
- **PoE batch verification**: 100%

### Crypto-Agility

- **MOCKQPC ↔ real PQC switch**: <1 hour
- **Algorithm swap**: <1 day

---

**QFS × ATLAS**: Deterministic, PoE-backed, crypto-agile, and cost-efficient—MOCKQPC-tested, mainnet-ready. 🚀
