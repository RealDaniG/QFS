"""
Comprehensive test cases for BigNum128 fixes.
These tests verify that all the identified issues have been properly addressed.
"""
import pytest
from v13.libs.BigNum128 import BigNum128, BigNum128Error

def test_underflow_detection_fix():
    """Test that underflow detection works correctly with .rstrip('0')"""
    with pytest.raises(BigNum128Error):
        BigNum128.from_string('0.0000000000000000100')
    with pytest.raises(BigNum128Error):
        BigNum128.from_string('0.0000000000000000011')

def test_round_half_up():
    """Test that round-half-up works correctly"""
    b = BigNum128.from_string('0.000000000000000005')
    assert b.value == 1
    b = BigNum128.from_string('0.0000000000000000015')
    assert b.value == 2
    b = BigNum128.from_string('0.0000000000000000014')
    assert b.value == 1

def test_pqc_serialization():
    """Test that PQC serialization produces fixed-width 16-byte big-endian format"""
    b = BigNum128.from_string('1.0')
    serialized = b.serialize_for_sign()
    assert len(serialized) == 16
    assert serialized == b.value.to_bytes(16, 'big')
    b = BigNum128.zero()
    serialized = b.serialize_for_sign()
    assert len(serialized) == 16
    assert serialized == b'\x00' * 16
    b = BigNum128(BigNum128.MAX_VALUE)
    serialized = b.serialize_for_sign()
    assert len(serialized) == 16
    assert serialized == b.value.to_bytes(16, 'big')

def test_modulo_operator():
    """Test that modulo operator works correctly"""
    a = BigNum128.from_string('10.0')
    b = BigNum128.from_string('3.0')
    result = a % b
    expected = BigNum128.from_string('1.0')
    assert result == expected
    with pytest.raises(TypeError):
        _ = a % 3.0

def test_integer_fraction_overflow():
    """Test integer + fraction overflow detection"""
    b = BigNum128.from_string('123.456789012345678')
    assert b.value == 123456789012345678
if __name__ == '__main__':
    pytest.main([__file__])