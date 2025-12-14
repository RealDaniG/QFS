"""
NODInvariantChecker.py - Formal Invariant Enforcement for NOD Token System

Implements the NODInvariantChecker class to enforce the four formal NOD invariants:
- NOD-I1: Non-transferability (all state changes from NODAllocator only)
- NOD-I2: Supply conservation (total NOD supply matches allocations)
- NOD-I3: Voting power bounds (max 25% per node)
- NOD-I4: Allocation fairness (deterministic, bit-for-bit reproducible)

These invariants serve as audit anchors and enforce negative guarantees:
- No transfer between entities
- No supply inflation/deflation
- No governance capture via excessive voting power
- Bit-for-bit replay determinism

This is a CRITICAL component of the V13.6 constitutional integration.
All NOD-related state changes MUST pass through NODInvariantChecker.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List, Set, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum

# V13.6: TYPE_CHECKING import to avoid circular dependency with NODAllocator
if TYPE_CHECKING:
    from .NODAllocator import NODAllocation

# Import required modules
try:
    from ..CertifiedMath import BigNum128, CertifiedMath
    from ..economics.economic_constants import MAX_NOD_VOTING_POWER_RATIO
except ImportError:
    try:
        from v13.libs.CertifiedMath import BigNum128, CertifiedMath
        from v13.libs.economics.economic_constants import MAX_NOD_VOTING_POWER_RATIO
    except ImportError:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from CertifiedMath import BigNum128, CertifiedMath
        from economics.economic_constants import MAX_NOD_VOTING_POWER_RATIO


# =============================================================================
# STRUCTURED ERROR CODES FOR NOD INVARIANT VIOLATIONS
# =============================================================================

class NODInvariantViolationType(Enum):
    """Enumeration of NOD invariant violation types for structured error handling."""
    
    # NOD-I1: Non-Transferability Violations
    INVARIANT_NOD_I1_TRANSFER_DETECTED = "INVARIANT_NOD_I1_TRANSFER_DETECTED"
    INVARIANT_NOD_I1_UNAUTHORIZED_WRITE = "INVARIANT_NOD_I1_UNAUTHORIZED_WRITE"
    INVARIANT_NOD_I1_USER_BUNDLE_CONTAMINATION = "INVARIANT_NOD_I1_USER_BUNDLE_CONTAMINATION"
    
    # NOD-I2: Supply Conservation Violations
    INVARIANT_NOD_I2_SUPPLY_MISMATCH = "INVARIANT_NOD_I2_SUPPLY_MISMATCH"
    INVARIANT_NOD_I2_NEGATIVE_BALANCE = "INVARIANT_NOD_I2_NEGATIVE_BALANCE"
    INVARIANT_NOD_I2_UNACCOUNTED_ISSUANCE = "INVARIANT_NOD_I2_UNACCOUNTED_ISSUANCE"
    
    # NOD-I3: Voting Power Bounds Violations
    INVARIANT_NOD_I3_VOTING_POWER_EXCEEDED = "INVARIANT_NOD_I3_VOTING_POWER_EXCEEDED"
    INVARIANT_NOD_I3_GOVERNANCE_SCOPE_VIOLATION = "INVARIANT_NOD_I3_GOVERNANCE_SCOPE_VIOLATION"
    INVARIANT_NOD_I3_USER_FACING_MUTATION = "INVARIANT_NOD_I3_USER_FACING_MUTATION"
    
    # NOD-I4: Determinism Violations
    INVARIANT_NOD_I4_REPLAY_MISMATCH = "INVARIANT_NOD_I4_REPLAY_MISMATCH"
    INVARIANT_NOD_I4_NON_DETERMINISTIC_ORDER = "INVARIANT_NOD_I4_NON_DETERMINISTIC_ORDER"
    INVARIANT_NOD_I4_HASH_VERIFICATION_FAILURE = "INVARIANT_NOD_I4_HASH_VERIFICATION_FAILURE"


@dataclass
class InvariantCheckResult:
    """Result of NOD invariant validation."""
    passed: bool
    invariant_id: str  # NOD-I1, NOD-I2, NOD-I3, or NOD-I4
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    violation_severity: str = "CRITICAL"  # All NOD invariants are CRITICAL
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "passed": self.passed,
            "invariant_id": self.invariant_id,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "details": self.details or {},
            "violation_severity": self.violation_severity
        }


class NODInvariantChecker:
    """
    Formal Invariant Enforcer for NOD Token System.
    
    Enforces the four constitutional NOD invariants:
    - NOD-I1: Non-transferability
    - NOD-I2: Supply conservation
    - NOD-I3: Voting power bounds
    - NOD-I4: Allocation fairness (determinism)
    
    All NOD-related state changes MUST pass through this checker.
    Violations trigger structured errors for CIR-302 handler integration.
    """
    
    def __init__(self, cm_instance: CertifiedMath):
        """
        Initialize the NOD Invariant Checker.
        
        Args:
            cm_instance: CertifiedMath instance for deterministic comparisons
        """
        self.cm = cm_instance
        
        # Registry of authorized NOD writers (only NODAllocator allowed)
        self.authorized_writers = {"NODAllocator"}
    
    # =========================================================================
    # NOD-I1: NON-TRANSFERABILITY ENFORCEMENT
    # =========================================================================
    
    def check_non_transferability(
        self,
        caller_module: str,
        operation_type: str,
        node_balances: Dict[str, BigNum128],
        log_list: Optional[List[Dict[str, Any]]] = None
    ) -> InvariantCheckResult:
        """
        Enforce NOD-I1: At no point may NOD be transferred between entities.
        
        All NOD state changes must originate from NODAllocator.
        Any attempt to transfer, trade, or move NOD between accounts is a violation.
        
        Args:
            caller_module: Name of the module attempting NOD state change
            operation_type: Type of operation (e.g., "allocation", "transfer", "trade")
            node_balances: Current NOD balance state (for audit trail)
            log_list: Optional log list for audit trail
            
        Returns:
            InvariantCheckResult with pass/fail and violation details
        """
        if log_list is None:
            log_list = []
        
        # Check 1: Caller must be authorized (NODAllocator only)
        if caller_module not in self.authorized_writers:
            return InvariantCheckResult(
                passed=False,
                invariant_id="NOD-I1",
                error_code=NODInvariantViolationType.INVARIANT_NOD_I1_UNAUTHORIZED_WRITE.value,
                error_message=f"NOD-I1 violation: Unauthorized write from {caller_module}. Only NODAllocator may modify NOD balances.",
                details={
                    "caller_module": caller_module,
                    "authorized_writers": list(self.authorized_writers),
                    "operation_type": operation_type
                }
            )
        
        # Check 2: Operation type must not be "transfer" or "trade"
        forbidden_operations = {"transfer", "trade", "swap", "exchange", "send", "receive"}
        if operation_type.lower() in forbidden_operations:
            return InvariantCheckResult(
                passed=False,
                invariant_id="NOD-I1",
                error_code=NODInvariantViolationType.INVARIANT_NOD_I1_TRANSFER_DETECTED.value,
                error_message=f"NOD-I1 violation: NOD transfer operation '{operation_type}' is forbidden. NOD is non-transferable.",
                details={
                    "operation_type": operation_type,
                    "forbidden_operations": list(forbidden_operations)
                }
            )
        
        return InvariantCheckResult(
            passed=True,
            invariant_id="NOD-I1"
        )
    
    # =========================================================================
    # NOD-I2: SUPPLY CONSERVATION ENFORCEMENT
    # =========================================================================
    
    def check_supply_conservation(
        self,
        previous_total_supply: BigNum128,
        new_total_supply: BigNum128,
        allocations: List['NODAllocation'],
        log_list: Optional[List[Dict[str, Any]]] = None
    ) -> InvariantCheckResult:
        """
        Enforce NOD-I2: Total NOD supply must equal sum of all allocations.
        
        Supply conservation ensures:
        - No unaccounted issuance
        - No supply inflation/deflation
        - Perfect audit trail
        
        Args:
            previous_total_supply: Total NOD supply before allocation
            new_total_supply: Total NOD supply after allocation
            allocations: List of NOD allocations made
            log_list: Optional log list for audit trail
            
        Returns:
            InvariantCheckResult with pass/fail and violation details
        """
        if log_list is None:
            log_list = []
        
        # Calculate total allocated amount
        total_allocated = BigNum128.from_int(0)
        for allocation in allocations:
            total_allocated = self.cm.add(total_allocated, allocation.nod_amount, log_list)
        
        # Calculate expected new supply
        expected_new_supply = self.cm.add(previous_total_supply, total_allocated, log_list)
        
        # Check 1: New supply must equal previous + allocated
        if new_total_supply.value != expected_new_supply.value:
            return InvariantCheckResult(
                passed=False,
                invariant_id="NOD-I2",
                error_code=NODInvariantViolationType.INVARIANT_NOD_I2_SUPPLY_MISMATCH.value,
                error_message=f"NOD-I2 violation: Supply mismatch. Expected {expected_new_supply.to_decimal_string()}, got {new_total_supply.to_decimal_string()}",
                details={
                    "previous_total_supply": previous_total_supply.to_decimal_string(),
                    "total_allocated": total_allocated.to_decimal_string(),
                    "expected_new_supply": expected_new_supply.to_decimal_string(),
                    "actual_new_supply": new_total_supply.to_decimal_string(),
                    "discrepancy": self.cm.sub(new_total_supply, expected_new_supply, log_list).to_decimal_string()
                }
            )
        
        # Check 2: No negative balances in allocations
        for allocation in allocations:
            if allocation.nod_amount.value < 0:
                return InvariantCheckResult(
                    passed=False,
                    invariant_id="NOD-I2",
                    error_code=NODInvariantViolationType.INVARIANT_NOD_I2_NEGATIVE_BALANCE.value,
                    error_message=f"NOD-I2 violation: Negative allocation detected for node {allocation.node_id}",
                    details={
                        "node_id": allocation.node_id,
                        "nod_amount": allocation.nod_amount.to_decimal_string()
                    }
                )
        
        return InvariantCheckResult(
            passed=True,
            invariant_id="NOD-I2"
        )
    
    # =========================================================================
    # NOD-I3: VOTING POWER BOUNDS ENFORCEMENT
    # =========================================================================
    
    def check_voting_power_bounds(
        self,
        node_balances: Dict[str, BigNum128],
        total_nod_supply: BigNum128,
        log_list: Optional[List[Dict[str, Any]]] = None
    ) -> InvariantCheckResult:
        """
        Enforce NOD-I3: No single node may exceed 25% of total voting power.
        
        Voting power bounds prevent governance capture by ensuring:
        - No single node dominance (max 25% voting power)
        - Distributed governance control
        - Sybil resistance via AEGIS registration
        
        Args:
            node_balances: Dictionary mapping node IDs to NOD balances
            total_nod_supply: Total NOD supply across all nodes
            log_list: Optional log list for audit trail
            
        Returns:
            InvariantCheckResult with pass/fail and violation details
        """
        if log_list is None:
            log_list = []
        
        # Avoid division by zero
        if total_nod_supply.value == 0:
            return InvariantCheckResult(
                passed=True,
                invariant_id="NOD-I3"
            )
        
        # Check each node's voting power ratio
        for node_id, node_balance in node_balances.items():
            voting_power_ratio = self.cm.div(node_balance, total_nod_supply, log_list)
            
            if voting_power_ratio.value > MAX_NOD_VOTING_POWER_RATIO.value:
                return InvariantCheckResult(
                    passed=False,
                    invariant_id="NOD-I3",
                    error_code=NODInvariantViolationType.INVARIANT_NOD_I3_VOTING_POWER_EXCEEDED.value,
                    error_message=f"NOD-I3 violation: Node {node_id} voting power {voting_power_ratio.to_decimal_string()} exceeds maximum {MAX_NOD_VOTING_POWER_RATIO.to_decimal_string()}",
                    details={
                        "node_id": node_id,
                        "node_balance": node_balance.to_decimal_string(),
                        "total_supply": total_nod_supply.to_decimal_string(),
                        "voting_power_ratio": voting_power_ratio.to_decimal_string(),
                        "max_allowed": MAX_NOD_VOTING_POWER_RATIO.to_decimal_string()
                    }
                )
        
        return InvariantCheckResult(
            passed=True,
            invariant_id="NOD-I3"
        )
    
    # =========================================================================
    # NOD-I4: DETERMINISTIC ALLOCATION ENFORCEMENT
    # =========================================================================
    
    def check_deterministic_allocation(
        self,
        allocations: List['NODAllocation'],
        expected_hash: Optional[str] = None,
        log_list: Optional[List[Dict[str, Any]]] = None
    ) -> InvariantCheckResult:
        """
        Enforce NOD-I4: Given identical inputs, NOD allocation must be bit-for-bit reproducible.
        
        Determinism enforcement ensures:
        - Replay integrity (identical ledger state + telemetry → identical allocation)
        - Sorted iteration (deterministic node order)
        - Hash verification (allocation results match expected hash)
        
        Args:
            allocations: List of NOD allocations to verify
            expected_hash: Optional SHA-256 hash of expected allocation results
            log_list: Optional log list for audit trail
            
        Returns:
            InvariantCheckResult with pass/fail and violation details
        """
        if log_list is None:
            log_list = []
        
        # Check 1: Allocations must be in deterministic sorted order (by node_id)
        sorted_allocations = sorted(allocations, key=lambda a: a.node_id)
        
        # Compare original order with sorted order
        for i, allocation in enumerate(allocations):
            if allocation.node_id != sorted_allocations[i].node_id:
                return InvariantCheckResult(
                    passed=False,
                    invariant_id="NOD-I4",
                    error_code=NODInvariantViolationType.INVARIANT_NOD_I4_NON_DETERMINISTIC_ORDER.value,
                    error_message=f"NOD-I4 violation: Allocations not in deterministic sorted order",
                    details={
                        "expected_order": [a.node_id for a in sorted_allocations],
                        "actual_order": [a.node_id for a in allocations]
                    }
                )
        
        # Check 2: If expected hash provided, verify allocation results match
        if expected_hash is not None:
            actual_hash = self.generate_allocation_hash(allocations)
            
            if actual_hash != expected_hash:
                return InvariantCheckResult(
                    passed=False,
                    invariant_id="NOD-I4",
                    error_code=NODInvariantViolationType.INVARIANT_NOD_I4_HASH_VERIFICATION_FAILURE.value,
                    error_message=f"NOD-I4 violation: Allocation hash mismatch (replay failure)",
                    details={
                        "expected_hash": expected_hash,
                        "actual_hash": actual_hash,
                        "allocation_count": len(allocations)
                    }
                )
        
        return InvariantCheckResult(
            passed=True,
            invariant_id="NOD-I4"
        )
    
    # =========================================================================
    # COMPREHENSIVE INVARIANT VALIDATION
    # =========================================================================
    
    def validate_all_invariants(
        self,
        caller_module: str,
        operation_type: str,
        previous_total_supply: BigNum128,
        new_total_supply: BigNum128,
        node_balances: Dict[str, BigNum128],
        allocations: List['NODAllocation'],
        expected_hash: Optional[str] = None,
        log_list: Optional[List[Dict[str, Any]]] = None
    ) -> List[InvariantCheckResult]:
        """
        Validate all four NOD invariants in a single call.
        
        This is the primary entry point for comprehensive NOD validation.
        Returns a list of results, one for each invariant.
        
        Args:
            caller_module: Module attempting NOD state change
            operation_type: Type of operation being performed
            previous_total_supply: Total NOD supply before operation
            new_total_supply: Total NOD supply after operation
            node_balances: Current NOD balance state
            allocations: List of NOD allocations made
            expected_hash: Optional expected hash for replay verification
            log_list: Optional log list for audit trail
            
        Returns:
            List[InvariantCheckResult]: Results for all four invariants
        """
        if log_list is None:
            log_list = []
        
        results = []
        
        # Check NOD-I1: Non-transferability
        results.append(self.check_non_transferability(
            caller_module, operation_type, node_balances, log_list
        ))
        
        # Check NOD-I2: Supply conservation
        results.append(self.check_supply_conservation(
            previous_total_supply, new_total_supply, allocations, log_list
        ))
        
        # Check NOD-I3: Voting power bounds
        results.append(self.check_voting_power_bounds(
            node_balances, new_total_supply, log_list
        ))
        
        # Check NOD-I4: Deterministic allocation
        results.append(self.check_deterministic_allocation(
            allocations, expected_hash, log_list
        ))
        
        return results
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def generate_allocation_hash(self, allocations: List['NODAllocation']) -> str:
        """
        Generate SHA-256 hash of allocation results for replay verification.
        
        Args:
            allocations: List of NOD allocations
            
        Returns:
            str: 64-character SHA-256 hash
        """
        # Sort allocations by node_id for deterministic ordering
        sorted_allocations = sorted(allocations, key=lambda a: a.node_id)
        
        # Create deterministic representation
        allocation_data = {
            "allocations": [
                {
                    "node_id": a.node_id,
                    "nod_amount": a.nod_amount.to_decimal_string(),
                    "contribution_score": a.contribution_score.to_decimal_string(),
                    "timestamp": a.timestamp
                }
                for a in sorted_allocations
            ]
        }
        
        # Generate SHA-256 hash
        allocation_json = json.dumps(allocation_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(allocation_json.encode('utf-8')).hexdigest()
    
    def generate_violation_event_hash(
        self,
        result: InvariantCheckResult,
        timestamp: int
    ) -> str:
        """
        Generate SHA-256 event hash for invariant violation (Merkle inclusion).
        
        Args:
            result: Invariant check result with violation details
            timestamp: Deterministic timestamp
            
        Returns:
            str: 64-character SHA-256 hash
        """
        event_data = {
            "operation": "nod_invariant_violation",
            "invariant_id": result.invariant_id,
            "error_code": result.error_code,
            "error_message": result.error_message,
            "details": result.details,
            "timestamp": timestamp
        }
        
        event_json = json.dumps(event_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(event_json.encode('utf-8')).hexdigest()


# =============================================================================
# TEST FUNCTION
# =============================================================================

def test_nod_invariant_checker():
    """
    Test the NODInvariantChecker implementation with all four invariants.
    """
    print("\n=== Testing NODInvariantChecker - Formal Invariant Enforcement ===")
    
    cm = CertifiedMath()
    checker = NODInvariantChecker(cm)
    
    print("\n--- Scenario 1: NOD-I1 Non-Transferability (Happy Path) ---")
    result = checker.check_non_transferability(
        caller_module="NODAllocator",
        operation_type="allocation",
        node_balances={"node1": BigNum128.from_int(1000)}
    )
    print(f"NOD-I1 check: {result.passed}")
    assert result.passed == True, "Authorized allocation should pass NOD-I1"
    
    print("\n--- Scenario 2: NOD-I1 Unauthorized Write Violation ---")
    result = checker.check_non_transferability(
        caller_module="TreasuryEngine",
        operation_type="allocation",
        node_balances={"node1": BigNum128.from_int(1000)}
    )
    print(f"NOD-I1 check: {result.passed}")
    print(f"Error code: {result.error_code}")
    assert result.passed == False, "Unauthorized write should violate NOD-I1"
    assert result.error_code == "INVARIANT_NOD_I1_UNAUTHORIZED_WRITE"
    
    print("\n--- Scenario 3: NOD-I1 Transfer Detection Violation ---")
    result = checker.check_non_transferability(
        caller_module="NODAllocator",
        operation_type="transfer",  # Forbidden operation
        node_balances={"node1": BigNum128.from_int(1000)}
    )
    print(f"NOD-I1 check: {result.passed}")
    print(f"Error code: {result.error_code}")
    assert result.passed == False, "Transfer operation should violate NOD-I1"
    assert result.error_code == "INVARIANT_NOD_I1_TRANSFER_DETECTED"
    
    print("\n--- Scenario 4: NOD-I2 Supply Conservation (Happy Path) ---")
    allocations = [
        NODAllocation("node1", BigNum128.from_int(500), BigNum128.from_int(50), 1000),
        NODAllocation("node2", BigNum128.from_int(500), BigNum128.from_int(50), 1000)
    ]
    previous_supply = BigNum128.from_int(10000)
    new_supply = BigNum128.from_int(11000)  # 10000 + 1000 allocated
    
    result = checker.check_supply_conservation(previous_supply, new_supply, allocations)
    print(f"NOD-I2 check: {result.passed}")
    assert result.passed == True, "Conserved supply should pass NOD-I2"
    
    print("\n--- Scenario 5: NOD-I2 Supply Mismatch Violation ---")
    bad_new_supply = BigNum128.from_int(11500)  # Incorrect (should be 11000)
    
    result = checker.check_supply_conservation(previous_supply, bad_new_supply, allocations)
    print(f"NOD-I2 check: {result.passed}")
    print(f"Error code: {result.error_code}")
    assert result.passed == False, "Supply mismatch should violate NOD-I2"
    assert result.error_code == "INVARIANT_NOD_I2_SUPPLY_MISMATCH"
    
    print("\n--- Scenario 6: NOD-I3 Voting Power Bounds (Happy Path) ---")
    node_balances = {
        "node1": BigNum128.from_int(2000),  # 20% of 10000
        "node2": BigNum128.from_int(2000),  # 20%
        "node3": BigNum128.from_int(6000)   # 60% - but we'll test 25% cap later
    }
    total_supply = BigNum128.from_int(10000)
    
    # First test with balanced distribution
    balanced_balances = {
        "node1": BigNum128.from_int(2000),  # 20%
        "node2": BigNum128.from_int(2000),  # 20%
        "node3": BigNum128.from_int(2000),  # 20%
        "node4": BigNum128.from_int(2000),  # 20%
        "node5": BigNum128.from_int(2000)   # 20%
    }
    
    result = checker.check_voting_power_bounds(balanced_balances, total_supply)
    print(f"NOD-I3 check: {result.passed}")
    assert result.passed == True, "Balanced voting power should pass NOD-I3"
    
    print("\n--- Scenario 7: NOD-I3 Voting Power Exceeded Violation ---")
    excessive_balances = {
        "node1": BigNum128.from_int(3000),  # 30% > 25% cap!
        "node2": BigNum128.from_int(7000)   # 70%
    }
    
    result = checker.check_voting_power_bounds(excessive_balances, total_supply)
    print(f"NOD-I3 check: {result.passed}")
    print(f"Error code: {result.error_code}")
    assert result.passed == False, "Excessive voting power should violate NOD-I3"
    assert result.error_code == "INVARIANT_NOD_I3_VOTING_POWER_EXCEEDED"
    
    print("\n--- Scenario 8: NOD-I4 Deterministic Allocation (Happy Path) ---")
    sorted_allocations = [
        NODAllocation("node1", BigNum128.from_int(500), BigNum128.from_int(50), 1000),
        NODAllocation("node2", BigNum128.from_int(500), BigNum128.from_int(50), 1000)
    ]
    
    result = checker.check_deterministic_allocation(sorted_allocations)
    print(f"NOD-I4 check: {result.passed}")
    assert result.passed == True, "Sorted allocations should pass NOD-I4"
    
    print("\n--- Scenario 9: NOD-I4 Non-Deterministic Order Violation ---")
    unsorted_allocations = [
        NODAllocation("node2", BigNum128.from_int(500), BigNum128.from_int(50), 1000),
        NODAllocation("node1", BigNum128.from_int(500), BigNum128.from_int(50), 1000)  # Wrong order!
    ]
    
    result = checker.check_deterministic_allocation(unsorted_allocations)
    print(f"NOD-I4 check: {result.passed}")
    print(f"Error code: {result.error_code}")
    assert result.passed == False, "Unsorted allocations should violate NOD-I4"
    assert result.error_code == "INVARIANT_NOD_I4_NON_DETERMINISTIC_ORDER"
    
    print("\n--- Scenario 10: NOD-I4 Hash Verification (Happy Path) ---")
    expected_hash = checker.generate_allocation_hash(sorted_allocations)
    
    result = checker.check_deterministic_allocation(sorted_allocations, expected_hash)
    print(f"NOD-I4 check: {result.passed}")
    print(f"Allocation hash: {expected_hash[:32]}...")
    assert result.passed == True, "Matching hash should pass NOD-I4"
    assert len(expected_hash) == 64, "Hash should be 64 characters"
    
    print("\n--- Scenario 11: NOD-I4 Hash Mismatch Violation ---")
    bad_hash = "0" * 64  # Wrong hash
    
    result = checker.check_deterministic_allocation(sorted_allocations, bad_hash)
    print(f"NOD-I4 check: {result.passed}")
    print(f"Error code: {result.error_code}")
    assert result.passed == False, "Hash mismatch should violate NOD-I4"
    assert result.error_code == "INVARIANT_NOD_I4_HASH_VERIFICATION_FAILURE"
    
    print("\n--- Scenario 12: Comprehensive Validation (All Invariants) ---")
    all_results = checker.validate_all_invariants(
        caller_module="NODAllocator",
        operation_type="allocation",
        previous_total_supply=previous_supply,
        new_total_supply=new_supply,
        node_balances=balanced_balances,
        allocations=sorted_allocations,
        expected_hash=expected_hash
    )
    
    print(f"Total invariants checked: {len(all_results)}")
    for i, r in enumerate(all_results, 1):
        print(f"  {r.invariant_id}: {'PASS' if r.passed else 'FAIL'}")
    
    assert len(all_results) == 4, "Should check all 4 invariants"
    assert all(r.passed for r in all_results), "All invariants should pass"
    
    print("\n--- Scenario 13: Violation Event Hash Generation ---")
    violation = InvariantCheckResult(
        passed=False,
        invariant_id="NOD-I1",
        error_code="INVARIANT_NOD_I1_TRANSFER_DETECTED",
        error_message="Test violation",
        details={"operation": "transfer"}
    )
    event_hash = checker.generate_violation_event_hash(violation, 1000)
    print(f"Violation event hash: {event_hash[:32]}...")
    assert len(event_hash) == 64, "Event hash should be 64 characters"
    
    print("\n✅ All 13 NODInvariantChecker scenarios passed!")
    print("\n=== NODInvariantChecker is QFS V13.6 Compliant ===")


if __name__ == "__main__":
    test_nod_invariant_checker()
