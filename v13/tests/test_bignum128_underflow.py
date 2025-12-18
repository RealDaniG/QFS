"""
Test cases for BigNum128 fractional underflow handling.
These tests verify that inputs with significant digits beyond the 18th decimal place
correctly trigger BigNum128Error as required for QFS V13 Zero-Simulation compliance.
"""
import pytest
from v13.libs.BigNum128 import BigNum128, BigNum128Error

def test_fractional_underflow_exact_case():
    """Test the exact case from the verification checklist: 0.0000000000000000011"""
    with pytest.raises(BigNum128Error, match='Input value too small for BigNum128 \\(underflow\\)'):
        BigNum128.from_string('0.0000000000000000011')

def test_fractional_underflow_long_fraction():
    """Test various cases with significant digits beyond 18 decimal places"""
    with pytest.raises(BigNum128Error):
        BigNum128.from_string('123.1234567890123456789')
    with pytest.raises(BigNum128Error):
        BigNum128.from_string('0.00000000000000000001')
    with pytest.raises(BigNum128Error):
        BigNum128.from_string('1.000000000000000000000001')

def test_no_underflow_at_boundary():
    """Test that values exactly at the boundary do not trigger underflow"""
    b = BigNum128.from_string('0.000000000000000001')
    assert b.value == 1
    b = BigNum128.from_string('123.123456789012345678')
    assert b.value == 123123456789012345678

def test_valid_rounding_within_scale():
    """Test deterministic rounding behavior for values within scale"""
    b1 = BigNum128.from_string('1.5')
    assert b1.value == 1500000000000000000
    b2 = BigNum128.from_string('0.123456789012345678')
    assert b2.value == 123456789012345678
if __name__ == '__main__':
    pytest.main([__file__])
