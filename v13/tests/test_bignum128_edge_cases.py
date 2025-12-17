"""
Test cases for BigNum128 edge-case arithmetic with MAX_VALUE.
These tests verify that arithmetic operations correctly handle overflow and underflow conditions.
"""
import pytest
from v13.libs.BigNum128 import BigNum128, BigNum128Error

def test_addition_overflow():
    """Test addition overflow with MAX_VALUE"""
    max_val = BigNum128(BigNum128.MAX_VALUE)
    with pytest.raises(OverflowError):
        max_val.add(BigNum128(1))
    with pytest.raises(OverflowError):
        max_val.add(max_val)

def test_subtraction_underflow():
    """Test subtraction underflow with zero"""
    zero = BigNum128(0)
    with pytest.raises(BigNum128Error):
        zero.sub(BigNum128(1))

def test_division_by_zero():
    """Test division by zero"""
    val = BigNum128(1000000000000000000)
    zero = BigNum128(0)
    with pytest.raises(ZeroDivisionError):
        val.div(zero)

def test_multiplication_overflow():
    """Test multiplication overflow with MAX_VALUE"""
    max_val = BigNum128(BigNum128.MAX_VALUE)
    half_max = BigNum128(BigNum128.MAX_VALUE // 2)
    with pytest.raises(OverflowError):
        max_val.mul(BigNum128(2 * BigNum128.SCALE))
    result = half_max.mul(BigNum128(2 * BigNum128.SCALE))
    assert result.value <= BigNum128.MAX_VALUE
    slightly_over_half = BigNum128(BigNum128.MAX_VALUE // 2 + BigNum128.SCALE)
    with pytest.raises(OverflowError):
        slightly_over_half.mul(BigNum128(2 * BigNum128.SCALE))

def test_valid_boundary_operations():
    """Test valid operations at boundary values"""
    max_val = BigNum128(BigNum128.MAX_VALUE)
    zero = BigNum128(0)
    one = BigNum128(1000000000000000000)
    result = max_val.sub(max_val)
    assert result.value == 0
    result = zero.add(one)
    assert result.value == 1000000000000000000
    result = one.sub(one)
    assert result.value == 0
if __name__ == '__main__':
    pytest.main([__file__])