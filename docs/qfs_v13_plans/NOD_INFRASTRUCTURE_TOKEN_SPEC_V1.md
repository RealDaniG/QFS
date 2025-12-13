# NOD (Node Operator Determination) Token Specification - V1.1

**Date:** 2025-12-13  
**Author:** QFS V13.6 Team  
**Version:** 1.1 (V13.6 Constitutional Integration)  
**Status:** V13.6 Implementation Complete (Phase 2 Integration: 100%)

---

## Executive Summary

NOD is the **sixth token in the Harmonic System (infrastructure-only)** of the QFS V13.5 Six-Token Harmonic System, serving as the **infrastructure sovereignty incentive mechanism**. Unlike user-facing tokens (FLX, CHR, etc.), NOD is **strictly protocol-internal**, **non-transferable**, and **infrastructure-only**.

**Purpose:** Ensure sustainable, economically incentivized node operation without reliance on altruistic participation.

---

## 1. Token Design Principles

### 1.1 Non-Financial by Design
- **No trading**: NOD cannot be transferred between addresses
- **No market**: No secondary market or liquidity pools
- **No redemption**: Cannot be exchanged for other tokens or fiat
- **Pure utility**: Protocol primitive for infrastructure coordination

### 1.2 Infrastructure-Scoped Utility
- **Governance**: Limited to infrastructure parameters only
  - Storage replication factor
  - AI model version approval
  - Network bandwidth/fee parameters
- **No social policy**: Cannot affect content, identity, or user rewards
- **No financial parameters**: Cannot control token emission rates or fees

### 1.3 Deterministic & Auditable
- **Issuance**: Deterministically derived from ATR fees (fixed %)
- **Distribution**: Proportional to node contribution metrics
- **Full EQM logging**: All NOD events PQC-signed and hash-chained

### 1.4 System Invariants (Non-Negotiable)

**Invariant NOD-I1:** At no point may NOD be transferred between entities; all state changes must originate from NODAllocator.

**Invariant NOD-I2:** NOD balances may only be associated with verified AEGIS node public keys.

**Invariant NOD-I3:** NOD-weighted governance outcomes must never alter user-facing scoring, rewards, or identity logic.

**Invariant NOD-I4:** Given identical ledger state and telemetry inputs, NOD allocation must be bit-for-bit reproducible.

### 1.5 Orthogonality to the Harmonic Core

NOD does not participate in harmonic balancing, coherence scoring, or social equilibrium loops. It exists in a strictly orthogonal plane governing infrastructure continuity.

NOD is not a "sixth harmonic token" but rather a "sixth token in the system, five harmonic + one sovereignty token" to avoid conceptual confusion.

---

## 2. Technical Specification

### 2.1 Token Properties
| Property | Value |
|---------|-------|
| **Symbol** | NOD |
| **Name** | Node Operator Determination |
| **Type** | Infrastructure-only, non-transferable |
| **Representation** | BigNum128 (SCALE=10^18) |
| **Transferable** | ❌ No |
| **Visible to Users** | ❌ No (until Phase 4+) |
| **Scope** | Infrastructure governance only |

> **Enforcement Rule**: The `StateTransitionEngine` must reject any transaction attempting to modify NOD in a non-infrastructure bundle. `RewardAllocator` and `NODAllocator` are the only authorized writers.
>
> **Static Analysis Rule**: AST_ZeroSimChecker must flag any call to `NOD.transfer()` or direct assignment outside `NODAllocator.py`. |

### 2.2 Integration Points

#### 2.2.1 TokenStateBundle Extension
```python
class TokenStateBundle:
    def __init__(self, chr: BigNum128, flx: BigNum128, psi: BigNum128,
                 atr: BigNum128, res: BigNum128, nod: BigNum128):
        self.CHR = chr
        self.FLX = flx
        self.PSI = psi
        self.ATR = atr
        self.RES = res
        self.NOD = nod  # ← NEW
```

> **Account Distinction**: NOD balances are only assigned to entities verified as registered AEGIS infrastructure nodes via `AEGIS_API.get_telemetry_metrics()`. User `TokenStateBundle` instances must initialize `NOD = BigNum128.ZERO` and never modify it.

