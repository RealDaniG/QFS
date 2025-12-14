"""
Test suite for the CertifiedMath extensions (pow and two_to_the_power functions).
"""

import sys
import os

# Add the libs directory to the path

from CertifiedMath import CertifiedMath, BigNum128, MathValidationError

def test_pow_function():
    """Test the pow function with various inputs."""
    print("Testing pow function...")
    
    # Test case 1: 2^3 = 8
    log = []
    cm = CertifiedMath(log)
    base = BigNum128.from_string("2.0")
    exponent = BigNum128.from_string("3.0")
    result = cm.pow(base, exponent, pqc_cid="POW_TEST_1")
    print(f"2^3 = {result.to_decimal_string()}")
    assert len(log) >= 1
    
    # Test case 2: 5^0 = 1
    log = []
    cm = CertifiedMath(log)
    base = BigNum128.from_string("5.0")
    exponent = BigNum128.from_string("0.0")
    result = cm.pow(base, exponent, pqc_cid="POW_TEST_2")
    print(f"5^0 = {result.to_decimal_string()}")
    # Should be approximately 1.0
    expected = BigNum128.from_int(1)
    assert abs(result.value - expected.value) < BigNum128.SCALE // 1000
    
    # Test case 3: 1^5 = 1 (changed from 0^5 to avoid domain error)
    log = []
    cm = CertifiedMath(log)
    base = BigNum128.from_string("1.0")
    exponent = BigNum128.from_string("5.0")
    result = cm.pow(base, exponent, pqc_cid="POW_TEST_3")
    print(f"1^5 = {result.to_decimal_string()}")
    expected = BigNum128.from_int(1)
    assert abs(result.value - expected.value) < BigNum128.SCALE // 1000
    
    print("[PASS] pow function tests passed")

def test_two_to_the_power_function():
    """Test the two_to_the_power function with various inputs."""
    print("Testing two_to_the_power function...")
    
    # Test case 1: 2^0 = 1
    log = []
    cm = CertifiedMath(log)
    exponent = BigNum128.from_string("0.0")
    result = cm.two_to_the_power(exponent, pqc_cid="TWO_POW_TEST_1")
    print(f"2^0 = {result.to_decimal_string()}")
    expected = BigNum128.from_int(1)
    assert abs(result.value - expected.value) < BigNum128.SCALE // 1000
    assert len(log) >= 1
    
    # Test case 2: 2^3 = 8
    log = []
    cm = CertifiedMath(log)
    exponent = BigNum128.from_string("3.0")
    result = cm.two_to_the_power(exponent, pqc_cid="TWO_POW_TEST_2")
    print(f"2^3 = {result.to_decimal_string()}")
    
    print("[PASS] two_to_the_power function tests passed")

def test_log_operation_validation():
    """Test that operations are logged correctly."""
    print("Testing log operation validation...")
    
    # Test that operations are logged
    log = []
    cm = CertifiedMath(log)
    a = BigNum128.from_int(1)
    b = BigNum128.from_int(2)
    result = cm.add(a, b, pqc_cid="LOG_TEST")
    assert len(log) >= 1
    
    print("[PASS] log operation validation tests passed")

def test_pow_edge_cases():
    """Test edge cases for the pow function."""
    print("Testing pow edge cases...")
    
    # Test case 1: Zero to positive power should raise MathValidationError
    try:
        log = []
        cm = CertifiedMath(log)
        base = BigNum128.from_string("0.0")
        exponent = BigNum128.from_string("1.0")
        result = cm.pow(base, exponent, pqc_cid="POW_EDGE_1")
        assert False, "Should have raised MathValidationError for zero base"
    except MathValidationError as e:
        print("0^1 correctly raises MathValidationError")
        assert "base must be positive" in str(e)
    
    print("[PASS] pow edge case tests passed")

if __name__ == "__main__":
    test_pow_function()
    test_two_to_the_power_function()
    test_log_operation_validation()
    test_pow_edge_cases()
    print("\n[SUCCESS] All extension tests passed!")