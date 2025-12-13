# QFS V13.6 Release Task Tracker
# Constitutional Integration & Operational Deployment

**Release Name:** QFS V13.6 - Constitutional Integration Release  
**Status:** IN PROGRESS  
**Start Date:** 2025-12-13  
**Target Completion:** TBD (no time schedule - precision over speed)

---

## Executive Summary

### Release Theme

**V13.5 Achievement:** Defined and documented the constitutional layer  
**V13.6 Mission:** Operationalize the constitution in the real (AEGIS-backed) world

### Core Transition

```
V13.5 = Constitutional Foundation (Define & Enforce)
  ✅ economic_constants.py with bounded parameters
  ✅ NODAllocator.py with anti-centralization guards
  ✅ InfrastructureGovernance.py (65% complete) with protections
  ✅ Constitutional task tracker (129 changes documented)

V13.6 = Operational Integration (Run in Real World)
  🎯 Fully guarded economics (no bypass paths)
  🎯 Enforced invariants (NOD-I1 through NOD-I4)
  🎯 Deterministic AEGIS integration (replayable telemetry)
  🎯 Migration plan (pre-constitution → V13.6)
  🎯 Performance validation (2,000 TPS with guards enabled)
```

### Success Criteria

By end of V13.6 release, QFS achieves:
- ✅ **Constitutional Compliance:** All economic operations bounded by [IMMUTABLE] constants
- ✅ **Structural Safety:** Guards are mandatory, not optional (SDK enforced)
- ✅ **AEGIS Integration:** Node verification + telemetry snapshots deterministic
- ✅ **Replay Integrity:** Bit-for-bit deterministic given identical inputs
- ✅ **Performance Verified:** 2,000 TPS minimum with all guards enabled
- ✅ **Migration Ready:** Clean path from V13.5 to V13.6 for existing ledgers

---

## Phase 1: V13.5 Delta Closure (Stabilization)

**Goal:** Complete all V13.5 constitutional backlog so V13.6 starts clean

**Status:** 4/9 components complete (44%)

### Component 1.1: InfrastructureGovernance.py Completion ✅ CRITICAL

**Current Status:** 13/20 changes complete (65%)  
**Remaining:** 7 changes  
**Blocks:** Phase 2 governance integration, Phase 4 governance replay tests

#### Tasks (7 remaining)

1. ⏳ **execute_proposal() method**
   - Enforce timelock (check current_timestamp >= execution_earliest_timestamp)
   - Enforce once-only execution (check executed flag, set after execution)
   - Mutate infrastructure config state (not code)
   - Emit irreversible log entry with SHA-256 event hash
   - Return execution result for ledger entry
   - **Acceptance:** Proposal cannot execute before timelock expires, double-execution rejected

2. ⏳ **cancel_proposal() method**
   - Allow only proposer to cancel ACTIVE proposals
   - Reject cancellation of PASSED/REJECTED/EXECUTED proposals
   - Update status to CANCELLED
   - Emit cancellation log with SHA-256 event hash
   - **Acceptance:** Only proposer can cancel, only ACTIVE proposals cancellable

3. ⏳ **expire_stale_proposals() batch method**
   - Deterministically mark proposals EXPIRED if voting window passed
   - Process all proposals in sorted order (deterministic iteration)
   - Emit expiry log for each expired proposal with SHA-256 event hash
   - **Acceptance:** Stale proposals automatically expired, deterministic order

4. ⏳ **Update _log_vote() signature**
   - Add `capped: bool` parameter (was vote weight capped?)
   - Add SHA-256 event hash of vote details
   - Include capped status in log entry
   - **Acceptance:** Vote logs show cap application, event hash for Merkle inclusion

5. ⏳ **Update _log_proposal_creation()**
   - Add SHA-256 event hash of proposal details
   - Include total_nod_supply_snapshot in log
   - Include execution_earliest_timestamp in log
   - **Acceptance:** Proposal logs include snapshot and timelock, event hash present

6. ⏳ **Update _log_tally_result()**
   - Add SHA-256 event hash of tally details
   - Include quorum calculation details
   - Include execution eligibility status
   - **Acceptance:** Tally logs show quorum math, execution timing, event hash

7. ⏳ **Update test_infra_governance() function**
   - Test happy path: create → vote → pass → execute
   - Test double-vote rejection
   - Test vote weight capping
   - Test timelock enforcement
   - Test cancellation (proposer-only)
   - Test expiry (stale proposals)
   - Test parameter validation rejection
   - **Acceptance:** All 7 scenarios pass, event hashes verified

**Exit Criteria:**
- [ ] All 7 changes implemented
- [ ] All 7 test scenarios passing
- [ ] InfrastructureGovernance.py at 100% completion
- [ ] Evidence artifact: infra_governance_completion_report.json

**Estimated Effort:** MEDIUM (7 changes, ~150 lines, 7 test scenarios)

---

### Component 1.2: EconomicsGuard.py Creation ✅ CRITICAL

**Current Status:** 0/1 file created (0%)  
**Blocks:** ENTIRE economic wiring layer (TreasuryEngine, RewardAllocator, NODAllocator, SDK)

#### Purpose
Centralized constitutional bounds validator called by ALL modules before economic mutations.

#### Implementation Structure

```python
# File: src/libs/economics/EconomicsGuard.py

from typing import Dict, Any, Optional
from dataclasses import dataclass
from src.libs.math.BigNum128 import BigNum128
from src.libs.math.CertifiedMath import CertifiedMath
from src.libs.economics.economic_constants import *

@dataclass
class ValidationResult:
    """Result of constitutional validation check."""
    passed: bool
    error_code: Optional[str] = None  # ECON_BOUND_VIOLATION, GOV_SAFETY_VIOLATION, etc.
    details: Optional[Dict[str, Any]] = None
    proximity_to_limit: Optional[str] = None  # e.g., "CHR reward at 95% of cap"

class EconomicsGuard:
    """
    Constitutional economic bounds validator.
    
    All state-changing economic operations MUST pass through this guard.
    Returns structured ValidationResult with error codes for CIR-302 integration.
    """
    
    def __init__(self, cm_instance: CertifiedMath):
        self.cm = cm_instance
    
    # 8 validation methods (detailed below)
```

#### Tasks (8 methods to implement)

1. ⏳ **validate_chr_reward()**
   - Check CHR_MIN_REWARD_PER_ACTION <= reward <= CHR_MAX_REWARD_PER_ACTION
   - Check cumulative daily emissions against CHR_DAILY_EMISSION_CAP
   - Check total supply against CHR_SATURATION_THRESHOLD
   - Apply CHR_DECAY_RATE based on epoch number
   - Return ValidationResult with proximity tracking
   - **Acceptance:** All CHR bounds enforced, structured errors on violation

2. ⏳ **validate_flx_reward()**
   - Check MIN_FLX_REWARD_FRACTION <= fraction <= MAX_FLX_REWARD_FRACTION
   - Check per-user allocation against FLX_MAX_PER_USER
   - Check total supply against FLX_SATURATION_THRESHOLD
   - Apply FLX_DECAY_RATE based on epoch number
   - **Acceptance:** All FLX bounds enforced, per-user caps applied

3. ⏳ **validate_nod_allocation()**
   - Check MIN_NOD_ALLOCATION_FRACTION <= fraction <= MAX_NOD_ALLOCATION_FRACTION
   - Check epoch issuance against NOD_MAX_ISSUANCE_PER_EPOCH
   - Check per-node allocation against MAX_NODE_REWARD_SHARE
   - Check total voting power against MAX_NOD_VOTING_POWER_RATIO
   - Enforce NOD_MIN_ACTIVE_NODES requirement
   - **Acceptance:** All NOD bounds enforced, anti-centralization guards active

4. ⏳ **validate_governance_change()**
   - Check quorum threshold against MIN/MAX_QUORUM_THRESHOLD
   - Check allocation fraction changes against bounds
   - Reject changes to [IMMUTABLE] constants
   - Validate proposal parameters via type-specific rules
   - **Acceptance:** [IMMUTABLE] constants protected, [MUTABLE] within bounds

5. ⏳ **validate_emission_rate()**
   - Check total emission against MAX_TOTAL_SUPPLY_RATIO_CHANGE per epoch
   - Check single event impact against MAX_SINGLE_EVENT_IMPACT
   - Apply decay rates (CHR_DECAY_RATE, FLX_DECAY_RATE, PSI_DECAY_RATE)
   - **Acceptance:** System-wide emission caps enforced, no economic shocks

6. ⏳ **validate_supply_change()**
   - Check delta against token-specific saturation thresholds
   - Check cross-token balance constraints
   - Validate reserve management (RES_TARGET_RATIO, RES_MAX_DRAW_PER_EPOCH)
   - **Acceptance:** No unbounded supply growth, reserves managed

7. ⏳ **validate_psi_accumulation()**
   - Check PSI total against PSI_SATURATION_CAP
   - Validate PSI penalty thresholds
   - Apply PSI_DECAY_RATE
   - **Acceptance:** PSI accumulation bounded, penalties deterministic

8. ⏳ **validate_atr_usage()**
   - Check ATR base costs against ATR_BASE_COST_*
   - Validate abuse threshold detection
   - Check decay rate application
   - **Acceptance:** ATR costs deterministic, abuse detection bounded

**Additional Requirements:**