#### 2.2.2 TreasuryEngine Extension
```python
# In TreasuryEngine.compute_reward()
atr_total_fees = ...  # Current ATR fee calculation
NOD_FRACTION = BigNum128.from_string("0.10")  # 10% of ATR fees
nod_share = CertifiedMath.multiply(atr_total_fees, NOD_FRACTION)
```

#### 2.2.3 New Modules
1. **NODAllocator.py** - Distributes NOD to infrastructure accounts
2. **InfrastructureGovernance.py** - Manages infrastructure-only governance

> **Module Design**: New components must follow existing deterministic validation patterns: pure functions, no I/O, PQC-signed inputs only. Consider extending `CoherenceEngine.py` rather than creating new top-level modules unless absolutely necessary.

---

## 3. Economic Model

### 3.1 Issuance Mechanism
- **Source**: Fixed percentage of all ATR fees collected
- **Default Rate**: 10% of ATR fees → NOD pool
- **Calculation**: `nod_issued = atr_fees_collected × 0.10`
- **Frequency**: Per user action that generates ATR fees

### 2.3 NOD Lifecycle

**Dormant:**
- No issuance if no ATR activity
- NOD logic never queries AEGIS and no issuance happens
- AEGIS nodes still run, but NOD remains zero-change

**Accrual:**
- ATR fees accumulate in deterministic pool (10% of ATR fees)
- Independent of AEGIS; no NOD is credited until scheduled allocation run

**Allocation:**
- On allocation, QFS pulls latest deterministic telemetry snapshot from AEGIS
- Uses it to split the NOD pool pro-rata
- Writes results into TokenStateBundle.NOD only for registered node keys

**Governance Usage:**
- NOD balances weight infrastructure-only votes on AEGIS-relevant parameters
- Vote execution handled by QFS governance modules
- No user-visible state is touched

**Decay / Burn (Optional, Future - Phase 5+):**
- Explicitly not active in V1
- Any decay/burn, dashboard, or slashing logic requires hard fork plus legal/audit approval

> **Important Note**: NOD has no terminal redemption state and does not represent claim rights. This shuts down profit-expectation arguments even harder.

### 3.3 Governance Power
- **Voting Weight**: Directly proportional to NOD balance
- **Quorum Calculation**: 
  ```python
  quorum = CertifiedMath.multiply(total_nod_supply, BigNum128.from_string("0.66"))
  ```
- **Scope**: Infrastructure parameters only (storage, AI models, network)

> **Hard Rule**: Infrastructure governance cannot modify its own scope, quorum rules, or voting mechanics without a protocol-level hard fork.

### 3.4 Relationship to Hard Forks & Epochs

Any change to NOD issuance rate, scope, or enforcement requires an epoch-bound protocol upgrade agreed via PBFT consensus and activated at a predefined block height.

---

## 4. Security & Compliance

### 4.1 Zero-Simulation Compliance
- **Deterministic Issuance**: Triggered only by user actions that generate ATR fees
- **Timestamps**: Sourced from `DRV_Packet.ttsTimestamp` (not OS time)
- **Math**: All calculations via `BigNum128` + `CertifiedMath`

### 4.2 Audit Trail (EQM Extension)
```json
{
  "nod_allocation": {
    "source_atr_fee": "123.456",
    "nod_issued": "12.345",
    "recipient_nodes": ["node_0xabc...", "node_0xdef..."]
  }
}
```

### 4.3 Explicit Non-Rights

NOD does not grant:

- Profit participation
- Ownership of protocol
- Revenue share
- Asset claims
- Priority liquidation rights

### 4.4 Failure Modes & Safe Degradation

**Telemetry Unavailable:**
- Allocation round skipped
- NOD issuance deferred, not approximated

**Node Set < Quorum:**
- Infrastructure governance frozen
- Social system continues uninterrupted

**Conflicting Telemetry Hashes:**
- Deterministic tie-break (lexicographic node ID)
- No subjective arbitration

> **Principles**: No emergency powers, no human override, no hidden centralization lever

### 4.5 Threat Model Coverage

