# Quantum Financial System (QFS) – Deterministic Engine

> **Core:** Deterministic, replayable coordination and settlement engine

# ATLAS – Social & Governance Layer on QFS

> **Surface:** Conversations, contributions, and disputes backed by incorruptible memory

---

<div align="center">

**🚧 IN ACTIVE DEVELOPMENT 🚧**

**Status:** V18 Integration Complete • Core Hardening (v13.5) • Distributed Fabric (Design Phase) • GitHub Identity Integration (In Progress)
**Current Focus:** Zero-Sim Remediation, Real PQC Integration & GitHub Bounties
**Architecture:** MOCKQPC-first • Zero-Sim enforced • EvidenceBus-centric • Privacy-first data strategy • AGPL-3.0 licensed  

[**📂 Repo Structure**](REPO_STRUCTURE.md) • [**✅ Integration Status**](docs/V18_INTEGRATION_STATUS_DETAILED.md) • [**🧪 Testing Guide**](docs/TESTING.md)

</div>

---

## 🛡️ Implementation vs Design (Reality Map)

| Component | Status | Details |
| :--- | :--- | :--- |
| **HSMF Core** | ✅ Implemented | [Code](v13/core/HSMF.py) • [Docs](v13/docs/HSMF_HarmonicDesign.md) • [Tests](v13/tests/HSMF) |
| **HSMF × ATLAS** | ✅ Implemented | Wall integration confirmed. |
| **Governance Proofs** | ✅ Implemented | [Contracts](v13/docs/Governance_MathContracts.md) • [Replay Test](v13/tests/governance/test_governance_replay.py) |
| **Zero-Sim** | ⚠️ Enforced | [Scanner](scripts/check_zero_sim.py) • [Backlog](v13/docs/ZeroSim_Backlog_v18.md) |
| **GitHub Identity** | 🚧 Started | [Docs](BOUNTIES.md) • [Importer](tools/github/github_import_contributions.py) |
| **PQC Anchoring** | 🚧 Stubbed | [Plan](v13/docs/PQC_Anchoring_Plan.md) • [Stub](v13/core/pqc/PQCAnchorService.py) |
| **Raft / Fabric** | 📝 Planned | [Design Notes](v13/docs/Fabric_Design_Notes.md) (Single-node baseline) |

---

## Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- MetaMask browser extension (or other Web3 wallet)

Run `scripts/check_prerequisites.ps1` to verify and auto-install dependencies.

---

## ⚡ Full System Verification

To verify the entire V18 integration (Backend, Frontend, Auth, E2E Flows) in one go, use the **Orchestrator**:

```powershell
powershell -ExecutionPolicy Bypass -File run_atlas_full.ps1
```

This script:

1. Starts the Backend (Port 8001) and Frontend (Port 3000).
2. Waits for health checks to pass.
3. Runs:
   - `verify_atlas_e2e.py` (API Check)
   - `verify_auth.py` (Auth Flow)
   - `pytest` (Route Regression)
   - `npm run test:e2e` (Playwright UI Smoke Tests)
4. Logs results to `logs/atlas_full_run.log`.

**Exit Code 0** indicates a fully healthy system.

## 🏛️ What is QFS × ATLAS?

**QFS** is the deterministic truth engine and event spine:

- **EvidenceBus**: Hash-chained, immutable event log
- **PoE (Proof of Execution)**: Cryptographic verification of all decisions
- **Zero-Sim**: Enforced determinism—same inputs always produce same outputs
- **MOCKQPC**: Zero-cost crypto in dev/beta, batched PQC for mainnet anchors

**ATLAS** is the social, governance, and bounty UX built on QFS:

- **Conversations & Threads**: Social layer where history cannot be silently altered
- **Governance**: Proposals, voting, execution—all deterministic and replayable
- **Bounties & Contributions**: Fair reward allocation with transparent formulas
- **Disputes**: Evidence-backed escalation and resolution

### Physical & Network Layer (Fabric Architecture)