9. ⏳ **Structured error codes**
   - ECON_BOUND_VIOLATION_CHR_MIN
   - ECON_BOUND_VIOLATION_CHR_MAX
   - ECON_BOUND_VIOLATION_CHR_DAILY_CAP
   - ECON_BOUND_VIOLATION_FLX_FRACTION
   - ECON_BOUND_VIOLATION_NOD_ALLOCATION
   - GOV_SAFETY_VIOLATION_IMMUTABLE
   - GOV_SAFETY_VIOLATION_QUORUM
   - (20+ total codes defined)

10. ⏳ **CIR-302 integration**
    - Map all error codes to severity levels (CRITICAL, WARNING, INFO)
    - Provide violation details for AEGIS_FINALITY_SEAL
    - Enable audit interpretation of violations

**Exit Criteria:**
- [ ] File created with all 8 validation methods
- [ ] All 20+ structured error codes defined
- [ ] Returns ValidationResult with proximity tracking
- [ ] Unit tests cover all validation paths (100+ test cases)
- [ ] Integration stubs for TreasuryEngine, RewardAllocator, NODAllocator
- [ ] Evidence artifact: economics_guard_validation_matrix.json

**Estimated Effort:** HIGH (new file, ~300 lines, 8 methods, 100+ tests, critical integration)

---

### Component 1.3: NODInvariantChecker.py Creation ✅ CRITICAL

**Current Status:** 0/1 file created (0%)  
**Blocks:** NOD invariant enforcement, Phase 4 invariant violation tests

#### Purpose
Explicit runtime encoding of NOD-I1 through NOD-I4 constitutional invariants.

#### Implementation Structure

```python
# File: src/libs/governance/NODInvariantChecker.py

from typing import Dict, Any, Optional
from dataclasses import dataclass
from src.libs.math.BigNum128 import BigNum128

@dataclass
class InvariantResult:
    """Result of invariant check."""
    passed: bool
    invariant_id: str  # NOD-I1, NOD-I2, NOD-I3, NOD-I4
    error_code: Optional[str] = None  # INVARIANT_VIOLATION_*
    details: Optional[Dict[str, Any]] = None

class NODInvariantChecker:
    """
    Enforces NOD V1 constitutional invariants.
    
    Invariants:
    - NOD-I1: No transfers between entities (allocation-only)
    - NOD-I2: NOD balances only for verified AEGIS node keys
    - NOD-I3: NOD governance never alters user-facing logic
    - NOD-I4: Bit-for-bit replay given identical inputs
    """
    
    def __init__(self, node_verifier):
        self.node_verifier = node_verifier  # AEGIS_Node_Verification instance
    
    # 4 invariant check methods (detailed below)
```

#### Tasks (4 invariant checks + integration)

1. ⏳ **check_nod_i1_no_transfer()**
   - Assert all NOD state changes originate from NODAllocator only
   - Reject any transfer between user addresses
   - Detect unauthorized NOD delta in TokenStateBundle
   - Emit INVARIANT_VIOLATION_NOD_I1_TRANSFER on violation
   - **Acceptance:** NOD transfers impossible outside allocator

2. ⏳ **check_nod_i2_node_keys_only()**
   - Assert all NOD balance holders pass node verification
   - Query AEGIS_Node_Verification for each NOD recipient
   - Reject allocations to unverified keys
   - Emit INVARIANT_VIOLATION_NOD_I2_UNVERIFIED on violation
   - **Acceptance:** No NOD to non-node addresses

3. ⏳ **check_nod_i3_no_user_impact()**
   - Assert governance outcomes only mutate infrastructure config
   - Detect any changes to reward logic, user token balances, content policy
   - Reject governance proposals touching user-facing systems
   - Emit INVARIANT_VIOLATION_NOD_I3_USER_IMPACT on violation
   - **Acceptance:** NOD governance firewall enforced

4. ⏳ **check_nod_i4_replay_determinism()**
   - Compare output hash against expected hash from identical inputs
   - Verify telemetry snapshot consistency
   - Check config version consistency
   - Emit INVARIANT_VIOLATION_NOD_I4_REPLAY on mismatch
   - **Acceptance:** Replay produces identical outputs

5. ⏳ **Integration into StateTransitionEngine**
   - Call check_nod_i1_no_transfer() on every state transition
   - Halt with CIR-302 on violation

6. ⏳ **Integration into NODAllocator**
   - Call check_nod_i2_node_keys_only() before allocation
   - Call check_nod_i4_replay_determinism() after allocation

7. ⏳ **Integration into InfrastructureGovernance**
   - Call check_nod_i2_node_keys_only() on vote casting
   - Call check_nod_i3_no_user_impact() on proposal execution

**Exit Criteria:**
- [ ] File created with all 4 invariant check methods
- [ ] All 3 integration points implemented
- [ ] Invariant violations trigger CIR-302 halt
- [ ] Unit tests cover all 4 invariants (violation + pass scenarios)
- [ ] Evidence artifact: nod_invariant_verification.json

**Estimated Effort:** HIGH (new file, ~250 lines, deep integration, critical invariants)

---

### Component 1.4: StateTransitionEngine NOD Firewall

**Current Status:** 0/5 changes complete (0%)  
**Blocks:** NOD-I1 structural enforcement

#### Tasks (5 changes)

1. ⏳ **Add NOD_TRANSFER_FORBIDDEN check**
   - Detect any NOD delta in apply_transition() outside authorized callers
   - Check caller against authorized_allocators list

2. ⏳ **Reject unauthorized NOD mutations**
   - Emit INVARIANT_VIOLATION_NOD_I1_TRANSFER
   - Trigger CIR-302 halt

3. ⏳ **Add authorized_allocator parameter**
   - Accept list of authorized modules (NODAllocator, InfrastructureGovernance)
   - Default to empty list (reject all NOD changes)

4. ⏳ **Integration with NODInvariantChecker**
   - Call NODInvariantChecker.check_nod_i1_no_transfer()
   - Pass violation details to CIR-302

5. ⏳ **Test unauthorized transfer attempts**
   - Test user-to-user NOD transfer → rejection
   - Test direct TreasuryEngine NOD mutation → rejection
   - Test NODAllocator mutation → pass

**Exit Criteria:**
- [ ] All 5 changes implemented
- [ ] NOD transfers structurally impossible outside allocator
- [ ] Test suite covers bypass attempts
- [ ] Integration with NODInvariantChecker complete

**Estimated Effort:** MEDIUM (5 changes, ~80 lines, structural enforcement)

---

### Component 1.5: CIR302_Handler Economic Violations

**Current Status:** 0/4 changes complete (0%)  
**Blocks:** Economic violation auditing, CIR-302 integration

#### Tasks (4 changes)

1. ⏳ **Add economic_bound_violation() handler**
   - Accept ValidationResult from EconomicsGuard
   - Generate AEGIS_FINALITY_SEAL with economic violation details
   - Include: which constant violated, proximity to limit, attempted value

2. ⏳ **Add governance_safety_violation() handler**
   - Accept ValidationResult from governance checks
   - Include: proposal details, parameter attempted, constitutional limit

3. ⏳ **Map structured error codes**
   - ECON_BOUND_VIOLATION → CRITICAL severity
   - GOV_SAFETY_VIOLATION → CRITICAL severity
   - INVARIANT_VIOLATION_* → CRITICAL severity + immediate halt

4. ⏳ **Enhanced AEGIS_FINALITY_SEAL**
   - Add economic_violation section
   - Add governance_violation section
   - Add invariant_violation section
   - Include constitutional config hash at time of violation

**Exit Criteria:**
- [ ] All 4 changes implemented
- [ ] Economic violations generate enhanced finality seals
- [ ] Test suite covers all violation types
- [ ] Evidence artifact: cir302_economic_violations_test.json

**Estimated Effort:** MEDIUM (4 changes, ~100 lines, CIR-302 integration)

---

## Phase 1 Summary

**Total Components:** 5  
**Completion Status:** 0/5 (0%)  
**Total Changes:** 29 (7 + 10 + 7 + 5 + 4)  
**Estimated Lines:** ~880 lines of new/modified code

**Exit Criteria for Phase 1:**
- [ ] InfrastructureGovernance.py at 100% (all 20 changes)
- [ ] EconomicsGuard.py created and tested (8 validation methods)
- [ ] NODInvariantChecker.py created and integrated (4 invariants)
- [ ] StateTransitionEngine NOD firewall active (5 changes)
- [ ] CIR302_Handler economic violations wired (4 changes)
- [ ] All V13.5 constitutional tasks marked complete
- [ ] All existing tests passing with new guards

---

## Phase 2: Integration Layer (V13.6 Core)

**Goal:** Make guards structural (no bypass paths) via SDK + API enforcement

**Status:** 0/3 components complete (0%)

### Component 2.1: QFSV13SDK.py Guard Integration ✅ CRITICAL

**Current Status:** 0/8 changes complete (0%)  
**Blocks:** Entire live system (guards become mandatory, not optional)

#### Purpose
Force ALL state-changing operations through constitutional guards at SDK level.

#### Tasks (8 changes)

**A. Economics Guard Integration (3 changes)**

1. ⏳ **Import EconomicsGuard in SDK __init__**
   ```python
   from src.libs.economics.EconomicsGuard import EconomicsGuard, ValidationResult
   
   def __init__(self, ...):
       self.economics_guard = EconomicsGuard(self.cm)
   ```

