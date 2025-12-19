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
import sys
import os
from typing import Dict, Any, Optional, List, Set, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum

if TYPE_CHECKING:
    from .NODAllocator import NODAllocation
try:
    from ..CertifiedMath import BigNum128, CertifiedMath
    from ..economics.economic_constants import MAX_NOD_VOTING_POWER_RATIO
except ImportError:
    try:
        from v13.libs.CertifiedMath import BigNum128, CertifiedMath
        from v13.libs.economics.economic_constants import MAX_NOD_VOTING_POWER_RATIO
    except ImportError:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from CertifiedMath import BigNum128, CertifiedMath
        from economics.economic_constants import MAX_NOD_VOTING_POWER_RATIO


class NODInvariantViolationType(Enum):
    """Enumeration of NOD invariant violation types for structured error handling."""

    INVARIANT_NOD_I1_TRANSFER_DETECTED = "INVARIANT_NOD_I1_TRANSFER_DETECTED"
    INVARIANT_NOD_I1_UNAUTHORIZED_WRITE = "INVARIANT_NOD_I1_UNAUTHORIZED_WRITE"
    INVARIANT_NOD_I1_USER_BUNDLE_CONTAMINATION = (
        "INVARIANT_NOD_I1_USER_BUNDLE_CONTAMINATION"
    )
    INVARIANT_NOD_I2_SUPPLY_MISMATCH = "INVARIANT_NOD_I2_SUPPLY_MISMATCH"
    INVARIANT_NOD_I2_NEGATIVE_BALANCE = "INVARIANT_NOD_I2_NEGATIVE_BALANCE"
    INVARIANT_NOD_I2_UNACCOUNTED_ISSUANCE = "INVARIANT_NOD_I2_UNACCOUNTED_ISSUANCE"
    INVARIANT_NOD_I3_VOTING_POWER_EXCEEDED = "INVARIANT_NOD_I3_VOTING_POWER_EXCEEDED"
    INVARIANT_NOD_I3_GOVERNANCE_SCOPE_VIOLATION = (
        "INVARIANT_NOD_I3_GOVERNANCE_SCOPE_VIOLATION"
    )
    INVARIANT_NOD_I3_USER_FACING_MUTATION = "INVARIANT_NOD_I3_USER_FACING_MUTATION"
    INVARIANT_NOD_I4_REPLAY_MISMATCH = "INVARIANT_NOD_I4_REPLAY_MISMATCH"
    INVARIANT_NOD_I4_NON_DETERMINISTIC_ORDER = (
        "INVARIANT_NOD_I4_NON_DETERMINISTIC_ORDER"
    )
    INVARIANT_NOD_I4_HASH_VERIFICATION_FAILURE = (
        "INVARIANT_NOD_I4_HASH_VERIFICATION_FAILURE"
    )


