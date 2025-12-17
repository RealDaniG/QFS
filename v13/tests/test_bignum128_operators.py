"""
Test cases for BigNum128 operator overloads.
These tests verify that all comparison and arithmetic operators work correctly.
"""
import pytest
from v13.libs.BigNum128 import BigNum128

def test_comparison_operators():
    """Test all comparison operators"""
    a = BigNum128.from_string('1.5')
    b = BigNum128.from_string('2.0')
    c = BigNum128.from_string('1.5')
    assert a == c
    assert not a == b
    assert a != b
    assert not a != c
    assert a < b
    assert not b < a
    assert not a < c
    assert a <= b
    assert a <= c
    assert not b <= a
    assert b > a
    assert not a > b
    assert not a > c
    assert b >= a
    assert a >= c
    assert not a >= b

def test_arithmetic_operators():
    """Test all arithmetic operators"""
    a = BigNum128.from_string('1.5')
    b = BigNum128.from_string('2.0')
    result = a + b
    expected = BigNum128.from_string('3.5')
    assert result == expected
    result = b - a
    expected = BigNum128.from_string('0.5')
    assert result == expected
    result = a * b
    expected = BigNum128.from_string('3.0')
    assert result == expected
    result = b / a
    expected = BigNum128.from_string('1.333333333333333333')
    assert result == expected
    result = b // a
    expected = BigNum128.from_string('1.333333333333333333')
    assert result == expected

def test_operator_type_safety():
    """Test that operators properly handle type mismatches"""
    a = BigNum128.from_string('1.5')
    assert not a == 1.5
    assert not a == '1.5'
    assert not a == 1500000000000000000
    assert not a < 2.0
    assert not a > '2.0'
    with pytest.raises(TypeError):
        _ = a + 1.5
    with pytest.raises(TypeError):
        _ = a - '1.5'
    with pytest.raises(TypeError):
        _ = a * 2
    with pytest.raises(TypeError):
        _ = a / 3

def test_hash_function():
    """Test that the hash function works correctly"""
    a = BigNum128.from_string('1.5')
    b = BigNum128.from_string('1.5')
    c = BigNum128.from_string('2.0')
    assert hash(a) == hash(b)
    assert hash(a) != hash(c)
    d = {a: 'value1', c: 'value2'}
    assert d[a] == 'value1'
    assert d[b] == 'value1'
    assert d[c] == 'value2'
if __name__ == '__main__':
    pytest.main([__file__])