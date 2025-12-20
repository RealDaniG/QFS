# QFS × ATLAS — Platform Evolution Plan

> **Status:** Authoritative Strategic Roadmap  
> **Current Version:** v17.0.0-beta (Governance & Bounty F-Layer)  
> **Foundation:** v16.1.1-pre-v17-ready (Deterministic, Cost-Efficient, MOCKQPC-First)  
> **Agent Strategy:** CrewAI/LangGraph (replacing OpenAGI)

---

## Overview

This plan outlines the complete platform evolution built on the evergreen v16 capability baseline. The platform is MOCKQPC-first, EvidenceBus-centric, with deterministic governance and moderation at its core.

### Core Principles

- **MOCKQPC-First**: Zero PQC cost in dev/beta, batched signatures in mainnet
- **EvidenceBus-Centric**: All significant events emitted, hash-chained, and PoE-backed
- **Deterministic**: Pure function `F` for all decisions, 100% replayable
- **Wallet-Based Identity**: EVM wallet authentication with scope-based access control
- **Cost-Conscious**: PQC <0.01/decision, Agents <0.2/decision
- **Cross-Platform**: Windows/macOS/Linux with single-node default

---

## 1. Core Platform Enhancements

### 1.1 Dashboard & UI

**Goals**

- Single responsive dashboard surface for governance, moderation, bounties, and contributors
- Role-aware UIs driven by wallet scopes and EvidenceBus streams

**Implementation Plan**

**Dashboard Shell** (Next.js/React):

- Global layout (top nav + side nav): "Home", "Bounties", "Governance", "Moderation", "Contributions", "Settings"
- Mobile-first responsive design with tailwind/CSS grid

**Role-Aware Routing/Components**:

- Middleware reads wallet session scopes (`bounty:claim`, `bounty:read`, `mod:*`, `admin:*`)
- Hides actions the user cannot perform
- Prevents client calls to restricted endpoints (defense in depth with backend checks)

**Realtime EvidenceBus Subscriptions**:

- Frontend WebSocket/SSE client subscribes to channels:
  - `governance.*` (proposals, votes, execution)
  - `moderation.*` (queue updates, decisions)
  - `bounty.*` (created/claimed/paid)
- Dashboard widgets:
  - PoE event feed (recent events with filters)
  - Governance activity timeline
  - Moderation queue counts and status

### 1.2 User Platform Features

**Goals**

- Wallet as primary identity, with contribution intelligence surfaced directly

**Implementation Plan**

**Wallet Login Flows**:

- EVM/QFS-native wallet login via `NonceManager` + `WalletAuth` + `SessionManager`
- Session tokens carry scopes and are validated on every API call

**Dual-Proof Contribution Mapping**:

- Endpoint `/auth/bind-github`:
  - Wallet signs a challenge
  - GitHub account proves control (e.g., signed commit, Gist, or OAuth)
  - Store immutable link wallet ↔ GitHub handle

**Contribution Dashboard**:

- Sections:
  - "Verified contributions": from GitHub indexer + on-chain/off-chain events
  - "Eligible bounties": filtered by skills + history
  - "Rewards & history": claimed, pending, paid, with PoE links

### 1.3 Decentralized Connectivity

**Goals**

- Make MOCKQPC and EvidenceBus **visible** to users, not just infra concerns

**Implementation Plan**

**MOCKQPC-First Enforcement**:

- ✅ All dev/beta setups: `MOCKQPC_ENABLED=true` + `env=dev|beta` (Enforced by `scripts/check_zero_sim.py` and Adapter)
- Only mainnet config enables real PQC paths

**EvidenceBus Event Taxonomy**:

- Event types: `governance_decision`, `moderation_decision`, `bounty_event`, `agent_advisory`, `wallet_auth_event`, etc.
- Each event carries `env`, `hash_prev`, `hash_self`, and payload

**PoE Verification Tools** (UI + CLI):

- ✅ CLI: `verify_poe`, `scripts/verify_mockqpc_determinism.py` exist
- UI: "Verify PoE" page that:
  - Accepts an artifact or ID
  - Calls backend to verify hash-chain and signature (mock or real)
  - Shows deterministic replay status