| Threat | Mitigation |
|--------|------------|
| Node Sybil Attack | AEGIS registration + telemetry hashes |
| Fake Contribution | Deterministic telemetry validation |
| Governance Capture | NOD non-transferability + vote weight caps (25% max per node) |
| Collusion | PBFT + quorum thresholds (51%-90% bounded) |
| Economic Exploitation | No market, no transfer |
| Early-Node Monopolization | Minimum 3 active nodes required for allocation |
| Issuance Death Spiral | Hard cap: max 1M NOD per epoch |
| Parameter Manipulation | Constitutional bounds on all economic constants |

---

## 4.6 Constitutional Economic Bounds

**All NOD economic parameters are defined in `src/libs/economics/economic_constants.py` with [IMMUTABLE] or [MUTABLE] tags:**

### V13.6 Guard Enforcement

**EconomicsGuard** (`src/libs/economics/EconomicsGuard.py`) enforces all NOD bounds:

- `validate_nod_allocation()` - Called by NODAllocator and QFSV13SDK
- Validates allocation fraction, epoch issuance, per-node caps, voting power limits
- Emits structured error codes: `ECON_NOD_ALLOCATION_FRACTION_VIOLATION`, `ECON_NOD_ISSUANCE_CAP_EXCEEDED`, `ECON_NOD_NODE_DOMINANCE_VIOLATION`
- On violation: halts allocation, logs structured error, routes to CIR-302

**NODInvariantChecker** (`src/libs/governance/NODInvariantChecker.py`) enforces NOD-I1..I4:

- `check_allocation_invariants()` - Called by StateTransitionEngine, NODAllocator, QFSV13SDK
- Validates non-transferability, supply conservation, voting power bounds, deterministic replay
- Emits structured error codes: `NOD_INVARIANT_I1_VIOLATED`, `NOD_INVARIANT_I2_VIOLATED`, `NOD_INVARIANT_I3_VIOLATED`, `NOD_INVARIANT_I4_VIOLATED`
- On violation: halts state transition, logs structured error, routes to CIR-302

**AEGIS_Node_Verification** (`src/libs/governance/AEGIS_Node_Verification.py`) enforces NOD-I2:

- `verify_node()` - Called by NODAllocator, InfrastructureGovernance, QFSV13SDK
- Pure deterministic node verification (no HTTP calls)
- Returns `NodeVerificationResult` with reason codes
- Unverified nodes: filtered BEFORE NOD allocation or governance participation

### Allocation Bounds
- `NOD_ALLOCATION_FRACTION`: 10% (default, mutable)
- `MIN_NOD_ALLOCATION_FRACTION`: 1% (hard floor, immutable)
- `MAX_NOD_ALLOCATION_FRACTION`: 15% (hard cap, immutable)

### Governance Bounds
- `NOD_DEFAULT_QUORUM_THRESHOLD`: 66% (default, mutable)
- `MIN_QUORUM_THRESHOLD`: 51% (hard floor, immutable)
- `MAX_QUORUM_THRESHOLD`: 90% (hard cap, immutable)

### Anti-Centralization Guards
- `MAX_NOD_VOTING_POWER_RATIO`: 25% (single node max voting power, immutable)
- `MAX_NODE_REWARD_SHARE`: 30% (single node max allocation share, immutable)
- `NOD_MIN_ACTIVE_NODES`: 3 (minimum network size for allocation, immutable)

### Emission Controls
- `NOD_MAX_ISSUANCE_PER_EPOCH`: 1,000,000 (maximum NOD per epoch, mutable)
- `NOD_ZERO_ACTIVITY_FLOOR`: 0 (no issuance when idle, immutable)

### Governance Timing
- `GOVERNANCE_PROPOSAL_COOLDOWN_BLOCKS`: 120 (~34 min, immutable)
- `GOVERNANCE_VOTING_WINDOW_BLOCKS`: 720 (~3.4 hours, mutable)
- `GOVERNANCE_EXECUTION_DELAY_BLOCKS`: 240 (~1.1 hours timelock, immutable)
- `GOVERNANCE_EMERGENCY_QUORUM`: 80% (emergency proposals only, immutable)

**Rationale**: These bounds prevent governance capture, economic death spirals, and ensure all parameter changes are auditable, provable, and deterministically enforceable.

