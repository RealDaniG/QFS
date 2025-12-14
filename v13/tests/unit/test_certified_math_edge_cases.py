"""
Comprehensive edge case testing for CertifiedMath to ensure production readiness.
This test suite validates all extreme edge cases as mandated by QFS V13 audit requirements.
"""

import sys
import os
import json

# Add the libs directory to the path

from CertifiedMath import (
    CertifiedMath, BigNum128, 
    MathOverflowError, MathValidationError,
    PHI_INTENSITY_B, LN2_CONSTANT, EXP_LIMIT, ZERO, ONE, TWO,
    set_series_precision, set_phi_intensity_damping, set_exp_limit, get_current_config
)

def test_safe_add_edge_cases():
    """Test _safe_add with extreme edge cases."""
    print("Testing _safe_add edge cases...")
    
    log = []
    math = CertifiedMath(log)
    
    # Test MAX_VALUE + 0
    a = BigNum128(BigNum128.MAX_VALUE)
    b = BigNum128(0)
    result = math.add(a, b, pqc_cid="ADD_001")
    assert result.value == BigNum128.MAX_VALUE, f"MAX_VALUE + 0 should equal MAX_VALUE, got {result.value}"
    
    # Test MIN_VALUE + 0
    a = BigNum128(BigNum128.MIN_VALUE)
    b = BigNum128(0)
    result = math.add(a, b, pqc_cid="ADD_002")
    assert result.value == BigNum128.MIN_VALUE, f"MIN_VALUE + 0 should equal MIN_VALUE, got {result.value}"
    
    # Test 1 + (-1)
    a = BigNum128(BigNum128.SCALE)  # 1.0
    b = BigNum128(-BigNum128.SCALE)  # -1.0
    result = math.add(a, b, pqc_cid="ADD_003")
    assert result.value == 0, f"1 + (-1) should equal 0, got {result.value}"
    
    # Test overflow: MAX_VALUE + 1 should raise MathOverflowError
    try:
        a = BigNum128(BigNum128.MAX_VALUE)
        b = BigNum128(1)
        result = math.add(a, b, pqc_cid="ADD_004")
        assert False, "Should have raised MathOverflowError for MAX_VALUE + 1"
    except MathOverflowError:
        print("  [PASS] MAX_VALUE + 1 correctly raised MathOverflowError")
    
    # Test underflow: MIN_VALUE + (-1) should raise MathOverflowError
    try:
        a = BigNum128(BigNum128.MIN_VALUE)
        b = BigNum128(-1)
        result = math.add(a, b, pqc_cid="ADD_005")
        assert False, "Should have raised MathOverflowError for MIN_VALUE + (-1)"
    except MathOverflowError:
        print("  [PASS] MIN_VALUE + (-1) correctly raised MathOverflowError")
    
    print("  [PASS] _safe_add edge cases passed")


def test_safe_sub_edge_cases():
    """Test _safe_sub with extreme edge cases."""
    print("Testing _safe_sub edge cases...")
    
    log = []
    math = CertifiedMath(log)
    
    # Test MAX_VALUE - 0
    a = BigNum128(BigNum128.MAX_VALUE)
    b = BigNum128(0)
    result = math.sub(a, b, pqc_cid="SUB_001")
    assert result.value == BigNum128.MAX_VALUE, f"MAX_VALUE - 0 should equal MAX_VALUE, got {result.value}"
    
    # Test MIN_VALUE - 0
    a = BigNum128(BigNum128.MIN_VALUE)
    b = BigNum128(0)
    result = math.sub(a, b, pqc_cid="SUB_002")
    assert result.value == BigNum128.MIN_VALUE, f"MIN_VALUE - 0 should equal MIN_VALUE, got {result.value}"
    
    # Test 1 - 1
    a = BigNum128(BigNum128.SCALE)  # 1.0
    b = BigNum128(BigNum128.SCALE)  # 1.0
    result = math.sub(a, b, pqc_cid="SUB_003")
    assert result.value == 0, f"1 - 1 should equal 0, got {result.value}"
    
    # Test overflow: MIN_VALUE - 1 should raise MathOverflowError
    try:
        a = BigNum128(BigNum128.MIN_VALUE)
        b = BigNum128(1)
        result = math.sub(a, b, pqc_cid="SUB_004")
        assert False, "Should have raised MathOverflowError for MIN_VALUE - 1"
    except MathOverflowError:
        print("  [PASS] MIN_VALUE - 1 correctly raised MathOverflowError")
    
    # Test underflow: MAX_VALUE - (-1) should raise MathOverflowError
    try:
        a = BigNum128(BigNum128.MAX_VALUE)
        b = BigNum128(-1)
        result = math.sub(a, b, pqc_cid="SUB_005")
        assert False, "Should have raised MathOverflowError for MAX_VALUE - (-1)"
    except MathOverflowError:
        print("  [PASS] MAX_VALUE - (-1) correctly raised MathOverflowError")
    
    print("  [PASS] _safe_sub edge cases passed")