---

## 2. Secure Communication & Media

### 2.1 Secure Chat

**Goals**

- Governance/moderation discussions with E2E and PoE-backed accountability

**Implementation Plan**

**Wallet-Based Identity for Chat**:

- Chats scoped by wallet session and roles (mod/admin vs general)
- Channels: `#governance`, `#moderation`, project-specific rooms

**E2E Encryption**:

- Per-room key management tied to wallet identities
- Store only ciphertext + PoE hashes of content

**EvidenceBus Integration for Moderation**:

- When a message is flagged or actioned:
  - Emit `moderation_decision` with content hash, moderator wallet, decision, and reason
  - Allow replay of moderation decisions over chat logs

### 2.2 Spaces & Social

**Goals**

- Social layer is fully deterministic and PoE-backed

**Implementation Plan**

**Spaces**:

- Room metadata + membership + events (join/leave/post) all emit EvidenceBus events
- Apply `F_moderation_v1` to content with score + rules; only advisory agents provide scores

**Content Lifecycle**:

- Events for create/edit/delete/react/pin, all hashed and chained
- Admin tools in the panel to replay a space's content and decisions

**Optional External Bridges**:

- Adapter that logs external posts/tweets into QFS as `external_contribution` events with content hash + metadata
- Use these for reward calculation without trusting external platforms

---

## 3. Governance, Moderation & Agents

### 3.1 Deterministic Governance / Moderation

**Goals**

- Every decision is reproducible and replayable

**Implementation Plan**

**v17 Governance F-Layer** ✅ COMPLETE:

- ✅ Deterministic proposal creation and state reconstruction
- ✅ Vote casting with validation and eligibility checks
- ✅ Outcome computation with quorum/approval thresholds
- ✅ Deterministic tie-breaking rules
- ✅ Full PoE logging to EvidenceBus
- ✅ Pure functions (state from events only)

**`F_moderation_v1` as Single Decision Engine**:

- Inputs: content, scores, rules, roles
- Outputs: deterministic action and rationale

**Admin/Mod Panel**:

- API endpoints: `/admin/mod/queue`, `/admin/mod/decision`, `/admin/mod/history`
- Every decision emits an EvidenceBus event and is included in PoE batches

**Governance UI** 🔄 IN PROGRESS:

- Governance timelines (proposal → votes → execution)
- Decision explanation panels
- Evidence links to PoE events
- CLI replay tools

### 3.2 Lean Agent Layer

**Goals**

- Replace OpenAGI with minimal, pluggable advisory agents under strict cost constraints

**Implementation Plan**

**Agent Framework Selection**:

- **CrewAI / LangGraph** for backend agents
- **n8n** for ops workflows

**Agent Functionality**:

- Run on historical logs, telemetry, and content snapshots
- Output advisory scores (e.g., toxicity, priority, reward suggestions)

**Sampling Strategy**:

- Only 10-20% of items go through agents
- Enforced at API level

**Integration Pattern**:

- Agent outputs → `agent_advisory` EvidenceBus events
- `F_moderation_v1` reads these scores but maintains deterministic behavior
- Agent calls and PQC cost tracked in cost metrics tools

---

## 4. Contributor & Bounty System

### 4.1 Wallet-Linked Bounties

**Goals**

- Deterministic, wallet-based rewards with PoE-backed proof

**Implementation Plan**

**v17 Bounty F-Layer** ✅ COMPLETE:

- ✅ Deterministic bounty creation and contribution submission
- ✅ State reconstruction from EvidenceBus events
- ✅ Deterministic reward computation with advisory integration
- ✅ Normalized score-based distribution
- ✅ Full PoE logging to EvidenceBus
- ✅ Pure functions (state from events only)

**Bounty Lifecycle**:

- Creation → EvidenceBus `BOUNTY_CREATED`
- Contribution → `BOUNTY_CONTRIBUTION_SUBMITTED`
- Reward Decision → `BOUNTY_REWARD_DECIDED`
- All batched into PoE