2. ⏳ **Wrap all reward/allocation calls**
   ```python
   def allocate_rewards(self, metrics, bundle, log_list, ...):
       # PRE-VALIDATION through EconomicsGuard
       chr_validation = self.economics_guard.validate_chr_reward(
           proposed_reward=metrics.chr_reward,
           total_supply=bundle.total_chr,
           epoch_number=epoch,
           ...
       )
       if not chr_validation.passed:
           raise StructuredError(chr_validation.error_code, chr_validation.details)
       
       # Only proceed if validation passed
       result = self.treasury_engine.calculate_rewards(...)
       return result
   ```

3. ⏳ **Propagate structured error codes**
   - Catch ValidationResult failures
   - Emit StructuredError with code + details
   - Propagate to CIR-302 handler
   - Log to CoherenceLedger with guard verdict

**B. NOD Invariant Integration (3 changes)**

4. ⏳ **Import NODInvariantChecker in SDK __init__**
   ```python
   from src.libs.governance.NODInvariantChecker import NODInvariantChecker
   
   def __init__(self, ...):
       self.nod_invariant_checker = NODInvariantChecker(self.node_verifier)
   ```

5. ⏳ **Wrap all NOD operations with invariant checks**
   ```python
   def allocate_nod(self, atr_fees, node_contributions, ...):
       # PRE-CHECK: NOD-I2 (node keys only)
       i2_result = self.nod_invariant_checker.check_nod_i2_node_keys_only(
           node_contributions
       )
       if not i2_result.passed:
           raise StructuredError(i2_result.error_code, i2_result.details)
       
       # Proceed with allocation
       result = self.nod_allocator.allocate_from_atr_fees(...)
       
       # POST-CHECK: NOD-I4 (replay determinism)
       i4_result = self.nod_invariant_checker.check_nod_i4_replay_determinism(
           input_snapshot, output_hash
       )
       if not i4_result.passed:
           self.cir302_handler.halt_with_finality_seal(i4_result)
       
       return result
   ```

6. ⏳ **Catch invariant violations**
   - Map INVARIANT_VIOLATION_* codes to CIR-302
   - Trigger immediate halt on invariant breach
   - Log violation to EQM with full context

**C. Backwards Compatibility Guards (2 changes)**

7. ⏳ **Deprecate old direct-call methods**
   ```python
   @deprecated(reason="Use allocate_rewards() with guard validation", version="V13.6")
   def direct_treasury_call(self, ...):
       raise DeprecationError("Direct TreasuryEngine calls forbidden in V13.6")
   ```

8. ⏳ **Reject unguarded paths**
   - Detect if caller bypassing SDK methods
   - Emit warning + error code
   - Block execution (fail-hard, not soft warning)

**Exit Criteria:**
- [ ] All 8 changes implemented
- [ ] Old code paths cannot bypass guards (tested with bypass attempts)
- [ ] Structured errors propagate to SDK callers
- [ ] CIR-302 integration tested
- [ ] Test suite covers: guarded path success, guard rejection, bypass attempt
- [ ] Evidence artifact: sdk_guard_integration_test.json

**Estimated Effort:** HIGH (8 changes, ~150 lines, critical path integration)

---

### Component 2.2: aegisapi.py Telemetry Snapshots ✅ CRITICAL

**Current Status:** 0/6 changes complete (0%)  
**Blocks:** NOD-I4 (replay determinism), AEGIS offline policy

#### Purpose
Transform AEGIS from live API to deterministic snapshot system for replay integrity.

#### Tasks (6 changes)

**A. Telemetry Snapshot Format (3 changes)**

1. ⏳ **Define AEGISTelemetrySnapshot dataclass**
   ```python
   @dataclass
   class AEGISTelemetrySnapshot:
       """Immutable, versioned AEGIS telemetry snapshot for deterministic replay."""
       snapshot_version: str  # "AEGIS_SNAPSHOT_V1"
       block_height: int
       snapshot_timestamp: int  # deterministic timestamp
       snapshot_hash: str  # SHA3-512 of entire snapshot
       node_metrics: Dict[str, Dict[str, Any]]  # node_id → metrics
       schema_version: str  # defines metrics structure
       
       def validate_completeness(self) -> bool:
           """Reject partial or ambiguous data."""
           # All required fields present
           # All node metrics have required keys
           # Hash verification passes
   ```

2. ⏳ **Add get_telemetry_snapshot() method**
   ```python
   def get_telemetry_snapshot(self, block_height: int, log_list, pqc_cid, quantum_metadata) -> AEGISTelemetrySnapshot:
       """
       Return versioned, hashed telemetry snapshot for given block height.
       
       For replay: fetch historical snapshot by block_height.
       For live: query AEGIS, hash result, store in EQM.
       """
       # Query AEGIS (or retrieve from cache)
       raw_telemetry = self._query_aegis_at_block(block_height)
       
       # Create immutable snapshot
       snapshot = AEGISTelemetrySnapshot(
           snapshot_version="AEGIS_SNAPSHOT_V1",
           block_height=block_height,
           snapshot_timestamp=deterministic_timestamp,
           node_metrics=raw_telemetry,
           schema_version="NODE_METRICS_V1",
           snapshot_hash=None  # computed next
       )
       
       # Compute deterministic hash
       snapshot.snapshot_hash = self._hash_snapshot(snapshot)
       
       # Validate completeness
       if not snapshot.validate_completeness():
           raise ValueError("Incomplete AEGIS telemetry snapshot")
       
       # Log to EQM
       self._log_snapshot(snapshot, log_list, pqc_cid, quantum_metadata)
       
       return snapshot
   ```

3. ⏳ **Validate snapshot completeness**
   - Reject if any required field missing
   - Reject if hash verification fails
   - Reject if schema version unknown
   - Emit structured error on incomplete data

**B. Constitutional Guard Integration (3 changes)**

4. ⏳ **Wrap AEGIS calls with rate limit checks**
   ```python
   def query_node_metrics(self, node_id, ...):
       # Check rate limit via EconomicsGuard
       rate_check = self.economics_guard.validate_aegis_query_rate(
           queries_this_epoch=self.query_count
       )
       if not rate_check.passed:
           raise StructuredError("AEGIS_RATE_LIMIT_EXCEEDED", rate_check.details)
       
       # Proceed with query
       result = self._query_aegis(node_id)
       self.query_count += 1
       return result
   ```

5. ⏳ **Add AEGIS offline detection and degradation**
   ```python
   def get_telemetry_snapshot_with_fallback(self, block_height, ...):
       try:
           return self.get_telemetry_snapshot(block_height, ...)
       except AEGISOfflineError:
           # SAFE DEGRADATION (no approximations)
           self._trigger_aegis_offline_policy()
           # User rewards continue (cached state)
           # NOD allocation skipped
           # Infrastructure governance frozen
           return None  # Caller must handle gracefully
   ```

6. ⏳ **Log all interactions with snapshot hash**
   ```python
   def _log_snapshot(self, snapshot, log_list, pqc_cid, quantum_metadata):
       """Record snapshot hash in EQM for audit trail."""
       log_entry = {
           "event": "AEGIS_TELEMETRY_SNAPSHOT",
           "snapshot_version": snapshot.snapshot_version,
           "block_height": snapshot.block_height,
           "snapshot_hash": snapshot.snapshot_hash,
           "schema_version": snapshot.schema_version,
           "timestamp": snapshot.snapshot_timestamp
       }
       log_list.append(log_entry)
       # Also commit to CoherenceLedger
       self.ledger.record_aegis_snapshot(snapshot)
   ```

**Exit Criteria:**
- [ ] All 6 changes implemented
- [ ] Telemetry snapshots are deterministic and versioned
- [ ] AEGIS offline triggers safe degradation (tested)
- [ ] All snapshots committed to EQM with hash
- [ ] Test suite covers: snapshot creation, hash verification, offline scenario, replay
- [ ] Evidence artifact: aegis_telemetry_determinism_test.json

**Estimated Effort:** HIGH (6 changes, ~200 lines, external system integration)

---

### Component 2.3: CoherenceLedger Constitutional Tracking

**Current Status:** 0/5 changes complete (0%)  
**Blocks:** Constitutional replay verification, config versioning

#### Tasks (5 changes)

**A. Constitutional Config Tracking (3 changes)**

1. ⏳ **Add economic_constants_hash field**
   ```python
   @dataclass
   class LedgerEntry:
       # ... existing fields ...
       economic_constants_hash: str  # SHA3-512 of economic_constants.py
       economic_constants_version: str  # "ECON_V1", "ECON_V2", etc.
   ```
   - Compute hash of entire economic_constants.py file
   - Include version tag for migration tracking
   - Record at entry creation time

2. ⏳ **Add guard_checks_passed field**
   ```python
   guard_checks_passed: Dict[str, bool] = {
       "EconomicsGuard.validate_chr_reward": True,
       "EconomicsGuard.validate_nod_allocation": True,
       "NODInvariantChecker.check_nod_i1": True,
       # ... all guard checks that validated this entry
   }
   ```
   - List all guards that validated this entry
   - Enable audit to verify guard coverage

3. ⏳ **Add bounds_proximity field**
   ```python
   bounds_proximity: Dict[str, str] = {
       "CHR_MAX_REWARD_PER_ACTION": "85% of limit",
       "NOD_MAX_ISSUANCE_PER_EPOCH": "42% of limit",
       # Track how close operations came to constitutional limits
   }
   ```
   - Warn if approaching limits (>90% of cap)
   - Enable predictive analysis

**B. Replay Verification Support (2 changes)**

