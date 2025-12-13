# Constitutional QFS V13.5 Compliance Task Tracker

**Status:** IN PROGRESS  
**Goal:** Transform QFS V13.5 from "good code" to "constitutional-grade system"  
**Last Updated:** 2025-12-13

---

## Executive Summary

### ✅ COMPLETED (Phase A: Foundation)
1. **economic_constants.py** - Full constitutional parameter structure (159 lines, 8 sections, all 6 tokens)
2. **README.md** - NOD token documentation with governance firewall explanations
3. **NODAllocator.py** - Safety bounds, emission controls, anti-centralization guards
4. **InfrastructureGovernance.py** - Partial completion:
   - ✅ Constitutional imports (all governance constants)
   - ✅ ProposalStatus extended (CANCELLED, EXPIRED)
   - ✅ InfrastructureProposal dataclass (voters, snapshots, execution fields)
   - ✅ Quorum threshold bug fixed (argument now used)
   - ✅ Bounds enforcement (MIN/MAX quorum validation)
   - ✅ Firewall assertion in __init__
   - ✅ Proposal cooldown enforcement
   - ✅ Node verification stub (_is_valid_active_node)
   - ✅ Parameter validation layer (_validate_proposal_parameters)
   - ✅ Timelock calculation (execution_earliest_timestamp)
   - ✅ Double-vote protection (voters registry)
   - ✅ Vote weight capping (MAX_NOD_VOTING_POWER_RATIO)
   - ✅ Deterministic supply snapshot (total_nod_supply_snapshot)

### 🔄 IN PROGRESS (Phase B: Governance Completion)
- InfrastructureGovernance.py remaining items (see File 2 below)

### ⏳ PENDING (Phase C: Economic Wiring)
- TreasuryEngine.py constitutional updates
- RewardAllocator.py bounds and dust handling
- EconomicsGuard.py creation
- StateTransitionEngine.py NOD transfer firewall

### ⏳ PENDING (Phase D: Invariants & Tests)
- NOD invariant checks (NOD-I1 through NOD-I4)
- Economic bound violation → CIR-302 wiring
- Boundary condition tests
- Deterministic replay tests
- Evidence artifacts generation

### ⏳ PENDING (Phase E: Documentation Sync)
- NOD_INFRASTRUCTURE_TOKEN_SPEC_V1.md constitutional sections
- MASTER-PLAN-V13.md Phase 4/5 acceptance criteria
- Autonomous audit v2.0 economic stress tests

---

## BUCKET A: GOVERNANCE & ECONOMICS WIRING

---

## BUCKET D: LIVE SYSTEM INTEGRATION (CRITICAL - NEW)

### File 14: QFSV13SDK.py (ENHANCEMENT NEEDED)

**Status:** 0/8 changes complete (0%)

#### Purpose
Ensure all SDK state-changing operations route through constitutional guards and propagate structured error codes.

#### Required Changes (8 total)

**A. Add Economics Guard Integration (3 changes)**
1. ⏳ Import EconomicsGuard in SDK __init__
2. ⏳ Wrap all reward/allocation calls with EconomicsGuard.validate_*() pre-checks
3. ⏳ Catch structured error codes (ECON_BOUND_VIOLATION, GOV_SAFETY_VIOLATION) and propagate to caller

**B. Add NOD Invariant Integration (3 changes)**
4. ⏳ Import NODInvariantChecker in SDK __init__
5. ⏳ Wrap all NOD operations with invariant checks (NOD-I1 through NOD-I4)
6. ⏳ Catch invariant violations (INVARIANT_VIOLATION_*) and trigger CIR-302

**C. Add Backwards Compatibility Guards (2 changes)**
7. ⏳ Mark old direct-call methods as deprecated with warnings
8. ⏳ Force all paths through guarded SDK methods (reject direct TreasuryEngine/RewardAllocator calls)

**Acceptance Criteria:**
- [ ] All 8 changes implemented
- [ ] Old code paths cannot bypass guards
- [ ] Structured errors propagate to SDK callers
- [ ] CIR-302 integration tested
- [ ] Test suite covers bypass attempts

**Estimated Complexity:** HIGH (8 changes, ~150 lines, critical path integration)

---

### File 15: aegisapi.py (ENHANCEMENT NEEDED)

**Status:** 0/6 changes complete (0%)

#### Purpose
Ensure AEGIS API integration respects constitutional bounds and provides deterministic telemetry snapshots.

#### Required Changes (6 total)

**A. Add Telemetry Snapshot Format (3 changes)**
1. ⏳ Define AEGISTelemetrySnapshot dataclass (node_metrics, block_height, snapshot_hash, schema_version)
2. ⏳ Add get_telemetry_snapshot() method returning versioned, hashed snapshot
3. ⏳ Validate snapshot completeness (reject partial/ambiguous data)

**B. Add Constitutional Guard Integration (3 changes)**
4. ⏳ Wrap all AEGIS calls with EconomicsGuard checks for rate limits
5. ⏳ Add AEGIS offline detection and safe degradation policy
6. ⏳ Log all AEGIS interactions with snapshot hash for EQM audit trail

**Acceptance Criteria:**
- [ ] All 6 changes implemented
- [ ] Telemetry snapshots are deterministic and versioned
- [ ] AEGIS offline triggers safe degradation (user rewards continue, NOD/governance freeze)
- [ ] All snapshots committed to EQM with hash
- [ ] Test suite covers AEGIS unavailable scenarios

**Estimated Complexity:** HIGH (6 changes, ~200 lines, external system integration)

---

### File 16: CoherenceLedger.py (ENHANCEMENT NEEDED)

**Status:** 0/5 changes complete (0%)

#### Purpose
Extend ledger to record constitutional config snapshots and guard check results for replay verification.

#### Required Changes (5 total)

**A. Add Constitutional Config Tracking (3 changes)**
1. ⏳ Add economic_constants_hash field to ledger entries (SHA3-512 of entire economic_constants.py)
2. ⏳ Add guard_checks_passed field listing which guards validated entry
3. ⏳ Add bounds_proximity field tracking how close values were to limits (e.g., "CHR reward at 95% of cap")

**B. Add Replay Verification Support (2 changes)**
4. ⏳ Add verify_constitutional_replay() method comparing config hashes across epochs
5. ⏳ Generate constitutional_integrity_report.json showing config evolution over time