**Dual-Proof Enforcement**:

- Wallet ↔ GitHub link required for dev bounties
- Indexer verifies PR/commit references

**Bounty UI** 🔄 IN PROGRESS:

- Views: "Open", "My Bounties", "History"
- Bounty timelines (creation → contributions → rewards)
- Each entry links to PoE artifacts for audit
- Advisory vs F-layer distinction visible

### 4.2 Cost-Efficient Verification

**Goals**

- Keep PQC and agent costs predictable and low

**Implementation Plan**

**MOCKQPC-Only in Dev/Beta**:

- ✅ Mainnet uses batched PQC only for anchors (Enforced by Adapter)

**Configuration**:

- Batch sizes and sampling rates encoded in config and documented in CONTRIBUTING:
  - PQC: target <0.01 calls per decision
  - Agents: target <0.2 calls per decision

**Contributor Dashboard**:

- Display cost metrics (approximate), PoE coverage, and audit-ready bundles for user's actions

---

## 5. Repo & Documentation Alignment

**Goals**

- No more temporal drift; docs describe a capability baseline

**Implementation Plan**

**Root Directory**:

- ✅ Keep minimal: README, CHANGELOG, LICENSE, config files, core launchers
- All other docs:
  - Under `/docs` (architecture, audits, guides)
  - `/scripts`, `/deploy`, `/monitoring`, `/checkpoints` per function

**Canonical Documentation**:

- `DEV_GUIDE.md` for setup and deployment
- `MASTER_PROMPT_v15.5.md` encoding invariants:
  - MOCKQPC-first
  - EvidenceBus required for PoE
  - Deterministic `F` for moderation/governance
  - Wallet auth as baseline
  - Cross-platform single node as default
  - Cost ceilings (PQC, agents)

**Evergreen Language**:

- ✅ No dates, phases, or "new in vX.Y" language in core docs
- ✅ Changelog is historical; README + RELEASE_NOTES are "Current Baseline Capabilities"

---

## 6. Deployment & Operations

### 6.1 Baseline Deployment

**Goals**

- One simple, cheap path to full stack

**Implementation Plan**

**Single-Node Setup**:

- Backend: FastAPI/uvicorn
- Frontend: Next.js dev/production
- DB: SQLite (dev), Postgres (beta/mainnet)
- EvidenceBus listener + MOCKQPC service

**Templates**:

- `.env.example` for dev/beta/mainnet
- Docker Compose for full stack local run

### 6.2 Observability & Audit

**Goals**

- Anyone can measure cost and verify behavior

**Implementation Plan**

**CLI Tooling**:

- `cost_metrics.py`: PQC calls, agent calls, infra cost per decision
- `generate_replay_bundle.py`: export PoE+events
- ✅ `verify_poe.py`, `replay_*` for governance and moderation (MOCKQPC verify script added)

**Monitoring Dashboards**:

- Basic Grafana or simple custom UI showing:
  - Event throughput
  - PQC/agent usage
  - Error rates and replay success rates

---

## 7. Launch Readiness Checklist

