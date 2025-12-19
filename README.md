# QFS × ATLAS: Quantum Financial System

> **Current Baseline:** Deterministic Governance + PoE-Backed Verification + Wallet Authentication  
> **Status:** Production-Ready - Structural Verifiability + MOCKQPC-First Architecture  
> **Test Coverage:** 26/26 tests passing, 13/13 invariants verified

---

## 📋 System Overview

**QFS × ATLAS** provides a **structurally verifiable infrastructure** for sovereign, deterministic governance with externalized Proof-of-Execution (PoE) and cost-efficient development through MOCKQPC-first architecture.

### Current Capabilities

The system baseline includes the following capabilities:

#### Governance & PoE

End-to-end governance with full verifiability: **create proposal → vote → finalize → execute → PoE → verify artifact → verify index → deterministic replay**.

- **PoE as External Assurance**: Each governance execution yields a cryptographically-signed PoE artifact, indexed in a hash-chained governance log for replay without trusting executors
- **Automated Validation**: Dedicated validation scripts catch structural drift; any anomaly exits non-zero
- **Verification Tools**: CLI tools ([`verify_poe.py`](v15/tools/verify_poe.py), [`replay_gov_cycle.py`](v15/tools/replay_gov_cycle.py)) make auditability first-class

#### Architecture Foundation

- **v14** remains the immutable constitution and regression oracle
- **Current baseline** adds features (UX, rewards, PoE, auth) without violating v14 invariants, verified via regression suites like `phase_v14_social_full`

### Wallet Authentication & Protected Features

The system provides end-to-end wallet authentication with scope-based access control:

#### Backend Authentication

- **NonceManager**: Ephemeral challenge generation (TTL, single-use)
- **WalletAuth**: EIP-191 signature verification (EVM/`eth_account`)
- **SessionManager**: Token-based session state (scopes, expiry)
- Unit tests ensure all flows are deterministic and secure

#### Frontend Integration

- React hook `useWalletAuth` + `WalletConnectButton` for EVM wallet login
- Session tokens are client-side validated; backend enforces TTL, scope, and nonce checks

#### Protected Features

- **Auth Middleware**: Scope-based route protection (`bounty:read`, `bounty:claim`)
- **Frontend Components**: `BountyList`, `MyBounties`, `BountyDashboard`
- **Integration Tests**: End-to-end protected routes flow verified
- **Browser Verification**: Ongoing validation of wallet connection and session persistence

#### Planned Enhancements

- Dual-proof wallet ↔ GitHub linking
- GitHub Contributions Indexer → deterministic rewards → PoE
- Contributor dashboard with transparent formulas and PoE links
- Additional hardening (Redis for sessions, rate limiting, CI gating, audit logs)

### Fiat, Crypto & Currency-Agnostic Design

#### Fiat (off-ledger, non-custodial)

- PSPs/banks handle actual funds; QFS logs deterministic facts only

#### Crypto (rails, not core)

- External crypto for optional on/off-ramps and settlement
- **No governance or economics execute on public chains**

#### Internal vs External Tokens

- **Internal tokens** (NOD, CHR, ATR, etc.) are for governance, reputation, and coordination—**not financial instruments**
- External tokens remain signals, not governance levers

### Agent Layer Evolution

#### Conceptual Position

The advisory/agent layer transitions from AEGIS to a **lean, open-source, evidence-first stack**.

#### Current State

- AEGIS is used for zero-trust node verification and multimodal tasks, but has low adoption and limited real-world proof

#### Target Frameworks

- **SuperAGI**: Primary candidate; OSS, multi-agent, multi-modal, active ecosystem
- **LangGraph (LangChain)**: Backup; strong orchestration, checkpointing, and complex workflow management

#### Architecture Principle: Agent Layer as Oracle

- Agents produce proposed scores/moderation outcomes
- **Adapter Layer** ensures outputs are deterministic, schema-validated, and hashed
- **QFS core retains** BigNum128 math, PoE, governance, and PQC; **agents never have authority**

#### Lean Migration Plan

1. **Start Small**: Run SuperAGI locally or on inexpensive VM against historical telemetry/moderation samples
2. **Compare Side-by-Side**: Benchmark AEGIS vs agent stack for speed, consistency, and quality
3. **Swap Incrementally**: Begin with low-risk flows (moderation scoring) while logging and verifying outputs
4. **Phase Out AEGIS**: Retire once PoE-backed logs confirm stability, retaining any unique PQC components if needed

#### Strategic Flexibility

- The plan remains flexible: other OSS frameworks may be evaluated as agent stacks evolve
- Migration is **evidence-first and cost-conscious**: spend only once metrics and PoE logs prove value

### Governance & PoE Fusion

In QFS × ATLAS, **Governance and PoE form a single, fused system** where every governance decision, state change, and critical off-chain commitment leaves a cryptographic PoE trail on the protocol timeline.

#### Roles, Permissions, and PoE Duties

**Protocol level**:

- Governance keys (council/multisig) control upgradeable modules, emergency switches, and parameter sets (fees, limits, risk knobs)
- Validators/oracles attest to state transitions (settlement finality, oracle updates), and each attestation becomes a PoE event

**Application level (ATLAS)**:

- Project/pool/vault owners have scoped admin rights; every privileged action emits a PoE event with actor, scope, and parameters
- User actions (account creation, granting access, delegating rights) also generate PoE records, so the full social/governance surface is replayable and auditable