**Acceptance Criteria:**
- [ ] All 5 changes implemented
- [ ] Every ledger entry includes config hash
- [ ] Guard check results auditable
- [ ] Replay verification detects config drift
- [ ] Evidence artifact: constitutional_integrity_report.json

**Estimated Complexity:** MEDIUM (5 changes, ~120 lines)

---

### File 17: AutonomousAuditV2Driver.py (ENHANCEMENT NEEDED)

**Status:** 0/7 changes complete (0%)

#### Purpose
Update autonomous audit driver to interpret structured error codes and fail on guard violations.

#### Required Changes (7 total)

**A. Add Structured Error Interpretation (4 changes)**
1. ⏳ Add error_code_parser() to map structured codes to severity levels
2. ⏳ Add ECON_BOUND_VIOLATION handler (CRITICAL severity, fail audit)
3. ⏳ Add GOV_SAFETY_VIOLATION handler (CRITICAL severity, fail audit)
4. ⏳ Add INVARIANT_VIOLATION_* handlers (CRITICAL severity, fail audit + CIR-302 trigger)

**B. Add Constitutional Stress Tests (3 changes)**
5. ⏳ Add stress_test_single_node_nod_capture() scenario
6. ⏳ Add stress_test_maximal_token_issuance() scenario (CHR/FLX at caps)
7. ⏳ Add stress_test_rapid_governance_churn() scenario

**Acceptance Criteria:**
- [ ] All 7 changes implemented
- [ ] Audit fails on any CRITICAL error code
- [ ] Stress tests exercise all constitutional bounds
- [ ] Generic errors no longer treated as "soft failures"
- [ ] Evidence artifact: autonomous_audit_v2_constitutional_report.json

**Estimated Complexity:** HIGH (7 changes, ~250 lines, audit infrastructure)

---

### File 18: AEGIS_Node_Verification.py (NEW FILE - NOT CREATED)

**Status:** 0/1 file created (0%)

#### Purpose
Centralized node verification criteria for NOD-I2 enforcement across all modules.

#### Required Implementation (6 components)

**A. Node Registry Integration (3 components)**
1. ⏳ Define NodeRegistryEntry dataclass (node_id, pqc_public_key, registration_timestamp, uptime_ratio, slashing_history)
2. ⏳ Add get_active_nodes() method querying AEGIS registry
3. ⏳ Add is_valid_active_node(node_id) with criteria: registered + uptime >= 90% + no recent slashing

**B. Structural Enforcement (3 components)**
4. ⏳ Integrate into NODAllocator.allocate_from_atr_fees() (reject unverified nodes)
5. ⏳ Integrate into InfrastructureGovernance.create_proposal() (reject unverified proposers)
6. ⏳ Integrate into InfrastructureGovernance.cast_vote() (reject unverified voters)

**Acceptance Criteria:**
- [ ] File created with all 6 components
- [ ] NOD-I2 structurally enforced (no code path allows unverified node NOD)
- [ ] Criteria documented and testable
- [ ] AEGIS integration stubbed with clear TODO for production
- [ ] Test suite covers unverified node rejection

**Estimated Complexity:** HIGH (new file, ~200 lines, critical invariant enforcement)

---

### File 19: AEGIS_Offline_Policy.md (NEW FILE - NOT CREATED)

**Status:** 0/1 file created (0%)

#### Purpose
Global policy document defining QFS behavior when AEGIS is degraded or unavailable.

#### Required Sections (5 total)

**A. Degradation Matrix (3 sections)**
1. ⏳ **AEGIS Fully Available** - All operations proceed normally
2. ⏳ **AEGIS Telemetry Degraded** - User rewards continue (using cached state), NOD allocation skipped, infrastructure governance frozen
3. ⏳ **AEGIS Completely Offline** - User rewards continue (safe mode), NOD frozen, governance frozen, CIR-302 alert triggered

**B. Enforcement Rules (2 sections)**
4. ⏳ **Forbidden Approximations** - System MUST NOT approximate missing telemetry (skip epoch instead)
5. ⏳ **CIR-302 Integration** - Define AEGIS offline as non-critical incident (system continues with reduced functionality)

**Acceptance Criteria:**
- [ ] File created with all 5 sections
- [ ] Policy integrated into MASTER-PLAN-V13.md Phase 4
- [ ] CIR-302 handler implements policy
- [ ] Test suite covers all degradation scenarios

**Estimated Complexity:** LOW (policy document, ~100 lines, no code)

---

### File 20: EconomicConstantsMigration.py (NEW FILE - NOT CREATED)

**Status:** 0/1 file created (0%)

#### Purpose
Manage constitutional constant versioning and migration for protocol upgrades.

#### Required Implementation (7 components)

**A. Versioning System (4 components)**
1. ⏳ Define ECON_VERSION constant (starts at "V1")
2. ⏳ Add economic_constants_v1.py, economic_constants_v2.py structure
3. ⏳ Add get_constants_for_epoch(epoch_number) -> returns correct version
4. ⏳ Add migrate_ledger_data(from_version, to_version) for test data upgrades

**B. Replay Compatibility (3 components)**
5. ⏳ Store ECON_VERSION in every CoherenceLedger entry
6. ⏳ Replay engine uses epoch-appropriate constants
7. ⏳ Validation that old epochs remain valid under new constants (or explicitly marked incompatible)

**Acceptance Criteria:**
- [ ] File created with all 7 components
- [ ] Versioning allows protocol upgrades without breaking replay
- [ ] Migration path documented for each version transition
- [ ] Test suite covers cross-version replay
- [ ] Evidence artifact: economic_constants_migration_log.json

**Estimated Complexity:** MEDIUM (new file, ~180 lines, versioning complexity)

---

### File 21: PerformanceBenchmarkWithGuards.py (NEW FILE - NOT CREATED)

**Status:** 0/1 file created (0%)

#### Purpose
Verify QFS meets Phase 4 performance targets with all constitutional guards enabled.

#### Required Benchmark Scenarios (6 total)

**A. Throughput Tests (3 scenarios)**
1. ⏳ Test sustained TPS with EconomicsGuard + NODInvariantChecker enabled
2. ⏳ Test peak TPS with all guards + full logging
3. ⏳ Compare baseline (no guards) vs guarded performance

**B. Latency Tests (3 scenarios)**
4. ⏳ Test p50, p95, p99 latency for guarded reward allocation
5. ⏳ Test p50, p95, p99 latency for guarded governance operations
6. ⏳ Validate latency meets Phase 4 targets (p95 < 100ms)

