"""
Constitutional Guard Validation - Simple ASCII Output
Tests all economic guards with plain text output.
"""

import sys
from pathlib import Path

# Setup paths
root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root))

from v13.libs.CertifiedMath import CertifiedMath
from v13.libs.BigNum128 import BigNum128
from v13.libs.economics.EconomicsGuard import EconomicsGuard, EconomicViolationType


def test_chr_bounds():
    """Test CHR reward bounds"""
    print("\n[TEST 1/5] CHR Reward Bounds...")

    cm = CertifiedMath()
    guard = EconomicsGuard(cm)
    log_list = []

    # Valid CHR reward
    chr_valid = BigNum128.from_int(5000)
    daily = BigNum128.from_int(100000)
    supply = BigNum128.from_int(10000000)

    result = guard.validate_chr_reward(chr_valid, daily, supply, log_list)
    assert result.passed, f"Valid CHR rejected: {result.error_message}"
    print("  [PASS] Valid CHR reward accepted")

    # CHR above max
    chr_invalid = BigNum128.from_int(1000000)
    result = guard.validate_chr_reward(chr_invalid, daily, supply, log_list)
    assert not result.passed, "Invalid CHR accepted"
    assert result.error_code == EconomicViolationType.ECON_CHR_REWARD_ABOVE_MAX.value
    print("  [PASS] CHR above max correctly rejected")

    return True


def test_res_cap():
    """Test RES resonance cap (0.5% limit) - CRITICAL"""
    print("\n[TEST 2/5] RES Resonance Cap (0.5%) - CRITICAL...")

    cm = CertifiedMath()
    guard = EconomicsGuard(cm)
    log_list = []

    total_supply = BigNum128.from_int(10000000)

    # Valid: 0.4%
    res_valid = BigNum128.from_int(40000)
    result = guard.validate_res_reward(res_valid, total_supply, log_list)
    assert result.passed, f"Valid RES rejected: {result.error_message}"
    print("  [PASS] Valid RES reward (0.4%) accepted")

    # Invalid: 0.6%
    res_invalid = BigNum128.from_int(60000)
    result = guard.validate_res_reward(res_invalid, total_supply, log_list)
    assert not result.passed, "RES exceeding 0.5% accepted"
    assert result.error_code == EconomicViolationType.ECON_RES_REWARD_EXCEEDED.value
    print("  [PASS] RES exceeding 0.5% cap correctly rejected")

    return True


def test_nod_voting_power():
    """Test NOD voting power (25% max) - CRITICAL"""
    print("\n[TEST 3/5] NOD Voting Power (25% max) - CRITICAL...")

    cm = CertifiedMath()
    guard = EconomicsGuard(cm)
    log_list = []

    total_nod = BigNum128.from_int(1000000)

    # Valid: 20%
    nod_valid = BigNum128.from_int(200000)
    result = guard.validate_nod_allocation(nod_valid, total_nod, 10, log_list)
    assert result.passed, f"Valid NOD rejected: {result.error_message}"
    print("  [PASS] Valid NOD allocation (20%) accepted")

    # Invalid: 30%
    nod_invalid = BigNum128.from_int(300000)
    result = guard.validate_nod_allocation(nod_invalid, total_nod, 10, log_list)
    assert not result.passed, "NOD exceeding 25% accepted"
    print("  [PASS] NOD exceeding 25% correctly rejected")

    return True


def test_flx_bounds():
    """Test FLX reward fraction bounds"""
    print("\n[TEST 4/5] FLX Reward Fraction Bounds...")

    cm = CertifiedMath()
    guard = EconomicsGuard(cm)
    log_list = []

    # Valid FLX
    flx_valid = BigNum128.from_int(100)
    chr_total = BigNum128.from_int(1000)
    result = guard.validate_flx_reward(flx_valid, chr_total, log_list)
    assert result.passed, f"Valid FLX rejected: {result.error_message}"
    print("  [PASS] Valid FLX reward accepted")

    # FLX above max
    flx_invalid = BigNum128.from_int(600)
    result = guard.validate_flx_reward(flx_invalid, chr_total, log_list)
    assert not result.passed, "FLX above max accepted"
    print("  [PASS] FLX above max correctly rejected")

    return True


def test_psi_bounds():
    """Test PSI delta bounds"""
    print("\n[TEST 5/5] PSI Delta Bounds...")

    cm = CertifiedMath()
    guard = EconomicsGuard(cm)
    log_list = []

    # Valid PSI
    psi_valid = BigNum128.from_int(100)
    current_psi = BigNum128.from_int(1000)
    result = guard.validate_psi_accumulation(psi_valid, current_psi, log_list)
    assert result.passed, f"Valid PSI rejected: {result.error_message}"
    print("  [PASS] Valid PSI delta accepted")

    # PSI above max
    psi_invalid = BigNum128.from_int(100000)
    result = guard.validate_psi_accumulation(psi_invalid, current_psi, log_list)
    assert not result.passed, "PSI above max accepted"
    print("  [PASS] PSI above max correctly rejected")

    return True


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("CONSTITUTIONAL GUARD VALIDATION")
    print("=" * 80)

    tests = [
        test_chr_bounds,
        test_res_cap,
        test_nod_voting_power,
        test_flx_bounds,
        test_psi_bounds,
    ]

    passed = 0
    failed = 0
    errors = []

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            failed += 1
            errors.append(f"{test_func.__name__}: {e}")
            print(f"\n  [FAIL] {e}")
        except Exception as e:
            failed += 1
            errors.append(f"{test_func.__name__}: {e}")
            print(f"\n  [ERROR] {e}")

    print("\n" + "=" * 80)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    if errors:
        print("\nFAILURES:")
        for error in errors:
            print(f"  - {error}")
    print("=" * 80)

    if failed > 0:
        print(f"\n[FAIL] VALIDATION FAILED ({failed} tests failed)")
        sys.exit(1)

    print("\n[PASS] ALL CONSTITUTIONAL GUARDS OPERATIONAL")
    sys.exit(0)
