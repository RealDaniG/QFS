# QFS × ATLAS Cost-Efficient Architecture & Roadmap

## Determinism First, PQC/Agents When Needed

> **Version:** Master Reference  
> **Date:** December 19, 2025  
> **Purpose:** Guide all design, implementation, and documentation decisions for cost-efficient rollout

---

## Objective

Optimize QFS × ATLAS for full web-app rollout while minimizing costs. The system must stay:

- **Deterministic and replayable**
- **PoE-backed and crypto-agile**
- **Ready for real PQC and agents later, but cheap to run now**

---

## 1. Cost Drivers

### A. Crypto (PQC/PoE)

- **Per-action PQC signatures and verifications**
- **Key management** (HSM/KMS), audits, compliance
- **Impact**: Scales linearly with events; expensive at high volume

### B. Infrastructure

- **Multi-node HA clusters**, DB replication, load balancing, multi-region
- **Significant fixed cost** even at low usage
- **Impact**: High upfront and maintenance cost

### C. Agent/LLM Usage

- **Hosted SaaS orchestration**, proprietary models
- **Always-on scoring/moderation** dominates OPEX if used per event
- **Impact**: Continuous cost regardless of value delivered

### D. Observability/Security

- **Enterprise tracing**, SIEM, HSMs deployed too early
- **High upfront and maintenance cost**
- **Impact**: Overhead before product-market fit

**Observation**: Most cost comes from compute-heavy or always-on systems. **Determinism and replayability do not require real PQC/LLM in early stages.**

---

## 2. Cost-Reduction Strategies

### A. Crypto & PoE Optimizations

#### Default to MOCKQPC

All dev, test, and closed beta environments use **MOCKQPC**:

- Hash-chained logs
- Simulated PQC signatures with test keys
- **Real PQC only for**:
  - Treasury moves and NOD allocation
  - Final governance anchors and PoE batches

#### Batch PQC

For all environments:

- **Hash-chain every event** (moderation, admin, agent outputs)
- **PQC-sign only batches** (hundreds/thousands of events)
- **Benefit**: Reduces PQC calls by orders of magnitude while preserving replayability

#### Crypto-Agile Abstraction

All signing/verification goes through:

```python
sign_poe(payload_hash, env)
verify_poe(payload_hash, signature, env)
```

**Environments**:

- `env=dev/beta` → MOCKQPC keys/algorithms
- `env=mainnet` → Production PQC keys/algorithms (e.g., Dilithium) in HSM/KMS

**Application logic must never depend on specific algorithms**; only on hashes and verified results.

---

### B. Infrastructure Efficiency

#### Monolithic-but-Modular Early

One main stack:

- Web frontend (Next.js)
- Backend APIs (FastAPI/Starlette)
- One DB (Postgres) for auth/bounties/mod decisions
- One PoE/MOCKQPC service

**Introduce microservices only when traffic/load clearly demand separation.**

#### Stateless Agent Layers

Agent services (moderation, scoring) must be **stateless**:

- Horizontally scalable on a few mid-tier VMs or containers
- PQC/PoE/governance services remain small, hardened, stateful, and called sparsely

#### "Good Enough" Observability

Start with:

- Structured logs (JSON)
- Basic metrics (Prometheus + Grafana)

**Add advanced tracing, SIEM, and complex alerts later**, once real usage and revenue exist.

---

### C. Agent/LLM Optimization

#### OSS & Small Models

Use **self-hosted OSS frameworks**:

- SuperAGI, LangGraph, AutoGPT-class toolings

**Prefer**:

- 7B–8B open models or cheap APIs
- **Batch or sample events** (e.g., score 10–20% of traffic) instead of per-event evaluation

#### Oracle/Advisory Role

**Agent outputs never decide directly**:

- Agents produce scores/labels
- A deterministic function `F(content, scores, rules, role)` consumes these as inputs
- **Agents are replaceable**; governance and PoE are unaffected by which agent framework/model is in use

---

### D. Web-App Specific Efficiencies

#### Frontend Consolidation

One ATLAS shell containing:

- Wallet connect/session
- Bounties (BountyList, MyBounties, BountyDashboard)
- Admin/Mod Panel (current baseline.5)
- GitHub linking & contributions dashboard

**Use SSG/ISR** for public/read-only pages to reduce backend load.

#### Backend Design

Favor **coarse-grained endpoints**:

```
GET /admin/mod/queue?filters=...
GET /admin/mod/decisions?cursor=...
```

For auditing:

- Provide **replay bundles/log files** rather than heavy query APIs

#### Scope-Driven UI

Use session scopes (`bounty:read`, `bounty:claim`, `mod:*`, `admin:*`) to:

- **Hide or disable actions** in the UI when not permitted
- Backend still enforces scopes; fewer failed calls reduce noise and cost

---

## 3. Recommended Cost-Efficient Roadmap

### Keep PQC/PoE Abstraction Layer

All code and docs assume:

- Crypto calls go through `sign_poe` / `verify_poe`
- Events carry `env` and algorithm identifiers

**This enables**:

- MOCKQPC in dev/beta
- Real PQC in mainnet
- Future algorithm swaps without redesign

### Default MOCKQPC Environment

For all **non-critical events**:

- Moderation decisions
- Agent scores
- Dashboard metrics

**Real PQC reserved for**:

- Final governance decisions
- Treasury/NOD operations
- Final PoE batch anchors

### Defer Expensive Infra

**No**:

- Multi-region clusters
- Early HSM deployments
- Enterprise SIEM

**Until**:

- Governance/PoE are stable
- There is sustained traffic and/or regulatory pressure that justifies cost

### OSS Agents + Small Models

Self-host SuperAGI/LangGraph or similar, with:

- **Sampling and batching** of events
- Ensure outputs are **advisory**, flowing into `F`, not determining outcomes

### Push Logic into Deterministic F + Rules

Encode as much as possible in:

- Pure functions
- Rule tables and configs

**Benefits**:

- Cheaper infra and agents
- Easier PQC migration
- Easier audit and replay

---

## 4. Open-Source / Low-Cost Stack Recommendations

For all design and implementation decisions, prefer:

| Component | Recommendation |
|-----------|----------------|
| **Agents** | SuperAGI, LangGraph, AutoGPT-class (self-hosted, batched) |
| **Web/Backend** | Next.js (web), FastAPI/Starlette (API) |
| **DB** | Postgres (production); SQLite (dev) |
| **Observability** | Prometheus + Grafana; log-based debugging initially |
| **Crypto/PQC** | MOCKQPC (dev/beta); PQClean/liboqs (mainnet) |

---

## 5. What You Should Produce (For Each New Feature)

Whenever you design or implement new QFS × ATLAS features (Admin/Mod Panel, GitHub rewards, NOD scoring, etc.), your output must include:

### A. Cost-Aware Design Notes

- Which parts run under **MOCKQPC vs real PQC**
- Whether actions are **batched for PoE**
- Whether agents are **advisory** and how they're sampled/batched

### B. Updated Schemas/Interfaces

Ensure events are:

- **Hash-chained**
- **Environment-tagged** (`env=dev|beta|mainnet`)
- Using the **crypto abstraction** (`sign_poe`, `verify_poe`)

### C. Test Plans

**Determinism**:

- Replays produce the same output and hashes

**MOCKQPC vs Real PQC**:

- Same payload hash signed/verified in both backends

**Basic Cost Metrics**:

- Approximate calls to PQC and LLM/agents per decision

### D. Short "Cost Impact" Paragraph

For internal docs/SOTU:

**2–3 sentences** on how this feature aligns with the lean PQC and MOCKQPC strategy and avoids unnecessary infra/agent cost.

---

## 6. Cost-Efficiency Checklist

Before implementing any new feature, verify:

- [ ] **MOCKQPC-first**: Dev/beta use MOCKQPC, not real PQC
- [ ] **Batched PoE**: Events hash-chained, PQC-signed in batches
- [ ] **Crypto abstraction**: Uses `sign_poe`/`verify_poe` with `env` parameter
- [ ] **Agent advisory**: Agent outputs feed deterministic `F`, don't decide directly
- [ ] **Sampling/batching**: Agents process subset of events, not all
- [ ] **Stateless agents**: Agent services horizontally scalable
- [ ] **Coarse-grained APIs**: Minimize backend calls
- [ ] **Scope-driven UI**: Hide unavailable actions to reduce failed calls
- [ ] **Deterministic core**: Logic in pure functions + rule configs
- [ ] **Defer expensive infra**: No HA/multi-region/SIEM until justified

---

## 7. Example: Admin/Moderator Panel Cost Analysis

### Feature: current baseline.5 Admin/Moderator Panel

**Cost-Aware Design**:

- **MOCKQPC**: All Phase 1-3 development and closed beta use MOCKQPC
- **Batched PoE**: Moderation decisions hash-chained, PQC-signed in hourly batches (1 signature per ~1000 decisions)
- **Agent Advisory**: Optional agent scores feed deterministic `F(content, scores, rules, role)`; agents sample 10% of content
- **Stateless**: Agent scoring service runs on 2-3 mid-tier VMs, scales horizontally

**Cost Impact**:

> The Admin/Moderator Panel uses MOCKQPC for all dev/beta environments, reducing PQC costs to zero during development. In production, batched PoE signing (1 signature per ~1000 decisions) reduces PQC calls by 99.9% vs per-decision signing. Optional agent scoring samples 10% of content and feeds a deterministic decision engine, keeping LLM costs predictable and low while maintaining full auditability.

**Estimated Costs** (production, 10K decisions/day):

- **PQC**: ~10 signatures/day (batched) vs 10K/day (per-decision) = **99.9% reduction**
- **Agent/LLM**: ~1K API calls/day (10% sampling) vs 10K/day (always-on) = **90% reduction**
- **Infrastructure**: Single backend + DB + PoE service = **~$200/month** vs multi-region HA = **~$2000/month**

---

## 8. Integration with current baseline.5 Planning

All current baseline.5 Admin/Moderator Panel work follows this cost-efficient architecture:

### Phase 1: Backend Foundations (MOCKQPC)

- ✅ Rule schema + storage (deterministic config, no PQC)
- ✅ Decision models + hash-chained log (MOCKQPC signatures)
- ✅ Deterministic engine `F` (pure function, no agents required)
- ✅ RBAC scopes (session-based, no per-action crypto)

### Phase 2: Panel APIs (MOCKQPC)

- ✅ All endpoints use MOCKQPC for PoE anchoring
- ✅ Batched PoE: decisions accumulated, signed hourly
- ✅ Scope enforcement at API layer (reduce failed calls)

### Phase 3: Frontend Panel (MOCKQPC + Closed Beta)

- ✅ Scope-driven UI (hide unavailable actions)
- ✅ Coarse-grained API calls (minimize backend load)
- ✅ Closed beta on MOCKQPC testnet (zero PQC cost)

### Mainnet Graduation

- ⏳ Governance approval required
- ⏳ Switch `env=beta` → `env=mainnet` in `sign_poe` calls
- ⏳ Real PQC only for final batch anchors
- ⏳ Agent sampling remains at 10% (or lower if cost-prohibitive)

---

## 9. Success Metrics

### Cost Efficiency

- **PQC calls**: <100/day for 10K decisions (99%+ reduction via batching)
- **Agent/LLM calls**: <1K/day for 10K decisions (90%+ reduction via sampling)
- **Infrastructure**: <$500/month for 10K decisions/day (monolithic stack)

### Determinism

- **Replay success**: 100% of decisions reproducible via `F(inputs)`
- **Hash chain integrity**: 100% of PoE batches verifiable

### Crypto-Agility

- **Environment switch**: <1 hour to swap MOCKQPC ↔ real PQC
- **Algorithm upgrade**: <1 day to swap PQC algorithms (abstraction layer)

---

**QFS × ATLAS**: Deterministic, PoE-backed, crypto-agile, and cost-efficient. Build lean, scale smart. 🚀