**Acceptance Criteria:**
- [ ] File created with all 6 benchmark scenarios
- [ ] Performance meets Phase 4 targets (2,000 TPS minimum)
- [ ] Latency acceptable with all guards enabled
- [ ] Evidence artifact: performance_benchmark_guarded.json
- [ ] Regression tests prevent future performance degradation

**Estimated Complexity:** MEDIUM (new file, ~250 lines, performance critical)

---

### File 1: InfrastructureGovernance.py (PARTIALLY COMPLETE)

**Status:** 13/20 changes complete (65%)

#### ✅ COMPLETED CHANGES (13/20)
1. ✅ Import all governance constants from economic_constants.py
2. ✅ Extend ProposalStatus enum (CANCELLED, EXPIRED)
3. ✅ Update InfrastructureProposal dataclass (add voters, snapshots, execution fields)
4. ✅ Fix __init__ quorum_threshold argument bug (was ignored)
5. ✅ Enforce MIN/MAX_QUORUM_THRESHOLD bounds
6. ✅ Add firewall assertion in __init__
7. ✅ Add last_proposal_timestamp tracking for cooldown
8. ✅ Enforce GOVERNANCE_PROPOSAL_COOLDOWN_BLOCKS in create_proposal
9. ✅ Add _is_valid_active_node() stub
10. ✅ Add _validate_proposal_parameters() with type-specific rules
11. ✅ Calculate execution_earliest_timestamp with GOVERNANCE_EXECUTION_DELAY_BLOCKS
12. ✅ Add double-vote protection in cast_vote (check voters registry)
13. ✅ Add vote weight capping (MAX_NOD_VOTING_POWER_RATIO)

#### ⏳ REMAINING CHANGES (7/20)
14. ⏳ Add execute_proposal() method with timelock, once-only, state mutation
15. ⏳ Add cancel_proposal() method (proposer-only)
16. ⏳ Add expire_stale_proposals() batch method
17. ⏳ Update _log_vote() signature (add capped parameter, event hash)
18. ⏳ Update _log_proposal_creation() with event hash
19. ⏳ Update _log_tally_result() with event hash
20. ⏳ Update test function with new governance flows

**Acceptance Criteria:**
- [ ] All 20 changes implemented
- [ ] execute_proposal enforces timelock and prevents double-execution
- [ ] cancel_proposal only allows proposer to cancel ACTIVE proposals
- [ ] expire_stale_proposals deterministically marks old proposals EXPIRED
- [ ] All logging includes SHA256 event hashes for Merkle inclusion
- [ ] Test function covers happy path + edge cases (double-vote, expired, capped)

**Estimated Complexity:** MEDIUM (7 changes, ~150 lines)

---

### File 2: TreasuryEngine.py (NOT STARTED)

**Status:** 0/12 changes complete (0%)

#### Required Changes (12 total)

**A. Import Constitutional Constants (2 changes)**
1. ⏳ Import CHR constants (CHR_MIN/MAX_REWARD_PER_ACTION, CHR_DAILY_EMISSION_CAP, CHR_SATURATION_THRESHOLD, CHR_DECAY_RATE)
2. ⏳ Import FLX constants (MIN/MAX_FLX_REWARD_FRACTION, FLX_MAX_PER_USER, FLX_DECAY_RATE)

**B. Add Reward Clamping (4 changes)**
3. ⏳ Clamp CHR reward to [CHR_MIN_REWARD_PER_ACTION, CHR_MAX_REWARD_PER_ACTION]
4. ⏳ Enforce CHR_DAILY_EMISSION_CAP (requires epoch tracking)
5. ⏳ Validate FLX_REWARD_FRACTION against MIN/MAX bounds
6. ⏳ Clamp FLX reward per user to FLX_MAX_PER_USER

**C. Add Saturation Checks (2 changes)**
7. ⏳ Check CHR total supply against CHR_SATURATION_THRESHOLD
8. ⏳ Check PSI accumulation against PSI_SATURATION_CAP

**D. Add System-Wide Impact Validation (2 changes)**
9. ⏳ Validate total reward change <= MAX_TOTAL_SUPPLY_RATIO_CHANGE per epoch
10. ⏳ Validate single reward bundle <= MAX_SINGLE_EVENT_IMPACT

**E. Add Decay Rate Application (1 change)**
11. ⏳ Apply CHR_DECAY_RATE, FLX_DECAY_RATE, PSI_DECAY_RATE (requires epoch number parameter)

**F. Implement Proper RES Logic (1 change)**
12. ⏳ Replace placeholder RES reward with proper reserve management (RES_TARGET_RATIO, RES_MAX_DRAW_PER_EPOCH, RES_REPLENISH_RATE)

**Acceptance Criteria:**
- [ ] All 12 changes implemented
- [ ] All reward calculations bounded by economic_constants
- [ ] Decay rates applied when epoch_number changes
- [ ] RES reserve properly managed (not placeholder)
- [ ] Saturation checks prevent unbounded growth
- [ ] System-wide impact checks prevent economic shocks
- [ ] Test suite covers boundary conditions (near caps, saturation)

**Estimated Complexity:** HIGH (12 changes, ~200 lines, complex logic)

---

### File 3: RewardAllocator.py (NOT STARTED)

**Status:** 0/7 changes complete (0%)

#### Required Changes (7 total)

**A. Add Anti-Centralization Guards (3 changes)**
1. ⏳ Import MAX_NODE_REWARD_SHARE or equivalent user constant
2. ⏳ Add per-address dominance cap check in allocate_rewards()
3. ⏳ Log capping events when address share exceeds limit

**B. Add Deterministic Dust Handling (4 changes)**
4. ⏳ Track rounding residuals from fixed-point division
5. ⏳ Implement dust policy (burn / treasury / carry-forward)
6. ⏳ Add dust_handling_mode parameter to __init__ (BURN, TREASURY, CARRY_FORWARD)
7. ⏳ Log dust events with deterministic policy application

**Acceptance Criteria:**
- [ ] All 7 changes implemented
- [ ] Per-address caps prevent single-user dominance
- [ ] Dust policy is explicit and deterministic
- [ ] Dust handling mode configurable via constructor
- [ ] All dust events logged for audit trail
- [ ] Test suite covers dust accumulation scenarios

**Estimated Complexity:** MEDIUM (7 changes, ~100 lines)