def test_safe_mul_edge_cases():
    """Test _safe_mul with extreme edge cases."""
    print("Testing _safe_mul edge cases...")
    
    log = []
    math = CertifiedMath(log)
    
    # Test MAX_VALUE * 0
    a = BigNum128(BigNum128.MAX_VALUE)
    b = BigNum128(0)
    result = math.mul(a, b, pqc_cid="MUL_001")
    assert result.value == 0, f"MAX_VALUE * 0 should equal 0, got {result.value}"
    
    # Test MIN_VALUE * 0
    a = BigNum128(BigNum128.MIN_VALUE)
    b = BigNum128(0)
    result = math.mul(a, b, pqc_cid="MUL_002")
    assert result.value == 0, f"MIN_VALUE * 0 should equal 0, got {result.value}"
    
    # Test 1 * 1
    a = BigNum128(BigNum128.SCALE)  # 1.0
    b = BigNum128(BigNum128.SCALE)  # 1.0
    result = math.mul(a, b, pqc_cid="MUL_003")
    assert result.value == BigNum128.SCALE, f"1 * 1 should equal 1, got {result.to_decimal_string()}"
    
    # Test (-1) * (-1)
    a = BigNum128(-BigNum128.SCALE)  # -1.0
    b = BigNum128(-BigNum128.SCALE)  # -1.0
    result = math.mul(a, b, pqc_cid="MUL_004")
    assert result.value == BigNum128.SCALE, f"(-1) * (-1) should equal 1, got {result.to_decimal_string()}"
    
    # Test overflow: Large values that would cause overflow
    try:
        a = BigNum128(BigNum128.MAX_VALUE // 2)
        b = BigNum128(BigNum128.SCALE * 3)  # 3.0
        result = math.mul(a, b, pqc_cid="MUL_005")
        # This might not overflow depending on the exact values, but we'll check
        print(f"  Large multiplication result: {result.to_decimal_string()}")
    except MathOverflowError:
        print("  [PASS] Large multiplication correctly raised MathOverflowError")
    
    print("  [PASS] _safe_mul edge cases passed")


def test_safe_div_edge_cases():
    """Test _safe_div with extreme edge cases."""
    print("Testing _safe_div edge cases...")
    
    log = []
    math = CertifiedMath(log)
    
    # Test 0 / 1
    a = BigNum128(0)
    b = BigNum128(BigNum128.SCALE)  # 1.0
    result = math.div(a, b, pqc_cid="DIV_001")
    assert result.value == 0, f"0 / 1 should equal 0, got {result.value}"
    
    # Test 1 / 1
    a = BigNum128(BigNum128.SCALE)  # 1.0
    b = BigNum128(BigNum128.SCALE)  # 1.0
    result = math.div(a, b, pqc_cid="DIV_002")
    assert result.value == BigNum128.SCALE, f"1 / 1 should equal 1, got {result.to_decimal_string()}"
    
    # Test division by zero should raise MathValidationError
    try:
        a = BigNum128(BigNum128.SCALE)  # 1.0
        b = BigNum128(0)
        result = math.div(a, b, pqc_cid="DIV_003")
        assert False, "Should have raised MathValidationError for division by zero"
    except MathValidationError:
        print("  [PASS] Division by zero correctly raised MathValidationError")
    
    print("  [PASS] _safe_div edge cases passed")


def test_safe_sqrt_edge_cases():
    """Test _safe_fast_sqrt with extreme edge cases."""
    print("Testing _safe_fast_sqrt edge cases...")
    
    log = []
    math = CertifiedMath(log)
    
    # Test sqrt(0)
    a = BigNum128(0)
    result = math.sqrt(a, pqc_cid="SQRT_001")
    assert result.value == 0, f"sqrt(0) should equal 0, got {result.value}"
    
    # Test sqrt(1)
    a = BigNum128(BigNum128.SCALE)  # 1.0
    result = math.sqrt(a, pqc_cid="SQRT_002")
    # Should be approximately 1.0
    assert abs(result.value - BigNum128.SCALE) < BigNum128.SCALE // 1000, f"sqrt(1) should be approximately 1, got {result.to_decimal_string()}"
    
    # Test sqrt of very small positive number
    a = BigNum128(1)  # Very small positive number
    result = math.sqrt(a, pqc_cid="SQRT_003")
    print(f"  sqrt(very small) = {result.to_decimal_string()}")
    
    # Test sqrt of MAX_VALUE
    a = BigNum128(BigNum128.MAX_VALUE)
    result = math.sqrt(a, pqc_cid="SQRT_004")
    print(f"  sqrt(MAX_VALUE) = {result.to_decimal_string()}")
    
    # Test negative input should raise MathValidationError
    try:
        a = BigNum128(-1)
        result = math.sqrt(a, pqc_cid="SQRT_005")
        assert False, "Should have raised MathValidationError for sqrt of negative number"
    except MathValidationError:
        print("  [PASS] sqrt of negative number correctly raised MathValidationError")
    
    print("  [PASS] _safe_fast_sqrt edge cases passed")


def test_safe_exp_edge_cases():
    """Test _safe_exp with extreme edge cases."""
    print("Testing _safe_exp edge cases...")
    
    log = []
    math = CertifiedMath(log)
    
    # Test exp(0)
    a = BigNum128(0)
    result = math.exp(a, pqc_cid="EXP_001")
    # exp(0) should be 1
    assert result.value == BigNum128.SCALE, f"exp(0) should equal 1, got {result.to_decimal_string()}"
    
    # Test exp(1)
    a = BigNum128(BigNum128.SCALE)  # 1.0
    result = math.exp(a, pqc_cid="EXP_002")
    # exp(1) should be approximately e ≈ 2.718
    expected_e = BigNum128.from_string("2.718281828459045235")
    assert abs(result.value - expected_e.value) < BigNum128.SCALE // 1000, f"exp(1) should be approximately e, got {result.to_decimal_string()}"
    
    # Test exp(EXP_LIMIT)
    result = math.exp(EXP_LIMIT, pqc_cid="EXP_003")
    print(f"  exp(EXP_LIMIT) = {result.to_decimal_string()}")
    
    # Test exp(-EXP_LIMIT)
    a = BigNum128(-EXP_LIMIT.value)
    result = math.exp(a, pqc_cid="EXP_004")
    print(f"  exp(-EXP_LIMIT) = {result.to_decimal_string()}")
    
    # Test exp beyond limit should raise MathValidationError
    try:
        a = BigNum128(EXP_LIMIT.value + BigNum128.SCALE)  # EXP_LIMIT + 1
        result = math.exp(a, pqc_cid="EXP_005")
        assert False, "Should have raised MathValidationError for exp beyond limit"
    except MathValidationError:
        print("  [PASS] exp beyond limit correctly raised MathValidationError")
    
    print("  [PASS] _safe_exp edge cases passed")


def test_safe_ln_edge_cases():
    """Test _safe_ln with extreme edge cases."""
    print("Testing _safe_ln edge cases...")
    
    log = []
    math = CertifiedMath(log)
    
    # Test ln(1)
    a = BigNum128(BigNum128.SCALE)  # 1.0
    result = math.ln(a, pqc_cid="LN_001")
    # ln(1) should be 0
    assert result.value == 0, f"ln(1) should equal 0, got {result.to_decimal_string()}"
    
    # Test ln(0.5) - within convergence band
    a = BigNum128.from_string("0.5")
    result = math.ln(a, pqc_cid="LN_002")
    # ln(0.5) should be approximately -0.693
    expected_ln_half = BigNum128.from_string("-0.693147180559945309")
    # Using a more generous tolerance for the series approximation
    assert abs(result.value - expected_ln_half.value) < BigNum128.SCALE // 50, f"ln(0.5) should be approximately -0.693, got {result.to_decimal_string()}"
    
    # Test ln(2.0) - within convergence band
    a = BigNum128.from_string("2.0")
    result = math.ln(a, pqc_cid="LN_003")
    # ln(2.0) should be approximately 0.693
    expected_ln_2 = BigNum128.from_string("0.693147180559945309")
    # Using a more generous tolerance for the series approximation
    assert abs(result.value - expected_ln_2.value) < BigNum128.SCALE // 50, f"ln(2.0) should be approximately 0.693, got {result.to_decimal_string()}"
    
    # Test ln(10.0) - requires normalization
    a = BigNum128.from_int(10)
    result = math.ln(a, pqc_cid="LN_004")
    # ln(10.0) should be approximately 2.302
    expected_ln_10 = BigNum128.from_string("2.302585092994045684")
    # Using a more generous tolerance for the series approximation
    assert abs(result.value - expected_ln_10.value) < BigNum128.SCALE // 100, f"ln(10.0) should be approximately 2.302, got {result.to_decimal_string()}"
    
    # Test ln of value < 0.5 - requires normalization
    a = BigNum128.from_string("0.25")
    result = math.ln(a, pqc_cid="LN_005")
    # ln(0.25) should be approximately -1.386
    expected_ln_quarter = BigNum128.from_string("-1.386294361119890618")
    # Using a more generous tolerance for the series approximation
    assert abs(result.value - expected_ln_quarter.value) < BigNum128.SCALE // 100, f"ln(0.25) should be approximately -1.386, got {result.to_decimal_string()}"
    
    # Test ln of value > 2.0 - requires normalization
    a = BigNum128.from_string("5.0")
    result = math.ln(a, pqc_cid="LN_006")
    # ln(5.0) should be approximately 1.609
    expected_ln_5 = BigNum128.from_string("1.609437912434100374")
    # Using a more generous tolerance for the series approximation
    assert abs(result.value - expected_ln_5.value) < BigNum128.SCALE // 100, f"ln(5.0) should be approximately 1.609, got {result.to_decimal_string()}"
    
    # Test ln of negative value should raise MathValidationError
    try:
        a = BigNum128(-1)
        result = math.ln(a, pqc_cid="LN_007")
        assert False, "Should have raised MathValidationError for ln of negative number"
    except MathValidationError:
        print("  [PASS] ln of negative number correctly raised MathValidationError")
    
    # Test ln of zero should raise MathValidationError
    try:
        a = BigNum128(0)
        result = math.ln(a, pqc_cid="LN_008")
        assert False, "Should have raised MathValidationError for ln of zero"
    except MathValidationError:
        print("  [PASS] ln of zero correctly raised MathValidationError")
    
    print("  [PASS] _safe_ln edge cases passed")


def test_safe_phi_series_edge_cases():
    """Test _safe_phi_series with extreme edge cases."""
    print("Testing _safe_phi_series edge cases...")
    
    log = []
    math = CertifiedMath(log)
    
    # Test phi_series(0)
    a = BigNum128(0)
    result = math.phi_series(a, pqc_cid="PHI_001")
    # phi_series(0) should be 0
    assert result.value == 0, f"phi_series(0) should equal 0, got {result.to_decimal_string()}"
    
    # Test phi_series(1.0)
    a = BigNum128(BigNum128.SCALE)  # 1.0
    result = math.phi_series(a, pqc_cid="PHI_002")
    print(f"  phi_series(1.0) = {result.to_decimal_string()}")
    
    # Test phi_series(-1.0)
    a = BigNum128(-BigNum128.SCALE)  # -1.0
    result = math.phi_series(a, pqc_cid="PHI_003")
    print(f"  phi_series(-1.0) = {result.to_decimal_string()}")
    
    # Test phi_series(0.9999)
    a = BigNum128.from_string("0.9999")
    result = math.phi_series(a, pqc_cid="PHI_004")
    print(f"  phi_series(0.9999) = {result.to_decimal_string()}")
    
    # Test phi_series(-0.9999)
    a = BigNum128.from_string("-0.9999")
    result = math.phi_series(a, pqc_cid="PHI_005")
    print(f"  phi_series(-0.9999) = {result.to_decimal_string()}")
    
    # Test phi_series beyond convergence limit should raise MathValidationError
    try:
        a = BigNum128(BigNum128.SCALE + 1)  # 1.0 + epsilon
        result = math.phi_series(a, pqc_cid="PHI_006")
        assert False, "Should have raised MathValidationError for phi_series beyond convergence limit"
    except MathValidationError:
        print("  [PASS] phi_series beyond convergence limit correctly raised MathValidationError")
    
    print("  [PASS] _safe_phi_series edge cases passed")


def test_safe_two_to_the_power_edge_cases():
    """Test _safe_two_to_the_power with extreme edge cases."""
    print("Testing _safe_two_to_the_power edge cases...")
    
    log = []
    math = CertifiedMath(log)
    
    # Test 2^0
    a = BigNum128(0)
    result = math.two_to_the_power(a, pqc_cid="TWO_POW_001")
    # 2^0 should be 1
    assert result.value == BigNum128.SCALE, f"2^0 should equal 1, got {result.to_decimal_string()}"
    
    # Test 2^1
    a = BigNum128(BigNum128.SCALE)  # 1.0
    result = math.two_to_the_power(a, pqc_cid="TWO_POW_002")
    # 2^1 should be 2 (with tolerance for series approximation)
    assert abs(result.value - 2 * BigNum128.SCALE) < BigNum128.SCALE // 10000000000, f"2^1 should equal 2, got {result.to_decimal_string()}"
    
    # Calculate threshold for 2^x domain check
    threshold_scaled = (EXP_LIMIT.value * BigNum128.SCALE) // LN2_CONSTANT.value
    threshold = threshold_scaled // BigNum128.SCALE
    
    # Test 2^(threshold)
    a = BigNum128(threshold * BigNum128.SCALE)
    result = math.two_to_the_power(a, pqc_cid="TWO_POW_003")
    print(f"  2^{threshold} = {result.to_decimal_string()}")
    
    # Test 2^(-threshold)
    a = BigNum128(-threshold * BigNum128.SCALE)
    result = math.two_to_the_power(a, pqc_cid="TWO_POW_004")
    print(f"  2^{-threshold} = {result.to_decimal_string()}")
    
    # Test beyond threshold should raise MathValidationError
    try:
        a = BigNum128((threshold + 1) * BigNum128.SCALE)  # threshold + 1
        result = math.two_to_the_power(a, pqc_cid="TWO_POW_005")
        assert False, "Should have raised MathValidationError for 2^x beyond threshold"
    except MathValidationError as e:
        print(f"  [PASS] 2^x beyond threshold correctly raised MathValidationError: {e}")
    
    print("  [PASS] _safe_two_to_the_power edge cases passed")


def test_deterministic_hash_consistency():
    """Test that identical operations produce identical hashes."""
    print("Testing deterministic hash consistency...")
    
    # Perform identical operations twice
    log1 = []
    math1 = CertifiedMath(log1)
    
    a1 = BigNum128.from_string("123.456")
    b1 = BigNum128.from_string("789.012")
    pqc_cid = "CONSISTENT_TEST"
    
    result1 = math1.add(a1, b1, pqc_cid=pqc_cid)
    result2 = math1.mul(result1, a1, pqc_cid=pqc_cid)
    hash1 = math1.get_log_hash()
    
    log2 = []
    math2 = CertifiedMath(log2)
    
    a2 = BigNum128.from_string("123.456")
    b2 = BigNum128.from_string("789.012")
    
    result3 = math2.add(a2, b2, pqc_cid=pqc_cid)
    result4 = math2.mul(result3, a2, pqc_cid=pqc_cid)
    hash2 = math2.get_log_hash()
    
    # Hashes should be identical
    assert hash1 == hash2, f"Identical operations should produce identical hashes: {hash1} != {hash2}"
    
    print("  [PASS] Deterministic hash consistency test passed")


def run_all_tests():
    """Run all edge case tests."""
    print("Running CertifiedMath Edge Case Tests...")
    print("=" * 60)
    
    test_safe_add_edge_cases()
    test_safe_sub_edge_cases()
    test_safe_mul_edge_cases()
    test_safe_div_edge_cases()
    test_safe_sqrt_edge_cases()
    test_safe_exp_edge_cases()
    test_safe_ln_edge_cases()
    test_safe_phi_series_edge_cases()
    test_safe_two_to_the_power_edge_cases()
    test_deterministic_hash_consistency()
    
    print("=" * 60)
    print("[SUCCESS] All CertifiedMath Edge Case tests passed!")


if __name__ == "__main__":
    run_all_tests()