4. ⏳ **Add verify_constitutional_replay() method**
   ```python
   def verify_constitutional_replay(self, epoch_start, epoch_end) -> VerificationResult:
       """
       Verify constitutional config consistency across epoch range.
       Detect config drift, guard bypass, bound violations.
       """
       entries = self.get_entries_in_range(epoch_start, epoch_end)
       
       # Check: Same config hash within epoch
       config_hashes = set([e.economic_constants_hash for e in entries])
       if len(config_hashes) > 1:
           return VerificationResult(
               passed=False,
               error="Config hash changed mid-epoch",
               details=config_hashes
           )
       
       # Check: All entries have guard coverage
       for entry in entries:
           if not entry.guard_checks_passed:
               return VerificationResult(
                   passed=False,
                   error="Entry missing guard validation",
                   details=entry
               )
       
       return VerificationResult(passed=True)
   ```

5. ⏳ **Generate constitutional_integrity_report.json**
   ```python
   def generate_integrity_report(self, output_path):
       """
       Show constitutional config evolution over time.
       Identify: when constants changed, which guards were active, proximity trends.
       """
       report = {
           "report_version": "CONST_INTEGRITY_V1",
           "ledger_range": {"start": first_block, "end": latest_block},
           "config_versions": [
               {"version": "ECON_V1", "epochs": "1-100", "hash": "..."},
               {"version": "ECON_V2", "epochs": "101-200", "hash": "..."}
           ],
           "guard_coverage": "100%",  # All entries validated
           "proximity_alerts": [
               {"epoch": 150, "token": "CHR", "proximity": "95% of daily cap"}
           ]
       }
       # Write to evidence artifact
   ```

**Exit Criteria:**
- [ ] All 5 changes implemented
- [ ] Every ledger entry includes config hash
- [ ] Guard check results auditable
- [ ] Replay verification detects config drift
- [ ] Evidence artifact: constitutional_integrity_report.json generated
- [ ] Test suite covers: config hash consistency, guard coverage, proximity alerts

**Estimated Effort:** MEDIUM (5 changes, ~120 lines, ledger integration)

---

## Phase 2 Summary

**Total Components:** 3  
**Completion Status:** 0/3 (0%)  
**Total Changes:** 19 (8 + 6 + 5)  
**Estimated Lines:** ~470 lines of new/modified code

**Exit Criteria for Phase 2:**
- [ ] QFSV13SDK.py routes all calls through guards (no bypass paths)
- [ ] aegisapi.py provides deterministic telemetry snapshots
- [ ] CoherenceLedger tracks constitutional config hashes
- [ ] All integration tests passing
- [ ] Evidence artifacts: sdk_guard_integration_test.json, aegis_telemetry_determinism_test.json, constitutional_integrity_report.json

---

## Phase 3: AEGIS / NOD Realism

**Goal:** Turn AEGIS from conceptual to actual deterministic data source

**Status:** 0/2 components complete (0%)

### Component 3.1: AEGIS_Node_Verification.py ✅ CRITICAL

**Current Status:** 0/1 file created (0%)  
**Blocks:** NOD-I2 structural enforcement

#### Purpose
Centralized, deterministic node verification criteria for NOD-I2 invariant.

#### Implementation Structure

```python
# File: src/libs/governance/AEGIS_Node_Verification.py

from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class NodeRegistryEntry:
    """AEGIS node registry entry."""
    node_id: str
    pqc_public_key: str  # Dilithium-5 public key
    registration_timestamp: int
    uptime_ratio: float  # 0.0 to 1.0
    slashing_history: list  # Past violations
    last_telemetry_timestamp: int

class AEGIS_Node_Verification:
    """
    Centralized node verification for NOD-I2 enforcement.
    Pure function API used by NODAllocator, InfrastructureGovernance, StateTransitionEngine.
    """
    
    def __init__(self, aegis_registry):
        self.registry = aegis_registry
    
    # 6 components (detailed below)
```

#### Tasks (6 components)

**A. Node Registry Integration (3 components)**

1. ⏳ **Define NodeRegistryEntry dataclass**
   - node_id: Unique identifier
   - pqc_public_key: Dilithium-5 key for verification
   - registration_timestamp: When node joined
   - uptime_ratio: Percentage uptime (90%+ required)
   - slashing_history: Past violations (disqualifies if recent)
   - last_telemetry_timestamp: Freshness check

2. ⏳ **Add get_active_nodes() method**
   ```python
   def get_active_nodes(self, block_height: int) -> List[NodeRegistryEntry]:
       """
       Query AEGIS registry for active nodes at given block height.
       Returns only nodes meeting verification criteria.
       """
       all_nodes = self.registry.query_nodes_at_block(block_height)
       active_nodes = [
           node for node in all_nodes
           if self.is_valid_active_node(node.node_id, block_height)
       ]
       return sorted(active_nodes, key=lambda n: n.node_id)  # Deterministic order
   ```

3. ⏳ **Add is_valid_active_node() method**
   ```python
   def is_valid_active_node(self, node_id: str, block_height: int) -> bool:
       """
       Verification criteria for active node status.
       
       Requirements:
       - Registered in AEGIS
       - Uptime >= 90%
       - No slashing events in last 1000 blocks
       - Telemetry fresh (within last 100 blocks)
       """
       entry = self.registry.get_node(node_id, block_height)
       if not entry:
           return False  # Not registered
       
       if entry.uptime_ratio < 0.90:
           return False  # Insufficient uptime
       
       recent_slashing = [
           s for s in entry.slashing_history
           if block_height - s.block_height < 1000
       ]
       if recent_slashing:
           return False  # Recent violations
       
       if block_height - entry.last_telemetry_timestamp > 100:
           return False  # Stale telemetry
       
       return True  # Passes all criteria
   ```

**B. Structural Enforcement (3 components)**

4. ⏳ **Integrate into NODAllocator**
   ```python
   def allocate_from_atr_fees(self, atr_fees, node_contributions, ...):
       # ENFORCE NOD-I2: Only verified nodes
       verified_contributions = {}
       for node_id, contribution in node_contributions.items():
           if self.node_verifier.is_valid_active_node(node_id, block_height):
               verified_contributions[node_id] = contribution
           else:
               # Log rejection (unverified node)
               log_list.append({
                   "event": "NOD_ALLOCATION_REJECTED",
                   "reason": "Node not verified",
                   "node_id": node_id
               })
       
       # Allocate only to verified nodes
       return self._allocate_to_nodes(verified_contributions, ...)
   ```

5. ⏳ **Integrate into InfrastructureGovernance.create_proposal()**
   ```python
   def create_proposal(self, proposer_node_id, ...):
       # ENFORCE NOD-I2: Only verified nodes can propose
       if not self.node_verifier.is_valid_active_node(proposer_node_id, current_timestamp):
           raise ValueError(f"Proposer {proposer_node_id} not a verified active node")
       
       # Proceed with proposal creation
       proposal = InfrastructureProposal(...)
       return proposal
   ```

6. ⏳ **Integrate into InfrastructureGovernance.cast_vote()**
   ```python
   def cast_vote(self, proposal_id, voter_node_id, ...):
       # ENFORCE NOD-I2: Only verified nodes can vote
       if not self.node_verifier.is_valid_active_node(voter_node_id, timestamp):
           raise ValueError(f"Voter {voter_node_id} not a verified active node")
       
       # Proceed with vote
       proposal.voters[voter_node_id] = True
       # ...
   ```

**Exit Criteria:**
- [ ] File created with all 6 components
- [ ] NOD-I2 structurally enforced (no code path allows unverified node NOD)
- [ ] Criteria documented and testable
- [ ] AEGIS integration stubbed with clear TODO for production
- [ ] Test suite covers: verified node pass, unverified node rejection, stale telemetry rejection
- [ ] Evidence artifact: node_verification_test.json

**Estimated Effort:** HIGH (new file, ~200 lines, critical invariant enforcement)

---

### Component 3.2: AEGIS Offline Policy

**Current Status:** 0/1 file created (0%)  
**Blocks:** Failure mode definition, safe degradation testing

#### Purpose
Global policy document defining QFS behavior when AEGIS degraded/unavailable.

#### Implementation (5 sections)

**A. Degradation Matrix (3 sections)**

1. ⏳ **AEGIS Fully Available**
   - All operations proceed normally
   - NOD allocation active
   - Infrastructure governance active
   - User rewards active
   - Full telemetry validation

2. ⏳ **AEGIS Telemetry Degraded**
   - User rewards continue (using cached TokenStateBundle)
   - NOD allocation SKIPPED (no telemetry = no allocation)
   - Infrastructure governance FROZEN (cannot verify voters)
   - CIR-302 alert: AEGIS_DEGRADED (non-critical)
   - Log degradation event for audit trail

3. ⏳ **AEGIS Completely Offline**
   - User rewards continue (safe mode, cached state only)
   - NOD frozen (zero allocation)
   - Governance frozen (no proposals, no votes)
   - CIR-302 alert: AEGIS_OFFLINE (critical if >1000 blocks)
   - System continues with reduced functionality
   - NO APPROXIMATIONS (skip epoch rather than guess)

**B. Enforcement Rules (2 sections)**

4. ⏳ **Forbidden Approximations**
   ```markdown
   ## Forbidden Approximations
   
   When AEGIS telemetry is unavailable, the system MUST NOT:
   - Approximate missing node metrics
   - Carry forward stale telemetry (>100 blocks old)
   - Interpolate between known values
   - Use default/fallback telemetry
   
   Instead, the system MUST:
   - Skip NOD allocation epoch
   - Freeze infrastructure governance
   - Continue user-facing operations with cached state
   - Emit AEGIS_OFFLINE structured error
   ```

