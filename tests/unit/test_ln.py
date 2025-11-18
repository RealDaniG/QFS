"""
Test cases for the _safe_ln function in CertifiedMath
"""
import math
import sys
import os

# Add the src directory to the path so we can import CertifiedMath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from libs.CertifiedMath import CertifiedMath, BigNum128

def test_ln_basic_values():
    """Test ln function with basic values"""
    with CertifiedMath.LogContext() as log:
        # Test ln(1) = 0
        one = BigNum128.from_int(1)
        result = CertifiedMath.safe_ln(one, log)
        expected = BigNum128(0)
        assert result.value == expected.value, f"ln(1) should be 0, got {result.to_decimal_string()}"
        
        # Test ln(e) = 1
        e_val = BigNum128(2718281828459045235)  # e * 1e18
        result = CertifiedMath.safe_ln(e_val, log)
        expected = BigNum128.from_int(1)
        # Allow some tolerance for floating point errors
        assert abs(result.value - expected.value) < 1000000000000, f"ln(e) should be 1, got {result.to_decimal_string()}"

def test_ln_known_constants():
    """Test ln function with known mathematical constants"""
    with CertifiedMath.LogContext() as log:
        # Test ln(2)
        two = BigNum128.from_int(2)
        result = CertifiedMath.safe_ln(two, log)
        # ln(2) ≈ 0.693147180559945309
        expected = BigNum128(693147180559945309)
        assert abs(result.value - expected.value) < 1000000000000, f"ln(2) should be ~0.693, got {result.to_decimal_string()}"
        
        # Test ln(10)
        ten = BigNum128.from_int(10)
        result = CertifiedMath.safe_ln(ten, log)
        # ln(10) ≈ 2.302585092994045684
        expected = BigNum128(2302585092994045684)
        assert abs(result.value - expected.value) < 1000000000000, f"ln(10) should be ~2.303, got {result.to_decimal_string()}"

def test_ln_edge_cases():
    """Test ln function with edge cases"""
    with CertifiedMath.LogContext() as log:
        # Test x = 1
        one = BigNum128.from_int(1)
        result = CertifiedMath.safe_ln(one, log)
        expected = BigNum128(0)
        assert result.value == expected.value, f"ln(1) should be 0, got {result.to_decimal_string()}"
        
        # Test x approaching 0+
        small_val = BigNum128(1)  # 1e-18
        try:
            result = CertifiedMath.safe_ln(small_val, log)
            # Should be a large negative number
            assert result.value < 0, f"ln(small) should be negative, got {result.to_decimal_string()}"
        except ValueError:
            # Expected for very small values
            pass
        
        # Test x = 2
        two = BigNum128.from_int(2)
        result = CertifiedMath.safe_ln(two, log)
        expected = BigNum128(693147180559945309)
        assert abs(result.value - expected.value) < 1000000000000, f"ln(2) should be ~0.693, got {result.to_decimal_string()}"

def test_ln_randomized_deterministic():
    """Test that ln produces deterministic results"""
    # Run the same calculation twice and ensure results are identical
    with CertifiedMath.LogContext() as log1:
        val = BigNum128.from_int(5)
        result1 = CertifiedMath.safe_ln(val, log1)
        hash1 = CertifiedMath.get_log_hash(log1)
    
    with CertifiedMath.LogContext() as log2:
        val = BigNum128.from_int(5)
        result2 = CertifiedMath.safe_ln(val, log2)
        hash2 = CertifiedMath.get_log_hash(log2)
    
    assert result1.value == result2.value, "ln should produce deterministic results"
    assert hash1 == hash2, "Log hashes should be identical for deterministic operations"

if __name__ == "__main__":
    test_ln_basic_values()
    test_ln_known_constants()
    test_ln_edge_cases()
    test_ln_randomized_deterministic()
    print("All ln tests passed!")