| Component | Acceptance Tests | EvidenceBus Integration | PoE/Replay | Cost Metrics | Status |
|-----------|-----------------|------------------------|------------|--------------|--------|
| **Dashboard UI** | Role-aware routing works, WebSocket subscriptions active | ✅ All events subscribed | ✅ Event feed verified | N/A | ⏳ |
| **Wallet Auth** | Login/logout, session persistence, scope enforcement | ✅ `wallet_auth_event` emitted | ✅ Auth replay works | <0.001/session | ⏳ |
| **GitHub Link** | Dual-proof binding, link verification | ✅ `github_link_event` emitted | ✅ Link replay verified | N/A | ⏳ |
| **Secure Chat** | E2E encryption, moderation integration | ✅ `chat_message`, `moderation_decision` | ✅ Chat log replay | <0.01/message | ⏳ |
| **Spaces** | Create/join/post, content moderation | ✅ `space_*` events | ✅ Space replay verified | <0.01/action | ⏳ |
| **Deterministic Governance** | Proposal lifecycle, voting, execution | ✅ `governance_*` events | ✅ Gov cycle replay (100%) | <0.01/decision | ⏳ |
| **Agent Layer** | CrewAI/LangGraph integration, sampling works | ✅ `agent_advisory` events | ✅ Agent output replay | <0.2/decision | ⏳ |
| **Bounty System** | Create/claim/submit/pay workflow | ✅ `bounty_*` events | ✅ Bounty lifecycle replay | <0.01/bounty | ⏳ |
| **PoE/EvidenceBus** | Hash-chain integrity, batch signing | ✅ Core infrastructure | ✅ MOCKQPC replay (100%) | <0.01 PQC/decision | ✅ |
| **Repo & Docs** | Links resolve, no temporal language | N/A | N/A | N/A | ✅ |
| **Deployment** | Single-node runs on Win/Mac/Linux | ✅ All events in logs | ✅ Full system replay | <$50/month | ⏳ |
| **Observability** | Cost metrics, dashboards, CLI tools work | ✅ Metrics collected | ✅ Audit bundles generated | N/A | ⏳ |

**Acceptance Criteria**:

- ✅ = Complete when UI flows work, events emit, PoE replay succeeds, cost within target

---

## 8. Execution Order (Practical)

### Phase 1: Foundation Lock (Immediate)

1. ✅ **Finalize `MASTER_PROMPT_v15.5.md`** and CONTRIBUTING requirements
2. ✅ **Complete evergreen docs**: Apply manual replacements to README, CHANGELOG, BOUNTIES, CONTRIBUTING, RELEASE_NOTES
3. ✅ **Commit repository cleanup and evergreen alignment**
4. ✅ **Implement MOCKQPC & Zero-Sim Checker**

### Phase 2: Core Infrastructure (Week 1-2)

5. ⏳ **Implement wallet ↔ GitHub dual-proof** (`/auth/bind-github` endpoint)
6. ⏳ **Complete bounty endpoints** (create/claim/submit/pay with EvidenceBus)
7. ⏳ **Wire EvidenceBus everywhere** (governance, moderation, bounties, agents)

### Phase 3: Agent Integration (Week 2-3)

8. ⏳ **Integrate CrewAI/LangGraph** (replacing OpenAGI)
9. ⏳ **Implement sampling strategy** (10-20% configurable)
10. ⏳ **Emit `agent_advisory` events** to EvidenceBus

### Phase 4: UI/UX (Week 3-5)

11. ⏳ **Dashboard shell** with role-aware routing
12. ⏳ **Spaces implementation** with deterministic moderation
13. ⏳ **Secure chat** with E2E encryption
14. ⏳ **Contributor dashboard** with verified contributions and rewards

### Phase 5: Testing & Verification (Week 5-6)

15. ⏳ **End-to-end replay tests** for governance, moderation, bounties
16. ⏳ **Cross-platform testing** (Windows/macOS/Linux with MOCKQPC)
17. ⏳ **Cost metrics validation** (PQC <0.01, Agents <0.2 per decision)

### Phase 6: Observability & Tooling (Week 6-7)

18. ⏳ **Grafana/Custom dashboard** for throughput and cost
19. ⏳ **CLI tools** for deep inspection and replay bundles

---

## 9. v18 Outlook: Distributed Fabric

**Goal**: Transform v17's single-node deterministic core into a distributed, PQC-anchored mesh.

**Blueprint**: See [V18_DESIGN_AND_DEPLOYMENT.md](V18_DESIGN_AND_DEPLOYMENT.md).

- **Phase 1: Multi-Node Core**: Introduce deterministic consensus (Raft/PBFT) between Tier A nodes sharing the EvidenceBus.
- **Phase 2: PQC Anchors**: Replace MOCKQPC with real PQC signatures for batch sealing at Tier A.
- **Phase 3: Edge Expansion**: Deploy UI and Advisory logic to Tier B (PoE++ Edge Nodes) and Tier C (Sensors).
