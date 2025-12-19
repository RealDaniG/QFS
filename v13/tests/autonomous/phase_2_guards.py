"""
Autonomous Phase 2: Constitutional Guard Validation
Location: v13/tests/autonomous/phase_2_guards.py

Validates all economic guards are operational and enforce constitutional bounds.
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Add root to path
root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root))

try:
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.libs.BigNum128 import BigNum128
    from v13.libs.economics.EconomicsGuard import EconomicsGuard, EconomicViolationType
except ImportError:
    # Fallback for direct execution
    import os

    os.chdir(root)
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.libs.BigNum128 import BigNum128
    from v13.libs.economics.EconomicsGuard import EconomicsGuard, EconomicViolationType


class GuardValidator:
    """Autonomous constitutional guard validation"""

    def __init__(self):
        self.cm = CertifiedMath()
        self.guard = EconomicsGuard(self.cm)
        self.test_results = []
        self.log_list = []

    def test_chr_bounds(self) -> bool:
        """Test CHR reward bounds"""
        print("\n[TEST] CHR Reward Bounds...")

        # Test 1: Valid CHR reward
        chr_valid = BigNum128.from_int(5000)
        daily = BigNum128.from_int(100000)
        supply = BigNum128.from_int(10000000)

        result = self.guard.validate_chr_reward(chr_valid, daily, supply, self.log_list)
        if not result.passed:
            print(f"  ✗ Valid CHR reward rejected: {result.error_message}")
            return False
        print("  ✓ Valid CHR reward accepted")

        # Test 2: CHR reward above max
        chr_invalid = BigNum128.from_int(1000000)  # Way above max
        result = self.guard.validate_chr_reward(
            chr_invalid, daily, supply, self.log_list
        )
        if result.passed:
            print("  ✗ Invalid CHR reward accepted (should reject)")
            return False
        if result.error_code != EconomicViolationType.ECON_CHR_REWARD_ABOVE_MAX.value:
            print(f"  ✗ Wrong error code: {result.error_code}")
            return False
        print("  ✓ CHR above max correctly rejected")

        return True

    def test_res_cap(self) -> bool:
        """Test RES resonance cap (0.5% limit)"""
        print("\n[TEST] RES Resonance Cap (0.5%)...")

        total_supply = BigNum128.from_int(10000000)  # 10M total

        # Test 1: Valid RES reward (0.4%)
        res_valid = BigNum128.from_int(40000)  # 0.4% of 10M
        result = self.guard.validate_res_reward(res_valid, total_supply, self.log_list)
        if not result.passed:
            print(f"  ✗ Valid RES reward rejected: {result.error_message}")
            return False
        print("  ✓ Valid RES reward (0.4%) accepted")

        # Test 2: RES reward exceeding 0.5% cap
        res_invalid = BigNum128.from_int(60000)  # 0.6% of 10M
        result = self.guard.validate_res_reward(
            res_invalid, total_supply, self.log_list
        )
        if result.passed:
            print("  ✗ RES reward exceeding 0.5% cap accepted (should reject)")
            return False
        if result.error_code != EconomicViolationType.ECON_RES_REWARD_EXCEEDED.value:
            print(f"  ✗ Wrong error code: {result.error_code}")
            return False
        print("  ✓ RES exceeding 0.5% cap correctly rejected")

        return True

    def test_nod_voting_power(self) -> bool:
        """Test NOD voting power bounds (25% max)"""
        print("\n[TEST] NOD Voting Power (25% max)...")

        total_nod = BigNum128.from_int(1000000)

        # Test 1: Valid NOD allocation (20%)
        nod_valid = BigNum128.from_int(200000)
        result = self.guard.validate_nod_allocation(
            nod_valid, total_nod, active_nodes=10, log_list=self.log_list
        )
        if not result.passed:
            print(f"  ✗ Valid NOD allocation rejected: {result.error_message}")
            return False
        print("  ✓ Valid NOD allocation (20%) accepted")

        # Test 2: NOD allocation exceeding 25%
        nod_invalid = BigNum128.from_int(300000)  # 30%
        result = self.guard.validate_nod_allocation(
            nod_invalid, total_nod, active_nodes=10, log_list=self.log_list
        )
        if result.passed:
            print("  ✗ NOD allocation exceeding 25% accepted (should reject)")
            return False
        print("  ✓ NOD exceeding 25% correctly rejected")

        return True

    def test_flx_bounds(self) -> bool:
        """Test FLX reward fraction bounds"""
        print("\n[TEST] FLX Reward Fraction Bounds...")

        # Test 1: Valid FLX fraction
        flx_valid = BigNum128.from_int(100)
        chr_total = BigNum128.from_int(1000)
        result = self.guard.validate_flx_reward(flx_valid, chr_total, self.log_list)
        if not result.passed:
            print(f"  ✗ Valid FLX reward rejected: {result.error_message}")
            return False
        print("  ✓ Valid FLX reward accepted")

        # Test 2: FLX fraction above max
        flx_invalid = BigNum128.from_int(600)  # 60% of CHR
        result = self.guard.validate_flx_reward(flx_invalid, chr_total, self.log_list)
        if result.passed:
            print("  ✗ FLX fraction above max accepted (should reject)")
            return False
        print("  ✓ FLX above max correctly rejected")

        return True

    def test_psi_bounds(self) -> bool:
        """Test PSI delta bounds"""
        print("\n[TEST] PSI Delta Bounds...")

        # Test 1: Valid PSI delta
        psi_valid = BigNum128.from_int(100)
        current_psi = BigNum128.from_int(1000)
        result = self.guard.validate_psi_accumulation(
            psi_valid, current_psi, self.log_list
        )
        if not result.passed:
            print(f"  ✗ Valid PSI delta rejected: {result.error_message}")
            return False
        print("  ✓ Valid PSI delta accepted")

        # Test 2: PSI delta above max
        psi_invalid = BigNum128.from_int(100000)  # Way above max
        result = self.guard.validate_psi_accumulation(
            psi_invalid, current_psi, self.log_list
        )
        if result.passed:
            print("  ✗ PSI delta above max accepted (should reject)")
            return False
        print("  ✓ PSI above max correctly rejected")

        return True

    def execute(self) -> bool:
        """Execute Phase 2 guard validation"""
        print("\n" + "=" * 80)
        print("PHASE 2: CONSTITUTIONAL GUARD VALIDATION")
        print("=" * 80)

        tests = [
            ("CHR Bounds", self.test_chr_bounds),
            ("RES Cap (0.5%)", self.test_res_cap),
            ("NOD Voting Power (25%)", self.test_nod_voting_power),
            ("FLX Bounds", self.test_flx_bounds),
            ("PSI Bounds", self.test_psi_bounds),
        ]

        passed = 0
        failed = 0

        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
                    print(f"\n[FAILED] {test_name}")
            except Exception as e:
                failed += 1
                print(f"\n[ERROR] {test_name}: {e}")

        print("\n" + "=" * 80)
        print(f"RESULTS: {passed}/{len(tests)} tests passed")
        print("=" * 80)

        if failed > 0:
            print(f"\n[PHASE 2] FAILED ✗ ({failed} tests failed)")
            return False

        print("\n[PHASE 2] COMPLETE ✓")
        return True


if __name__ == "__main__":
    validator = GuardValidator()
    success = validator.execute()
    sys.exit(0 if success else 1)