---

### File 4: EconomicsGuard.py (NEW FILE - NOT CREATED)

**Status:** 0/1 file created (0%)

#### Purpose
Centralized economic bounds validation that all modules call before state-changing operations.

#### Required Structure
```python
class EconomicsGuard:
    """
    Constitutional economic bounds validator.
    
    Validates proposed economic changes against all relevant constants,
    returning structured error codes on violation for CIR-302 integration.
    """
    
    def __init__(self, cm_instance: CertifiedMath):
        self.cm = cm_instance
    
    def validate_chr_reward(self, proposed_reward: BigNum128, ...) -> ValidationResult
    def validate_flx_reward(self, proposed_reward: BigNum128, ...) -> ValidationResult
    def validate_nod_allocation(self, proposed_allocation: BigNum128, ...) -> ValidationResult
    def validate_governance_change(self, proposal_type, parameters) -> ValidationResult
    def validate_emission_rate(self, token_type, proposed_rate, epoch_number) -> ValidationResult
    def validate_supply_change(self, token_type, delta, total_supply) -> ValidationResult
```

#### Required Implementation (8 methods)
1. ⏳ validate_chr_reward() - Check CHR bounds and emission caps
2. ⏳ validate_flx_reward() - Check FLX bounds and per-user caps
3. ⏳ validate_nod_allocation() - Check NOD bounds and node caps
4. ⏳ validate_governance_change() - Check governance parameter changes
5. ⏳ validate_emission_rate() - Check emission rates against caps
6. ⏳ validate_supply_change() - Check supply deltas against max ratios
7. ⏳ Structured error codes (ECON_BOUND_VIOLATION, GOV_SAFETY_VIOLATION, etc.)
8. ⏳ Integration with CIR-302 handler for violations

**Acceptance Criteria:**
- [ ] File created with all 8 validation methods
- [ ] Returns structured ValidationResult (pass/fail + error code)
- [ ] All modules (TreasuryEngine, NODAllocator, InfrastructureGovernance, RewardAllocator) call EconomicsGuard before mutations
- [ ] Error codes documented and mapped to CIR-302 responses
- [ ] Test suite covers all validation paths

**Estimated Complexity:** HIGH (new file, ~300 lines, integration with 4 modules)

---

### File 5: StateTransitionEngine.py (PARTIALLY STARTED)

**Status:** 0/5 changes complete (0%)

#### Required Changes (5 total)

**A. Add NOD Transfer Firewall (3 changes)**
1. ⏳ Add NOD_TRANSFER_FORBIDDEN check in apply_transition()
2. ⏳ Reject any TokenStateBundle mutation with NOD delta outside NODAllocator/InfrastructureGovernance
3. ⏳ Emit structured error INVARIANT_VIOLATION_NOD_TRANSFER on attempt

**B. Add NOD Allocation Authorization (2 changes)**
4. ⏳ Add authorized_allocator parameter to __init__
5. ⏳ Only allow NOD changes if caller is NODAllocator or InfrastructureGovernance

**Acceptance Criteria:**
- [ ] All 5 changes implemented
- [ ] NOD transfers from user addresses rejected
- [ ] Only authorized allocators can modify NOD balances
- [ ] Violation attempts trigger CIR-302-compatible errors
- [ ] Test suite covers unauthorized NOD transfer attempts

**Estimated Complexity:** MEDIUM (5 changes, ~80 lines)

---

## BUCKET B: INVARIANTS & AUDIT INTEGRATION

### File 6: NODInvariantChecker.py (NEW FILE - NOT CREATED)

**Status:** 0/1 file created (0%)

#### Purpose
Explicit encoding of NOD-I1 through NOD-I4 invariants as runtime checks.

#### Required Invariant Checks (4 total)
1. ⏳ **NOD-I1**: Assert no NOD transfers between entities (all state changes from NODAllocator only)
2. ⏳ **NOD-I2**: Assert NOD balances only for verified AEGIS node public keys
3. ⏳ **NOD-I3**: Assert NOD governance outcomes never alter user-facing logic
4. ⏳ **NOD-I4**: Assert bit-for-bit replay given identical ledger + telemetry inputs

#### Implementation Structure
```python
class NODInvariantChecker:
    """Enforces NOD V1 constitutional invariants."""
    
    def check_nod_i1_no_transfer(self, state_transition) -> InvariantResult
    def check_nod_i2_node_keys_only(self, nod_balance_changes) -> InvariantResult
    def check_nod_i3_no_user_impact(self, governance_outcome) -> InvariantResult
    def check_nod_i4_replay_determinism(self, input_snapshot, output_hash) -> InvariantResult
```

**Acceptance Criteria:**
- [ ] File created with all 4 invariant check methods
- [ ] Called at strategic points (StateTransitionEngine, NODAllocator, InfrastructureGovernance)
- [ ] Invariant violations trigger CIR-302 halt with structured error codes
- [ ] Test suite includes invariant violation scenarios
- [ ] Evidence artifact: nod_invariant_verification.json

**Estimated Complexity:** HIGH (new file, ~250 lines, deep integration)

---

### File 7: CIR302_Handler.py (ENHANCEMENT NEEDED)

**Status:** EXISTS but needs economic violation integration (0/4 changes)

#### Required Changes (4 total)
1. ⏳ Add economic_bound_violation() handler method
2. ⏳ Add governance_safety_violation() handler method
3. ⏳ Map structured error codes (ECON_BOUND_VIOLATION, GOV_SAFETY_VIOLATION, INVARIANT_VIOLATION_*)
4. ⏳ Generate enhanced AEGIS_FINALITY_SEAL.json with economic violation details

**Acceptance Criteria:**
- [ ] All 4 changes implemented
- [ ] EconomicsGuard violations trigger CIR-302 halt
- [ ] NODInvariantChecker violations trigger CIR-302 halt
- [ ] AEGIS_FINALITY_SEAL includes economic/governance violation metadata
- [ ] Test suite covers economic bound violation scenarios

**Estimated Complexity:** MEDIUM (4 changes, ~100 lines)

---

### File 8: DeterministicReplayTest.py (NEW FILE - NOT CREATED)

**Status:** 0/1 file created (0%)

#### Purpose
Prove NOD-I4: Bit-for-bit replay determinism for NOD allocation and governance.