5. ⏳ **CIR-302 Integration**
   ```markdown
   ## CIR-302 Integration
   
   AEGIS offline is classified as:
   - **Non-Critical Incident** (0-100 blocks offline)
     - System continues with degraded functionality
     - Alert logged, no halt
   
   - **Critical Incident** (>1000 blocks offline)
     - Trigger CIR-302 investigation
     - Generate AEGIS_FINALITY_SEAL
     - Manual intervention may be required
   
   Recovery procedure:
   1. AEGIS restored
   2. Validate telemetry integrity
   3. Resume NOD allocation from next epoch
   4. Resume governance with fresh snapshot
   ```

**Exit Criteria:**
- [ ] File created with all 5 sections (policy doc, no code)
- [ ] Policy integrated into MASTER-PLAN-V13.md Phase 4
- [ ] CIR-302 handler implements policy
- [ ] Test suite covers all degradation scenarios
- [ ] Evidence artifact: aegis_offline_policy_test.json

**Estimated Effort:** LOW (policy document, ~100 lines, no code)

---

## Phase 3 Summary

**Total Components:** 2  
**Completion Status:** 0/2 (0%)  
**Total Changes:** 7 (6 + 1 policy doc)  
**Estimated Lines:** ~300 lines of code + policy doc

**Exit Criteria for Phase 3:**
- [ ] AEGIS_Node_Verification.py created and integrated
- [ ] NOD-I2 structurally enforced across all NOD operations
- [ ] AEGIS_Offline_Policy.md created and implemented
- [ ] Test suite covers verification criteria and offline scenarios
- [ ] Evidence artifacts: node_verification_test.json, aegis_offline_policy_test.json

---

## Phase 4: Replay, Boundaries, Performance (V13.6 Verification)

**Goal:** Prove determinism, bounds enforcement, and performance targets met

**Status:** 0/4 components complete (0%)

### Component 4.1: DeterministicReplayTest.py

**Current Status:** 0/1 file created (0%)  
**Blocks:** NOD-I4 verification, replay integrity proof

#### Purpose
Prove bit-for-bit replay determinism for NOD allocation and governance.

#### Test Cases (5 total)

1. ⏳ **Test NOD allocation replay**
   - Run allocation twice with identical: ATR fees, telemetry snapshot, block height
   - Assert: Identical NOD distributions (bit-for-bit)
   - Assert: Identical log hashes
   - Evidence: allocation_replay_proof.json

2. ⏳ **Test governance voting replay**
   - Create proposal, cast votes (identical inputs)
   - Run twice from same starting state
   - Assert: Identical tally results
   - Assert: Identical event hashes

3. ⏳ **Test governance execution replay**
   - Execute PASSED proposal twice
   - Assert: Identical config mutations
   - Assert: Identical execution logs

4. ⏳ **Test hash chain integrity**
   - Run 100-block sequence twice
   - Assert: Identical CRS hash chain
   - Assert: Identical ledger hashes at each block

5. ⏳ **Test cross-platform replay**
   - Run on Windows (mock PQC) vs Linux (liboqs)
   - Assert: Platform-agnostic outputs (with PQC abstraction)
   - Note: Signature bytes may differ, but state transitions identical

**Exit Criteria:**
- [ ] File created with all 5 test cases
- [ ] All tests pass (100% deterministic replay)
- [ ] Evidence artifact: nod_replay_determinism.json
- [ ] Integrated into autonomous audit v2.0 pipeline

**Estimated Effort:** HIGH (new file, ~400 lines, complex test scenarios)

---

### Component 4.2: BoundaryConditionTests.py

**Current Status:** 0/1 file created (0%)  
**Blocks:** Economic bounds verification, stress testing

#### Purpose
Test constitutional bounds enforcement at edge cases and violation attempts.

#### Test Scenarios (12 total)

**CHR Tests (3)**
1. ⏳ Test CHR reward at MIN boundary (CHR_MIN_REWARD_PER_ACTION) → should pass
2. ⏳ Test CHR reward at MAX boundary (CHR_MAX_REWARD_PER_ACTION) → should pass
3. ⏳ Test CHR reward over MAX → should clamp or reject with ECON_BOUND_VIOLATION

**FLX Tests (3)**
4. ⏳ Test FLX allocation fraction at MIN → should pass
5. ⏳ Test FLX allocation fraction at MAX → should pass
6. ⏳ Test FLX per-user cap exceeded (FLX_MAX_PER_USER) → should clamp

**NOD Tests (6)**
7. ⏳ Test NOD allocation with < MIN_ACTIVE_NODES (e.g., 2 nodes) → should skip allocation
8. ⏳ Test NOD allocation at MAX_ISSUANCE_PER_EPOCH → should cap at limit
9. ⏳ Test single node dominance > MAX_NODE_REWARD_SHARE (30%) → should cap
10. ⏳ Test governance quorum < MIN_QUORUM_THRESHOLD (51%) → should reject
11. ⏳ Test governance quorum > MAX_QUORUM_THRESHOLD (90%) → should reject
12. ⏳ Test vote power > MAX_NOD_VOTING_POWER_RATIO (25%) → should cap

**Exit Criteria:**
- [ ] File created with all 12 test scenarios
- [ ] All tests pass (bounds enforced correctly)
- [ ] Evidence artifact: economic_bounds_verification.json
- [ ] Integrated into autonomous audit v2.0 pipeline

**Estimated Effort:** HIGH (new file, ~500 lines, comprehensive scenarios)

---

### Component 4.3: FailureModeTests.py

**Current Status:** 0/1 file created (0%)  
**Blocks:** Safe degradation verification, CIR-302 triggers

#### Purpose
Test safe degradation paths and CIR-302 triggers under failure conditions.

#### Test Scenarios (8 total)

**NOD Degradation (3)**
1. ⏳ Test NOD allocation skip when telemetry unavailable → zero allocation, no approximation
2. ⏳ Test governance freeze when node set < quorum → proposals frozen, votes rejected
3. ⏳ Test conflicting telemetry hash resolution → lexicographic tie-break (deterministic)

**Economic Violations (3)**
4. ⏳ Test CHR emission cap violation (exceed CHR_DAILY_EMISSION_CAP) → CIR-302 halt
5. ⏳ Test governance parameter outside [IMMUTABLE] bounds → reject proposal
6. ⏳ Test total supply ratio change > MAX_TOTAL_SUPPLY_RATIO_CHANGE → halt

**Invariant Violations (2)**
7. ⏳ Test NOD transfer attempt (user-to-user) → CIR-302 halt (NOD-I1 violation)
8. ⏳ Test NOD governance touching user rewards → CIR-302 halt (NOD-I3 violation)

**Exit Criteria:**
- [ ] File created with all 8 test scenarios
- [ ] All degradation paths preserve zero-simulation integrity
- [ ] All violations trigger appropriate CIR-302 responses
- [ ] Evidence artifact: failure_mode_verification.json
- [ ] Integrated into autonomous audit v2.0 pipeline

**Estimated Effort:** HIGH (new file, ~400 lines, complex failure scenarios)

---

### Component 4.4: PerformanceBenchmarkWithGuards.py

**Current Status:** 0/1 file created (0%)  
**Blocks:** Performance verification, Phase 4 TPS targets

#### Purpose
Verify QFS meets 2,000 TPS minimum with all constitutional guards enabled.

#### Benchmark Scenarios (6 total)

**A. Throughput Tests (3 scenarios)**

1. ⏳ **Test sustained TPS with guards**
   - Run 10,000 transactions with EconomicsGuard + NODInvariantChecker enabled
   - Measure: average TPS over 5-minute window
   - Target: >= 2,000 TPS sustained

2. ⏳ **Test peak TPS with full logging**
   - Run burst of 5,000 transactions with all guards + full EQM logging
   - Measure: peak TPS in 10-second window
   - Target: >= 3,000 TPS peak

3. ⏳ **Compare baseline vs guarded performance**
   - Run same workload with guards disabled (baseline) vs enabled
   - Measure: overhead percentage
   - Target: <10% overhead from constitutional layer

**B. Latency Tests (3 scenarios)**

4. ⏳ **Test p50, p95, p99 latency for guarded reward allocation**
   - Run 1,000 reward allocations with EconomicsGuard validation
   - Measure: latency distribution
   - Target: p95 < 100ms, p99 < 200ms

5. ⏳ **Test p50, p95, p99 latency for guarded governance operations**
   - Create/vote/execute proposals with all guards
   - Measure: latency distribution
   - Target: p95 < 150ms, p99 < 300ms

6. ⏳ **Validate latency meets Phase 4 targets**
   - Combined workload: 70% rewards, 20% NOD, 10% governance
   - Measure: overall system latency
   - Target: p95 < 100ms for mixed workload

**Exit Criteria:**
- [ ] File created with all 6 benchmark scenarios
- [ ] Performance meets Phase 4 targets (2,000 TPS minimum)
- [ ] Latency acceptable with all guards enabled (p95 < 100ms)
- [ ] Evidence artifact: performance_benchmark_guarded.json
- [ ] Regression tests prevent future performance degradation

**Estimated Effort:** MEDIUM (new file, ~250 lines, performance critical)

---

## Phase 4 Summary

**Total Components:** 4  
**Completion Status:** 0/4 (0%)  
**Total Changes:** 4 new test files  
**Estimated Lines:** ~1,550 lines of test code

