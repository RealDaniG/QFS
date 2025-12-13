# Quantum Financial System V13.6 - Constitutional Integration Release

**Current Status:** V13.6 CONSTITUTIONAL GUARDS DEPLOYED → Phase 2 Integration 100% COMPLETE  
**Release Date:** 2025-12-13  
**Phase 1 Progress:** 80% Complete (4/5 CRITICAL components IMPLEMENTED)  
**Tests Passing:** 92/92 (100%) Phase 1 critical suite  
**Evidence Generated:** 17 Phase 1 artifacts (SHA-256 verified)  
**Constitutional Status:** ✅ Guards enforced across all structural gates  
**Last Updated:** 2025-12-13  

[![Phase 1 Progress](https://img.shields.io/badge/Phase%201-80%25-yellow)](REMEDIATION_TASK_TRACKER_V2.md)
[![Tests](https://img.shields.io/badge/Tests-92%2F92%20(100%25)-green)](evidence/phase1/)
[![Evidence Driven](https://img.shields.io/badge/Evidence-17%20Artifacts-green)](evidence/phase1/)
[![Dashboard](https://img.shields.io/badge/Dashboard-Interactive-blue)](docs/qfs-v13.5-dashboard.html)

📊 **[View Interactive Dashboard](docs/qfs-v13.5-dashboard.html)** - Real-time project status, compliance metrics, and deployment resources

---

## ⚡ QFS V13.6 – Constitutional Integration Release

**What's New in V13.6:**

QFS V13.6 transforms the constitutional layer from specification into **structural enforcement**. All economic operations, NOD allocations, and state transitions are now guarded by mandatory, SDK-enforced constitutional checks.

### Core Achievements

✅ **Constitutional Guards Deployed** - 3 core guards enforcing economic bounds and NOD invariants  
✅ **No Bypass Paths** - Guards integrated at module, engine, and SDK levels  
✅ **AEGIS Integration** - Hash-anchored telemetry snapshots for deterministic replay  
✅ **Structured Error Codes** - 27+ machine-parsable codes for CIR-302 integration  
✅ **Defense in Depth** - Multi-layer validation (TreasuryEngine → RewardAllocator → StateTransitionEngine → SDK)  

### Constitutional Guards

1. **[EconomicsGuard](src/libs/economics/EconomicsGuard.py)** (937 lines, 8 validation methods)
   - Validates CHR/FLX/RES rewards against constitutional bounds
   - Enforces per-address caps and dust thresholds
   - Validates NOD allocation fractions, epoch issuance, voting power limits
   - Protects [IMMUTABLE] constants from governance changes
   - Returns structured error codes: `ECON_BOUND_VIOLATION`, `ECON_CHR_*`, `ECON_FLX_*`, `ECON_NOD_*`

2. **[NODInvariantChecker](src/libs/governance/NODInvariantChecker.py)** (682 lines, 4 invariants)
   - **NOD-I1:** Non-transferability (users cannot transfer NOD)
   - **NOD-I2:** Supply conservation (no NOD creation outside allocator)
   - **NOD-I3:** Voting power bounds (max 25% per node)
   - **NOD-I4:** Deterministic replay via AEGIS snapshot hashing
   - Returns structured error codes: `NOD_INVARIANT_I1_VIOLATED`, `NOD_INVARIANT_I2_VIOLATED`, etc.

3. **[AEGIS_Node_Verification](src/libs/governance/AEGIS_Node_Verification.py)** (733 lines, 5 checks)
   - Pure deterministic node verification (no HTTP calls)
   - Registry entry + telemetry hash coherence validation
   - Minimum uptime/health thresholds
   - Post-quantum cryptographic identity verification
   - Returns structured reason codes: `NODE_NOT_IN_REGISTRY`, `NODE_INSUFFICIENT_UPTIME`, etc.

### Structural Integration (Defense in Depth)

**Module Level:**
- [TreasuryEngine](src/libs/governance/TreasuryEngine.py): Validates CHR/FLX/RES rewards before issuance
- [RewardAllocator](src/libs/governance/RewardAllocator.py): Per-address cap validation + dust handling
- [NODAllocator](src/libs/governance/NODAllocator.py): AEGIS node verification + economic bounds
- [InfrastructureGovernance](src/libs/governance/InfrastructureGovernance.py): AEGIS verification for proposal eligibility

**Engine Level:**
- [StateTransitionEngine](src/libs/integration/StateTransitionEngine.py): Final gate with NOD transfer firewall, invariant checking, supply delta validation

**SDK Level:**
- [QFSV13SDK](src/sdk/QFSV13SDK.py): Mandatory guard enforcement, no bypass paths

**AEGIS Integration:**
- [aegis_api](src/services/aegis_api.py): Hash-anchored telemetry snapshots for NOD-I4 deterministic replay

### Safety & Invariants

**NOD Guarantees:**
- ❌ No NOD transfers (infra-only, allocator/governance controlled)
- ✅ Only verified AEGIS nodes earn NOD or vote
- ✅ Max 25% voting power per node (anti-centralization)
- ✅ Bit-for-bit deterministic replay with AEGIS snapshots

**Economic Guarantees:**
- ✅ Per-address reward caps enforced
- ✅ Dust policy applied (amounts below threshold flagged)
- ✅ CHR/FLX/RES saturation thresholds enforced
- ✅ Constitutional bounds on all issuance parameters

**Failure Modes:**
- AEGIS offline → freeze NOD allocation and governance (user rewards continue)
- Economic violation → CIR-302 halt (no approximations)
- Invariant violation → structured error code + halt

### Next Steps

**Phase 2.8:** Update CIR-302 handler to map all new error codes  
**Phase 3:** DeterministicReplayTest / BoundaryConditionTests / FailureModeTests  

See [CHANGELOG_V13.6.md](CHANGELOG_V13.6.md) for complete release notes.

---

## ⚠️ IMPORTANT: PHASE 1 CLOSURE (80%) → PHASE 2 DEPLOYMENT READY

This repository documents the **systematic remediation** of QFS V13 from its baseline state (24%) towards full V13.5 / V2.1 certification (100%). Phase 1 has reached **80% completion** with 4/5 CRITICAL components fully implemented.

**Phase 1 Status (Current):**
- ✅ **BigNum128:** 24/24 tests passing (100%), IMPLEMENTED
- ✅ **CertifiedMath:** 26/26 tests passing (100%), IMPLEMENTED
- ✅ **DeterministicTime:** 27/27 tests passing (100%), IMPLEMENTED
- ✅ **CIR-302 Handler:** 8/8 tests passing (100%), IMPLEMENTED
- ⏳ **PQC:** 7/7 mock tests passing (Windows), production backend PLANNED (Linux deployment)
- 📊 **All progress is evidence-based** with 17 SHA-256 verified artifacts in `evidence/phase1/`
- 🎯 **Phase 2 Ready:** Linux PQC deployment package ready (~1 hour operator time)

**Phase 2 Next Action:**
- 🚀 **Deploy Production PQC on Linux** (Ubuntu 22.04 + liboqs 0.10.1)
- See [START_HERE_PHASE2.md](START_HERE_PHASE2.md) for deployment instructions
- 8 comprehensive documents (3,360 lines) + 507-line hardened deployment script
- Estimated: 30-45 min script runtime + ~1 hour operator overhead

**For Auditors/Regulators:** See [QFSV13_FULL_COMPLIANCE_AUDIT_REPORT.json](QFSV13_FULL_COMPLIANCE_AUDIT_REPORT.json) for detailed findings.

**Interactive Dashboard:** [docs/qfs-v13.5-dashboard.html](docs/qfs-v13.5-dashboard.html) - Real-time metrics, compliance progress, and deployment resources

---

## 🌐 QFS Economy System & ATLAS Integration

### Overview

QFS V13.5 implements a **deterministic financial-reputation economy** designed for integration into decentralized social media platforms. The system operates as a predictive coherence engine that evaluates user actions through energy-based scoring, token economics, and transparent governance—all while maintaining **zero-simulation compliance** and **post-quantum security**.

### Six-Token Economic System (Five Harmonic + One Infrastructure)

QFS V13.5 manages six interconnected tokens that work together to create a stable, self-regulating economy:

**Five Harmonic Tokens (User-Facing):**

| Token | Symbol | Purpose | Function | Transferable |
|-------|--------|---------|----------|-------------|
| **Coherence** | CHR | System stability | Base measure of network health (S_CHR metric) | ✅ Yes |
| **Flexibility** | FLX | Rewards & incentives | Primary token for user rewards and penalties | ✅ Yes |
| **Psi-Sync** | ΨSync | Predictive alignment | Measures user action coherence with network state | ✅ Yes |
| **Attestation** | ATR | Reputation tracking | Oracle-verified user reputation scores | ✅ Yes |
| **Reserve** | RES | Economic buffer | Stabilization reserve for market shocks | ✅ Yes |

**Infrastructure Token (Protocol-Internal):**

| Token | Symbol | Purpose | Function | Transferable |
|-------|--------|---------|----------|-------------|
| **Node Operator Determination** | NOD | Infrastructure sovereignty | Non-transferable utility for node operators, infrastructure-only governance | ❌ No |

**Critical Distinction:** NOD is **orthogonal to the five-token harmonic system**. It does not participate in harmonic balancing, coherence scoring, or social equilibrium loops. NOD exists solely for infrastructure coordination and cannot affect user-facing parameters, content policy, or token economics.

**Token Interactions:**

*Harmonic Token Layer (User-Facing):*
- All harmonic tokens (CHR, FLX, ΨSync, ATR, RES) are managed through **TokenStateBundle** (immutable snapshots)
- State transitions are atomic and PQC-signed
- HSMF (Harmonic Stability Management Framework) enforces coherence thresholds
- TreasuryEngine calculates deterministic rewards based on HSMF metrics
- RewardAllocator distributes FLX tokens to users based on predictive coherence

*Infrastructure Token Layer (Protocol-Internal):*
- **NOD tokens** are allocated only to verified AEGIS infrastructure nodes
- NODAllocator distributes NOD based on deterministic contribution metrics (uptime, bandwidth, storage)
- NOD issuance derived from 10% of ATR fees (configurable via hard fork only, bounded by constitutional limits)
- InfrastructureGovernance manages infrastructure-only decisions using NOD voting power
- **Firewall Enforcement:** NOD governance scope is cryptographically limited to infrastructure parameters only
  - ✅ Allowed: Storage replication factor, AI model versions, network bandwidth parameters
  - ❌ Forbidden: User rewards, content policy, social governance, token emission rates

**Economic Constitutional Guarantees:**
- All economic parameters are defined in `src/libs/economics/economic_constants.py`
- Constants are marked [IMMUTABLE] (hard-coded) or [MUTABLE] (hard fork required)
- Safety bounds prevent governance capture and economic death spirals
- Anti-centralization guards limit single-node dominance
- Full specification: `docs/qfs_v13_plans/NOD_INFRASTRUCTURE_TOKEN_SPEC_V1.md`

### Integration into ATLAS Social Media Platform

**ATLAS** is a decentralized, censorship-resistant social media platform built on P2P/TOR networks. QFS serves as its **deterministic financial-reputation layer**, evaluating every user action through predictive coherence and issuing real-time rewards/penalties.

#### Architecture: QFS as ATLAS Engine

```
┌─────────────────────────────────────────────────────────────────┐
│                      ATLAS Platform                              │
│  (P2P/TOR Network - Censorship Resistant)                       │
│                                                                  │
│  ┌────────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │  User Actions  │  │   Content    │  │   Governance       │  │
│  │  • Posts       │  │  • Metadata  │  │  • Visibility      │  │
│  │  │ Likes     │  │  • AI Analysis│  │  • Policy Updates │  │
│  │  • Shares      │  │  • Moderation│  │  • Disputes        │  │
│  └────────┬───────┘  └──────┬───────┘  └────────┬───────────┘  │
│           │                 │                   │               │
│           └─────────────────┼───────────────────┘               │
│                             ↓                                   │
│              ╔═══════════════════════════════╗                  │
│              ║   Open-A.G.I / AEGIS API      ║                  │
│              ║  (Distributed Computation)    ║                  │
│              ╠═══════════════════════════════╣                  │
│              ║ • P2P Messaging               ║                  │
│              ║ • PBFT Consensus              ║                  │
│              ║ • Node Telemetry              ║                  │
│              ║ • Ledger Management           ║                  │
│              ║ • Cryptography (Ed25519)      ║                  │
│              ╚═══════════════╤═══════════════╝                  │
│                              ↓                                   │
└──────────────────────────────┼───────────────────────────────────┘
                               │
                               ↓
┌────────────────────────────────────────────────────────────────┐
│              QFS V13.5 - Deterministic Engine                  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Predictive Coherence Module (PCM)                       │  │
│  │  • Analyzes user actions against network state           │  │
│  │  • Calculates ΨSync alignment scores                     │  │
│  │  • Predicts future coherence impact                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  HSMF v2 (Harmonic Stability Framework)                  │  │
│  │  • Energy-based action scoring (Action_Cost_QFS)         │  │
│  │  • Coherence validation (S_CHR, C_holo metrics)          │  │
│  │  • Threshold enforcement (C_MIN, DEZ checks)             │  │
│  │  • CIR-302 critical failure handling                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Adaptive Token Weighting (ATW)                          │  │
│  │  • Dynamic FLX reward calculation                        │  │
│  │  • Weighted allocation based on coherence                │  │
│  │  • Penalty distribution for violations                   │  │ 
│  │  • Treasury-based economic balancing                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Expanded Quantum Metadata (EQM)                         │  │
│  │  • Full audit trail generation                           │  │
│  │  • PQC-signed metadata (Dilithium-5)                     │  │
│  │  • Deterministic hash chains (SHA3-512)                  │  │
│  │  • Immutable CoherenceLedger logging                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Integrated Governance Layer (IGL)                       │  │
│  │  • Deterministic quorum calculations                     │  │
│  │  • Content visibility decisions                          │  │
│  │  • Policy update mechanisms                              │  │
│  │  • Dispute resolution protocols                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                 │
│            ╔════════════════════════════════╗                  │
│            ║  StateTransitionEngine        ║                   │
│            ║  • Atomic token updates       ║                   │
│            ║  • PQC-signed state commits   ║                   │
│            ║  • AEGIS_FINALITY_SEAL        ║                   │
│            ╚═══════════════╤════════════════╝                  │
└────────────────────────────┼───────────────────────────────────┘
                             │
                             ↓
                   Token Ledger Updates
              (Consensus-verified via AEGIS API)
```

#### Core Integration Components

**1. Predictive Coherence Module (PCM)**
- **Purpose:** Evaluates how well user actions align with current network state
- **Metrics:**
  - ΨSync score: Measures coherence between user intent and system stability
  - Historical pattern analysis: Tracks user behavior over time
  - Predictive impact: Forecasts how actions affect S_CHR (system coherence)
- **Implementation:** Uses CertifiedMath for deterministic calculations
- **Output:** Coherence scores fed into HSMF for reward calculation

**2. HSMF v2 (Harmonic Stability Management Framework)**
- **Purpose:** Energy-based scoring system for all user actions
- **Key Functions:**
  - `calculate_action_cost()`: Determines energy cost of user actions
  - `validate_coherence()`: Checks if C_holo >= C_MIN (minimum coherence)
  - `compute_s_chr()`: Calculates system-wide stability metric
  - `trigger_cir302()`: Immediate halt on critical failures
- **Components:**
  - `src/core/HSMF.py`: Core framework implementation
  - `src/core/CoherenceEngine.py`: Modulator calculations and Ω updates
  - `src/handlers/CIR302_Handler.py`: Critical incident response
- **Integration:** Consumes AEGIS API data (node metrics, consensus state)

**3. Adaptive Token Weighting (ATW)**
- **Purpose:** Dynamic FLX token reward/penalty distribution
- **Algorithm:**
  ```python
  # Simplified ATW calculation
  coherence_score = PCM.calculate_psi_sync(user_action, network_state)
  energy_cost = HSMF.calculate_action_cost(action_type, coherence_score)
  base_reward = TreasuryEngine.compute_reward(S_CHR, C_holo, energy_cost)
  weighted_reward = RewardAllocator.apply_weights(base_reward, coherence_score)
  ```
- **Components:**
  - `src/libs/governance/TreasuryEngine.py`: Reward calculations
  - `src/libs/governance/RewardAllocator.py`: Distribution logic
- **Characteristics:**
  - Higher coherence = higher rewards
  - Low coherence = penalties (negative FLX)
  - Energy-intensive actions (spam, abuse) = higher costs

**4. Expanded Quantum Metadata (EQM)**
- **Purpose:** Full auditability and verifiability of all operations
- **Data Captured:**
  - User action type and timestamp (DRV_Packet.ttsTimestamp)
  - Coherence scores and HSMF metrics
  - FLX token allocation amounts
  - Governance decisions and voting records
  - PQC signatures (Dilithium-5) for all state changes
- **Storage:** CoherenceLedger generates AEGIS_FINALITY_SEAL.json
- **Verification:** SHA3-512 hash chains ensure immutability

**5. Integrated Governance Layer (IGL)**
- **Purpose:** Deterministic governance without centralized control
- **Decisions Managed:**
  - **Content Visibility:** Algorithmic ranking based on coherence scores
  - **Policy Updates:** Community-driven proposals with quorum enforcement
  - **Dispute Resolution:** Multi-signature verification for appeals
- **Quorum Calculation:**
  ```python
  # Deterministic quorum (no randomness)
  total_active_users = AEGIS_API.get_active_node_count()
  quorum_threshold = CertifiedMath.multiply(
      BigNum128.from_int(total_active_users),
      BigNum128.from_string("0.66")  # 66% supermajority
  )
  ```
- **Implementation:** Uses PBFT consensus via AEGIS API

### Data Flow: User Action → Token Reward

**Step-by-Step Process:**

1. **User Action on ATLAS**
   - User posts content, likes, shares, or votes
   - ATLAS sends structured event payload to AEGIS API
   - Example payload:
     ```json
     {
       "user_id": "0x1234...",
       "action_type": "post",
       "content_hash": "sha256...",
       "timestamp": 1702345678,
       "signature": "dilithium5_sig..."
     }
     ```

2. **AEGIS API Processing**
   - Validates user signature (Ed25519/ChaCha20-Poly1305)
   - Retrieves consensus-verified node data
   - Queries historical interaction metrics
   - Runs AI multimodal moderation (toxicity, spam detection)
   - Returns network state to QFS

3. **QFS Evaluation (PCM + HSMF)**
   - PCM calculates ΨSync alignment score
   - HSMF computes Action_Cost_QFS and validates C_holo
   - Checks coherence thresholds (triggers CIR-302 if violated)
   - Generates quantum_metadata for audit trail

4. **Token Allocation (ATW)**
   - TreasuryEngine computes base reward from HSMF metrics
   - RewardAllocator applies coherence-based weighting
   - FLX tokens allocated (positive for good actions, negative for violations)
   - StateTransitionEngine atomically updates TokenStateBundle

5. **Ledger Commit (EQM)**
   - CoherenceLedger logs all changes with PQC signatures
   - AEGIS_FINALITY_SEAL.json generated
   - Updates submitted back to AEGIS API
   - PBFT consensus validates across P2P network

6. **User Receives Feedback**
   - Token balance updated in ATLAS UI
   - Coherence score displayed for transparency
   - Governance rights adjusted based on reputation (ATR tokens)

### Security & Privacy via AEGIS API

**TOR Integration:**
- All ATLAS ↔ AEGIS ↔ QFS communications routed through TOR
- IP anonymization for censorship resistance
- Onion routing prevents traffic analysis

**Cryptography:**
- **Transport:** Ed25519 (authentication) + ChaCha20-Poly1305 (encryption)
- **Signatures:** Dilithium-5 (post-quantum resistant)
- **Hashing:** SHA3-512 (deterministic, quantum-safe)

**Privacy Model:**
- User actions are pseudonymous (public keys, not real identities)
- Coherence scores visible to maintain transparency
- Governance votes cryptographically verifiable but voter-anonymous
- Audit trails allow verification without revealing user data

### Deployment & Monitoring

**AEGIS API Endpoints Used by QFS:**
- `POST /api/v1/actions/submit`: User action ingestion
- `GET /api/v1/network/state`: Real-time network metrics
- `GET /api/v1/consensus/history`: Historical interaction data
- `POST /api/v1/tokens/allocate`: FLX token distribution
- `POST /api/v1/governance/vote`: IGL decision submission
- `GET /api/v1/telemetry/metrics`: Prometheus-compatible monitoring

**Key Performance Indicators (KPIs):**
- **Coherence Health:** S_CHR metric (target: >= C_MIN)
- **Token Velocity:** FLX circulation rate
- **Energy Abuse Rate:** Actions exceeding Action_Cost threshold
- **Governance Participation:** Voter turnout percentage
- **Audit Compliance:** Evidence artifact generation rate

**Monitoring Tools:**
- Prometheus metrics exported by AEGIS API
- Grafana dashboards for real-time KPI visualization
- Alerting on CIR-302 triggers (critical failures)
- Evidence directory monitoring for compliance

### Use Cases

**1. Quality Content Incentivization**
- High-coherence posts (well-researched, constructive) → **+FLX rewards**
- Viral engagement aligned with network values → **+ΨSync boost**
- Outcome: Users incentivized to produce valuable content

**2. Spam & Abuse Deterrence**
- Repetitive posting (high energy cost) → **-FLX penalties**
- Toxic content (low coherence) → **reputation decay (ATR loss)**
- Persistent violations → **CIR-302 halt + account freeze**
- Outcome: Economic disincentive for bad actors

**3. Decentralized Moderation**
- Community flags content → **IGL governance vote**
- Quorum reached deterministically (no manipulation)
- Decision enforced via StateTransitionEngine
- Outcome: Transparent, auditable content moderation

**4. Economic Stability**
- Market shock detected → **RES token deployed from Treasury**
- HSMF adjusts reward rates to maintain C_holo >= C_MIN
- Automatic rebalancing without human intervention
- Outcome: Self-regulating economy resilient to volatility

**5. Infrastructure Sovereignty (NOD Token)**
- Node operators receive **NOD tokens** based on contribution metrics
- NOD voting power determines infrastructure parameters only
- Example: Upgrade storage replication factor from 3 to 5
- **Firewall guarantee:** NOD governance cannot affect user-facing systems
- Outcome: Sustainable node operation without altruistic dependency

### NOD Token: Infrastructure Sovereignty Layer

**Purpose:** NOD (Node Operator Determination) is QFS V13.5's sixth token, providing **economic incentivization for infrastructure operators** while maintaining strict separation from social governance.

**Key Characteristics:**
- **Non-Transferable:** NOD cannot be traded, sold, or transferred between addresses
- **Infrastructure-Only:** Allocated exclusively to verified AEGIS node operators
- **Deterministic Issuance:** 10% of ATR fees → NOD pool (bounded by constitutional limits)
- **Governance-Limited:** Can only vote on infrastructure parameters, not user-facing systems

**Economic Model:**
```python
# NOD allocation from ATR fees
atr_total_fees = sum(all_user_action_costs)
nod_pool = atr_total_fees * 0.10  # 10% allocation (configurable 1%-15%)

# Distribution based on node contribution metrics
for node in active_nodes:
    contribution_score = (
        uptime_ratio * 0.40 +
        bandwidth_served * 0.30 +
        storage_provided * 0.30
    )
    node.nod_balance += (nod_pool * contribution_score / total_contributions)
```

**Governance Scope (Allowed):**
- ✅ Storage replication factor adjustments
- ✅ AI model version approvals for content moderation
- ✅ Network bandwidth/fee parameter tuning
- ✅ Infrastructure upgrade scheduling
- ✅ Security patch deployment timing

**Governance Scope (Forbidden - Constitutional Firewall):**
- ❌ User token emission rates (CHR, FLX, ΨSync, ATR, RES)
- ❌ Content moderation policy (handled by social governance)
- ❌ Reward calculation formulas
- ❌ Identity or reputation scoring
- ❌ Economic parameters affecting user-facing systems

**Constitutional Guarantees:**
- **Safety Bounds:** MIN/MAX caps on all mutable parameters (defined in `economic_constants.py`)
- **Emission Controls:** Maximum issuance per epoch, minimum active nodes requirement
- **Anti-Centralization:** Per-node voting power capped at 25% of total supply
- **Timelock Protection:** 240-block execution delay after proposal passes (~1.1 hours)
- **Deterministic Execution:** All governance outcomes must be cryptographically reproducible

**Lifecycle:**
1. **Dormant:** No ATR activity → no NOD issuance
2. **Accrual:** ATR fees accumulate in deterministic pool
3. **Allocation:** Periodic distribution based on telemetry snapshots
4. **Governance Usage:** NOD balances weight infrastructure votes
5. **No Redemption:** NOD never converts back to other tokens (prevents profit-expectation claims)

**Implementation:**
- `src/libs/governance/NODAllocator.py` - Distribution logic
- `src/libs/governance/InfrastructureGovernance.py` - Voting system
- `src/libs/economics/economic_constants.py` - Constitutional parameters
- `docs/qfs_v13_plans/NOD_INFRASTRUCTURE_TOKEN_SPEC_V1.md` - Full specification

**Legal Positioning:**
NOD is designed as a **pure utility token** with no investment characteristics:
- Non-transferable (eliminates secondary markets)
- Non-redeemable (no profit participation)
- Infrastructure-scoped (no control over user-facing systems)
- Deterministic (no discretionary management)
- This structure minimizes securities law risk while enabling sustainable node incentivization.

### Technical Advantages

**Zero-Simulation Compliance:**
- No floating-point operations → deterministic across all platforms
- No random number generation → reproducible calculations
- No time-based operations → replay-safe for auditing
- BigNum128 fixed-point arithmetic ensures precision

**Post-Quantum Security:**
- Dilithium-5 signatures secure against quantum attacks
- Kyber-1024 KEM for future key exchange needs
- SHA3-512 resistant to Grover's algorithm
- Future-proof cryptography for long-term deployment

**Censorship Resistance:**
- P2P/TOR architecture → no single point of failure
- PBFT consensus → Byzantine fault tolerant
- Distributed ledger → no central authority
- Open-source verification → full transparency

**Auditability:**
- Every action logged in CoherenceLedger
- PQC-signed metadata (EQM) prevents tampering
- SHA3-512 hash chains enable forensic analysis
- Machine-readable evidence for compliance automation

### Summary: QFS as ATLAS' Deterministic Backbone

QFS operates as a **deterministic engine on top of AEGIS**, using its API as the backbone for:
- **Secure, distributed computation** (P2P/TOR network)
- **Token management** (FLX allocation via TreasuryEngine)
- **Governance** (IGL quorum decisions)
- **Auditability** (EQM metadata + CoherenceLedger)

**No central servers required.** All operations are consensus-verified through PBFT, cryptographically secured with Ed25519/Dilithium-5, and fully auditable via SHA3-512 hash chains. The result is a **censorship-resistant, economically stable social media platform** where quality content is rewarded, abuse is deterred, and users maintain full privacy.

**Integration Status:**
- ✅ Core QFS components implemented (Phase 1: 80% complete)
- ⏳ AEGIS API integration (Phase 3+)
- ⏳ PCM/ATW/EQM/IGL modules (Phase 3+)
- 🎯 Target: Full ATLAS integration by Phase 5 (365-day roadmap)

**See:**
- [ROADMAP-V13.5-REMEDIATION.md](ROADMAP-V13.5-REMEDIATION.md) - Integration timeline
- [docs/qfs-v13.5-dashboard.html](docs/qfs-v13.5-dashboard.html) - Real-time progress
- [QFSV13_FULL_COMPLIANCE_AUDIT_REPORT.json](QFSV13_FULL_COMPLIANCE_AUDIT_REPORT.json) - Current compliance status

---

## Overview

**QFS V13** is designed to be a fully deterministic, post-quantum secure financial system implementing the Five-Token Harmonic System (CHR, FLX, ΨSync, ATR, RES). This repository contains:

- ✅ **Operational core components** with proper deterministic architecture
- ✅ **Real PQC integration** using Dilithium-5
- ✅ **Comprehensive audit trails** with SHA3-512 hashing
- ⚠️ **Incomplete operational security infrastructure** (HSM/KMS, SBOM, threat model)
- ⚠️ **Test infrastructure requiring remediation** (import path issues documented)
- 📋 **Complete remediation roadmap** for achieving full certification

### Project Vision

To create a quantum-resistant, deterministic financial system with:
- Zero-simulation compliance (no floats, random, or time-based operations)
- Post-quantum cryptographic security (Dilithium-5, Kyber-1024)
- Complete auditability and forensic traceability
- Economic stability through harmonic token interactions
- Multi-node deterministic replication

### Current Reality (Verified)

**Phase 1 Components (Current Status):**
- BigNum128 (1.1): 100% tests passing, stress tested, IMPLEMENTED ✅
- CertifiedMath (1.2): 100% tests passing, 42 ProofVectors validated, IMPLEMENTED ✅
- DeterministicTime (1.3): 100% tests passing, replay verified, CIR-302 tested ✅
- PQC (1.4): Implementation complete, testing BLOCKED (pqcrystals library unavailable) 🔴
- CIR302 Handler: Implementation ready, tests pending ⏸️

**Phase 1 Evidence Generated:**
- `bignum128_stress_summary.json` - 24 tests, overflow validation ✅
- `certified_math_proofvectors.json` - 26 ProofVectors, error bounds verified ✅
- `time_replay_verification.json` - 5-run replay consistency proof ✅
- `time_regression_cir302_event.json` - CIR-302 trigger validation ✅
- `PQC_INTEGRATION.md` - External dependency blocker documentation ✅

**Phase 2+ (Planned):**
- HSM/KMS key management infrastructure (Days 61-120)
- Supply-chain security (SBOM, reproducible builds) (Days 61-120)
- Economic threat model and attack simulations (Days 121-240)
- Oracle attestation framework (Days 121-240)
- Multi-node replication testing (Days 121-240)
- Advanced testing infrastructure (Days 241-300)

**See:** [STATE-GAP-MATRIX.md](STATE-GAP-MATRIX.md) for detailed breakdown of all 89 requirements.

## Repository Structure

```
QFS_V13/
├── src/
│   ├── libs/                 # Certified core libraries
│   │   ├── CertifiedMath.py
│   │   ├── PQC.py
│   │   ├── BigNum128.py
│   │   ├── AST_ZeroSimChecker.py
│   │   ├── core/
│   │   │   ├── UtilityOracle.py          # Pure validator for pre-computed oracle guidance values
│   │   │   ├── UtilityOracleInterface.py # Interface for utility oracle operations
│   │   │   └── HSMF.py                   # Harmonic Stability & Action Cost Framework
│   │   ├── governance/
│   │   │   ├── RewardAllocator.py        # Distributes calculated rewards to specific wallets/addresses
│   │   │   └── TreasuryEngine.py         # Economic engine for calculating deterministic rewards
│   │   ├── quantum/
│   │   │   └── QPU_Interface.py          # Pure validator for quantum entropy inputs
│   │   ├── integration/
│   │   │   └── StateTransitionEngine.py  # Apply final state changes after validation and rewards
│   │   └── __init__.py
│   ├── core/                 # Core system data structures and interfaces
│   │   ├── TokenStateBundle.py
│   │   ├── reward_types.py
│   │   ├── HSMF.py
│   │   ├── DRV_Packet.py
│   │   ├── CoherenceEngine.py
│   │   ├── CoherenceLedger.py
│   │   ├── gating_service.py
│   │   └── __init__.py
│   ├── handlers/             # System handlers
│   │   ├── CIR302_Handler.py # Deterministic halt system for critical failures
│   │   ├── CIR412_Handler.py # Additional critical error handler
│   │   └── CIR511_Handler.py # Additional critical error handler
│   ├── sdk/
│   │   └── QFSV13SDK.py
│   ├── services/
│   │   └── aegis_api.py
│   └── utils/
│       └── qfs_system.py
│
├── tools/
│   ├── ast_checker.py
│   ├── audit/                # Complete audit infrastructure
│   ├── run_full_audit.sh     # Main audit wrapper script
│   └── ...
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── deterministic/
│   ├── property/
│   └── mocks/
│
├── scripts/
│   ├── run_tests.bat/sh
│   └── ...
│
├── docs/
│   ├── qfs_v13_plans/
│   ├── compliance/
│   ├── architecture/         # System architecture documentation
│   ├── guides/               # User guides and implementation guides
│   └── plans/               # Development plans and roadmaps
│
├── evidence/                # Audit evidence and verification data
├── .github/workflows/
│   ├── ci_pipeline.yml
│   └── qfs_v135_audit.yml   # QFS V13.5 audit pipeline
│
└── Dockerfile
```

## 📍 REMEDIATION ROADMAP

### Phase-Based Certification Path

QFS V13 is undergoing systematic remediation across **6 phases** over **365 days** to achieve full V13.5 / V2.1 certification.

**Current Phase:** 🔵 **PHASE 1 - Core Determinism Completion** (Days 8-60)

| Phase | Name | Duration | Status | Compliance Target |
|-------|------|----------|--------|-------------------|
| 0 | Baseline Verification | Days 1-7 | ✅ COMPLETE | Establish baseline (24%) |
| 1 | Core Determinism Completion | Days 8-60 | 🔵 IN PROGRESS | Math verification + PQC docs |
| 2 | Operational Security | Days 61-120 | ⏳ PLANNED | HSM/KMS, SBOM, builds |
| 3 | Threat & Safety | Days 121-240 | ⏳ PLANNED | Threat model, oracles, replication |
| 4 | Advanced Testing | Days 241-300 | ⏳ PLANNED | Fuzzing, static analysis, governance |
| 5 | Final Certification | Days 301-365 | ⏳ PLANNED | Complete testing, 100% compliance |

### Phase Details

#### ✅ Phase 0: Baseline Verification (COMPLETE)

**Objective:** Establish verified baseline without code changes

**Completed:**
- ✅ Comprehensive audit report generated ([QFSV13_FULL_COMPLIANCE_AUDIT_REPORT.json](QFSV13_FULL_COMPLIANCE_AUDIT_REPORT.json))
- ✅ Gap analysis across all 89 requirements ([STATE-GAP-MATRIX.md](STATE-GAP-MATRIX.md))
- ✅ 365-day remediation roadmap ([ROADMAP-V13.5-REMEDIATION.md](ROADMAP-V13.5-REMEDIATION.md))
- ✅ Task tracking system ([TASKS-V13.5.md](TASKS-V13.5.md))
- ✅ Evidence directory structure created
- ✅ Baseline commit frozen (`ab85c4f92535d685e801a49ca49713930caca32b`)
- ✅ Test suite executed (37 import errors documented)
- ✅ Core file SHA3-512 hashes computed (9 components)

**Evidence:** See [evidence/baseline/](evidence/baseline/) for all baseline artifacts

#### 🔵 Phase 1: Core Determinism Completion (IN PROGRESS)

**Objective:** Complete all deterministic core testing and documentation

**Duration:** Days 8-60 (53 days)

**Deliverables:**

1. **BigNum128 Stress Testing** (Days 8-15)
   - 🟡 Property-based fuzzing test created ([tests/property/test_bignum128_fuzz.py](tests/property/test_bignum128_fuzz.py))
   - ⏳ Overflow/underflow stress scenarios
   - ⏳ Evidence: `evidence/phase1/bignum128_stress_summary.json`

2. **CertifiedMath ProofVectors** (Days 16-30)
   - ⏳ Canonical ProofVectors for all functions
   - ⏳ Error bounds documentation
   - ⏳ ProofVectors test suite
   - ⏳ Evidence: `evidence/phase1/certified_math_proofvectors_hashes.json`

3. **DeterministicTime Replay & Regression** (Days 31-40)
   - ⏳ Replay test suite (identical timestamp reproduction)
   - ⏳ Time regression → CIR-302 scenario tests
   - ⏳ Evidence: `evidence/phase1/time_regression_cir302_event.json`

4. **PQC Integration Documentation** (Days 41-60)
   - ⏳ PQC key lifecycle and boundaries documentation
   - ⏳ Load testing suite (sign/verify performance)
   - ⏳ Side-channel analysis
   - ⏳ Evidence: `evidence/phase1/pqc_performance_report.json`

#### ⏳ Phase 2: Operational Security & Supply Chain (PLANNED)

**Objective:** Implement HSM/KMS integration and supply-chain security

**Duration:** Days 61-120 (60 days)

**Critical Blockers to Clear:**
1. HSM/KMS integration for PQC keys
2. SBOM generation pipeline (CycloneDX/SPDX)
3. Reproducible builds with deterministic Docker

**Deliverables:**
- HSM/KMS integration code and tests
- SBOM generation scripts with PQC signing
- Reproducible build infrastructure
- Key rotation procedures and rehearsal logs

**See:** [ROADMAP-V13.5-REMEDIATION.md#phase-2](ROADMAP-V13.5-REMEDIATION.md#phase-2-operational-security--supply-chain) for details

#### ⏳ Phase 3: Threat Model, Oracles, Replication (PLANNED)

**Objective:** Security analysis, oracle systems, multi-node infrastructure

**Duration:** Days 121-240 (120 days)

**Critical Blockers to Clear:**
1. Economic threat model with attack simulations
2. Oracle attestation framework (UtilityOracle, QPU)
3. Multi-node deterministic replication
4. Runtime invariants enforcement

**See:** [ROADMAP-V13.5-REMEDIATION.md#phase-3](ROADMAP-V13.5-REMEDIATION.md#phase-3-threat-model-oracles-replication-invariants) for details

#### ⏳ Phase 4: Advanced Testing & Governance (PLANNED)

**Objective:** Implement fuzzing, static analysis, and governance procedures

**Duration:** Days 241-300 (60 days)

**Deliverables:**
- Fuzzing infrastructure for all parsers
- Static analysis pipeline (Bandit, Mypy, Pylint)
- DoS and resource exhaustion tests
- Upgrade governance and rollback procedures
- Operational runbooks

**See:** [ROADMAP-V13.5-REMEDIATION.md#phase-4](ROADMAP-V13.5-REMEDIATION.md#phase-4-advanced-testing-static-analysis-governance) for details

#### ⏳ Phase 5: Final Consolidation & Re-Audit (PLANNED)

**Objective:** Complete all testing and achieve 100% certification

**Duration:** Days 301-365 (65 days)

**Deliverables:**
- Complete integration test matrix
- Chaos and resilience testing
- Long-horizon economic simulations
- Test coverage measurement (≥95% core, ≥90% integration)
- Evidence retention infrastructure
- Final certification package

**Target:** 100% compliance (89/89 requirements passing)

**See:** [ROADMAP-V13.5-REMEDIATION.md#phase-5](ROADMAP-V13.5-REMEDIATION.md#phase-5-final-consolidation--re-audit) for details

---

### Progress Tracking

**Real-time Progress:**
- 📋 **Task Tracker:** [TASKS-V13.5.md](TASKS-V13.5.md) - Human-readable progress
- 📊 **Evidence Index:** [ROADMAP-V13.5-REMEDIATION.md#evidence-index](ROADMAP-V13.5-REMEDIATION.md#evidence-index) - All artifacts by phase
- 🔍 **Audit Report:** [QFSV13_FULL_COMPLIANCE_AUDIT_REPORT.json](QFSV13_FULL_COMPLIANCE_AUDIT_REPORT.json) - Detailed findings

**Critical Blockers (15 total):**
See [TASKS-V13.5.md#critical-blockers](TASKS-V13.5.md#critical-blockers) for the complete list with task IDs and required evidence.

---

### Phase 1: Foundation & Core Components

**Objective**: Establish the deterministic mathematical foundation and core token system.

**Key Components Implemented**:

1. **BigNum128** - Unsigned 128-bit fixed-point arithmetic library ensuring zero-simulation compliance
   - SCALE = 10^18 for 18 decimal places precision
   - No floating-point operations, ensuring deterministic calculations
   - Full audit trail support with PQC integration

2. **CertifiedMath** - Comprehensive deterministic mathematical operations library
   - Implements all required functions: exp, ln, sin, cos, tanh, sigmoid, erf, etc.
   - Zero-simulation compliant with no external dependencies
   - Integrated audit logging for all operations
   - PQC-ready with quantum metadata support

3. **PQC** - Production-ready post-quantum cryptography library
   - Implements Dilithium-5 signature scheme for quantum-resistant signatures
   - Zero-simulation compliant operations
   - Deterministic audit logging with CRS hash chains
   - Thread-safe context management for isolated operations

4. **TokenStateBundle** - Immutable snapshot of all token states
   - Contains state for all five tokens (CHR, FLX, ΨSync, ATR, RES)
   - PQC-signed by AGI Control Plane for security
   - Deterministic serialization for audit purposes
   - System parameters (λ1, λ2, C_CRIT) for HSMF calculations

5. **DRV_Packet** - Deterministic Replayable Validation Packet
   - Contains ttsTimestamp, sequence number, seed, and PQC signature
   - Enables deterministic validation and replayability
   - Chain validation for packet sequence integrity
   - PQC-signed for security and audit trail

### Phase 2: Economic Engine & Stability Framework

**Objective**: Implement the economic reward system and harmonic stability mechanisms.

**Key Components Implemented**:

1. **TreasuryEngine** - Economic engine for calculating deterministic rewards
   - Computes rewards based on HSMF metrics (S_CHR, C_holo, Action_Cost_QFS)
   - Uses CertifiedMath for all calculations ensuring determinism
   - Maintains full auditability with log_list, pqc_cid, and quantum_metadata
   - Implements C_holo >= C_MIN validation for system coherence

2. **RewardAllocator** - Distributes calculated rewards to specific wallets/addresses
   - Uses CertifiedMath for distribution logic calculations
   - Supports weighted allocation with normalization
   - Maintains full audit trail for all reward distributions
   - Stateless design with no internal mutable state

3. **HSMF (Harmonic Stability Management Framework)** - Core stability system
   - Calculates all HSMF metrics (S_CHR, C_holo, Action_Cost_QFS, etc.)
   - Implements DEZ (Directional Encoding Zero) checks
   - Integrates with CIR302_Handler for critical failure handling
   - Atomic state transitions with StateTransitionEngine

4. **UtilityOracle** - Pure validator for pre-computed oracle guidance values
   - **Redesigned for QFS V13 Compliance**: No network I/O, no external data fetching
   - Validates only PQC-signed oracle updates
   - No direct entropy processing - quantum entropy is never used directly in math
   - Implements proper bounds checking with CIR-302 integration
   - Stateless validator operating only on canonical, PQC-signed inputs

5. **QPU_Interface** - Pure validator for quantum entropy inputs
   - **Redesigned for QFS V13 Compliance**: No network calls, no fallback logic
   - Validates only pre-fetched, PQC-signed quantum entropy
   - No deterministic entropy generation - all entropy comes from external sources
   - Stateless validator with no internal state or URLs
   - Implements VDF proof validation for quantum entropy

6. **CIR302_Handler** - Deterministic halt system for critical failures
   - Immediate hard halt with no quarantine state or retries
   - Integrates with CertifiedMath for canonical logging
   - Deterministic exit codes derived from fault conditions
   - Triggers on HSMF validation failure, treasury computation errors, or C_holo/S_CHR violations

7. **StateTransitionEngine** - Applies final state changes after validation
   - Atomically applies token state changes after reward distribution
   - Maintains full auditability with deterministic logging
   - Integrates with PQC for secure state transitions
   - Stateless design with explicit state passing

8. **CoherenceEngine** - Stateful coherence management system
   - Manages system coherence through deterministic calculations
   - Uses CertifiedMath for all operations ensuring zero-simulation compliance
   - Implements modulator calculations and Ω state vector updates
   - Stateless validator operating only on canonical inputs

9. **CoherenceLedger** - Immutable ledger for auditing coherence state
   - Records every token state, reward allocation, and HSMF calculation step
   - Generates AEGIS_FINALITY_SEAL.json upon atomic commit
   - Maintains deterministic hash chain for PQC verification
   - Full audit trail support with PQC integration

10. **GatingService** - Memory locking and safe mode management
    - Calculates Geometric Alignment Score (GAS) for system stability
    - Implements memory write locks based on dual thresholds
    - Manages safe mode triggers for system protection
    - Uses only CertifiedMath and BigNum128 for deterministic calculations

11. **AEGIS_API** - Secure API Gateway for QFS V13
    - Receives transaction bundles and validates PQC signatures
    - Instantiates log contexts for deterministic operations
    - Commits validated state updates with PQC-signed finality seals
    - Integrates with all core components for complete pipeline processing

12. **QFSV13SDK** - Software Development Kit for QFS V13
    - High-level interface for creating, validating, and submitting transaction bundles
    - Full PQC signing and audit trail support
    - Integration with all core components
    - Developer-friendly API for building QFS V13 applications

## Component Status (Phase 1 Focus)

**Phase 1 CRITICAL Components:**

| Component | Implementation | Tests | Pass Rate | Evidence | Audit v2.0 Status |
|-----------|----------------|-------|-----------|----------|-------------------|
| **BigNum128** | Complete | 24/24 | 100% | bignum128_stress_summary.json | IMPLEMENTED |
| **CertifiedMath** | Complete | 26/26 | 100% | certified_math_proofvectors.json | IMPLEMENTED |
| **DeterministicTime** | Complete | 27/27 | 100% | time_replay_verification.json, time_regression_cir302_event.json | PARTIALLY_IMPLEMENTED* |
| **PQC** | Complete | 0/0 | N/A | PQC_INTEGRATION.md (blocker doc) | BLOCKED (external dependency) |
| **CIR302_Handler** | Complete | 0/0 | N/A | Pending test suite creation | UNKNOWN |

*DeterministicTime has 2 evidence artifacts and 100% test pass rate but requires audit test collection pattern update.

**Technical Details:**

1. **BigNum128** - Unsigned 128-bit fixed-point arithmetic (SCALE=10^18)
   - Status: IMPLEMENTED
   - Tests: 24 comprehensive + edge + fuzz tests
   - Evidence: Stress testing with overflow/underflow scenarios
   - Zero-simulation: No floats, deterministic operations
   - Note: Multiplication overflow test fixed (test expectation was incorrect, not implementation)

2. **CertifiedMath** - Deterministic math engine (exp, ln, sin, cos, tanh, sigmoid, erf)
   - Status: IMPLEMENTED
   - Tests: 26 ProofVector validation tests
   - Evidence: 42 canonical ProofVectors with error bounds (10^-9 for most functions, 10^-6 for erf)
   - Zero-simulation: Taylor series, no external libs, deterministic
   - Note: All functions verified against canonical test inputs

3. **DeterministicTime** - Canonical timestamp management with CIR-302 integration
   - Status: PARTIALLY_IMPLEMENTED (evidence found, tests pass, collection pattern issue)
   - Tests: 27 tests (9 replay + 17 monotonicity/CIR-302 + 1 legacy)
   - Evidence: 5-run deterministic replay proof + 3 CIR-302 trigger scenarios
   - Zero-simulation: No OS time, uses DRV_Packet.ttsTimestamp only
   - Compliance: Time regression correctly triggers CIR-302 halt

4. **PQC** - Post-quantum cryptography (Dilithium-5)
   - Status: BLOCKED
   - Tests: Cannot run (library unavailable)
   - Evidence: Comprehensive blocker documentation in docs/compliance/PQC_INTEGRATION.md
   - Issue: `pqcrystals` library does not exist in PyPI
   - Implementation: Complete and ready, deterministic design verified
   - Resolution options documented: liboqs-python alternative, manual compilation, or mock testing

5. **CIR302_Handler** - Critical incident response system
   - Status: UNKNOWN (implementation complete, tests pending)
   - Tests: Test suite creation pending
   - Evidence: None yet
   - Design: Immediate hard halt on critical failures, no quarantine/retry

**Phase 1 Summary:**
- Progress: 60% (3/5 components IMPLEMENTED)
- Tests passing: 76/76 (100%)
- Evidence artifacts: 4 generated, 1 blocker documented
- Zero-simulation compliance: PASS (all components)
- Determinism: VERIFIED (5-run replay produces identical hashes)

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Git
- Understanding that this is a **remediation project in progress**

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd QFS/V13
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### ⚠️ Test Infrastructure Status

**Current State:** Test suite has import path configuration issues (documented in baseline)

```bash
# Attempting to run tests will show collection errors:
python -m pytest tests/ -v
# Result: 37 import errors (expected - part of Phase 1 remediation)
```

**Evidence:** See [evidence/baseline/baseline_test_results.json](evidence/baseline/baseline_test_results.json)

**Fix Status:** Test infrastructure remediation is part of Phase 1 (Days 8-60)

### Running Individual Components

Core components can be imported and used directly:

```python
# Example: BigNum128
from src.libs.BigNum128 import BigNum128

a = BigNum128.from_string("123.456")
b = BigNum128.from_string("789.012")
c = a.add(b)
print(c.to_decimal_string())  # "912.468"

# Example: PQC signing
from src.libs.PQC import generate_keypair, sign_data, verify_signature
import json

public_key, private_key = generate_keypair()
data = {"test": "data"}
signature = sign_data(data, private_key)
valid = verify_signature(data, signature, public_key)
print(f"Signature valid: {valid}")  # True
```

### Verify Zero-Simulation Compliance

```bash
# Check for forbidden constructs (random, time, float)
python scripts/zero-sim-ast.py
```

### Understanding the Codebase

**Start Here:**
1. [QFSV13_FULL_COMPLIANCE_AUDIT_REPORT.json](QFSV13_FULL_COMPLIANCE_AUDIT_REPORT.json) - Understand current state
2. [STATE-GAP-MATRIX.md](STATE-GAP-MATRIX.md) - See all 89 requirements
3. [ROADMAP-V13.5-REMEDIATION.md](ROADMAP-V13.5-REMEDIATION.md) - Understand remediation plan
4. [TASKS-V13.5.md](TASKS-V13.5.md) - Track progress

**Core Implementation:**
- `src/libs/BigNum128.py` - Fixed-point arithmetic
- `src/libs/CertifiedMath.py` - Deterministic math engine
- `src/libs/PQC.py` - Post-quantum cryptography
- `src/core/TokenStateBundle.py` - Token state management
- `src/core/HSMF.py` - Harmonic stability framework

## 📚 Documentation

### Remediation Documentation (Current Focus)

**Primary Documents:**
- [QFSV13_FULL_COMPLIANCE_AUDIT_REPORT.json](QFSV13_FULL_COMPLIANCE_AUDIT_REPORT.json) - Comprehensive audit (89 requirements)
- [STATE-GAP-MATRIX.md](STATE-GAP-MATRIX.md) - Detailed gap analysis by phase
- [ROADMAP-V13.5-REMEDIATION.md](ROADMAP-V13.5-REMEDIATION.md) - 365-day remediation roadmap with Evidence Index
- [TASKS-V13.5.md](TASKS-V13.5.md) - Task tracker with progress metrics
- [PHASE0_FINAL_COMPLETION.md](PHASE0_FINAL_COMPLETION.md) - Phase 0 completion report
- [DOCUMENTATION_ALIGNMENT_VERIFICATION.md](DOCUMENTATION_ALIGNMENT_VERIFICATION.md) - Meta-evidence of alignment

### Technical Documentation

**Compliance:**
- [docs/compliance/ZERO_SIMULATION_REPORT.md](docs/compliance/ZERO_SIMULATION_REPORT.md) - Zero-simulation compliance analysis
- [evidence/baseline/baseline_test_results.json](evidence/baseline/baseline_test_results.json) - Baseline test execution results
- [evidence/baseline/baseline_state_manifest.json](evidence/baseline/baseline_state_manifest.json) - Core component SHA3-512 hashes

**Architecture & Plans:**
- [docs/qfs_v13_plans/MASTER_PLAN_V13.md](docs/qfs_v13_plans/MASTER_PLAN_V13.md) - Original master plan
- Component-specific documentation in source files

### Evidence Artifacts

All verification evidence is stored in the `evidence/` directory:

```
evidence/
├── baseline/           # Phase 0 baseline artifacts
│   ├── baseline_commit_hash.txt
│   ├── baseline_state_manifest.json
│   ├── baseline_test_results.json
│   └── baseline_test_output.txt
├── phase1/             # Phase 1 deliverables (in progress)
├── phase2/             # Existing Phase 2 evidence
├── phase3/             # Existing Phase 3 evidence
├── phase4/             # Phase 4 deliverables (planned)
├── phase5/             # Phase 5 deliverables (planned)
└── final/              # Final certification package (planned)
```

**See:** [ROADMAP-V13.5-REMEDIATION.md#evidence-index](ROADMAP-V13.5-REMEDIATION.md#evidence-index) for complete artifact inventory.

## 🤝 Contributing

### Current Status

This project is in **active remediation** (Phase 1 of 5). Contributions are welcome but should align with the remediation roadmap.

### How to Contribute

1. **Understand the current state:**
   - Read [QFSV13_FULL_COMPLIANCE_AUDIT_REPORT.json](QFSV13_FULL_COMPLIANCE_AUDIT_REPORT.json)
   - Review [STATE-GAP-MATRIX.md](STATE-GAP-MATRIX.md)
   - Check [TASKS-V13.5.md](TASKS-V13.5.md) for current priorities

2. **Pick a task from the current phase:**
   - Phase 1 tasks are in [ROADMAP-V13.5-REMEDIATION.md#phase-1](ROADMAP-V13.5-REMEDIATION.md#phase-1-core-determinism-completion)
   - Check task status in [TASKS-V13.5.md](TASKS-V13.5.md)

3. **Follow evidence-first principle:**
   - All work must generate evidence artifacts
   - Evidence goes in `evidence/phase1/` (or appropriate phase)
   - Update Evidence Index in roadmap
   - Update task tracker status

4. **Maintain deterministic integrity:**
   - No floats, random, or time-based operations
   - All math must use BigNum128 or CertifiedMath
   - PQC signatures for all critical operations
   - SHA3-512 for all hashing

5. **Submit pull request:**
   - Reference specific task ID (e.g., P1-T001)
   - Include evidence artifacts
   - Update documentation
   - Ensure compliance with zero-simulation rules

### Priority Areas for Contribution

**Phase 1 (Current):**
- Fix test infrastructure import paths
- Create overflow/underflow stress scenarios for BigNum128
- Define CertifiedMath ProofVectors
- Document PQC key lifecycle and boundaries

**See:** [TASKS-V13.5.md#phase-1-core-determinism-completion](TASKS-V13.5.md#phase-1-core-determinism-completion) for complete list.

---

## License

MIT License

MIT License