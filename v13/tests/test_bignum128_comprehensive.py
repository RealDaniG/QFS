"""
Comprehensive test suite for BigNum128 covering all edge cases for QFS V13 Phase 1 compliance.
"""
import pytest
from v13.libs.BigNum128 import BigNum128, BigNum128Error

def test_integer_only_parsing():
    """Test parsing of integer-only strings"""
    b = BigNum128.from_string('0')
    assert b.value == 0
    b = BigNum128.from_string('123')
    assert b.value == 123 * BigNum128.SCALE

def test_fractional_parsing_exact_scale():
    """Test parsing of fractional strings with exactly SCALE_DIGITS digits"""
    b = BigNum128.from_string('0.000000000000000001')
    assert b.value == 1
    b = BigNum128.from_string('0.999999999999999999')
    assert b.value == 999999999999999999
    b = BigNum128.from_string('1.123456789012345678')
    expected = 1 * BigNum128.SCALE + 123456789012345678
    assert b.value == expected

def test_fractional_underflow():
    """Test that underflow is properly detected"""
    with pytest.raises(BigNum128Error):
        BigNum128.from_string('0.0000000000000000011')
    with pytest.raises(BigNum128Error):
        BigNum128.from_string('123.1234567890123456789')
    with pytest.raises(BigNum128Error):
        BigNum128.from_string('0.00000000000000000001')

def test_fractional_rounding_truncation():
    """Test deterministic truncation to SCALE_DIGITS"""
    b = BigNum128.from_string('0.1234567890123456780')
    expected = 123456789012345678
    assert b.value == expected

def test_edge_cases():
    """Test various edge cases"""
    b = BigNum128.from_string('0.0')
    assert b.value == 0
    b = BigNum128.from_string('0.100000000000000000')
    assert b.value == 100000000000000000
    b = BigNum128.from_string('1')
    assert b.value == BigNum128.SCALE

def test_scientific_notation():
    """Test that scientific notation is properly rejected"""
    with pytest.raises(ValueError, match='Input string must contain only digits'):
        BigNum128.from_string('1e-18')
    with pytest.raises(ValueError, match='Input string must contain only digits'):
        BigNum128.from_string('1E-18')
    with pytest.raises(ValueError, match='Input string parts must contain only digits'):
        BigNum128.from_string('1.5e-18')

def test_negative_values():
    """Test that negative values are properly rejected"""
    with pytest.raises(BigNum128Error):
        BigNum128.from_string('-1.0')
    with pytest.raises(BigNum128Error):
        BigNum128.from_string('-0.1')

def test_copy_method():
    """Test the copy method for deterministic behavior"""
    original = BigNum128.from_string('123.456789012345678')
    copied = original.copy()
    assert original.value == copied.value
    assert original == copied
    assert original is not copied
if __name__ == '__main__':
    pytest.main([__file__])