**Exit Criteria for Phase 4:**
- [ ] DeterministicReplayTest.py created and passing (5 test cases)
- [ ] BoundaryConditionTests.py created and passing (12 test scenarios)
- [ ] FailureModeTests.py created and passing (8 test scenarios)
- [ ] PerformanceBenchmarkWithGuards.py created and passing (6 benchmark scenarios)
- [ ] All evidence artifacts generated
- [ ] Integration into autonomous audit v2.0 complete

---

## Phase 5: Documentation and V13.6 Release

**Goal:** Lock constitution + implementation into coherent, auditable V13.6 release

**Status:** 0/4 components complete (0%)

### Component 5.1: NOD_INFRASTRUCTURE_TOKEN_SPEC_V1.md Updates

**Current Status:** Partial (constitutional bounds section added in V13.5)  
**Remaining:** 4 sections to add/update

#### Updates Required (4 sections)

1. ⏳ **Section 5: Threat Model (Enhancement)**
   - Expand threat table with constitutional defenses
   - Add: Parameter Manipulation → Constitutional bounds enforcement
   - Add: Replay Attack → Telemetry snapshot hashing
   - Add: AEGIS Compromise → Offline degradation policy
   - Add: Single-Node Capture → Vote weight caps + allocation caps

2. ⏳ **Section 6: Governance Timing (New)**
   ```markdown
   ## 6. Governance Timing Constants
   
   All governance operations follow constitutional timing rules:
   
   - **Proposal Cooldown:** 120 blocks (~34 minutes)
     - Prevents spam proposals
     - Enforced in `create_proposal()`
   
   - **Voting Window:** 720 blocks (~3.4 hours)
     - Sufficient time for operator participation
     - Mutable via governance (within bounds)
   
   - **Execution Delay (Timelock):** 240 blocks (~1.1 hours)
     - Safety buffer after passage
     - [IMMUTABLE] - cannot be reduced
   
   - **Emergency Quorum:** 80%
     - Required for critical infrastructure changes
     - [IMMUTABLE]
   ```

3. ⏳ **Section 7: Economic Failure Modes (New)**
   ```markdown
   ## 7. Economic Failure Modes
   
   ### 7.1 Emission Cap Violations
   - **Scenario:** Daily CHR emission exceeds CHR_DAILY_EMISSION_CAP
   - **Response:** EconomicsGuard rejects, CIR-302 halt
   - **Recovery:** Investigate cause, resume with capped emissions
   
   ### 7.2 AEGIS Offline
   - **Scenario:** AEGIS telemetry unavailable for >100 blocks
   - **Response:** Skip NOD allocation, freeze governance, continue user rewards
   - **Reference:** AEGIS_Offline_Policy.md
   
   ### 7.3 Governance Parameter Violation
   - **Scenario:** Proposal attempts to set quorum to 95% (> MAX_QUORUM_THRESHOLD)
   - **Response:** Parameter validation rejects before voting begins
   
   ### 7.4 Invariant Violation
   - **Scenario:** User attempts direct NOD transfer
   - **Response:** StateTransitionEngine firewall blocks, CIR-302 halt
   - **Invariant:** NOD-I1 (no transfers)
   ```

4. ⏳ **Appendix A: Reference to economic_constants.py (New)**
   ```markdown
   ## Appendix A: Constitutional Constants Reference
   
   All economic parameters are defined in:
   `src/libs/economics/economic_constants.py`
   
   Key constant categories:
   - CHR (Coherence): 8 constants
   - FLX (Flexibility): 7 constants
   - PSI (Ψ-Sync): 6 constants
   - ATR (Attention): 9 constants
   - RES (Reserve): 6 constants
   - NOD (Infrastructure): 12 constants
   - Governance Timing: 4 constants
   - System-Wide Limits: 3 constants
   
   Total: 55 constitutional constants (as of V13.6)
   
   Mutability Status:
   - [IMMUTABLE]: 38 constants (69%) - hard-coded, require protocol upgrade
   - [MUTABLE]: 17 constants (31%) - governance-changeable within [IMMUTABLE] bounds
   
   See economic_constants.py for complete listing and current values.
   ```

**Exit Criteria:**
- [ ] All 4 sections added/updated
- [ ] Cross-references to economic_constants.py
- [ ] Alignment with implemented code
- [ ] Examples show bounded behavior

**Estimated Effort:** MEDIUM (4 sections, ~150 lines)

---

### Component 5.2: MASTER-PLAN-V13.md Updates

**Current Status:** Exists but needs Phase 4/5 economic criteria  
**Remaining:** 3 sections to add

#### Updates Required (3 sections)

1. ⏳ **Phase 4: System-Level Verification - Add Economic Criteria**
   ```markdown
   ### Phase 4.5: Constitutional Economics / NOD Infrastructure Layer
   
   **Acceptance Criteria:**
   1. All economic operations bounded by economic_constants.py
   2. EconomicsGuard validates 100% of reward/allocation operations
   3. NODInvariantChecker enforces NOD-I1 through NOD-I4
   4. AEGIS telemetry snapshots deterministic (versioned, hashed)
   5. Performance >= 2,000 TPS with all guards enabled
   6. Replay tests prove bit-for-bit determinism
   7. Boundary condition tests verify all caps/limits
   8. Failure mode tests verify safe degradation
   
   **Evidence Artifacts:**
   - economic_bounds_verification.json
   - nod_replay_determinism.json
   - failure_mode_verification.json
   - performance_benchmark_guarded.json
   - sdk_guard_integration_test.json
   - aegis_telemetry_determinism_test.json
   - constitutional_integrity_report.json
   ```

2. ⏳ **Phase 5: Final Deliverables - Add Evidence Artifacts**
   ```markdown
   ### Phase 5: Final Deliverables
   
   ... existing content ...
   
   #### V13.6 Constitutional Evidence (New)
   - `economic_bounds_verification.json` - Proof of bounds enforcement
   - `nod_replay_determinism.json` - NOD-I4 verification
   - `failure_mode_verification.json` - Safe degradation tests
   - `performance_benchmark_guarded.json` - TPS/latency with guards
   - `sdk_guard_integration_test.json` - No-bypass verification
   - `aegis_telemetry_determinism_test.json` - Snapshot consistency
   - `constitutional_integrity_report.json` - Config evolution tracking
   - `node_verification_test.json` - NOD-I2 enforcement
   - `aegis_offline_policy_test.json` - Degradation scenarios
   ```

3. ⏳ **Appendix: Economic Constants - Add Quick Reference**
   ```markdown
   ## Appendix C: Constitutional Economic Constants
   
   Full listing of all 55 economic constants with mutability status.
   See `src/libs/economics/economic_constants.py` for canonical source.
   
   ### CHR (Coherence / Value Creation)
   - CHR_BASE_REWARD: 1,000 [MUTABLE]
   - CHR_MAX_REWARD_PER_ACTION: 10,000 [IMMUTABLE]
   - CHR_MIN_REWARD_PER_ACTION: 10 [IMMUTABLE]
   - CHR_DAILY_EMISSION_CAP: 10,000,000 [MUTABLE]
   - ... (complete listing)
   
   ### Governance Timing
   - GOVERNANCE_PROPOSAL_COOLDOWN_BLOCKS: 120 [IMMUTABLE]
   - GOVERNANCE_VOTING_WINDOW_BLOCKS: 720 [MUTABLE]
   - GOVERNANCE_EXECUTION_DELAY_BLOCKS: 240 [IMMUTABLE]
   - GOVERNANCE_EMERGENCY_QUORUM: 0.80 [IMMUTABLE]
   
   ### Anti-Centralization Guards
   - MAX_NOD_VOTING_POWER_RATIO: 0.25 [IMMUTABLE]
   - MAX_NODE_REWARD_SHARE: 0.30 [IMMUTABLE]
   - NOD_MIN_ACTIVE_NODES: 3 [IMMUTABLE]
   ```

**Exit Criteria:**
- [ ] All 3 sections added
- [ ] Phase 4 includes stress test requirements
- [ ] Phase 5 includes all new evidence artifacts
- [ ] Appendix serves as quick reference

**Estimated Effort:** LOW (3 sections, ~80 lines)

---

### Component 5.3: AutonomousAuditV2Prompts.md Updates

**Current Status:** Exists but needs economic stress tests  
**Remaining:** 2 sections to add

#### Updates Required (2 sections)

1. ⏳ **Section: Constitutional Economics Stress Tests**
   ```markdown
   ## Constitutional Economics Stress Tests
   
   ### Stress Test 1: Single-Node NOD Capture Attempt
   **Objective:** Verify anti-centralization guards prevent single-node dominance
   **Steps:**
   1. Simulate node with 50% of total network contribution
   2. Attempt NOD allocation
   3. **Expected:** Allocation capped at MAX_NODE_REWARD_SHARE (30%)
   4. **Verify:** Remaining allocation distributed to other nodes
   5. **Evidence:** economic_bounds_verification.json shows cap applied
   
   ### Stress Test 2: Maximal CHR/FLX Issuance
   **Objective:** Verify emission caps prevent unbounded inflation
   **Steps:**
   1. Simulate high-coherence activity triggering max rewards
   2. Approach CHR_DAILY_EMISSION_CAP
   3. **Expected:** Rewards capped at constitutional limit
   4. **Verify:** Total daily emission <= CHR_DAILY_EMISSION_CAP
   5. **Evidence:** economic_bounds_verification.json shows daily cap enforced
   
   ### Stress Test 3: Rapid Governance Churn
   **Objective:** Verify proposal cooldown and timelock prevent governance spam
   **Steps:**
   1. Create 10 proposals in rapid succession
   2. **Expected:** Only 1st proposal succeeds, rest rejected by cooldown
   3. Attempt immediate execution after passage
   4. **Expected:** Execution blocked by timelock (240 blocks)
   5. **Evidence:** infra_governance_completion_report.json shows timing enforcement
   ```

