"""
Autonomous Guard Debugging - Identify exact failure points
"""

import sys
from pathlib import Path

root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root))

from v13.libs.CertifiedMath import CertifiedMath
from v13.libs.BigNum128 import BigNum128
from v13.libs.economics.EconomicsGuard import EconomicsGuard, EconomicViolationType
from v13.libs.economics.economic_constants import (
    CHR_MAX_REWARD_PER_ACTION,
    CHR_MIN_REWARD_PER_ACTION,
    RES_MAX_DRAW_PER_EPOCH,
    MAX_NOD_VOTING_POWER_RATIO,
    MAX_FLX_REWARD_FRACTION,
    MIN_FLX_REWARD_FRACTION,
    PSI_MAX_DELTA_PER_EPOCH,
)


class GuardDebugger:
    """Autonomous guard debugging with detailed output"""

    def __init__(self):
        self.cm = CertifiedMath()
        self.guard = EconomicsGuard(self.cm)
        self.log_list = []

    def inspect_constants(self):
        """Inspect all economic constants"""
        print("\n[CONSTANTS INSPECTION]")
        print("=" * 80)

        constants = {
            "CHR_MAX_REWARD_PER_ACTION": CHR_MAX_REWARD_PER_ACTION,
            "CHR_MIN_REWARD_PER_ACTION": CHR_MIN_REWARD_PER_ACTION,
            "RES_MAX_DRAW_PER_EPOCH": RES_MAX_DRAW_PER_EPOCH,
            "MAX_NOD_VOTING_POWER_RATIO": MAX_NOD_VOTING_POWER_RATIO,
            "MAX_FLX_REWARD_FRACTION": MAX_FLX_REWARD_FRACTION,
            "MIN_FLX_REWARD_FRACTION": MIN_FLX_REWARD_FRACTION,
            "PSI_MAX_DELTA_PER_EPOCH": PSI_MAX_DELTA_PER_EPOCH,
        }

        for name, value in constants.items():
            if hasattr(value, "value"):
                print(f"{name}: {value.value} (BigNum128)")
                print(f"  -> Decimal: {value.to_decimal_string()}")
            else:
                print(f"{name}: {value}")

        print("=" * 80)

    def debug_chr_bounds(self):
        """Debug CHR reward bounds test"""
        print("\n[DEBUG] CHR Reward Bounds Test")
        print("-" * 80)

        # Test values
        chr_valid = BigNum128.from_int(5000)
        chr_invalid = BigNum128.from_int(1000000)
        daily = BigNum128.from_int(100000)
        supply = BigNum128.from_int(10000000)

        print(f"CHR_MAX_REWARD_PER_ACTION: {CHR_MAX_REWARD_PER_ACTION.value}")
        print(f"chr_valid: {chr_valid.value}")
        print(f"chr_invalid: {chr_invalid.value}")

        # Test valid
        print("\nTest 1: Valid CHR (5000)")
        result = self.guard.validate_chr_reward(chr_valid, daily, supply, self.log_list)
        print(f"  Result: {'PASS' if result.passed else 'FAIL'}")
        if not result.passed:
            print(f"  Error Code: {result.error_code}")
            print(f"  Error Message: {result.error_message}")
            print(f"  Details: {result.details}")

        # Test invalid
        print("\nTest 2: Invalid CHR (1000000)")
        result = self.guard.validate_chr_reward(
            chr_invalid, daily, supply, self.log_list
        )
        print(
            f"  Result: {'FAIL (Expected)' if not result.passed else 'PASS (UNEXPECTED!)'}"
        )
        if not result.passed:
            print(f"  Error Code: {result.error_code}")
            print(
                f"  Expected: {EconomicViolationType.ECON_CHR_REWARD_ABOVE_MAX.value}"
            )
            print(
                f"  Match: {result.error_code == EconomicViolationType.ECON_CHR_REWARD_ABOVE_MAX.value}"
            )

        print("-" * 80)

    def debug_res_cap(self):
        """Debug RES cap test (0.5% limit)"""
        print("\n[DEBUG] RES Resonance Cap Test (0.5%)")
        print("-" * 80)

        total_supply = BigNum128.from_int(10000000)

        # Calculate 0.5% of supply
        max_draw_ratio = RES_MAX_DRAW_PER_EPOCH.value
        max_allowed = (total_supply.value * max_draw_ratio) // BigNum128.SCALE

        print(f"Total Supply: {total_supply.value}")
        print(f"RES_MAX_DRAW_PER_EPOCH: {RES_MAX_DRAW_PER_EPOCH.value}")
        print(
            f"RES_MAX_DRAW_PER_EPOCH (decimal): {RES_MAX_DRAW_PER_EPOCH.to_decimal_string()}"
        )
        print(f"Calculated Max Allowed: {max_allowed}")
        print(f"Calculated Max Allowed (0.5%): {total_supply.value // 200}")

        # Test valid (0.4%)
        res_valid = BigNum128.from_int(40000)
        print(f"\nTest 1: Valid RES (40000 = 0.4%)")
        print(
            f"  Is {res_valid.value} <= {max_allowed}? {res_valid.value <= max_allowed}"
        )

        result = self.guard.validate_res_reward(res_valid, total_supply, self.log_list)
        print(f"  Result: {'PASS' if result.passed else 'FAIL'}")
        if not result.passed:
            print(f"  Error: {result.error_message}")
            print(f"  Details: {result.details}")

        # Test invalid (0.6%)
        res_invalid = BigNum128.from_int(60000)
        print(f"\nTest 2: Invalid RES (60000 = 0.6%)")
        print(
            f"  Is {res_invalid.value} > {max_allowed}? {res_invalid.value > max_allowed}"
        )

        result = self.guard.validate_res_reward(
            res_invalid, total_supply, self.log_list
        )
        print(
            f"  Result: {'FAIL (Expected)' if not result.passed else 'PASS (UNEXPECTED!)'}"
        )
        if not result.passed:
            print(f"  Error Code: {result.error_code}")
            print(f"  Expected: {EconomicViolationType.ECON_RES_REWARD_EXCEEDED.value}")

        print("-" * 80)

    def debug_nod_voting_power(self):
        """Debug NOD voting power test (25% max)"""
        print("\n[DEBUG] NOD Voting Power Test (25% max)")
        print("-" * 80)

        # Check method signature
        import inspect

        sig = inspect.signature(self.guard.validate_nod_allocation)
        print(f"validate_nod_allocation signature: {sig}")

        total_nod = BigNum128.from_int(1000000)

        # Valid: 20%
        nod_valid = BigNum128.from_int(200000)
        print(f"\nTest 1: Valid NOD (20%)")

        try:
            result = self.guard.validate_nod_allocation(
                nod_valid, total_nod, 10, self.log_list
            )
            print(f"  Result: {'PASS' if result.passed else 'FAIL'}")
            if not result.passed:
                print(f"  Error: {result.error_message}")
        except TypeError as e:
            print(f"  [ERROR] Parameter mismatch: {e}")

        print("-" * 80)

    def debug_flx_bounds(self):
        """Debug FLX bounds test"""
        print("\n[DEBUG] FLX Reward Fraction Bounds Test")
        print("-" * 80)

        chr_total = BigNum128.from_int(1000)
        user_balance = BigNum128.from_int(10000)

        print(f"MAX_FLX_REWARD_FRACTION: {MAX_FLX_REWARD_FRACTION.to_decimal_string()}")
        print(f"MIN_FLX_REWARD_FRACTION: {MIN_FLX_REWARD_FRACTION.to_decimal_string()}")

        # Check method signature
        import inspect

        sig = inspect.signature(self.guard.validate_flx_reward)
        print(f"validate_flx_reward signature: {sig}")

        # Valid FLX (10% of CHR)
        flx_valid = BigNum128.from_int(100)
        print(f"\nTest 1: Valid FLX (100 vs CHR 1000 = 10%)")

        try:
            result = self.guard.validate_flx_reward(
                flx_valid, chr_total, user_balance, self.log_list
            )
            print(f"  Result: {'PASS' if result.passed else 'FAIL'}")
            if not result.passed:
                print(f"  Error: {result.error_message}")
        except TypeError as e:
            print(f"  [ERROR] Parameter mismatch: {e}")

        print("-" * 80)

    def debug_psi_bounds(self):
        """Debug PSI bounds test"""
        print("\n[DEBUG] PSI Delta Bounds Test")
        print("-" * 80)

        current_psi = BigNum128.from_int(1000)

        print(f"PSI_MAX_DELTA_PER_EPOCH: {PSI_MAX_DELTA_PER_EPOCH.to_decimal_string()}")

        # Check method signature
        import inspect

        sig = inspect.signature(self.guard.validate_psi_accumulation)
        print(f"validate_psi_accumulation signature: {sig}")

        # Valid PSI
        psi_valid = BigNum128.from_int(100)
        print(f"\nTest 1: Valid PSI delta (100)")

        try:
            result = self.guard.validate_psi_accumulation(
                psi_valid, current_psi, self.log_list
            )
            print(f"  Result: {'PASS' if result.passed else 'FAIL'}")
            if not result.passed:
                print(f"  Error: {result.error_message}")
        except TypeError as e:
            print(f"  [ERROR] Parameter mismatch: {e}")

        print("-" * 80)

    def execute_full_debug(self):
        """Run all debug tests"""
        print("\n" + "=" * 80)
        print("AUTONOMOUS GUARD DEBUGGING SESSION")
        print("=" * 80)

        self.inspect_constants()
        self.debug_chr_bounds()
        self.debug_res_cap()
        self.debug_nod_voting_power()
        self.debug_flx_bounds()
        self.debug_psi_bounds()

        print("\n" + "=" * 80)
        print("DEBUG SESSION COMPLETE")
        print("=" * 80)


if __name__ == "__main__":
    debugger = GuardDebugger()
    debugger.execute_full_debug()
