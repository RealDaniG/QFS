"""
Test cases for BigNum128 copy method deterministic behavior.
These tests verify that the copy method works correctly in various contexts.
"""
import pytest
from v13.libs.BigNum128 import BigNum128

def test_copy_method_basic():
    """Test basic copy functionality"""
    original = BigNum128.from_string('123.456789012345678')
    copied = original.copy()
    assert original.value == copied.value
    assert original == copied
    assert original is not copied

def test_copy_method_edge_values():
    """Test copy method with edge values"""
    zero = BigNum128.zero()
    zero_copy = zero.copy()
    assert zero.value == zero_copy.value
    assert zero == zero_copy
    assert zero is not zero_copy
    one = BigNum128.one()
    one_copy = one.copy()
    assert one.value == one_copy.value
    assert one == one_copy
    assert one is not one_copy
    max_val = BigNum128(BigNum128.MAX_VALUE)
    max_val_copy = max_val.copy()
    assert max_val.value == max_val_copy.value
    assert max_val == max_val_copy
    assert max_val is not max_val_copy

def test_copy_method_modification_independence():
    """Test that modifying copy doesn't affect original"""
    original = BigNum128.from_string('100.0')
    copied = original.copy()
    copied = copied.add(BigNum128.from_string('50.0'))
    assert original.value == BigNum128.from_string('100.0').value
    assert copied.value == BigNum128.from_string('150.0').value
    assert original != copied

def test_copy_method_chained_operations():
    """Test copy method with chained operations"""
    original = BigNum128.from_string('10.0')
    copied = original.copy()
    result1 = original.add(BigNum128.from_string('5.0')).mul(BigNum128.from_string('2.0'))
    result2 = copied.add(BigNum128.from_string('5.0')).mul(BigNum128.from_string('2.0'))
    assert result1 == result2
    assert result1.value == result2.value
if __name__ == '__main__':
    pytest.main([__file__])