---

## 5. Phase-Aligned Rollout

| Phase | Action | Status |
|-------|--------|--------|
| **Phase 0** | Freeze NOD spec in documentation | ✅ COMPLETE |
| **Phase 1** | Create `economic_constants.py` with constitutional bounds for all 6 tokens | ✅ COMPLETE |
| **Phase 1.5** | Implement `NODAllocator.py` with safety bounds enforcement | ✅ COMPLETE |
| **Phase 1.5** | Implement `InfrastructureGovernance.py` with constitutional protections | ✅ COMPLETE |
| **V13.6 Phase 1** | Create EconomicsGuard.py | ✅ COMPLETE (937 lines, 8 methods, 27 error codes) |
| **V13.6 Phase 1** | Create NODInvariantChecker.py | ✅ COMPLETE (682 lines, 4 invariants, 13 tests) |
| **V13.6 Phase 1** | Create AEGIS_Node_Verification.py | ✅ COMPLETE (733 lines, 5 checks) |
| **V13.6 Phase 2** | Wire guards into TreasuryEngine | ✅ COMPLETE |
| **V13.6 Phase 2** | Wire guards into RewardAllocator | ✅ COMPLETE |
| **V13.6 Phase 2** | Wire guards into NODAllocator | ✅ COMPLETE |
| **V13.6 Phase 2** | Wire AEGIS verifier into InfrastructureGovernance | ✅ COMPLETE |
| **V13.6 Phase 2** | Wire guards into StateTransitionEngine (FINAL GATE) | ✅ COMPLETE |
| **V13.6 Phase 2** | Wire guards into QFSV13SDK (no bypass paths) | ✅ COMPLETE |
| **V13.6 Phase 2** | Add AEGIS telemetry snapshot infrastructure (aegis_api.py) | ✅ COMPLETE |
| **V13.6 Phase 2.8** | Update CIR-302 handler to map all new error codes | 🔄 NEXT |
| **V13.6 Phase 3** | DeterministicReplayTest / BoundaryConditionTests / FailureModeTests | 🔄 PLANNED |
| **Phase 2** | Extend `tests/deterministic/test_deterministic_time.py` to include a synthetic ATR → NOD issuance flow, producing `nod_distribution_simulation.json` with 5-run replay consistency | 🔄 PLANNED |
| **Phase 3** | Integrate with AEGIS node telemetry API | ✅ COMPLETE (aegis_api.py) |
| **Phase 4** | Complete governance execution layer (execute_proposal, cancel_proposal, expiry) | 🔄 PLANNED |
| **Phase 5** | Create comprehensive constitutional compliance tracker | ✅ COMPLETE |
| **Phase 6+** | Optional user visibility (node dashboard) | 🔄 PLANNED |

---

## 6. Risk Mitigation

### 6.1 Scope Creep Prevention
- **Strict governance isolation**: Infrastructure-only decisions
- **Code-level enforcement**: Separate modules with explicit scope limitations
- **Audit verification**: EQM logs track all governance actions

### 6.2 Financialization Prevention
- **Transfer prohibition**: Hardcoded non-transferability
- **No liquidity**: No exchange listings or market makers
- **Legal alignment**: Mirrors FLX's non-financial design

### 6.3 Implementation Risks
- **Deterministic replay**: All NOD events must be fully reproducible
- **Node sybil resistance**: AEGIS registration prevents fake node operators
- **Contribution verification**: Telemetry hashes ensure honest reporting

---

## 7. Integration Requirements

### 7.1 Core System Updates
1. **economic_constants.py**: ✅ COMPLETE - All NOD bounds defined with [IMMUTABLE]/[MUTABLE] tags
2. **TokenStateBundle**: Add NOD field (PLANNED)
3. **TreasuryEngine**: Allocate ATR fees to NOD pool (PLANNED)
4. **CoherenceLedger**: Log NOD issuance and distribution + constitutional config hash tracking (PLANNED)
5. **PQC Layer**: Sign all NOD-related state changes (PLANNED)
6. **QFSV13SDK.py**: Route all calls through EconomicsGuard to prevent guard bypass (PLANNED)
7. **StateTransitionEngine**: Enforce NOD invariants on every state change (PLANNED)

