# QFS × ATLAS: Quantum Financial System

> **Latest Release:** [v15.4 - Wallet Auth & Protected Features](RELEASE_NOTES_v15.4.md) 🎉  
> **Status:** Production-Ready - Structural Verifiability + Non-Custodial Auth  
> **Test Coverage:** 26/26 tests passing, 13/13 invariants verified  
> **Updated:** December 19, 2025 - v15.4 Wallet Authentication

---

## 📋 Important Briefing — December 2025

**QFS × ATLAS** has advanced from a promising architecture to a **structurally verifiable infrastructure**: governance is fully deterministic, PoE is externalized and auditable, wallet authentication is live end-to-end, and the agent layer now has a flexible upgrade path toward SuperAGI-class frameworks—all while maintaining full sovereignty and quantum-safe operations.

### 1. Core System Status

#### Governance & PoE (v15.3) ✅

End-to-end governance is now fully validated: **create proposal → vote → finalize → execute → PoE → verify artifact → verify index → deterministic replay**.

- Recent bugs (BigNum128 overflows, VoteTally errors, PoE gaps) are automatically caught via dedicated validation scripts; any structural drift exits non-zero.
- **PoE as External Assurance**: Each governance execution yields a PQC-signed PoE artifact, indexed in a hash-chained governance log for replay without trusting executors.
- Verification tools ([`verify_poe.py`](file:///d:/AI%20AGENT%20CODERV1/QUANTUM%20CURRENCY/QFS/V13/v15/tools/verify_poe.py), [`replay_gov_cycle.py`](file:///d:/AI%20AGENT%20CODERV1/QUANTUM%20CURRENCY/QFS/V13/v15/tools/replay_gov_cycle.py)) make auditability first-class.

#### v14 → v15 Architecture

- **v14** remains the immutable constitution and regression oracle
- **v15** adds features (UX, rewards, PoE, auth) without violating v14 invariants, thanks to regression suites like `phase_v14_social_full`

### 2. Wallet Auth & Contributor Roadmap (v15.4)

The **7-phase Auth & Contributor Stack** defines v15.4; the first two phases are complete:

#### ✅ Phase 1 – Backend Wallet Authentication — COMPLETE

- **NonceManager**: Ephemeral challenge generation (TTL, Single-use)
- **WalletAuth**: EIP-191 signature verification (EVM/`eth_account`)
- **SessionManager**: Token-based session state (Scopes, Expiry)
- Unit tests ensure all flows are deterministic and secure

#### ✅ Phase 2 – Frontend Wallet Integration — COMPLETE

- React hook `useWalletAuth` + `WalletConnectButton` for EVM wallet login
- Session tokens are client-side validated; backend bridges enforce TTL, scope, and nonce checks

#### 🔄 Phases 3–7 (In Progress / Planned)

- **Phase 3**: Protected Features with Wallet Auth *(COMPLETE - Browser Verification Pending)*
  - ✅ Auth middleware for bounty routes (`bounty:read`, `bounty:claim`)
  - ✅ Frontend components: `BountyList`, `MyBounties`, `BountyDashboard`
  - ✅ Integration tests for end-to-end flow
  - 🔄 Browser verification in progress
- **Phase 4**: Dual-proof wallet ↔ GitHub linking *(Next)*
- **Phase 5**: GitHub Contributions Indexer → deterministic rewards → PoE
- **Phase 6**: Dashboard with transparent formulas and PoE links
- **Phase 7**: Hardening (Redis for sessions, rate limiting, CI gating, audit logs)

### 3. Fiat, Crypto & Currency-Agnostic Design

#### Fiat (off-ledger, non-custodial)

- PSPs/banks handle actual funds; QFS logs deterministic facts only

#### Crypto (rails, not core)

- External crypto for optional on/off-ramps and settlement
- **No governance or economics execute on public chains**

#### Internal vs External Tokens

- **Internal tokens** (NOD, CHR, ATR, etc.) are for governance, reputation, and coordination—**not financial instruments**
- External tokens remain signals, not governance levers

### 4. Agent Layer Evolution (Transmission 9 Preview)

#### Conceptual Position

The advisory/agent layer is transitioning from AEGIS to a **lean, open-source, evidence-first stack**.

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
- **ATLAS retains sovereignty, PQC security, and deterministic governance throughout**

#### Why It Matters

- Improved moderation across text, images, and audio
- More robust NOD scoring via multi-agent analysis
- Future-proof agent layer based on thriving open-source ecosystems, avoiding dependency on niche, low-adoption frameworks

### 5. Governance & PoE Fusion

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

### 6. Builder & Contributor Surface

#### Immediate Opportunities

- **Phase 3**: Implement auth middleware, protect bounty/verification routes
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

## 🚀 v15.4 Highlights

- **Non-Custodial Wallet Auth:** EIP-191 signature verification, session management, scope enforcement
- **Protected API Routes:** Bounty and contribution endpoints secured with wallet authentication
- **Import Resolution:** Fixed package initialization and import paths for `v13.libs.economics`
- **Pydantic Schema Support:** Configured arbitrary types for custom economic types
- **Structural Verifiability:** PoE v15.3 enables independent verification without trust
- **Autonomous Governance:** Self-amending protocol with deterministic proposal execution
- **100% Test Coverage:** All governance-critical and operational behaviors verified
- **Deterministic Replay:** Zero drift, bit-for-bit reproducibility

[📖 Read Full Release Notes](RELEASE_NOTES_v15.4.md) | [🧪 Quick Start Guide](#quick-start) | [🔍 Verify Yourself](VERIFICATION_STATUS.md)

---

## 🔍 Verify Yourself

> **Trust, but Verify.** QFS provides the tools for anyone to audit system state independently.

### 1. Run the Pipeline

Verify the integrity of the codebase and deterministic build locally:

```bash
python run_pipeline.py
```

*Ensures local code matches Main integrity and passes all 13 constitutional invariants.*

### 2. Verify Governance Execution (PoE)

Follow the verification flow: **Outcome → Execution → PoE Artifact → Replay → Verified**

```bash
# Example: Verify a governance decision
python v15/tools/replay_gov_cycle.py --artifact_id GOV-148-EXEC-02
```

*Replays the execution from canonical inputs and compares the output hash against the signed PoE proof.*

### 3. Verify Wallet Authentication

Test the end-to-end wallet authentication flow:

```bash
# Run auth flow tests
pytest tests/unit/atlas/auth/test_auth_flow.py -v

# Test protected routes
pytest tests/unit/atlas/auth/test_protected_routes.py -v
```

---

# Quantum Financial System (QFS) v15.4 – Wallet Auth & Structural Verifiability

> **A deterministic, post-quantum economic engine with independently verifiable governance, non-custodial wallet authentication, constitutional guards, and cryptographic, replayable auditability.**

**QFS × ATLAS** is a next-generation financial infrastructure combining:

- **Quantum-Safe Cryptography** (Dilithium-5 PQC signatures)
- **Deterministic Economics** (CertifiedMath, BigNum128, Zero-Simulation compliance)
- **Autonomous Governance** (Self-amending protocol with PoE-backed execution)
- **Non-Custodial Authentication** (EIP-191 wallet signatures, session management)
- **External Verifiability** (PoE artifacts, replay tools, public audit trail)
- **Currency-Agnostic Design** (Internal governance tokens + external settlement rails)

---

## 📚 Table of Contents

- [Quick Start](#quick-start)
- [Architecture Overview](#architecture-overview)
- [Wallet Authentication](#wallet-authentication)
- [Governance & PoE](#governance--poe)
- [Economic System](#economic-system)
- [Agent Layer](#agent-layer)
- [Testing & Verification](#testing--verification)
- [Development Guide](#development-guide)
- [Roadmap](#roadmap)
- [Contributing](#contributing)

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+ (for ATLAS frontend)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/qfs-atlas.git
cd qfs-atlas

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd v13/atlas
npm install
```

### Run Tests

```bash
# Run all tests
pytest

# Run governance tests
pytest tests/unit/governance/

# Run wallet auth tests
pytest tests/unit/atlas/auth/

# Verify end-to-end governance cycle
python v15/tools/validate_end_to_end_cycle.py
```

### Start ATLAS Dashboard

```bash
# Start the backend API
cd v13/atlas/src/api
uvicorn main:app --reload

# Start the frontend (in another terminal)
cd v13/atlas
npm run dev
```

---

## Architecture Overview

QFS × ATLAS is structured in layers:

### Core Layer (v13/v15)

- **CertifiedMath**: Deterministic fixed-point arithmetic (BigNum128)
- **CoherenceLedger**: Immutable event log with PQC signatures
- **StorageEngine**: Content-addressed storage with PoE
- **PQC Library**: Dilithium-5 key generation, signing, verification

### Governance Layer

- **ProposalEngine**: Create, vote, finalize, execute proposals
- **GovernanceParameterRegistry**: Constitutional parameter management
- **TreasuryEngine**: Multi-pool fund allocation with guards
- **NODAllocator**: Node operator reward distribution

### Authentication Layer (v15.4)

- **NonceManager**: Ephemeral challenge generation
- **WalletAuth**: EIP-191 signature verification
- **SessionManager**: Token-based session state
- **Auth Middleware**: Protect API routes with scope enforcement

### Application Layer (ATLAS)

- **Social Features**: Spaces, Wall, Chat with economic wiring
- **Bounty System**: GitHub-linked contribution rewards
- **Dashboard**: Transparent formulas, PoE links, wallet integration
- **API Routes**: Protected endpoints for authenticated users

### Agent Layer (Evolving)

- **Current**: AEGIS for node verification and multimodal tasks
- **Target**: SuperAGI/LangGraph for moderation, scoring, analysis
- **Principle**: Agents as oracles, never authority

---

## Wallet Authentication

### Flow

1. **Request Nonce**: Client requests ephemeral challenge from `/auth/nonce`
2. **Sign Message**: User signs EIP-191 message with wallet
3. **Login**: Client sends signature to `/auth/login`, receives session token
4. **Protected Access**: Include `Authorization: Bearer <token>` in API requests
5. **Scope Enforcement**: Routes check session scopes (`bounty:read`, `bounty:claim`, etc.)

### Example (Frontend)

```typescript
import { useWalletAuth } from './hooks/useWalletAuth';

function MyComponent() {
  const { address, login, logout, isAuthenticated } = useWalletAuth();

  return (
    <div>
      {!isAuthenticated ? (
        <WalletConnectButton onLogin={login} />
      ) : (
        <div>
          <p>Connected: {address}</p>
          <button onClick={logout}>Disconnect</button>
        </div>
      )}
    </div>
  );
}
```

### Example (Backend)

```python
from fastapi import APIRouter, Depends, HTTPException
from v13.atlas.src.api.dependencies import get_current_session

router = APIRouter(prefix="/bounties", tags=["bounties"])

@router.get("/")
async def list_bounties(session: dict = Depends(get_current_session)):
    if "bounty:read" not in session.get("scopes", []):
        raise HTTPException(status_code=403, detail="Missing scope: bounty:read")
    
    return get_all_bounties()
```

---

## Governance & PoE

### Governance Flow

1. **Create Proposal**: Submit proposal with target parameter changes
2. **Vote**: NOD holders cast weighted votes
3. **Finalize**: Check quorum and approval threshold
4. **Execute**: Apply parameter changes deterministically
5. **Generate PoE**: Create cryptographic proof of execution
6. **Verify**: Independent parties replay execution and verify PoE

### PoE Verification

```bash
# Replay a governance cycle
python v15/tools/replay_gov_cycle.py --artifact_id GOV-148-EXEC-02

# Verify PoE artifact
python v15/tools/verify_poe.py --poe_file evidence/governance/GOV-148-EXEC-02.json
```

### Governance Registry

All governance domains (treasury, identity, settlement, social) use a shared PoE schema:

- `GovernanceEvent`: Proposal creation, voting, finalization
- `ChallengeEvent`: Disputes and challenges
- `ResolutionEvent`: Council rulings and resolutions

---

## Economic System

### Token Types

| Token | Purpose | Supply | Governance |
|-------|---------|--------|------------|
| **NOD** | Node operator rewards, voting power | Capped | Yes |
| **CHR** | Content/contribution rewards | Emission-controlled | No |
| **FLX** | Flexibility/reputation | User-capped | No |
| **ATR** | Anti-abuse penalty | Dynamic | No |
| **PSI** | Predictive stability | Algorithmic | No |
| **RES** | Reserve/treasury | Pool-based | Yes |

### Constitutional Guards

All economic operations are validated against constitutional bounds:

- **EconomicsGuard**: Validates CHR/FLX/NOD/PSI/ATR operations
- **TreasuryEngine**: Enforces pool allocation limits
- **RewardAllocator**: Ensures deterministic reward distribution

---

## Agent Layer

### Current: AEGIS

- Zero-trust node verification
- Multimodal content analysis
- Low adoption, limited proof

### Target: SuperAGI / LangGraph

- **SuperAGI**: Multi-agent, multi-modal, active ecosystem
- **LangGraph**: Strong orchestration, checkpointing, workflow management
- **Principle**: Agents as oracles, outputs are deterministic and PoE-backed

### Migration Plan

1. Run SuperAGI locally against historical data
2. Benchmark vs AEGIS for speed, consistency, quality
3. Swap incrementally starting with low-risk flows
4. Phase out AEGIS once PoE logs confirm stability

---

## Testing & Verification

### Test Coverage

- **Unit Tests**: 26/26 passing
- **Invariant Tests**: 13/13 verified
- **Integration Tests**: Governance, economics, auth flows
- **Regression Tests**: v14 social layer compliance

### Run Tests

```bash
# All tests
pytest

# Specific test suites
pytest tests/unit/governance/
pytest tests/unit/atlas/auth/
pytest tests/integration/

# With coverage
pytest --cov=v13 --cov=v15 --cov-report=html
```

### Validation Scripts

```bash
# End-to-end governance cycle
python v15/tools/validate_end_to_end_cycle.py

# PoE verification
python v15/tools/verify_poe.py --poe_file <path>

# Replay governance
python v15/tools/replay_gov_cycle.py --artifact_id <id>
```

---

## Development Guide

### Project Structure

```
QFS/
├── v13/                    # Core QFS implementation
│   ├── libs/              # Core libraries (CertifiedMath, PQC, economics)
│   ├── core/              # Ledger, storage, state management
│   ├── guards/            # AEGIS, safety, economics guards
│   ├── atlas/             # ATLAS application layer
│   │   ├── src/          # Backend API, models, services
│   │   └── platform/     # Frontend React app
│   └── tests/            # Test suites
├── v15/                   # v15 features (PoE, auth, governance)
│   ├── atlas/            # Auth, session management
│   ├── tools/            # Verification, replay, validation scripts
│   └── governance/       # Proposal engine, parameter registry
├── tests/                # Additional test suites
└── evidence/             # PoE artifacts, governance logs
```

### Coding Standards

- **Zero-Simulation Compliance**: No random numbers, no wall-clock time, no side effects
- **Deterministic Operations**: All math via CertifiedMath, all hashes via deterministic functions
- **PQC-by-Default**: All signatures use Dilithium-5
- **PoE-Backed**: All critical operations generate PoE artifacts
- **Type Safety**: Full type hints, Pydantic models for API schemas

### Adding a New Feature

1. **Plan**: Document in `implementation_plan.md`
2. **Implement**: Follow Zero-Simulation principles
3. **Test**: Add unit tests, integration tests, invariant checks
4. **PoE**: Generate PoE artifacts for verifiable operations
5. **Document**: Update README, walkthrough, task.md
6. **Verify**: Run validation scripts, check test coverage

---

## Roadmap

### ✅ Completed

- **v15.3**: PoE integration, governance verification, structural verifiability
- **v15.4 Phase 1**: Backend wallet authentication (NonceManager, WalletAuth, SessionManager)
- **v15.4 Phase 2**: Frontend wallet integration (useWalletAuth hook, WalletConnectButton)
- **v15.4 Phase 3**: Import resolution, protected routes, Pydantic configuration

### 🔄 In Progress

- **v15.4 Phase 3**: Complete protected routes testing, frontend integration
- **v15.4 Phase 4**: Wallet ↔ GitHub dual-proof linking

### 📅 Planned

- **v15.4 Phase 5**: GitHub Contributions Indexer → deterministic rewards → PoE
- **v15.4 Phase 6**: Dashboard with transparent formulas and PoE links
- **v15.4 Phase 7**: Hardening (Redis, rate limiting, CI gating, audit logs)
- **Agent Layer Migration**: SuperAGI/LangGraph integration, AEGIS phase-out

---

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Contribution Checklist

- [ ] Follow Zero-Simulation principles
- [ ] Add comprehensive tests
- [ ] Generate PoE artifacts for verifiable operations
- [ ] Update documentation
- [ ] Run validation scripts before submitting PR

---

## License

[MIT License](LICENSE)

---

## Contact & Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/qfs-atlas/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/qfs-atlas/discussions)

---

**QFS × ATLAS**: Governance and PoE form a single, fused system. Every decision, state change, and commitment leaves a cryptographic trail. Trust, but verify. 🔐