2. ⏳ **Section: Evidence Artifacts Definitions**
   ```markdown
   ## V13.6 Evidence Artifacts
   
   ### economic_bounds_verification.json
   **Purpose:** Prove all constitutional bounds enforced  
   **Required Fields:**
   - test_scenarios: List of 12 boundary tests
   - bounds_enforced: All caps/limits applied correctly
   - violations_rejected: Attempted violations blocked
   - proximity_warnings: Operations near limits
   
   ### nod_replay_determinism.json
   **Purpose:** Prove NOD-I4 (bit-for-bit replay)  
   **Required Fields:**
   - replay_runs: 2+ identical input runs
   - output_hashes_match: true
   - log_hashes_match: true
   - platform_agnostic: true (Windows vs Linux)
   
   ### failure_mode_verification.json
   **Purpose:** Prove safe degradation under failures  
   **Required Fields:**
   - degradation_scenarios: 8 test cases
   - cir302_triggers: Correct halt conditions
   - zero_simulation_preserved: No approximations used
   ```

**Exit Criteria:**
- [ ] All 2 sections added
- [ ] Stress test prompts are actionable
- [ ] Evidence artifacts defined with required fields

**Estimated Effort:** LOW (2 sections, ~60 lines)

---

### Component 5.4: Migration Documentation

**Current Status:** 0/1 file created (0%)  
**Purpose:** Document migration path from pre-constitution to V13.6

#### Implementation (1 file)

⏳ **Create MIGRATION_V13.5_TO_V13.6.md**

```markdown
# Migration Guide: V13.5 to V13.6

## Overview
This guide documents the migration path from V13.5 (constitutional foundation) to V13.6 (operational integration).

## Key Changes
1. **Guards now mandatory** - All economic operations routed through SDK
2. **AEGIS telemetry snapshots** - Deterministic, versioned data sources
3. **Economic constant versioning** - Config hash in every ledger entry
4. **Performance validated** - Proven 2,000 TPS with guards enabled

## Migration Steps

### Step 1: Update Dependencies
```bash
# Update to V13.6 release
git checkout v13.6-release
pip install -r requirements.txt
```

### Step 2: Verify Economic Constants
- Review `economic_constants.py` for any changes
- Check that ECON_VERSION = "V1" (or current version)
- Verify all bounds appropriate for your deployment

### Step 3: Enable Guards
- All SDK methods now include guard validation
- Old direct-call methods deprecated (will error)
- Update calling code to use SDK methods only

### Step 4: Replay Historical Data (Optional)
- Use `EconomicConstantsMigration.py` to load epoch-appropriate constants
- Run replay tests to verify ledger integrity
- Compare output hashes with historical records

### Step 5: Performance Validation
- Run `PerformanceBenchmarkWithGuards.py`
- Verify TPS meets targets for your workload
- Adjust infrastructure if needed

## Breaking Changes
- Direct calls to `TreasuryEngine`, `RewardAllocator`, `NODAllocator` now rejected
- Must use `QFSV13SDK` methods which include guard validation
- AEGIS integration now requires versioned telemetry snapshots

## Backwards Compatibility
- Ledger format unchanged (new fields added, old fields preserved)
- PQC signature format unchanged
- Token balances and state transitions fully compatible

## Rollback Procedure
If issues arise:
1. Stop V13.6 deployment
2. Revert to V13.5 commit
3. Existing ledger data remains valid
4. Report issues to development team

## Support
For migration assistance, reference:
- Constitutional V13.5 Task Tracker
- QFS V13.6 Release Tracker
- Autonomous Audit V2.0 evidence artifacts
```

**Exit Criteria:**
- [ ] Migration guide created
- [ ] All breaking changes documented
- [ ] Rollback procedure defined
- [ ] Compatible with existing ledgers

**Estimated Effort:** LOW (1 file, ~120 lines)

---

## Phase 5 Summary

**Total Components:** 4  
**Completion Status:** 0/4 (0%)  
**Total Changes:** 10 documentation updates  
**Estimated Lines:** ~410 lines of documentation

**Exit Criteria for Phase 5:**
- [ ] NOD_INFRASTRUCTURE_TOKEN_SPEC_V1.md updated (4 sections)
- [ ] MASTER-PLAN-V13.md updated (3 sections)
- [ ] AutonomousAuditV2Prompts.md updated (2 sections)
- [ ] MIGRATION_V13.5_TO_V13.6.md created
- [ ] All docs and code aligned
- [ ] Audit v2.0 can certify V13.6 as constitutional release

---

## V13.6 Release Summary

### Grand Total Scope

**Phase 1 (V13.5 Delta Closure):**
- Components: 5
- Changes: 29
- Lines: ~880
- Critical files: InfrastructureGovernance.py, EconomicsGuard.py, NODInvariantChecker.py

**Phase 2 (Integration Layer):**
- Components: 3
- Changes: 19
- Lines: ~470
- Critical files: QFSV13SDK.py, aegisapi.py, CoherenceLedger.py

**Phase 3 (AEGIS/NOD Realism):**
- Components: 2
- Changes: 7
- Lines: ~300
- Critical files: AEGIS_Node_Verification.py, AEGIS_Offline_Policy.md

**Phase 4 (Verification):**
- Components: 4
- Test files: 4
- Lines: ~1,550
- Test scenarios: 31 total

**Phase 5 (Documentation):**
- Components: 4
- Updates: 10
- Lines: ~410

**OVERALL V13.6 SCOPE:**
- **Total Phases:** 5
- **Total Components:** 18
- **Total Code Changes:** 55
- **Total Code Lines:** ~3,200 lines
- **Total Test Lines:** ~1,550 lines
- **Total Doc Lines:** ~410 lines
- **New Files:** 8 code files + 4 test files + 1 policy doc + 1 migration guide = 14 new files
- **Enhanced Files:** 11 existing files
- **Evidence Artifacts:** 9 new artifacts

---

## Critical Path Analysis

### Immediate Blockers (Must Complete First)

1. **InfrastructureGovernance.py completion** (7 changes)
   - Blocks: Phase 2 governance integration, Phase 4 governance tests
   - Estimated: 2-3 hours

2. **EconomicsGuard.py creation** (10 components)
   - Blocks: ALL economic wiring (TreasuryEngine, RewardAllocator, SDK)
   - Estimated: 4-6 hours

3. **NODInvariantChecker.py creation** (7 components)
   - Blocks: Invariant enforcement, Phase 4 violation tests
   - Estimated: 3-4 hours

### Integration Layer (Next Priority)

4. **QFSV13SDK.py guard integration** (8 changes)
   - Makes guards structural (no bypass paths)
   - Estimated: 3-4 hours

5. **aegisapi.py telemetry snapshots** (6 changes)
   - Enables replay determinism
   - Estimated: 3-4 hours

6. **AEGIS_Node_Verification.py** (6 components)
   - Enforces NOD-I2 structurally
   - Estimated: 3-4 hours

### Testing & Verification

7. **Test file creation** (4 files, 31 scenarios)
   - Proves bounds, replay, degradation, performance
   - Estimated: 8-12 hours

### Documentation Closure

8. **Doc updates** (4 files, 10 sections)
   - Aligns specs with implementation
   - Estimated: 2-3 hours

**Total Estimated Effort:** 28-40 hours of focused development

---

## Execution Strategy

### Week 1: Foundation (Phase 1)
**Goal:** Complete V13.5 delta, enable guard infrastructure

**Day 1-2:**
- Complete InfrastructureGovernance.py (7 changes)
- Test all 7 governance scenarios

**Day 3-4:**
- Create EconomicsGuard.py (8 validation methods + error codes)
- Write 100+ unit tests for all validation paths

**Day 5:**
- Create NODInvariantChecker.py (4 invariants)
- Integrate into StateTransitionEngine, NODAllocator, InfrastructureGovernance
- Add CIR302_Handler economic violations

**Week 1 Exit:** Phase 1 complete, all V13.5 tasks closed

---

### Week 2: Integration (Phase 2 & 3)
**Goal:** Make guards structural, integrate AEGIS deterministically

**Day 1-2:**
- Update QFSV13SDK.py (8 changes)
- Deprecate old direct-call paths
- Test bypass attempts (must fail)

**Day 3:**
- Update aegisapi.py (6 changes)
- Implement AEGISTelemetrySnapshot
- Test offline degradation

**Day 4:**
- Update CoherenceLedger.py (5 changes)
- Add constitutional config tracking
- Test replay verification

**Day 5:**
- Create AEGIS_Node_Verification.py
- Create AEGIS_Offline_Policy.md
- Integrate node verification across all NOD operations

**Week 2 Exit:** Phases 2 & 3 complete, integration layer operational

---

### Week 3: Verification & Documentation (Phase 4 & 5)
**Goal:** Prove system works, finalize docs

**Day 1-2:**
- Create DeterministicReplayTest.py (5 test cases)
- Create BoundaryConditionTests.py (12 test scenarios)

**Day 3:**
- Create FailureModeTests.py (8 test scenarios)
- Create PerformanceBenchmarkWithGuards.py (6 benchmarks)

**Day 4:**
- Run all tests, generate evidence artifacts
- Verify 2,000 TPS target met
- Fix any discovered issues

**Day 5:**
- Update NOD spec, MASTER-PLAN, audit prompts
- Create migration guide
- Final documentation review