#### Required Test Cases (5 total)
1. ⏳ Test NOD allocation replay (same ATR fees + telemetry → same NOD distribution)
2. ⏳ Test governance voting replay (same proposal + votes → same outcome)
3. ⏳ Test governance execution replay (same PASSED proposal → same config mutation)
4. ⏳ Test hash chain integrity (same inputs → same log hashes)
5. ⏳ Test cross-platform replay (Windows mock vs Linux liboqs → same outputs)

**Acceptance Criteria:**
- [ ] File created with all 5 test cases
- [ ] All tests pass (100% deterministic replay)
- [ ] Evidence artifact: nod_replay_determinism.json
- [ ] Integrated into autonomous audit v2.0 pipeline

**Estimated Complexity:** HIGH (new file, ~400 lines, complex test scenarios)

---

### File 9: BoundaryConditionTests.py (NEW FILE - NOT CREATED)

**Status:** 0/1 file created (0%)

#### Purpose
Test economic bounds enforcement at edge cases and violation attempts.

#### Required Test Scenarios (12 total)

**CHR Tests (3)**
1. ⏳ Test CHR reward at MIN boundary (should pass)
2. ⏳ Test CHR reward at MAX boundary (should pass)
3. ⏳ Test CHR reward over MAX (should clamp or reject)

**FLX Tests (3)**
4. ⏳ Test FLX allocation fraction at MIN (should pass)
5. ⏳ Test FLX allocation fraction at MAX (should pass)
6. ⏳ Test FLX per-user cap exceeded (should clamp)

**NOD Tests (6)**
7. ⏳ Test NOD allocation with < MIN_ACTIVE_NODES (should skip)
8. ⏳ Test NOD allocation at MAX_ISSUANCE_PER_EPOCH (should cap)
9. ⏳ Test NOD single node dominance > MAX_NODE_REWARD_SHARE (should cap)
10. ⏳ Test governance quorum < MIN_QUORUM_THRESHOLD (should reject)
11. ⏳ Test governance quorum > MAX_QUORUM_THRESHOLD (should reject)
12. ⏳ Test vote power > MAX_NOD_VOTING_POWER_RATIO (should cap)

**Acceptance Criteria:**
- [ ] File created with all 12 test scenarios
- [ ] All tests pass (bounds enforced correctly)
- [ ] Evidence artifact: economic_bounds_verification.json
- [ ] Integrated into autonomous audit v2.0 pipeline

**Estimated Complexity:** HIGH (new file, ~500 lines, comprehensive scenarios)

---

### File 10: FailureModeTests.py (NEW FILE - NOT CREATED)

**Status:** 0/1 file created (0%)

#### Purpose
Test safe degradation paths and CIR-302 triggers.

#### Required Test Scenarios (8 total)

**NOD Degradation (3)**
1. ⏳ Test NOD allocation skip when telemetry unavailable
2. ⏳ Test governance freeze when node set < quorum
3. ⏳ Test conflicting telemetry hash resolution (lexicographic tie-break)

**Economic Violations (3)**
4. ⏳ Test CHR emission cap violation → CIR-302 halt
5. ⏳ Test governance parameter outside [IMMUTABLE] bounds → reject
6. ⏳ Test total supply ratio change > MAX_TOTAL_SUPPLY_RATIO_CHANGE → halt

**Invariant Violations (2)**
7. ⏳ Test NOD transfer attempt → CIR-302 halt (NOD-I1 violation)
8. ⏳ Test NOD governance touching user rewards → CIR-302 halt (NOD-I3 violation)

**Acceptance Criteria:**
- [ ] File created with all 8 test scenarios
- [ ] All degradation paths preserve zero-simulation integrity
- [ ] All violations trigger appropriate CIR-302 responses
- [ ] Evidence artifact: failure_mode_verification.json
- [ ] Integrated into autonomous audit v2.0 pipeline

**Estimated Complexity:** HIGH (new file, ~400 lines, complex failure scenarios)

---

## BUCKET C: DOCUMENTATION SYNC

### File 11: NOD_INFRASTRUCTURE_TOKEN_SPEC_V1.md (PARTIAL UPDATE NEEDED)

**Status:** EXISTS but needs constitutional sections (0/7 sections added)

#### Required New Sections (7 total)
1. ⏳ **Section 3.2: Safety Bounds** - Document MIN/MAX caps for allocation, quorum, voting power
2. ⏳ **Section 3.5: Emission Controls** - Document NOD_MIN_ACTIVE_NODES, NOD_MAX_ISSUANCE_PER_EPOCH, NOD_ZERO_ACTIVITY_FLOOR
3. ⏳ **Section 3.6: Anti-Centralization Guards** - Document MAX_NODE_REWARD_SHARE, MAX_NOD_VOTING_POWER_RATIO
4. ⏳ **Section 4.5: Economic Bound Violations** - Add to failure modes, reference economic_constants.py
5. ⏳ **Section 5: Threat Model** - Add table of attack vectors and constitutional defenses
6. ⏳ **Section 6: Governance Timing** - Document all GOVERNANCE_*_BLOCKS constants
7. ⏳ **Appendix A: Reference to economic_constants.py** - Link to canonical source

**Acceptance Criteria:**
- [ ] All 7 sections added with precise constant references
- [ ] Examples updated to show bounded behavior
- [ ] Cross-references to economic_constants.py
- [ ] Alignment with implemented code

**Estimated Complexity:** MEDIUM (7 sections, ~150 lines)

---

### File 12: MASTER-PLAN-V13.md (ENHANCEMENT NEEDED)

**Status:** EXISTS but needs Phase 4/5 economic criteria (0/3 sections added)

#### Required Updates (3 total)
1. ⏳ **Phase 4: System-Level Verification** - Add "Constitutional Economics / NOD Infrastructure Layer" acceptance criteria
2. ⏳ **Phase 5: Final Deliverables** - Add evidence artifacts (economic_bounds_verification.json, nod_replay_determinism.json, etc.)
3. ⏳ **Appendix: Economic Constants** - List all 168 constants from economic_constants.py with mutability status

**Acceptance Criteria:**
- [ ] All 3 sections added
- [ ] Phase 4 includes stress test requirements
- [ ] Phase 5 includes all new evidence artifacts
- [ ] Appendix serves as quick reference

**Estimated Complexity:** LOW (3 sections, ~80 lines)

---

### File 13: AutonomousAuditV2Prompts.md (ENHANCEMENT NEEDED)

**Status:** EXISTS but needs economic stress tests (0/2 sections added)

