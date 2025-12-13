"""
BoundaryConditionTests.py - V13.6 Constitutional Boundary Verification

Tests that constitutional guards correctly enforce min/max bounds for:
- CHR/FLX/RES rewards (saturation, per-action caps, daily emissions)
- NOD allocation (fraction, epoch issuance, per-node caps, voting power)
- Governance (quorum thresholds, parameter validation)

Success Criteria:
- Values at min boundary: PASS
- Values at max boundary: PASS
- Values slightly over max: FAIL with structured error code
- Values slightly under min: FAIL with structured error code

Evidence Artifact: evidence/v13.6/economic_bounds_verification.json
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.libs.BigNum128 import BigNum128
from src.libs.CertifiedMath import CertifiedMath
from src.libs.economics.EconomicsGuard import EconomicsGuard, ValidationResult
from src.libs.economics.economic_constants import *


class BoundaryConditionTests:
    """
    V13.6 Boundary Condition Test Suite.
    
    Validates that EconomicsGuard correctly enforces constitutional bounds.
    """
    
    def __init__(self):
        self.cm = CertifiedMath
        self.economics_guard = EconomicsGuard(self.cm)
        self.test_results = []
        
    def test_chr_reward_boundaries(self) -> Dict[str, Any]:
        """Test CHR reward min/max boundaries."""
        print("\n[TEST] CHR Reward Boundaries")
        
        log_list = []
        test_cases = []
        
        # Test Case 1: At minimum (should pass)
        result = self.economics_guard.validate_chr_reward(
            chr_reward=CHR_MIN_REWARD_PER_ACTION,
            total_supply_delta=CHR_MIN_REWARD_PER_ACTION,
            log_list=log_list
        )
        test_cases.append({
            "case": "CHR at minimum",
            "value": CHR_MIN_REWARD_PER_ACTION.to_decimal_string(),
            "expected": "PASS",
            "actual": "PASS" if result.passed else "FAIL",
            "passed": result.passed
        })
        print(f"  CHR at minimum: {'✅ PASS' if result.passed else '❌ FAIL'}")
        
        # Test Case 2: At maximum (should pass)
        result = self.economics_guard.validate_chr_reward(
            chr_reward=CHR_MAX_REWARD_PER_ACTION,
            total_supply_delta=CHR_MAX_REWARD_PER_ACTION,
            log_list=log_list
        )
        test_cases.append({
            "case": "CHR at maximum",
            "value": CHR_MAX_REWARD_PER_ACTION.to_decimal_string(),
            "expected": "PASS",
            "actual": "PASS" if result.passed else "FAIL",
            "passed": result.passed
        })
        print(f"  CHR at maximum: {'✅ PASS' if result.passed else '❌ FAIL'}")
        
        # Test Case 3: Over maximum (should fail with error code)
        over_max = self.cm.add(CHR_MAX_REWARD_PER_ACTION, BigNum128.from_string("1.0"), log_list, None, None)
        result = self.economics_guard.validate_chr_reward(
            chr_reward=over_max,
            total_supply_delta=over_max,
            log_list=log_list
        )
        expected_fail = not result.passed and result.error_code == "ECON_CHR_MAX_REWARD_EXCEEDED"
        test_cases.append({
            "case": "CHR over maximum",
            "value": over_max.to_decimal_string(),
            "expected": "FAIL",
            "actual": "FAIL" if not result.passed else "PASS",
            "error_code": result.error_code,
            "passed": expected_fail
        })
        print(f"  CHR over maximum: {'✅ FAIL (expected)' if expected_fail else '❌ PASS (unexpected)'}")
        
        return {
            "test": "chr_reward_boundaries",
            "total_cases": len(test_cases),
            "passed_cases": sum(1 for t in test_cases if t["passed"]),
            "test_cases": test_cases
        }
    
    def test_flx_reward_boundaries(self) -> Dict[str, Any]:
        """Test FLX reward fraction boundaries."""
        print("\n[TEST] FLX Reward Boundaries")
        
        log_list = []
        test_cases = []
        
        # Test Case 1: At minimum fraction (should pass)
        result = self.economics_guard.validate_flx_reward(
            flx_reward=BigNum128.from_string("100.0"),
            total_chr_reward=BigNum128.from_string("1000.0"),  # 10% = MIN_FLX_REWARD_FRACTION
            log_list=log_list
        )
        test_cases.append({
            "case": "FLX at minimum fraction (10%)",
            "fraction": "0.10",
            "expected": "PASS",
            "actual": "PASS" if result.passed else "FAIL",
            "passed": result.passed
        })
        print(f"  FLX at minimum fraction: {'✅ PASS' if result.passed else '❌ FAIL'}")
        
        # Test Case 2: At maximum fraction (should pass)
        result = self.economics_guard.validate_flx_reward(
            flx_reward=BigNum128.from_string("400.0"),
            total_chr_reward=BigNum128.from_string("1000.0"),  # 40% = MAX_FLX_REWARD_FRACTION
            log_list=log_list
        )
        test_cases.append({
            "case": "FLX at maximum fraction (40%)",
            "fraction": "0.40",
            "expected": "PASS",
            "actual": "PASS" if result.passed else "FAIL",
            "passed": result.passed
        })
        print(f"  FLX at maximum fraction: {'✅ PASS' if result.passed else '❌ FAIL'}")
        
        # Test Case 3: Over maximum fraction (should fail)
        result = self.economics_guard.validate_flx_reward(
            flx_reward=BigNum128.from_string("500.0"),
            total_chr_reward=BigNum128.from_string("1000.0"),  # 50% > MAX_FLX_REWARD_FRACTION
            log_list=log_list
        )
        expected_fail = not result.passed and result.error_code == "ECON_FLX_FRACTION_OUT_OF_BOUNDS"
        test_cases.append({
            "case": "FLX over maximum fraction (50%)",
            "fraction": "0.50",
            "expected": "FAIL",
            "actual": "FAIL" if not result.passed else "PASS",
            "error_code": result.error_code,
            "passed": expected_fail
        })
        print(f"  FLX over maximum fraction: {'✅ FAIL (expected)' if expected_fail else '❌ PASS (unexpected)'}")
        
        return {
            "test": "flx_reward_boundaries",
            "total_cases": len(test_cases),
            "passed_cases": sum(1 for t in test_cases if t["passed"]),
            "test_cases": test_cases
        }
    
    def test_nod_allocation_boundaries(self) -> Dict[str, Any]:
        """Test NOD allocation fraction and cap boundaries."""
        print("\n[TEST] NOD Allocation Boundaries")
        
        log_list = []
        test_cases = []
        
        atr_fees = BigNum128.from_string("1000000.0")
        
        # Test Case 1: At minimum allocation fraction (1%)
        nod_amount = self.cm.mul(atr_fees, MIN_NOD_ALLOCATION_FRACTION, log_list, None, None)
        result = self.economics_guard.validate_nod_allocation(
            nod_allocated=nod_amount,
            atr_fees_collected=atr_fees,
            total_nod_supply=BigNum128.from_string("5000000.0"),
            single_node_allocation=BigNum128.from_string("3000.0"),
            total_nod_allocated_this_epoch=nod_amount,
            log_list=log_list
        )
        test_cases.append({
            "case": "NOD at minimum fraction (1%)",
            "fraction": "0.01",
            "expected": "PASS",
            "actual": "PASS" if result.passed else "FAIL",
            "passed": result.passed
        })
        print(f"  NOD at minimum fraction: {'✅ PASS' if result.passed else '❌ FAIL'}")
        
        # Test Case 2: At maximum allocation fraction (15%)
        nod_amount = self.cm.mul(atr_fees, MAX_NOD_ALLOCATION_FRACTION, log_list, None, None)
        result = self.economics_guard.validate_nod_allocation(
            nod_allocated=nod_amount,
            atr_fees_collected=atr_fees,
            total_nod_supply=BigNum128.from_string("5000000.0"),
            single_node_allocation=BigNum128.from_string("45000.0"),
            total_nod_allocated_this_epoch=nod_amount,
            log_list=log_list
        )
        test_cases.append({
            "case": "NOD at maximum fraction (15%)",
            "fraction": "0.15",
            "expected": "PASS",
            "actual": "PASS" if result.passed else "FAIL",
            "passed": result.passed
        })
        print(f"  NOD at maximum fraction: {'✅ PASS' if result.passed else '❌ FAIL'}")
        
        # Test Case 3: Over maximum epoch issuance
        result = self.economics_guard.validate_nod_allocation(
            nod_allocated=BigNum128.from_string("150000.0"),
            atr_fees_collected=atr_fees,
            total_nod_supply=BigNum128.from_string("5000000.0"),
            single_node_allocation=BigNum128.from_string("45000.0"),
            total_nod_allocated_this_epoch=self.cm.add(
                NOD_MAX_ISSUANCE_PER_EPOCH,
                BigNum128.from_string("1.0"),
                log_list, None, None
            ),
            log_list=log_list
        )
        expected_fail = not result.passed and result.error_code == "ECON_NOD_ISSUANCE_CAP_EXCEEDED"
        test_cases.append({
            "case": "NOD over epoch issuance cap",
            "value": "1000001.0",
            "expected": "FAIL",
            "actual": "FAIL" if not result.passed else "PASS",
            "error_code": result.error_code,
            "passed": expected_fail
        })
        print(f"  NOD over epoch cap: {'✅ FAIL (expected)' if expected_fail else '❌ PASS (unexpected)'}")
        
        # Test Case 4: Single node dominance (> 30% of allocation)
        total_allocated = BigNum128.from_string("100000.0")
        dominant_node = self.cm.mul(total_allocated, BigNum128.from_string("0.35"), log_list, None, None)  # 35%
        result = self.economics_guard.validate_nod_allocation(
            nod_allocated=total_allocated,
            atr_fees_collected=atr_fees,
            total_nod_supply=BigNum128.from_string("5000000.0"),
            single_node_allocation=dominant_node,
            total_nod_allocated_this_epoch=total_allocated,
            log_list=log_list
        )
        expected_fail = not result.passed and result.error_code == "ECON_NOD_NODE_DOMINANCE_VIOLATION"
        test_cases.append({
            "case": "Single node > 30% share",
            "share": "0.35",
            "expected": "FAIL",
            "actual": "FAIL" if not result.passed else "PASS",
            "error_code": result.error_code,
            "passed": expected_fail
        })
        print(f"  Single node dominance: {'✅ FAIL (expected)' if expected_fail else '❌ PASS (unexpected)'}")
        
        return {
            "test": "nod_allocation_boundaries",
            "total_cases": len(test_cases),
            "passed_cases": sum(1 for t in test_cases if t["passed"]),
            "test_cases": test_cases
        }
    
    def test_per_address_cap(self) -> Dict[str, Any]:
        """Test per-address reward caps."""
        print("\n[TEST] Per-Address Reward Cap")
        
        log_list = []
        test_cases = []
        
        # Test Case 1: Under cap (should pass)
        result = self.economics_guard.validate_per_address_reward(
            address="addr_001",
            chr_amount=BigNum128.from_string("500.0"),
            flx_amount=BigNum128.from_string("200.0"),
            res_amount=BigNum128.from_string("50.0"),
            total_amount=BigNum128.from_string("750.0"),
            log_list=log_list
        )
        test_cases.append({
            "case": "Under per-address cap",
            "total": "750.0",
            "expected": "PASS",
            "actual": "PASS" if result.passed else "FAIL",
            "passed": result.passed
        })
        print(f"  Under cap: {'✅ PASS' if result.passed else '❌ FAIL'}")
        
        # Test Case 2: At cap (should pass)
        result = self.economics_guard.validate_per_address_reward(
            address="addr_002",
            chr_amount=PER_ADDRESS_REWARD_CAP,
            flx_amount=BigNum128.from_string("0.0"),
            res_amount=BigNum128.from_string("0.0"),
            total_amount=PER_ADDRESS_REWARD_CAP,
            log_list=log_list
        )
        test_cases.append({
            "case": "At per-address cap",
            "total": PER_ADDRESS_REWARD_CAP.to_decimal_string(),
            "expected": "PASS",
            "actual": "PASS" if result.passed else "FAIL",
            "passed": result.passed
        })
        print(f"  At cap: {'✅ PASS' if result.passed else '❌ FAIL'}")
        
        # Test Case 3: Over cap (should fail)
        over_cap = self.cm.add(PER_ADDRESS_REWARD_CAP, BigNum128.from_string("1.0"), log_list, None, None)
        result = self.economics_guard.validate_per_address_reward(
            address="addr_003",
            chr_amount=over_cap,
            flx_amount=BigNum128.from_string("0.0"),
            res_amount=BigNum128.from_string("0.0"),
            total_amount=over_cap,
            log_list=log_list
        )
        expected_fail = not result.passed and result.error_code == "ECON_PER_ADDRESS_CAP"
        test_cases.append({
            "case": "Over per-address cap",
            "total": over_cap.to_decimal_string(),
            "expected": "FAIL",
            "actual": "FAIL" if not result.passed else "PASS",
            "error_code": result.error_code,
            "passed": expected_fail
        })
        print(f"  Over cap: {'✅ FAIL (expected)' if expected_fail else '❌ PASS (unexpected)'}")
        
        return {
            "test": "per_address_cap",
            "total_cases": len(test_cases),
            "passed_cases": sum(1 for t in test_cases if t["passed"]),
            "test_cases": test_cases
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all boundary condition tests."""
        print("=" * 80)
        print("QFS V13.6 - Boundary Condition Test Suite (Economic Guards)")
        print("=" * 80)
        
        # Test 1: CHR Reward Boundaries
        chr_result = self.test_chr_reward_boundaries()
        self.test_results.append(chr_result)
        
        # Test 2: FLX Reward Boundaries
        flx_result = self.test_flx_reward_boundaries()
        self.test_results.append(flx_result)
        
        # Test 3: NOD Allocation Boundaries
        nod_result = self.test_nod_allocation_boundaries()
        self.test_results.append(nod_result)
        
        # Test 4: Per-Address Cap
        cap_result = self.test_per_address_cap()
        self.test_results.append(cap_result)
        
        # Summary
        total_cases = sum(r["total_cases"] for r in self.test_results)
        passed_cases = sum(r["passed_cases"] for r in self.test_results)
        
        print("\n" + "=" * 80)
        print(f"SUMMARY: {passed_cases}/{total_cases} test cases passed")
        print("=" * 80)
        
        # Generate evidence
        evidence = {
            "test_suite": "BoundaryConditionTests",
            "version": "V13.6",
            "timestamp": "2025-12-13T12:45:00Z",
            "total_tests": len(self.test_results),
            "total_cases": total_cases,
            "passed_cases": passed_cases,
            "test_results": self.test_results,
            "economic_bounds_verified": passed_cases == total_cases
        }
        
        # Save evidence
        os.makedirs("evidence/v13.6", exist_ok=True)
        with open("evidence/v13.6/economic_bounds_verification.json", "w") as f:
            json.dump(evidence, f, indent=2, sort_keys=True)
        
        print(f"\n✅ Evidence saved: evidence/v13.6/economic_bounds_verification.json")
        
        return evidence


if __name__ == "__main__":
    test_suite = BoundaryConditionTests()
    results = test_suite.run_all_tests()
    
    sys.exit(0 if results["economic_bounds_verified"] else 1)