With the arrival of **v18**, the platform expands from a single-node core to a tiered, distributed fabric:

- **Tier A (Cluster Backbone)**: High-availability validators running Raft consensus and PQC anchoring (Planned).
- **Tier B (Edge Advisory)**: Read-only nodes hosting UI and local SLM agents (Planned).
- **Tier C (Telemetry/Sensors)**: Write-only edge devices submitting telemetry via consensus (Planned).

---

## 🎯 The Problem We Solve

Most digital platforms suffer from structural issues:

- **Opaque Decisions** → QFS: "View evidence" for every decision
- **Arbitrary Rules** → QFS: "See the rule applied" with deterministic logic
- **Unfair Rewards** → QFS: Deterministic bounty and contribution history
- **High Costs** → QFS: MOCKQPC-first architecture ($0 dev cost)
- **Unnecessary Complexity** → QFS: Single-node baseline, lean architecture

---

## 📈 Current Status: v17.0.0-beta (Full Feature Complete)

### v17 — Governance, Bounties, Social & Advisory

**Engine Layers (F-Layer):**

- ✅ **Governance**: Deterministic proposals, voting, execution, and quorum logic.
- ✅ **Bounties**: Lifecycle management, contribution tracking, and reward allocation.
- ✅ **Social**: Thread-binding, dispute lifecycle, and profile history.

**User Visibility Layers (Projection):**

- ✅ **Timelines**: Human-readable governance and bounty flows.
- ✅ **Explanations**: Plain-text summaries linked to cryptographic PoE.
- ✅ **Advisory**: Agent signals (Layer D) overlaid as "Suggestions" or "Flags".

**Verification:**

- ✅ **Zero-Sim**: Enforced determinism in CI.
- ✅ **PoE**: Full EvidenceBus logging for replay.

**Status:** Beta (Ready for Testing)

### v18 — Real Wallet & Cryptographic Auth

- ✅ **Real Web3 wallet connection** (RainbowKit + wagmi)
- ✅ **Cryptographic auth** (nonce → sign → verify → session token)
- ✅ **Internal credit economy** (non-transferable FLX)
- ✅ **Distributed Interface**: DistributedFeed and WalletInterface live
- ✅ **Secure Infrastructure**: AuthGate-protected views and route guards
- ✅ **Hardened Core**: Post-HSMF Proofs and Zero-Sim Scanner (v13.5).

### For Users

- **Trust**: Understand exactly how and why decisions are made
- **Fairness**: Same rules apply to everyone, universally
- **Transparency**: Outcomes can be audited by anyone
- **Meaningful Participation**: Contributions verified and rewarded

### For Operators & Builders

- **Efficient Cost Structure**: MOCKQPC-first = $0 dev cost, ~99% savings vs per-tx PQC
- **Smart Scalability**: Single-node baseline, growth without complexity
- **Lower Risk**: Deterministic replay + CI-enforced Zero-Sim
- **Accountability**: Verifiable governance logs reduce audit costs

---

## 🔐 Security & Determinism

### MOCKQPC-First Architecture

- **Dev/Beta**: Simulated, deterministic PQC signatures ($0 cost, instant)
- **Mainnet**: Batched PQC anchors (10-100× cost savings)
- **CI Enforcement**: Zero-Sim checker blocks non-deterministic code
- **Safety**: Real PQC libraries physically blocked in dev/beta

### EvidenceBus & PoE

**EvidenceBus** is the central event spine—all governance, moderation, bounty, wallet auth, and agent advisory events are:

- Emitted as structured events
- Hash-chained for integrity
- Batched for PoE signatures
- Fully replayable

| Feature | Dev/Beta/CI | Mainnet | Cost Impact |
| :--- | :--- | :--- | :--- |
| **Crypto** | MOCKQPC ($0) | Batched PQC Anchors | ~99% savings |
| **Agents** | Simulated/Local | Advisory-Only (Sampled) | Capped by sampling |
| **Infra** | Single Node | Single Node | <$50/mo baseline |

