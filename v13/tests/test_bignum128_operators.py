"""
Test cases for BigNum128 operator overloads.
These tests verify that all comparison and arithmetic operators work correctly.
"""

import pytest
from v13.libs.BigNum128 import BigNum128


def test_comparison_operators():
    """Test all comparison operators"""
    a = BigNum128.from_string("1.5")
    b = BigNum128.from_string("2.0")
    c = BigNum128.from_string("1.5")  # Same value as a

    # Equality
    assert a == c
    assert not (a == b)
    
    # Inequality
    assert a != b
    assert not (a != c)
    
    # Less than
    assert a < b
    assert not (b < a)
    assert not (a < c)
    
    # Less than or equal
    assert a <= b
    assert a <= c
    assert not (b <= a)
    
    # Greater than
    assert b > a
    assert not (a > b)
    assert not (a > c)
    
    # Greater than or equal
    assert b >= a
    assert a >= c
    assert not (a >= b)


def test_arithmetic_operators():
    """Test all arithmetic operators"""
    a = BigNum128.from_string("1.5")
    b = BigNum128.from_string("2.0")
    
    # Addition
    result = a + b
    expected = BigNum128.from_string("3.5")
    assert result == expected
    
    # Subtraction
    result = b - a
    expected = BigNum128.from_string("0.5")
    assert result == expected
    
    # Multiplication
    result = a * b
    expected = BigNum128.from_string("3.0")
    assert result == expected
    
    # Division
    result = b / a
    expected = BigNum128.from_string("1.333333333333333333")  # 2.0 / 1.5 = 1.333...
    assert result == expected
    
    # Floor division
    result = b // a
    expected = BigNum128.from_string("1.333333333333333333")  # Same as regular division for fixed-point
    assert result == expected


def test_operator_type_safety():
    """Test that operators properly handle type mismatches"""
    a = BigNum128.from_string("1.5")
    
    # Comparison with non-BigNum128 should return False or NotImplemented
    assert not (a == 1.5)
    assert not (a == "1.5")
    assert not (a == 1500000000000000000)
    
    # Comparison operators should handle non-BigNum128 gracefully
    assert not (a < 2.0)
    assert not (a > "2.0")
    
    # Arithmetic with non-BigNum128 should raise TypeError
    with pytest.raises(TypeError):
        _ = a + 1.5
    
    with pytest.raises(TypeError):
        _ = a - "1.5"
    
    with pytest.raises(TypeError):
        _ = a * 2
    
    with pytest.raises(TypeError):
        _ = a / 3


def test_hash_function():
    """Test that the hash function works correctly"""
    a = BigNum128.from_string("1.5")
    b = BigNum128.from_string("1.5")  # Same value
    c = BigNum128.from_string("2.0")  # Different value
    
    # Same values should have same hash
    assert hash(a) == hash(b)
    
    # Different values should have different hash (with high probability)
    assert hash(a) != hash(c)
    
    # Should be usable as dict key
    d = {a: "value1", c: "value2"}
    assert d[a] == "value1"
    assert d[b] == "value1"  # b has same value as a
    assert d[c] == "value2"


if __name__ == "__main__":
    pytest.main([__file__])