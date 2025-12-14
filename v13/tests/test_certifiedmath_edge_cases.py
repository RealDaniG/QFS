"""
Test cases for CertifiedMath edge-case inputs.
These tests verify that transcendental functions work correctly with very small fractions and very large integers.
"""

import pytest
from v13.libs.CertifiedMath import CertifiedMath
from v13.libs.BigNum128 import BigNum128


def test_very_small_fractions():
    """Test transcendental functions with very small fractions"""
    # Very small positive value
    small_val = BigNum128.from_string("0.000000000000000001")  # 1e-18
    
    # Create CertifiedMath instance
    cm = CertifiedMath()
    
    # Test exp with very small value (should be close to 1)
    with CertifiedMath.LogContext() as log:
        result = cm.exp(small_val, iterations=50, log_list=log)
        # exp(1e-18) should be very close to 1
        assert result.value >= BigNum128.from_string("0.999999999999999999").value
        assert result.value <= BigNum128.from_string("1.000000000000000001").value
    
    # Test ln with very small value (should be negative, but we can't represent negative values)
    # Instead, test with a value slightly greater than 1
    slightly_greater_than_one = BigNum128.from_string("1.000000000000000001")
    with CertifiedMath.LogContext() as log:
        result = cm.ln(slightly_greater_than_one, iterations=50, log_list=log)
        # ln(1 + 1e-18) should be very close to 1e-18
        assert result.value > 0
        assert result.value < BigNum128.from_string("0.000000000000000002").value


def test_very_large_integers():
    """Test transcendental functions with very large integers"""
    # Large value that's still within BigNum128 bounds
    large_val = BigNum128.from_string("1000000000.0")  # 1 billion
    
    # Create CertifiedMath instance
    cm = CertifiedMath()
    
    # Test exp with large value (should overflow)
    with pytest.raises(OverflowError):
        with CertifiedMath.LogContext() as log:
            cm.exp(large_val, iterations=50, log_list=log)
    
    # Test ln with large value
    with CertifiedMath.LogContext() as log:
        result = cm.ln(large_val, iterations=50, log_list=log)
        # ln(1e9) should be approximately 20.723... (in scaled form)
        # This is roughly 20.723 * 10^18
        assert result.value > BigNum128.from_string("20.0").value
        assert result.value < BigNum128.from_string("21.0").value


def test_boundary_values():
    """Test transcendental functions with boundary values"""
    # Test with exactly 1.0
    one = BigNum128.one()
    
    # Create CertifiedMath instance
    cm = CertifiedMath()
    
    # exp(0) = 1
    zero = BigNum128.zero()
    with CertifiedMath.LogContext() as log:
        result = cm.exp(zero, iterations=50, log_list=log)
        assert result == one
    
    # ln(1) = 0
    with CertifiedMath.LogContext() as log:
        result = cm.ln(one, iterations=50, log_list=log)
        assert result == zero
    
    # Test trigonometric functions at boundary
    with CertifiedMath.LogContext() as log:
        sin_result = cm.sin(zero, iterations=10, log_list=log)
        assert sin_result == zero
    
    with CertifiedMath.LogContext() as log:
        cos_result = cm.cos(zero, iterations=10, log_list=log)
        assert cos_result == one


def test_special_functions_edge_cases():
    """Test special functions with edge cases"""
    # Create CertifiedMath instance
    cm = CertifiedMath()
    
    # Test tanh with zero
    zero = BigNum128.zero()
    with CertifiedMath.LogContext() as log:
        result = cm.tanh(zero, iterations=30, log_list=log)
        assert result == zero
    
    # Test sigmoid with zero
    with CertifiedMath.LogContext() as log:
        result = cm.sigmoid(zero, iterations=30, log_list=log)
        # sigmoid(0) = 0.5
        expected = BigNum128.from_string("0.5")
        assert result == expected
    
    # Test erf with zero
    with CertifiedMath.LogContext() as log:
        result = cm.erf(zero, iterations=20, log_list=log)
        assert result == zero


if __name__ == "__main__":
    pytest.main([__file__])