### Zero-Sim Compliance

- **Enforced Determinism**: No `random()`, no wall-clock time, no floats in economics
- **CI Gating**: Every commit checked for Zero-Sim violations (Tier 1).
- **Deep Audit**: AST Checker available for comprehensive scans (Tier 2).
- **Replayability**: Same inputs → same outputs, always

---

## 🤖 Agent Layer (Advisory-Only)

Agents provide **suggestions**, never **authority**:

- **Architecture**: Agents produce `agent_advisory` events
- **Adapter Layer**: Outputs are deterministic, schema-validated, hashed
- **QFS Retains Authority**: Deterministic F-layer makes final decisions
- **Cost Control**: Sampling rate caps agent usage

> **Deep Dive:** [Agent Integration & Evolution](./docs/AGENT_INTEGRATION_EVOLUTION.md)

---

## 🏛️ Governance & PoE Fusion

In QFS × ATLAS, **governance and PoE form a single, fused system**:

### Every Governance Step is a PoE Object

- **Proposal**: PoE entry with hash, metadata, proposer
- **Voting**: PoE events for each vote, delegation, quorum update
- **Execution**: PoE entries linking proposal → contract calls → state changes
- **Disputes**: Challenge and resolution chains form evidentiary threads

### Roles & Permissions

**Protocol Level:**

- Governance keys control upgradeable modules, parameters
- Validators attest to state transitions (each = PoE event)

**Application Level (ATLAS):**

- Project/pool/vault owners have scoped admin rights
- Every privileged action emits PoE event with actor, scope, parameters
- Full social/governance surface is replayable and auditable

---

## 🚀 System Highlights (v16 + v17)

### v16 Baseline

- ✅ Non-custodial wallet auth (EIP-191, session management, scopes)
- ✅ Protected API routes (bounty, contribution endpoints)
- ✅ Admin dashboard with Evidence Chain Viewer
- ✅ Agent advisory layer (read-only, non-authoritative)
- ✅ EvidenceBus integration across all components

### v17 Governance F-Layer

- ✅ Deterministic proposal creation and state reconstruction
- ✅ Vote casting with validation and eligibility checks
- ✅ Outcome computation (quorum, approval thresholds, tie-breaking)
- ✅ Full PoE logging and replayability

### v17 Bounty F-Layer

- ✅ Deterministic bounty and contribution lifecycle
- ✅ Reward computation with advisory integration
- ✅ Normalized score-based distribution
- ✅ Full PoE logging and replayability

---

## 🔍 Verify Yourself

> **Trust, but Verify.** QFS provides tools for independent audit.

### 1. Run the Pipeline

```bash
python scripts/run_pipeline.py
```

### 2. Verify PoE Artifacts

```bash
# Verify individual PoE artifact
python v15/tools/verify_poe.py --artifact evidence/gov_cycle_001.poe

# Replay full governance cycle
python v15/tools/replay_gov_cycle.py --start 1 --end 50
```

### 3. Check Zero-Sim Compliance

```bash
# Run Zero-Sim checker
python scripts/check_zero_sim.py

# Verify MOCKQPC determinism
python scripts/verify_mockqpc_determinism.py
```

All tools guarantee deterministic outputs. Same inputs → same results, every time.

---

## 🛠️ Quick Start

See [DEV_GUIDE.md](./DEV_GUIDE.md) for complete cross-platform setup (Windows, macOS, Linux).

### Local Development

```bash
# Clone repository
git clone https://github.com/RealDaniG/QFS.git
cd QFS/v13

# Backend setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment
export ENV=dev
export MOCKQPC_ENABLED=true

# Start backend
uvicorn atlas.src.api.main:app --reload

# Frontend (new terminal)
cd atlas
npm install
npm run dev
```

---

## 📚 Documentation

### Core Documentation

