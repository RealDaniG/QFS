"""
Test cases for CertifiedMath edge-case inputs.
These tests verify that transcendental functions work correctly with very small fractions and very large integers.
"""
import pytest
from v13.libs.CertifiedMath import CertifiedMath
from v13.libs.BigNum128 import BigNum128

def test_very_small_fractions():
    """Test transcendental functions with very small fractions"""
    small_val = BigNum128.from_string('0.000000000000000001')
    cm = CertifiedMath()
    with CertifiedMath.LogContext() as log:
        result = cm.exp(small_val, iterations=50, log_list=log)
        assert result.value >= BigNum128.from_string('0.999999999999999999').value
        assert result.value <= BigNum128.from_string('1.000000000000000001').value
    slightly_greater_than_one = BigNum128.from_string('1.000000000000000001')
    with CertifiedMath.LogContext() as log:
        result = cm.ln(slightly_greater_than_one, iterations=50, log_list=log)
        assert result.value > 0
        assert result.value < BigNum128.from_string('0.000000000000000002').value

def test_very_large_integers():
    """Test transcendental functions with very large integers"""
    large_val = BigNum128.from_string('1000000000.0')
    cm = CertifiedMath()
    with pytest.raises(OverflowError):
        with CertifiedMath.LogContext() as log:
            cm.exp(large_val, iterations=50, log_list=log)
    with CertifiedMath.LogContext() as log:
        result = cm.ln(large_val, iterations=50, log_list=log)
        assert result.value > BigNum128.from_string('20.0').value
        assert result.value < BigNum128.from_string('21.0').value

def test_boundary_values():
    """Test transcendental functions with boundary values"""
    one = BigNum128.one()
    cm = CertifiedMath()
    zero = BigNum128.zero()
    with CertifiedMath.LogContext() as log:
        result = cm.exp(zero, iterations=50, log_list=log)
        assert result == one
    with CertifiedMath.LogContext() as log:
        result = cm.ln(one, iterations=50, log_list=log)
        assert result == zero
    with CertifiedMath.LogContext() as log:
        sin_result = cm.sin(zero, iterations=10, log_list=log)
        assert sin_result == zero
    with CertifiedMath.LogContext() as log:
        cos_result = cm.cos(zero, iterations=10, log_list=log)
        assert cos_result == one

def test_special_functions_edge_cases():
    """Test special functions with edge cases"""
    cm = CertifiedMath()
    zero = BigNum128.zero()
    with CertifiedMath.LogContext() as log:
        result = cm.tanh(zero, iterations=30, log_list=log)
        assert result == zero
    with CertifiedMath.LogContext() as log:
        result = cm.sigmoid(zero, iterations=30, log_list=log)
        expected = BigNum128.from_string('0.5')
        assert result == expected
    with CertifiedMath.LogContext() as log:
        result = cm.erf(zero, iterations=20, log_list=log)
        assert result == zero
if __name__ == '__main__':
    pytest.main([__file__])