@dataclass
class InvariantCheckResult:
    """Result of NOD invariant validation."""

    passed: bool
    invariant_id: str
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    violation_severity: str = "CRITICAL"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "passed": self.passed,
            "invariant_id": self.invariant_id,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "details": self.details or {},
            "violation_severity": self.violation_severity,
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
        self.authorized_writers = {"NODAllocator", "StateTransitionEngine"}

    def check_non_transferability(
        self,
        caller_module: str,
        operation_type: str,
        node_balances: Dict[str, BigNum128],
        log_list: Optional[List[Dict[str, Any]]] = None,
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
        if caller_module not in self.authorized_writers:
            return InvariantCheckResult(
                passed=False,
                invariant_id="NOD-I1",
                error_code=NODInvariantViolationType.INVARIANT_NOD_I1_UNAUTHORIZED_WRITE.value,
                error_message=f"NOD-I1 violation: Unauthorized write from {caller_module}. Only NODAllocator may modify NOD balances.",
                details={
                    "caller_module": caller_module,
                    "authorized_writers": list(self.authorized_writers),
                    "operation_type": operation_type,
                },
            )
        forbidden_operations = {
            "transfer",
            "trade",
            "swap",
            "exchange",
            "send",
            "receive",
        }
        if operation_type.lower() in forbidden_operations:
            return InvariantCheckResult(
                passed=False,
                invariant_id="NOD-I1",
                error_code=NODInvariantViolationType.INVARIANT_NOD_I1_TRANSFER_DETECTED.value,
                error_message=f"NOD-I1 violation: NOD transfer operation '{operation_type}' is forbidden. NOD is non-transferable.",
                details={
                    "operation_type": operation_type,
                    "forbidden_operations": list(forbidden_operations),
                },
            )
        return InvariantCheckResult(passed=True, invariant_id="NOD-I1")

    def check_supply_conservation(
        self,
        previous_total_supply: BigNum128,
        new_total_supply: BigNum128,
        allocations: List["NODAllocation"],
        log_list: Optional[List[Dict[str, Any]]] = None,
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
        total_allocated = BigNum128.from_int(0)
        for allocation in sorted(allocations, key=lambda a: a.node_id):
            total_allocated = self.cm.add(
                total_allocated, allocation.nod_amount, log_list
            )
        expected_new_supply = self.cm.add(
            previous_total_supply, total_allocated, log_list
        )
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
                    "discrepancy": self.cm.sub(
                        new_total_supply, expected_new_supply, log_list
                    ).to_decimal_string(),
                },
            )
        for allocation in sorted(allocations, key=lambda a: a.node_id):
            if allocation.nod_amount.value < 0:
                return InvariantCheckResult(
                    passed=False,
                    invariant_id="NOD-I2",
                    error_code=NODInvariantViolationType.INVARIANT_NOD_I2_NEGATIVE_BALANCE.value,
                    error_message=f"NOD-I2 violation: Negative allocation detected for node {allocation.node_id}",
                    details={
                        "node_id": allocation.node_id,
                        "nod_amount": allocation.nod_amount.to_decimal_string(),
                    },
                )
        return InvariantCheckResult(passed=True, invariant_id="NOD-I2")

    def check_voting_power_bounds(
        self,
        node_balances: Dict[str, BigNum128],
        total_nod_supply: BigNum128,
        log_list: Optional[List[Dict[str, Any]]] = None,
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
        if total_nod_supply.value == 0:
            return InvariantCheckResult(passed=True, invariant_id="NOD-I3")
        for node_id, node_balance in node_balances.items():
            if node_id == "balance":
                continue

            # node_balance might be a string from state dict, handle robustly
            voting_power_ratio = self.cm.div(node_balance, total_nod_supply, log_list)
            if voting_power_ratio.value > MAX_NOD_VOTING_POWER_RATIO.value:
                # Ensure we have a string for the error message
                node_bal_str = (
                    node_balance.to_decimal_string()
                    if hasattr(node_balance, "to_decimal_string")
                    else str(node_balance)
                )
                return InvariantCheckResult(
                    passed=False,
                    invariant_id="NOD-I3",
                    error_code=NODInvariantViolationType.INVARIANT_NOD_I3_VOTING_POWER_EXCEEDED.value,
                    error_message=f"NOD-I3 violation: Node {node_id} voting power {voting_power_ratio.to_decimal_string()} exceeds maximum {MAX_NOD_VOTING_POWER_RATIO.to_decimal_string()}",
                    details={
                        "node_id": node_id,
                        "node_balance": node_bal_str,
                        "total_supply": total_nod_supply.to_decimal_string(),
                        "voting_power_ratio": voting_power_ratio.to_decimal_string(),
                        "max_allowed": MAX_NOD_VOTING_POWER_RATIO.to_decimal_string(),
                    },
                )
        return InvariantCheckResult(passed=True, invariant_id="NOD-I3")

    def check_deterministic_allocation(
        self,
        allocations: List["NODAllocation"],
        expected_hash: Optional[str] = None,
        log_list: Optional[List[Dict[str, Any]]] = None,
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
        sorted_allocations = sorted(allocations, key=lambda a: a.node_id)
        for i, allocation in enumerate(allocations):
            if allocation.node_id != sorted_allocations[i].node_id:
                return InvariantCheckResult(
                    passed=False,
                    invariant_id="NOD-I4",
                    error_code=NODInvariantViolationType.INVARIANT_NOD_I4_NON_DETERMINISTIC_ORDER.value,
                    error_message=f"NOD-I4 violation: Allocations not in deterministic sorted order",
                    details={
                        "expected_order": [a.node_id for a in sorted_allocations],
                        "actual_order": [a.node_id for a in allocations],
                    },
                )
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
                        "allocation_count": len(allocations),
                    },
                )
        return InvariantCheckResult(passed=True, invariant_id="NOD-I4")

    def validate_all_invariants(
        self,
        caller_module: str,
        operation_type: str,
        previous_total_supply: BigNum128,
        new_total_supply: BigNum128,
        node_balances: Dict[str, BigNum128],
        allocations: List["NODAllocation"],
        expected_hash: Optional[str] = None,
        log_list: Optional[List[Dict[str, Any]]] = None,
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
        results.append(
            self.check_non_transferability(
                caller_module, operation_type, node_balances, log_list
            )
        )
        results.append(
            self.check_supply_conservation(
                previous_total_supply, new_total_supply, allocations, log_list
            )
        )
        results.append(
            self.check_voting_power_bounds(node_balances, new_total_supply, log_list)
        )
        results.append(
            self.check_deterministic_allocation(allocations, expected_hash, log_list)
        )
        return results

    def generate_allocation_hash(self, allocations: List["NODAllocation"]) -> str:
        """
        Generate SHA-256 hash of allocation results for replay verification.

        Args:
            allocations: List of NOD allocations

        Returns:
            str: 64-character SHA-256 hash
        """
        sorted_allocations = sorted(allocations, key=lambda a: a.node_id)
        allocation_data = {
            "allocations": [
                {
                    "node_id": a.node_id,
                    "nod_amount": a.nod_amount.to_decimal_string(),
                    "contribution_score": a.contribution_score.to_decimal_string(),
                    "timestamp": a.timestamp,
                }
                for a in sorted_allocations
            ]
        }
        allocation_json = json.dumps(
            allocation_data, sort_keys=True, separators=(",", ":")
        )
        return hashlib.sha256(allocation_json.encode("utf-8")).hexdigest()

    def generate_violation_event_hash(
        self, result: InvariantCheckResult, timestamp: int
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
            "timestamp": timestamp,
        }
        event_json = json.dumps(event_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(event_json.encode("utf-8")).hexdigest()


def test_nod_invariant_checker():
    """
    Test the NODInvariantChecker implementation with all four invariants.
    """
    cm = CertifiedMath()
    checker = NODInvariantChecker(cm)
    result = checker.check_non_transferability(
        caller_module="NODAllocator",
        operation_type="allocation",
        node_balances={"node1": BigNum128.from_int(1000)},
    )
    assert result.passed == True, "Authorized allocation should pass NOD-I1"
    result = checker.check_non_transferability(
        caller_module="TreasuryEngine",
        operation_type="allocation",
        node_balances={"node1": BigNum128.from_int(1000)},
    )
    assert result.passed == False, "Unauthorized write should violate NOD-I1"
    assert result.error_code == "INVARIANT_NOD_I1_UNAUTHORIZED_WRITE"
    result = checker.check_non_transferability(
        caller_module="NODAllocator",
        operation_type="transfer",
        node_balances={"node1": BigNum128.from_int(1000)},
    )
    assert result.passed == False, "Transfer operation should violate NOD-I1"
    assert result.error_code == "INVARIANT_NOD_I1_TRANSFER_DETECTED"
    allocations = [
        NODAllocation("node1", BigNum128.from_int(500), BigNum128.from_int(50), 1000),
        NODAllocation("node2", BigNum128.from_int(500), BigNum128.from_int(50), 1000),
    ]
    previous_supply = BigNum128.from_int(10000)
    new_supply = BigNum128.from_int(11000)
    result = checker.check_supply_conservation(previous_supply, new_supply, allocations)
    assert result.passed == True, "Conserved supply should pass NOD-I2"
    bad_new_supply = BigNum128.from_int(11500)
    result = checker.check_supply_conservation(
        previous_supply, bad_new_supply, allocations
    )
    assert result.passed == False, "Supply mismatch should violate NOD-I2"
    assert result.error_code == "INVARIANT_NOD_I2_SUPPLY_MISMATCH"
    node_balances = {
        "node1": BigNum128.from_int(2000),
        "node2": BigNum128.from_int(2000),
        "node3": BigNum128.from_int(6000),
    }
    total_supply = BigNum128.from_int(10000)
    balanced_balances = {
        "node1": BigNum128.from_int(2000),
        "node2": BigNum128.from_int(2000),
        "node3": BigNum128.from_int(2000),
        "node4": BigNum128.from_int(2000),
        "node5": BigNum128.from_int(2000),
    }
    result = checker.check_voting_power_bounds(balanced_balances, total_supply)
    assert result.passed == True, "Balanced voting power should pass NOD-I3"
    excessive_balances = {
        "node1": BigNum128.from_int(3000),
        "node2": BigNum128.from_int(7000),
    }
    result = checker.check_voting_power_bounds(excessive_balances, total_supply)
    assert result.passed == False, "Excessive voting power should violate NOD-I3"
    assert result.error_code == "INVARIANT_NOD_I3_VOTING_POWER_EXCEEDED"
    sorted_allocations = [
        NODAllocation("node1", BigNum128.from_int(500), BigNum128.from_int(50), 1000),
        NODAllocation("node2", BigNum128.from_int(500), BigNum128.from_int(50), 1000),
    ]
    result = checker.check_deterministic_allocation(sorted_allocations)
    assert result.passed == True, "Sorted allocations should pass NOD-I4"
    unsorted_allocations = [
        NODAllocation("node2", BigNum128.from_int(500), BigNum128.from_int(50), 1000),
        NODAllocation("node1", BigNum128.from_int(500), BigNum128.from_int(50), 1000),
    ]
    result = checker.check_deterministic_allocation(unsorted_allocations)
    assert result.passed == False, "Unsorted allocations should violate NOD-I4"
    assert result.error_code == "INVARIANT_NOD_I4_NON_DETERMINISTIC_ORDER"
    expected_hash = checker.generate_allocation_hash(sorted_allocations)
    result = checker.check_deterministic_allocation(sorted_allocations, expected_hash)
    assert result.passed == True, "Matching hash should pass NOD-I4"
    assert len(expected_hash) == 64, "Hash should be 64 characters"
    bad_hash = "0" * 64
    result = checker.check_deterministic_allocation(sorted_allocations, bad_hash)
    assert result.passed == False, "Hash mismatch should violate NOD-I4"
    assert result.error_code == "INVARIANT_NOD_I4_HASH_VERIFICATION_FAILURE"
    all_results = checker.validate_all_invariants(
        caller_module="NODAllocator",
        operation_type="allocation",
        previous_total_supply=previous_supply,
        new_total_supply=new_supply,
        node_balances=balanced_balances,
        allocations=sorted_allocations,
        expected_hash=expected_hash,
    )
    for i, r in enumerate(all_results, 1):
        pass
    assert len(all_results) == 4, "Should check all 4 invariants"
    assert all((r.passed for r in all_results)), "All invariants should pass"
    violation = InvariantCheckResult(
        passed=False,
        invariant_id="NOD-I1",
        error_code="INVARIANT_NOD_I1_TRANSFER_DETECTED",
        error_message="Test violation",
        details={"operation": "transfer"},
    )
    event_hash = checker.generate_violation_event_hash(violation, 1000)
    assert len(event_hash) == 64, "Event hash should be 64 characters"


if __name__ == "__main__":
    test_nod_invariant_checker()