- [Developer Guide](./DEV_GUIDE.md) - Cross-platform setup and deployment
- [Contributing Guidelines](./CONTRIBUTING.md) - How to contribute
- [Maintainers Guide](./docs/MAINTAINERS_GUIDE.md) - Triage and release procedures
- [FAQ - MOCKQPC & Agents](./docs/FAQ_MOCKQPC_AND_AGENTS.md) - Common questions
- [Bounties](./BOUNTIES.md) - Developer rewards and incentives

### Technical Documentation

- [Cost-Efficient Architecture](./docs/COST_EFFICIENT_ARCHITECTURE.md) - Cost optimization
- [Agent Integration Evolution](./docs/AGENT_INTEGRATION_EVOLUTION.md) - Agent strategy

### Architecture & Planning

- [Platform Evolution Plan](./docs/PLATFORM_EVOLUTION_PLAN.md) - Strategic roadmap

---

## 📈 Evolution Timeline

### v14 — Economic & Identity Foundations

Established structured internal economy and digital identity. System was powerful but complex and resource-intensive.

### v15 — Governance Clarity & Discipline

Strategic reset with structured processes. Decisions became consistent and traceable.

### v16 — Evergreen Baseline

Optimal balance between strength and efficiency. MOCKQPC-first architecture, reduced dependencies, single-node deployment.

### v16.1.x — Integration Complete (Current Main)

Wallet auth, admin dashboard, agent advisory layer, full EvidenceBus integration.

### 🌐 ATLAS V18 Status & Docs

The V18 integration is **Complete and Verified**, merging the Distributed Backbone with the User Application.

- **Backend**: `main_minimal.py` serves real v18 routes (Governance, Content, Auth) via `v13/src/api`.
- **Frontend**: `v13/atlas` is fully wired to live endpoints (`GovernanceInterface`, `DistributedFeed`).
- **V18 Integration**: Validated via [Testing Guide](docs/TESTING.md) and Playwright E2E tests.

**Key Documentation:**

- [Integration Status detailed](docs/V18_INTEGRATION_STATUS_DETAILED.md)
- [Design and Deployment](docs/V18_DESIGN_AND_DEPLOYMENT.md)
- [Zero-Sim Automation](docs/ZERO_SIM_AUTOMATION.md)

### v17.0.0-beta — Governance & Bounty F-Layer

Determinism-locked governance and bounty management with full PoE logging. Platform feature complete for single-node operation.

### v18.0.0-alpha — Distributed Fabric Backbone (Current)

Consensus-driven Tier A backbone complete. Deterministic replication (Raft), PQC batch anchoring, and integrated EvidenceBus wiring achieved.

---

## 🗺️ Roadmap: v18 Distributed Fabric

The distributed Tier A backbone is now in **Design Phase**, leveraging the hardened v13.5 core.

- **📝 Multi-Node Consensus**: Deterministic replication (Raft) for Tier A core (Design Completed).
- **🚧 PQC Anchors**: Stub implementation ready for Dilithium injection.
- **✅ Ascon Edge Crypto**: Session protection and message AEAD.
- **🔄 v18.9 ATLAS App Alpha**: Unifying UI with distributed backbone and real data projections (In Progress).
- **🔮 Phase 5: Edge Expansion**: UI and Advisory agents deployed to Tier B/C nodes.

See [Fabric_Design_Notes.md](v13/docs/Fabric_Design_Notes.md) for details.

---

## 💰 Support the Project

**Patreon**: [www.patreon.com/QFSxATLAS](https://www.patreon.com/QFSxATLAS)

Your support helps us build the future of deterministic, quantum-resistant coordination.

---

## 📜 License

This project is licensed under the AGPL-3.0 License with additional terms for ATLAS components - see [LICENSE.ATLAS.md](LICENSE.ATLAS.md) for details.

---

<div align="center">

**QFS × ATLAS**: Deterministic • PoE-backed • Quantum-safe • Ready for the future 🚀

**QFS** = Truth Engine • **ATLAS** = Social Surface • **Together** = Fair Coordination

</div>