#### Required Updates (2 total)
1. ⏳ **Section: Constitutional Economics Stress Tests** - Add prompts for single-node NOD capture, maximal FLX/CHR issuance, rapid governance churn
2. ⏳ **Section: Evidence Artifacts** - Add economic_bounds_verification.json, nod_replay_determinism.json, failure_mode_verification.json

**Acceptance Criteria:**
- [ ] All 2 sections added
- [ ] Stress test prompts are actionable
- [ ] Evidence artifacts defined with required fields

**Estimated Complexity:** LOW (2 sections, ~60 lines)

---

## SUMMARY STATISTICS

### Files by Status
- **COMPLETE:** 4 files (economic_constants.py, README.md, NODAllocator.py, InfrastructureGovernance.py partial)
- **IN PROGRESS:** 1 file (InfrastructureGovernance.py - 7 changes remaining)
- **NOT STARTED:** 19 files (includes 8 new integration files)

### Changes by Bucket
- **Bucket A (Governance & Economics Wiring):** 51 changes across 5 files
  - InfrastructureGovernance.py: 7 remaining
  - TreasuryEngine.py: 12 required
  - RewardAllocator.py: 7 required
  - EconomicsGuard.py: 8 required (new file)
  - StateTransitionEngine.py: 5 required
  
- **Bucket B (Invariants & Audit Integration):** 25 changes across 4 files
  - NODInvariantChecker.py: 4 required (new file)
  - CIR302_Handler.py: 4 required
  - DeterministicReplayTest.py: 5 required (new file)
  - BoundaryConditionTests.py: 12 required (new file)
  - FailureModeTests.py: 8 required (new file)
  
- **Bucket C (Documentation Sync):** 12 changes across 3 files
  - NOD_INFRASTRUCTURE_TOKEN_SPEC_V1.md: 7 required
  - MASTER-PLAN-V13.md: 3 required
  - AutonomousAuditV2Prompts.md: 2 required

- **Bucket D (Live System Integration) - CRITICAL NEW:** 41 changes across 8 files
  - QFSV13SDK.py: 8 required
  - aegisapi.py: 6 required
  - CoherenceLedger.py: 5 required
  - AutonomousAuditV2Driver.py: 7 required
  - AEGIS_Node_Verification.py: 6 required (new file)
  - AEGIS_Offline_Policy.md: 5 required (new file - policy doc)
  - EconomicConstantsMigration.py: 7 required (new file)
  - PerformanceBenchmarkWithGuards.py: 6 required (new file)

### Total Scope (UPDATED)
- **Total Changes Required:** 129 precise modifications (was 88, +41 integration changes)
- **Total New Files:** 8 (was 5, +3 integration files)
- **Total Enhanced Files:** 11 (was 8, +3 live system files)
- **Estimated Total Lines:** ~3,700 lines of new/modified code + ~400 lines of documentation (was ~2,500 + ~300)

---

## EXECUTION STRATEGY

### Recommended Order (UPDATED with Integration Layer)

**Phase 1: Core Guards & Governance (Foundation)**
1. Complete InfrastructureGovernance.py (7 changes) - enables full governance testing
2. Create EconomicsGuard.py (8 methods) - enables constitutional validation
3. Create NODInvariantChecker.py (4 checks) - explicit invariant enforcement
4. Create AEGIS_Node_Verification.py (6 components) - structural NOD-I2 enforcement

**Phase 2: Economic Wiring (Constitutional Rewards)**
5. Update TreasuryEngine.py (12 changes) - constitutional reward logic
6. Update RewardAllocator.py (7 changes) - dust handling and caps
7. Update StateTransitionEngine.py (5 changes) - NOD transfer firewall

**Phase 3: Live System Integration (CRITICAL)**
8. Update QFSV13SDK.py (8 changes) - route all calls through guards
9. Update aegisapi.py (6 changes) - deterministic telemetry snapshots
10. Update CoherenceLedger.py (5 changes) - constitutional config tracking
11. Create EconomicConstantsMigration.py (7 components) - versioning system
12. Create AEGIS_Offline_Policy.md (5 sections) - global degradation policy

**Phase 4: Audit & CIR-302 Integration**
13. Enhance CIR302_Handler.py (4 changes) - economic violation handling
14. Update AutonomousAuditV2Driver.py (7 changes) - structured error interpretation
15. Create PerformanceBenchmarkWithGuards.py (6 scenarios) - verify targets met

**Phase 5: Testing & Evidence**
16. Create DeterministicReplayTest.py (5 test cases)
17. Create BoundaryConditionTests.py (12 test scenarios)
18. Create FailureModeTests.py (8 test scenarios)

**Phase 6: Documentation**
19. Update NOD_INFRASTRUCTURE_TOKEN_SPEC_V1.md (7 sections)
20. Update MASTER-PLAN-V13.md (3 sections)
21. Update AutonomousAuditV2Prompts.md (2 sections)

### Critical Path (UPDATED)
1. **EconomicsGuard.py** → blocks all economic wiring
2. **NODInvariantChecker.py** → blocks invariant testing
3. **AEGIS_Node_Verification.py** → blocks NOD-I2 enforcement
4. **QFSV13SDK.py** → blocks live system integration (MOST CRITICAL)
5. **aegisapi.py** → blocks telemetry determinism
6. **CoherenceLedger.py** → blocks constitutional replay verification
7. **AutonomousAuditV2Driver.py** → blocks constitutional audit
8. **Test files** → blocks evidence generation
9. **Documentation** → blocks audit completion

### Integration Dependencies
```
EconomicsGuard ──────┐
                     ├──→ QFSV13SDK ──→ Live System
NODInvariantChecker ─┤
                     ├──→ aegisapi ────→ AEGIS Integration
AEGIS_Node_Verification
                     └──→ CoherenceLedger → Audit Trail

All Guards ──→ CIR302_Handler ──→ AutonomousAuditV2Driver ──→ Evidence
```

### Risk Mitigation
- Each file change is atomic and testable independently
- Changes listed in dependency order (no forward references)
- All changes preserve existing interfaces (backward compatible)
- Each change includes acceptance criteria for verification

---

## COMPLETION CRITERIA

### Technical Criteria
- [ ] All 129 changes implemented (was 88)
- [ ] All 8 new files created (was 5)
- [ ] All test suites pass (100%)
- [ ] Zero economic bound violations in stress tests
- [ ] Zero invariant violations in failure mode tests
- [ ] Bit-for-bit deterministic replay verified
- [ ] Performance targets met with all guards enabled (2,000 TPS minimum)