#### PoE as the Governance Ledger

**Every governance step is a PoE object**:

- **Proposal**: PoE entry with a hash of the proposal payload, metadata (proposer, domain, time), and any referenced spec hashes
- **Voting**: PoE events for each vote, delegation, and quorum update, so vote evolution can be reconstructed exactly
- **Execution**: PoE entries that link proposal → concrete contract calls → resulting state changes, enabling deterministic replay

**Dispute and override chains**:

- Challenges (e.g., suspected malicious proposal or mis-scored decision) create PoE "challenge" objects referencing the original decision
- Resolutions (council rulings, automated slashing, rollbacks) are new PoE entries extending the same chain, forming an evidentiary thread

#### Concrete Wiring for QFS × ATLAS

**Governance contracts and registries**:

- A root `GovernanceRegistry` manages:
  - Roles and upgrade rights
  - Mappings from governance domain (DEX, treasury, identity, settlement, social) → specific module
- Each domain uses a shared PoE schema (e.g., `GovernanceEvent`, `ChallengeEvent`, `ResolutionEvent`) so explorers and auditors can reconstruct end-to-end governance history across modules

**Off-chain reconciliation via PoE anchors**:

- Patreon posts, spec docs, RFCs, legal memos, meeting minutes, and architecture diagrams stay off-chain, but:
  - Their content hashes are signed with governance keys and stored as PoE records, proving ordering and integrity without revealing the contents
  - Implementation changes happen only via proposals that reference these hashes, binding "what was agreed" to "what was executed"

### Builder & Contributor Surface

#### Immediate Opportunities

- Implement auth middleware, protect bounty/verification routes
- **GitHub ↔ wallet** dual-proof backend
- **Contributions Indexer** → Dev Rewards Treasury → PoE

#### Agent Layer Participation

- Run local agent POCs
- Design and test scoring functions, moderation edge cases, and deterministic adapters

#### Strategic Direction

- Deterministic execution and replayability
- PQC-by-default security
- Non-custodial, currency-agnostic external rails
- **Agents enhance insight but never replace verifiable governance**

---

## 🚀 System Highlights

- **Non-Custodial Wallet Auth:** EIP-191 signature verification, session management, scope enforcement
- **Protected API Routes:** Bounty and contribution endpoints secured with wallet authentication
- **Import Resolution:** Fixed package initialization and import paths for `v13.libs.economics`
- **Pydantic Schema Support:** Configured arbitrary types for custom economic types
- **Structural Verifiability:** PoE enables independent verification without trust
- **Autonomous Governance:** Self-amending protocol with deterministic proposal execution
- **100% Test Coverage:** All governance-critical and operational behaviors verified
- **Deterministic Replay:** Zero drift, bit-for-bit reproducibility

[📖 Read Full Documentation](./docs) | [🧪 Developer Guide](./DEV_GUIDE.md) | [🔍 Audit Instructions](./docs/HOW_TO_AUDIT_QFS_V15.md)

---

## 🔍 Verify Yourself

> **Trust, but Verify.** QFS provides the tools for anyone to audit system state independently.

### 1. Run the Pipeline

Verify the integrity of the codebase and deterministic build locally:

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

### 3. Check Regression Hashes

```bash
# Run v14 regression suite
python v13/tests/regression/phase_v14_social_full.py

# Verify hash matches canonical baseline
cat v14_regression_hash.txt
```

All tools guarantee deterministic outputs. Same inputs → same results, every time.

---

## 🛠️ Quick Start

See [DEV_GUIDE.md](./DEV_GUIDE.md) for complete cross-platform setup instructions (Windows, macOS, Linux).

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
- [Contributing Guidelines](./docs/CONTRIBUTING.md) - How to contribute
- [Bounties](./BOUNTIES.md) - Developer rewards and incentives
- [Security Notes](./docs/SECURITY_NOTES.md) - Trust assumptions and limitations

### Technical Documentation

- [Audit Guide](./docs/HOW_TO_AUDIT_QFS_V15.md) - How to verify the system
- [Repository Structure](./docs/REPO_STRUCTURE.md) - Codebase organization
- [NOD Operator Guide](./docs/NOD_OPERATOR_GUIDE.md) - Node operation
- [Testnet Deployment](./docs/FIRST_TESTNET_DEPLOYMENT.md) - Deployment instructions

### Architecture & Planning

- [Master Prompt v15.5](./docs/MASTER_PROMPT_v15.5.md) - Authoritative reference
- [Cost-Efficient Architecture](./docs/COST_EFFICIENT_ARCHITECTURE.md) - Cost optimization
- [BETA Deployment Plan](./docs/BETA_DEPLOYMENT_PLAN.md) - Deployment strategy
- [State of the Union v15.5](./docs/STATE_OF_THE_UNION_v15.5.md) - Architectural decisions

---

## 💰 Support the Project

**Patreon**: [www.patreon.com/QFSxATLAS](https://www.patreon.com/QFSxATLAS)

Your support helps us build the future of quantum-resistant autonomous finance.

---

## 📜 License

This project is licensed under the AGPL-3.0 License with additional terms for ATLAS components - see [LICENSE.ATLAS.md](LICENSE.ATLAS.md) for details.

---

**QFS × ATLAS**: Deterministic, PoE-backed, quantum-safe, and ready for the future. 🚀