### 7.2 New Components
1. **NODAllocator.py**: ✅ COMPLETE - Distribute NOD to node operators with anti-centralization guards
2. **InfrastructureGovernance.py**: ✅ COMPLETE - Infrastructure-only governance with constitutional protections
3. **EconomicsGuard.py**: ✅ COMPLETE (V13.6) - Centralized bounds enforcement for all economic operations
4. **NODInvariantChecker.py**: ✅ COMPLETE (V13.6) - Enforce NOD-I1 through NOD-I4 invariants
5. **AEGIS_Node_Verification.py**: ✅ COMPLETE (V13.6) - Structural node verification enforcement
6. **EconomicConstantsMigration.py**: 🔄 PLANNED - Version-aware economic constant loading for protocol upgrades

> **Module Design**: All new components follow deterministic validation patterns: pure functions, no I/O, PQC-signed inputs only, CertifiedMath operations, BigNum128 fixed-point arithmetic, and comprehensive audit logging.

### 7.3 Evidence Artifacts (Phase 1+)
1. `nod_distribution_simulation.json` - Deterministic replay tests
2. `nod_infra_gov_test.json` - Governance vote with NOD quorum
3. `nod_issuance_audit.json` - Full issuance chain verification

> **Audit v2.0 Format**:
```json
{
  "component": "NOD",
  "phase": "1.5",
  "evidence_type": "deterministic_replay",
  "replay_consistent": true,
  "git_commit": "<SHA>",
  "timestamp": "2025-12-13T00:00:00Z"
}
```

---

## 8. Success Metrics

### 8.1 Technical
- ✅ NOD issuance fully deterministic and reproducible
- ✅ Infrastructure governance isolated from social governance
- ✅ Zero-simulation compliance maintained
- ✅ Full EQM audit trail for all NOD operations

### 8.2 Economic
- ✅ Sustainable node operator participation
- ✅ Infrastructure capacity growth aligned with user activity
- ✅ No centralization drift in node operator base
- ✅ ATR fee diversion < 15% (economic efficiency maintained)

### 8.3 Legal
- ✅ No financial classification risk
- ✅ No SEC/MiCA regulatory triggers
- ✅ Governance scope firewalls effective
- ✅ Protocol primitive classification maintained

### 8.4 Deterministic Compliance
- ✅ All NOD state changes originate from NODAllocator only
- ✅ NOD balances only associated with verified AEGIS node public keys
- ✅ NOD-weighted governance never alters user-facing logic
- ✅ Bit-for-bit reproducible given identical inputs
- ✅ Constitutional bounds prevent governance capture and economic death spirals
- ✅ All economic parameters versioned and tracked in CoherenceLedger
- ✅ Structured error codes enable CIR-302 audit interpretation
- ✅ No bypass paths - all SDK calls routed through EconomicsGuard

---

## 9. Future Considerations

> ⚠️ These features are explicitly OUT OF SCOPE for V13.5. Any implementation before Phase 5 requires full legal review and auditor sign-off to preserve non-financial classification.

### 9.1 Phase 4+ Visibility
- **Node dashboard**: Read-only NOD balance for operators
- **Performance metrics**: Display uptime/contribution scores
- **Governance history**: Show past infrastructure votes

### 9.2 Advanced Features
- **Staking mechanics**: Optional NOD staking for higher governance weight
- **Delegation**: Allow node operators to delegate NOD voting power
- **Slashing conditions**: Penalize malicious or non-compliant nodes

### 9.3 Economic Tuning
- **Dynamic NOD rate**: Adjust percentage based on infrastructure demand
- **Bonus mechanisms**: Reward exceptional node operators
- **Burn events**: Periodic NOD reduction to maintain scarcity

---

## 10. Conclusion

NOD transforms ATLAS × QFS from a *decentralized application* into a **Replicated Deterministic Social State Machine**—where infrastructure is not rented from cloud giants, but **owned, operated, and economically sustained by the protocol itself**.

Its inclusion is essential for long-term viability, not feature completeness.

> **This is not a token launch—it's an architectural necessity and a formal infrastructure sovereignty primitive.**