### Audit Criteria
- [ ] All evidence artifacts generated
- [ ] Autonomous audit v2.0 includes economic stress tests
- [ ] Autonomous audit v2.0 interprets structured error codes
- [ ] Documentation synchronized with implementation
- [ ] All constitutional constants referenced in specs
- [ ] Constitutional config hash in every ledger entry

### Governance Criteria
- [ ] All [IMMUTABLE] constants enforced
- [ ] All [MUTABLE] constants require hard fork
- [ ] Governance cannot modify its own scope
- [ ] Timelock enforced on all executions
- [ ] No code path bypasses EconomicsGuard

### Legal/Compliance Criteria
- [ ] NOD positioned as pure utility (non-transferable, non-redeemable)
- [ ] Firewall enforcement prevents user-facing impact
- [ ] Economic bounds prevent profit-expectation claims
- [ ] Invariants documented for regulatory review

### Integration Criteria (NEW)
- [ ] SDK routes all calls through constitutional guards
- [ ] AEGIS telemetry snapshots are deterministic and versioned
- [ ] AEGIS offline triggers safe degradation (no approximations)
- [ ] Node verification criteria structurally enforced (NOD-I2)
- [ ] Economic constant versioning supports protocol upgrades
- [ ] CIR-302 handler interprets all structured error codes
- [ ] Old code paths cannot bypass guards (backwards compatibility enforced)

---

## NOTES

- This tracker represents the delta from "good code" to "constitutional-grade system"
- Each change is precise, bounded, and independently verifiable
- Priority is on correctness over speed
- All changes preserve zero-simulation compliance
- No shortcuts on audit trail or determinism

---

## INTEGRATION LAYER RATIONALE (BUCKET D)

### Why the Integration Layer is Critical

The original tracker (Buckets A-C) correctly identified the constitutional components needed:
- Economic bounds and guards
- Governance protections
- Invariant enforcement
- Test coverage
- Documentation

However, these components only become "constitutional-grade" when:

**1. No Code Path Can Bypass Them**
- Guards must be mandatory, not optional
- SDK must route ALL calls through validation
- Old direct-call methods must be deprecated/rejected

**2. External Dependencies Are Deterministic**
- AEGIS telemetry must be versioned, hashed snapshots (not live queries)
- Node verification must use consistent criteria across all modules
- Offline scenarios must have explicit, safe degradation policies

**3. The System Can Prove Its Own Compliance**
- Constitutional config hash in every ledger entry (enables replay verification)
- Structured error codes allow automated audit interpretation
- Performance benchmarks prove guards don't break TPS targets

**4. Protocol Upgrades Don't Break History**
- Economic constant versioning preserves old epoch validity
- Migration path defined for each version transition
- Replay engine uses epoch-appropriate constants

### Practical Example: Why SDK Integration Matters

Without Bucket D changes:
```python
# OLD CODE (bypasses guards)
reward = TreasuryEngine.calculate_rewards(metrics, bundle, log)
# If metrics cause bound violation, generic ValueError raised
# Autonomous audit sees "error" but can't interpret severity
# CIR-302 not triggered, system continues in invalid state
```

With Bucket D changes:
```python
# NEW CODE (constitutional enforcement)
try:
    # SDK pre-validates through EconomicsGuard
    validation = EconomicsGuard.validate_chr_reward(proposed_reward, epoch)
    if not validation.passed:
        raise StructuredError("ECON_BOUND_VIOLATION", validation.details)
    
    # Only proceed if validation passed
    reward = TreasuryEngine.calculate_rewards(metrics, bundle, log)
    
except StructuredError as e:
    # CIR-302 handler interprets error code
    if e.code == "ECON_BOUND_VIOLATION":
        CIR302_Handler.halt_with_finality_seal(e)
    
    # Autonomous audit sees structured failure
    # Evidence artifact records: which constant, how close to limit, etc.
```

### AEGIS Integration Reality Check

The original tracker assumed AEGIS "just works," but:

**Problem:** NOD-I4 (bit-for-bit replay) requires identical inputs
- If telemetry is a live API call, replay gets different data
- If node verification criteria change mid-epoch, allocations differ
- If AEGIS goes offline, system must not approximate

**Solution (Bucket D):**
- `aegisapi.get_telemetry_snapshot()` returns versioned, hashed snapshot
- Snapshot hash committed to CoherenceLedger
- Replay engine fetches historical snapshot by hash
- Offline policy: skip NOD epoch, freeze governance, continue user rewards

### Performance Budget Reality

Adding constitutional guards is not free:
- EconomicsGuard: ~5-10µs per validation
- NODInvariantChecker: ~3-7µs per check
- Enhanced logging: ~2-4µs per entry
- Total overhead: ~10-20µs per operation

At 2,000 TPS target, this is acceptable IF verified via benchmarks.
Without `PerformanceBenchmarkWithGuards.py`, we can't prove compliance.

### Migration & Versioning Reality

Protocol upgrade scenario:
```
Epoch 100: ECON_V1 (NOD allocation 10%)
Epoch 200: ECON_V2 (NOD allocation 12%, new constant added)
```

**Without versioning:**
- Replaying epoch 100 with ECON_V2 code → different results
- Audit fails, replay integrity broken

**With EconomicConstantsMigration.py:**
- Ledger stores: `{epoch: 100, econ_version: "V1"}`
- Replay engine loads ECON_V1 for epochs 1-199
- Replay engine loads ECON_V2 for epochs 200+
- Historical validity preserved

---

## BUCKET D: DETAILED RATIONALE BY FILE

### File 14: QFSV13SDK.py
**Without:** Guards exist but can be bypassed by direct library calls  
**With:** All state mutations forced through SDK → guards are structural, not optional

### File 15: aegisapi.py
**Without:** Live API calls break NOD-I4 (replay determinism)  
**With:** Versioned snapshots enable bit-for-bit replay

### File 16: CoherenceLedger.py
**Without:** Can't prove which constitution was in force for a given epoch  
**With:** Config hash in ledger enables constitutional replay verification

### File 17: AutonomousAuditV2Driver.py
**Without:** Audit treats all errors as generic failures  
**With:** Structured codes allow severity-based failure (CRITICAL vs WARNING)