**Week 3 Exit:** Phases 4 & 5 complete, V13.6 ready for release

---

## Success Metrics

### Technical Metrics
- [ ] 100% code coverage on guards (EconomicsGuard, NODInvariantChecker)
- [ ] 100% test pass rate (all 31 test scenarios)
- [ ] >= 2,000 TPS sustained with all guards enabled
- [ ] < 10% performance overhead from constitutional layer
- [ ] p95 latency < 100ms for mixed workload
- [ ] Bit-for-bit replay verified (5 scenarios)
- [ ] All 12 boundary conditions enforced
- [ ] All 8 failure modes handle gracefully

### Audit Metrics
- [ ] 9 evidence artifacts generated
- [ ] Constitutional config hash in 100% of ledger entries
- [ ] Guard coverage: 100% of economic operations
- [ ] Invariant checks: 100% of NOD operations
- [ ] Structured error codes: All violations mapped to CIR-302
- [ ] Autonomous audit v2.0 integration complete

### Documentation Metrics
- [ ] All specs updated (NOD spec, MASTER-PLAN, audit prompts)
- [ ] Migration guide created
- [ ] 55 constitutional constants documented
- [ ] Threat model complete
- [ ] Economic failure modes documented

### Governance Metrics
- [ ] [IMMUTABLE] constants enforced (38 constants)
- [ ] [MUTABLE] constants within bounds (17 constants)
- [ ] Timelock enforced (240 blocks)
- [ ] Vote weight caps enforced (25% max)
- [ ] Allocation caps enforced (30% max)
- [ ] Quorum bounds enforced (51%-90%)

---

## Release Checklist

### Pre-Release
- [ ] All Phase 1-5 components complete
- [ ] All tests passing (100%)
- [ ] All evidence artifacts generated
- [ ] Documentation updated and reviewed
- [ ] Migration guide tested
- [ ] Performance benchmarks meet targets

### Release Preparation
- [ ] Create release branch: `v13.6-release`
- [ ] Tag commit: `QFS-V13.6-Constitutional-Integration`
- [ ] Generate CHANGELOG.md with all changes
- [ ] Update version in all relevant files
- [ ] Create release notes

### Release Artifacts
- [ ] Source code archive
- [ ] All 9 evidence artifacts
- [ ] Migration guide
- [ ] Updated documentation
- [ ] Performance benchmark results
- [ ] Test coverage report

### Post-Release
- [ ] Merge to master branch
- [ ] Deploy to staging environment
- [ ] Run integration tests in staging
- [ ] Monitor performance in production
- [ ] Collect feedback from operators

---

## V13.6 vs V13.5 Comparison

### V13.5 (Constitutional Foundation)
**Delivered:**
- ✅ economic_constants.py (55 constants defined)
- ✅ NODAllocator.py (anti-centralization guards)
- ✅ InfrastructureGovernance.py (65% complete)
- ✅ README.md (NOD documentation)
- ✅ Constitutional task tracker (129 changes documented)

**Status:** Constitutional layer DEFINED but not fully ENFORCED

### V13.6 (Operational Integration)
**Delivers:**
- ✅ Constitutional layer ENFORCED (guards mandatory)
- ✅ No bypass paths (SDK structural enforcement)
- ✅ AEGIS integration (deterministic snapshots)
- ✅ Replay integrity (versioned configs)
- ✅ Performance verified (2,000 TPS proven)
- ✅ Migration path (V13.5 → V13.6)

**Status:** Constitutional layer OPERATIONAL in real world

---

## Future Considerations (V13.7+)

### Potential Enhancements
1. **Economic Constant Governance** - Allow [MUTABLE] constant changes via governance proposals
2. **Advanced NOD Features** - Staking, delegation, slashing (requires legal review)
3. **Cross-Chain Integration** - Constitutional guarantees across chains
4. **ZK Proofs for Bounds** - Zero-knowledge proofs of constitutional compliance
5. **Formal Verification** - Machine-verified proofs of invariants

### V2.0 Considerations
The user mentioned "minimal V2 features" in V13.6. These are intentionally DEFERRED:
- Advanced governance features (beyond infrastructure)
- User-facing NOD visibility
- Economic tuning mechanisms
- Dynamic allocation rates

**Rationale:** V13.6 focuses on making the V13.5 constitution OPERATIONAL. V2.0 features require the operational layer to be stable first.

---

## Appendix A: File Dependency Graph

```
economic_constants.py
    ├── EconomicsGuard.py
    │   ├── QFSV13SDK.py
    │   ├── TreasuryEngine.py
    │   ├── RewardAllocator.py
    │   └── NODAllocator.py
    │
    ├── NODInvariantChecker.py
    │   ├── QFSV13SDK.py
    │   ├── StateTransitionEngine.py
    │   ├── NODAllocator.py
    │   └── InfrastructureGovernance.py
    │
    └── InfrastructureGovernance.py
        └── AEGIS_Node_Verification.py
            ├── NODAllocator.py
            └── InfrastructureGovernance.py

aegisapi.py
    ├── AEGISTelemetrySnapshot (dataclass)
    └── CoherenceLedger.py
        └── constitutional_integrity_report.json

CIR302_Handler.py
    ├── EconomicsGuard violations
    ├── NODInvariantChecker violations
    └── AEGIS_FINALITY_SEAL (enhanced)

Test Files:
    DeterministicReplayTest.py → nod_replay_determinism.json
    BoundaryConditionTests.py → economic_bounds_verification.json
    FailureModeTests.py → failure_mode_verification.json
    PerformanceBenchmarkWithGuards.py → performance_benchmark_guarded.json
```

---

## Appendix B: Error Code Reference

### Economics Guard Codes
- `ECON_BOUND_VIOLATION_CHR_MIN` - CHR reward below minimum
- `ECON_BOUND_VIOLATION_CHR_MAX` - CHR reward above maximum
- `ECON_BOUND_VIOLATION_CHR_DAILY_CAP` - CHR daily emission exceeded
- `ECON_BOUND_VIOLATION_FLX_FRACTION` - FLX allocation fraction out of bounds
- `ECON_BOUND_VIOLATION_NOD_ALLOCATION` - NOD allocation out of bounds
- `GOV_SAFETY_VIOLATION_IMMUTABLE` - Attempted change to [IMMUTABLE] constant
- `GOV_SAFETY_VIOLATION_QUORUM` - Quorum threshold out of bounds

### Invariant Violation Codes
- `INVARIANT_VIOLATION_NOD_I1_TRANSFER` - NOD transfer attempted
- `INVARIANT_VIOLATION_NOD_I2_UNVERIFIED` - NOD to unverified node
- `INVARIANT_VIOLATION_NOD_I3_USER_IMPACT` - NOD governance touched user logic
- `INVARIANT_VIOLATION_NOD_I4_REPLAY` - Replay determinism violated

### AEGIS Codes
- `AEGIS_OFFLINE` - AEGIS completely unavailable
- `AEGIS_DEGRADED` - AEGIS telemetry incomplete
- `AEGIS_RATE_LIMIT_EXCEEDED` - Too many queries in epoch

### CIR-302 Severity Mapping
- **CRITICAL** → Immediate halt, finality seal, manual intervention
- **WARNING** → Logged, operation blocked, system continues
- **INFO** → Logged for audit, operation proceeds

---

## Appendix C: Evidence Artifact Catalog

| Artifact | Purpose | Generated By | Phase |
|----------|---------|--------------|-------|
| `infra_governance_completion_report.json` | Governance testing | InfrastructureGovernance tests | 1 |
| `economics_guard_validation_matrix.json` | Guard coverage | EconomicsGuard tests | 1 |
| `nod_invariant_verification.json` | Invariant checks | NODInvariantChecker tests | 1 |
| `cir302_economic_violations_test.json` | CIR-302 integration | CIR302_Handler tests | 1 |
| `sdk_guard_integration_test.json` | No-bypass verification | QFSV13SDK tests | 2 |
| `aegis_telemetry_determinism_test.json` | Snapshot consistency | aegisapi tests | 2 |
| `constitutional_integrity_report.json` | Config evolution | CoherenceLedger | 2 |
| `node_verification_test.json` | NOD-I2 enforcement | AEGIS_Node_Verification tests | 3 |
| `aegis_offline_policy_test.json` | Degradation scenarios | aegisapi offline tests | 3 |
| `nod_replay_determinism.json` | NOD-I4 verification | DeterministicReplayTest | 4 |
| `economic_bounds_verification.json` | Bounds enforcement | BoundaryConditionTests | 4 |
| `failure_mode_verification.json` | Safe degradation | FailureModeTests | 4 |
| `performance_benchmark_guarded.json` | TPS/latency targets | PerformanceBenchmarkWithGuards | 4 |

---

## END OF QFS V13.6 RELEASE TRACKER

**Version:** 1.0  
**Created:** 2025-12-13  
**Status:** READY FOR IMPLEMENTATION

**Next Steps:**
1. Review this tracker with development team
2. Prioritize Phase 1 components (critical path)
3. Begin with InfrastructureGovernance.py completion
4. Create EconomicsGuard.py (highest leverage)
5. Proceed systematically through Phases 1-5

**Success Definition:**
V13.6 is complete when:
- All 18 components implemented and tested
- All 9 evidence artifacts generated
- Performance targets met (2,000 TPS)
- Documentation synchronized
- Migration guide tested
- Autonomous audit v2.0 can certify release

**This tracker transforms QFS from "constitutionalized" (V13.5) to "operational" (V13.6).**