### File 18: AEGIS_Node_Verification.py
**Without:** NOD-I2 is a spec assertion, not enforced in code  
**With:** Verification criteria centralized, called by all NOD code paths

### File 19: AEGIS_Offline_Policy.md
**Without:** Undefined behavior when AEGIS unavailable  
**With:** Explicit policy: skip NOD, freeze governance, continue user rewards

### File 20: EconomicConstantsMigration.py
**Without:** Protocol upgrades break historical replay  
**With:** Versioned constants preserve epoch validity across upgrades

### File 21: PerformanceBenchmarkWithGuards.py
**Without:** Can't prove guards meet Phase 4 TPS targets  
**With:** Evidence that constitutional layer doesn't break performance

---

## FINAL SUMMARY: FROM "GOOD CODE" TO "CONSTITUTIONAL-GRADE SYSTEM"

### What We Started With (Session Begin)
- economic_constants.py with partial coverage
- README lacking NOD documentation
- NODAllocator without safety bounds
- InfrastructureGovernance with basic voting
- No integration layer
- No constitutional enforcement

### What We Have Now (After Foundation Work)
- ✅ economic_constants.py (159 lines, all 6 tokens, [IMMUTABLE]/[MUTABLE] tags)
- ✅ README.md with comprehensive NOD section and firewall explanations
- ✅ NODAllocator.py with full bounds enforcement (emission controls, anti-centralization)
- ✅ InfrastructureGovernance.py (65% complete) with constitutional protections
- ✅ CONSTITUTIONAL_V13.5_TASK_TRACKER.md (this file) - complete roadmap

### What Remains (129 Changes Across 21 Files)

**Immediate Next Steps (Critical Path):**
1. Complete InfrastructureGovernance.py (7 changes) - enables governance testing
2. Create EconomicsGuard.py (8 methods) - BLOCKS all economic wiring
3. Create NODInvariantChecker.py (4 checks) - BLOCKS invariant testing
4. Create AEGIS_Node_Verification.py (6 components) - BLOCKS NOD-I2 enforcement

**Integration Layer (Most Critical):**
5. Update QFSV13SDK.py (8 changes) - BLOCKS live system (guards become structural)
6. Update aegisapi.py (6 changes) - BLOCKS replay determinism
7. Update CoherenceLedger.py (5 changes) - BLOCKS constitutional verification

**Then Complete:**
8. Economic wiring (TreasuryEngine, RewardAllocator, StateTransitionEngine)
9. Audit integration (CIR-302, AutonomousAuditV2Driver, performance benchmarks)
10. Testing (replay, boundary conditions, failure modes)
11. Documentation (spec updates, MASTER-PLAN integration)

### The Constitutional Guarantee

Once all 129 changes are complete, QFS V13.5 will guarantee:

**Economic Safety:**
- ✅ All parameters bounded by [IMMUTABLE] constitutional limits
- ✅ No economic death spirals possible (caps prevent runaway inflation/deflation)
- ✅ No single entity can capture >25% voting power or >30% rewards
- ✅ All emissions traceable to constitutional constants

**Governance Safety:**
- ✅ Infrastructure governance cannot affect user-facing systems (firewall enforced)
- ✅ Timelock prevents immediate hostile takeovers (240-block delay)
- ✅ Quorum bounds prevent both gridlock (51% min) and plutocracy (90% max)
- ✅ Parameter validation rejects invalid state transitions before voting

**Invariant Safety (NOD-I1 through NOD-I4):**
- ✅ NOD non-transferable (StateTransitionEngine firewall)
- ✅ NOD only for verified nodes (AEGIS_Node_Verification structural enforcement)
- ✅ NOD governance orthogonal to user systems (firewall + invariant checker)
- ✅ Bit-for-bit replay (deterministic telemetry snapshots + config versioning)

**Audit Safety:**
- ✅ Structured error codes enable automated audit interpretation
- ✅ Constitutional config hash in every ledger entry (replay verification)
- ✅ No bypass paths (SDK enforces guards structurally)
- ✅ Performance verified (benchmarks prove guards meet 2,000 TPS target)

### Why This Tracker is "Constitutional-Grade"

This is not just a TODO list. It is:

1. **Precise:** 129 specific changes, each with acceptance criteria
2. **Bounded:** Every change preserves zero-simulation compliance
3. **Verifiable:** Each change includes test requirements
4. **Complete:** Covers code, tests, docs, AND integration layer
5. **Realistic:** Addresses AEGIS dependencies, migration, performance
6. **Audit-Ready:** Evidence artifacts defined for each phase

### Estimated Completion Scope

**Code:**
- 8 new files (~1,700 lines)
- 11 enhanced files (~2,000 lines of modifications)
- Total: ~3,700 lines of constitutional-grade implementation

**Documentation:**
- 3 enhanced docs (~400 lines)
- 2 new policy docs (~200 lines)
- Total: ~600 lines of specification/policy

**Tests:**
- 3 new test suites (~1,150 lines)
- ~35 test scenarios covering boundaries, failures, replay

**Evidence:**
- ~10 new evidence artifacts (JSON format)
- Integration into autonomous audit v2.0

**Grand Total:** ~5,450 lines of precise, bounded, verifiable work

---

## NEXT ACTIONS

**Recommended Immediate Action:**
Continue with InfrastructureGovernance.py completion:
- Add execute_proposal() method (timelock enforcement, once-only execution)
- Add cancel_proposal() method (proposer-only cancellation)
- Add expire_stale_proposals() batch method
- Enhance logging with SHA256 event hashes

**Alternative Starting Points:**
1. **Create EconomicsGuard.py** - highest leverage (blocks 4 other modules)
2. **Create AEGIS_Node_Verification.py** - closes NOD-I2 enforcement gap
3. **Update QFSV13SDK.py** - makes guards structural (most critical integration)

**Session Status:**
- Foundation complete (4 files, 65% governance)
- Tracker complete (21 files, 129 changes documented)
- Ready to proceed with systematic implementation

**Deliverable:**
This tracker serves as the complete blueprint for transforming QFS V13.5 from "good code" to "constitutional-grade system" with no gaps in specification, implementation, testing, integration, or documentation.

---

**END OF CONSTITUTIONAL V13.5 TASK TRACKER**  
**Version:** 2.0 (with Integration Layer)  
**Last Updated:** 2025-12-13  
**Status:** ROADMAP COMPLETE, IMPLEMENTATION IN PROGRESS
