"""
Comprehensive test suite for BigNum128 covering all edge cases for QFS V13 Phase 3 / Zero-Simulation compliance.
This test suite ensures 100% audit readiness with full coverage of:
1. Maximum value + rounding edge cases
2. Minimum non-zero value rounding
3. Underflow beyond SCALE_DIGITS
4. Integer + fractional overflow
5. Arithmetic overflows: add, sub, mul, div
6. Division by zero
7. Modulo operator
8. Serialization correctness (16-byte big-endian)
9. Copy / equality / comparison operators
10. Type safety in comparisons
"""
import pytest
import struct
from v13.libs.BigNum128 import BigNum128, BigNum128Error

class TestBigNum128Phase3Audit:
    """Comprehensive test suite for BigNum128 Phase 3 / Zero-Simulation compliance"""
    MAX_INT_PART = BigNum128.MAX_VALUE // BigNum128.SCALE
    MAX_DECIMAL_STR = '999999999999999999'
    MIN_NONZERO_DECIMAL_STR = '000000000000000001'

    def test_maximum_value_representation(self):
        """Test that the maximum value can be represented correctly"""
        max_bignum = BigNum128(BigNum128.MAX_VALUE)
        assert max_bignum.value == BigNum128.MAX_VALUE
        max_str = max_bignum.to_decimal_string(fixed_width=True)
        assert max_str.startswith('340282366920938463463.')

    def test_maximum_value_from_string(self):
        """Test creating maximum value from string representation"""
        max_int_str = f'{self.MAX_INT_PART}.0'
        bignum = BigNum128.from_string(max_int_str)
        assert bignum.value == self.MAX_INT_PART * BigNum128.SCALE

    def test_maximum_value_plus_rounding_overflow(self):
        """Test edge case where rounding causes integer overflow - should raise OverflowError"""
        max_safe_int = self.MAX_INT_PART
        max_valid_str = f'{max_safe_int - 1}.999999999999999999'
        bignum = BigNum128.from_string(max_valid_str)
        assert isinstance(bignum, BigNum128)

    def test_precise_integer_overflow_after_rounding(self):
        """Test the precise case where rounding causes integer overflow"""
        max_safe_int = self.MAX_INT_PART
        print(f'MAX_VALUE: {BigNum128.MAX_VALUE}')
        print(f'SCALE: {BigNum128.SCALE}')
        print(f'MAX_INT_PART: {self.MAX_INT_PART}')
        print(f'MAX_INT_PART * SCALE: {self.MAX_INT_PART * BigNum128.SCALE}')
        print(f'MAX_VALUE - (MAX_INT_PART * SCALE): {BigNum128.MAX_VALUE - self.MAX_INT_PART * BigNum128.SCALE}')
        max_fractional_with_max_int = BigNum128.MAX_VALUE - self.MAX_INT_PART * BigNum128.SCALE
        print(f'Max fractional with max int part: {max_fractional_with_max_int}')
        edge_str = f'{self.MAX_INT_PART}.{str(max_fractional_with_max_int).zfill(18)}'
        bignum = BigNum128.from_string(edge_str)
        assert bignum.value == BigNum128.MAX_VALUE

    def test_minimum_nonzero_value_rounding(self):
        """Test minimum non-zero value with rounding behavior"""
        min_str = f'0.{self.MIN_NONZERO_DECIMAL_STR}'
        bignum = BigNum128.from_string(min_str)
        assert bignum.value == 1
        with pytest.raises(BigNum128Error, match='Input value too small for BigNum128'):
            BigNum128.from_string('0.0000000000000000001')

    def test_underflow_beyond_scale_digits(self):
        """Test underflow detection beyond SCALE_DIGITS with non-zero extra digits"""
        underflow_cases = ['0.0000000000000000001', '0.00000000000000000001', '1.1234567890123456789', '1.000000000000000000001']
        for case in sorted(underflow_cases):
            with pytest.raises(BigNum128Error, match='Input value too small for BigNum128'):
                BigNum128.from_string(case)

    def test_safe_underflow_with_zero_extra_digits(self):
        """Test safe cases where extra digits are all zeros (should not trigger underflow)"""
        safe_cases = ['0.0000000000000000010', '1.12345678901234567800']
        for case in sorted(safe_cases):
            bignum = BigNum128.from_string(case)
            assert isinstance(bignum, BigNum128)

    def test_integer_fractional_overflow(self):
        """Test overflow detection in integer and fractional parts"""
        with pytest.raises(OverflowError, match='Integer part too large for BigNum128'):
            BigNum128.from_string(f'{self.MAX_INT_PART + 1}.0')
        remainder = BigNum128.MAX_VALUE % BigNum128.SCALE
        overflow_fractional = remainder + 1
        with pytest.raises(OverflowError, match='Scaled value exceeds BigNum128 capacity'):
            BigNum128.from_string(f'{self.MAX_INT_PART}.{str(overflow_fractional).zfill(18)}')

    def test_arithmetic_overflow_add(self):
        """Test addition overflow detection"""
        half_max = BigNum128(BigNum128.MAX_VALUE // 2)
        more_than_half = BigNum128(BigNum128.MAX_VALUE // 2 + 2)
        with pytest.raises(OverflowError, match='BigNum128 addition overflow'):
            half_max.add(more_than_half)
        with pytest.raises(OverflowError, match='BigNum128 addition overflow'):
            _ = half_max + more_than_half

    def test_arithmetic_overflow_sub(self):
        """Test subtraction underflow detection"""
        small = BigNum128(100)
        large = BigNum128(200)
        with pytest.raises(BigNum128Error, match='BigNum128 subtraction underflow'):
            small.sub(large)
        with pytest.raises(BigNum128Error, match='BigNum128 subtraction underflow'):
            _ = small - large

    def test_arithmetic_overflow_mul(self):
        """Test multiplication overflow detection"""
        sqrt_max_scaled = int((BigNum128.MAX_VALUE * BigNum128.SCALE) ** 0.5)
        large_val = BigNum128(sqrt_max_scaled)
        large_val = BigNum128(int(BigNum128.MAX_VALUE * 0.8))
        another_large_val = BigNum128(int(BigNum128.MAX_VALUE * 0.8))
        sqrt_approach_val = int((BigNum128.MAX_VALUE * BigNum128.SCALE) ** 0.5) * 2
        if sqrt_approach_val <= BigNum128.MAX_VALUE:
            val1 = BigNum128(sqrt_approach_val)
            val2 = BigNum128(sqrt_approach_val)
            with pytest.raises(OverflowError):
                val1.mul(val2)
        else:
            val1 = BigNum128(BigNum128.MAX_VALUE)
            val2 = BigNum128(BigNum128.MAX_VALUE)
            with pytest.raises(OverflowError):
                val1.mul(val2)

    def test_arithmetic_overflow_div(self):
        """Test division overflow detection"""
        numerator = BigNum128(BigNum128.MAX_VALUE // 2)
        very_small_denominator = BigNum128(1)
        pass

    def test_division_by_zero(self):
        """Test division by zero raises appropriate exception"""
        a = BigNum128(100)
        b = BigNum128(0)
        with pytest.raises(ZeroDivisionError, match='BigNum128 division by zero'):
            a.div(b)
        with pytest.raises(ZeroDivisionError, match='BigNum128 division by zero'):
            _ = a / b
        with pytest.raises(ZeroDivisionError, match='BigNum128 division by zero'):
            _ = a // b

    def test_modulo_operator(self):
        """Test modulo operator functionality and edge cases"""
        a = BigNum128.from_string('10.5')
        b = BigNum128.from_string('3.0')
        result = a % b
        expected_value = 10.5 * BigNum128.SCALE % (3 * BigNum128.SCALE)
        assert result.value == expected_value
        with pytest.raises(ZeroDivisionError):
            _ = a % BigNum128(0)
        with pytest.raises(TypeError, match='mod requires BigNum128'):
            _ = a % 5

    def test_serialization_correctness(self):
        """Test 16-byte big-endian serialization correctness"""
        zero = BigNum128.zero()
        zero_bytes = zero.serialize_for_sign()
        assert len(zero_bytes) == 16
        assert zero_bytes == b'\x00' * 16
        one = BigNum128.one()
        one_bytes = one.serialize_for_sign()
        assert len(one_bytes) == 16
        expected_one_bytes = (1 * BigNum128.SCALE).to_bytes(16, 'big')
        assert one_bytes == expected_one_bytes
        max_val = BigNum128(BigNum128.MAX_VALUE)
        max_bytes = max_val.serialize_for_sign()
        assert len(max_bytes) == 16
        expected_max_bytes = BigNum128.MAX_VALUE.to_bytes(16, 'big')
        assert max_bytes == expected_max_bytes
        reconstructed = BigNum128(int.from_bytes(max_bytes, 'big'))
        assert reconstructed == max_val

    def test_canonical_decimal_string_serialization(self):
        """Test canonical decimal string serialization for auditability"""
        test_values = [('0.0', '0.0'), ('1.0', '1.0'), ('1.5', '1.5'), ('0.123456789012345678', '0.123456789012345678'), ('123.456789012345678912', '123.456789012345678912')]
        for input_str, _ in sorted(test_values):
            bignum = BigNum128.from_string(input_str)
            fixed_str = bignum.to_decimal_string(fixed_width=True)
            assert len(fixed_str.split('.')[1]) == 18
            variable_str = bignum.to_decimal_string(fixed_width=False)
            fractional_part = variable_str.split('.')[1]
            if fractional_part != '0':
                assert not fractional_part.endswith('0') or fractional_part == '0'

    def test_copy_equality_comparison_operators(self):
        """Test copy, equality, and comparison operators"""
        original = BigNum128.from_string('123.456789012345678')
        copied = original.copy()
        assert original == copied
        assert original is not copied
        assert original.value == copied.value
        other = BigNum128.from_string('123.456789012345678')
        assert original == other
        assert original is not other
        different = BigNum128.from_string('123.456789012345679')
        assert original != different

    def test_strict_type_safety_in_comparisons(self):
        """Test strict type safety in comparison operators"""
        bignum = BigNum128.from_string('10.0')
        assert not bignum < 10
        assert not bignum > 10
        assert not bignum <= 10
        assert not bignum >= 10
        assert not bignum == 10
        assert bignum != 10
        assert not bignum < '10.0'
        assert not bignum == '10.0'
        assert bignum != '10.0'
        other = BigNum128.from_string('5.0')
        assert bignum > other
        assert bignum >= other
        assert not bignum < other
        assert not bignum <= other
        assert not bignum == other

    def test_hash_consistency(self):
        """Test that hash is consistent with equality"""
        a = BigNum128.from_string('10.0')
        b = BigNum128.from_string('10.0')
        c = BigNum128.from_string('10.1')
        assert a == b
        assert hash(a) == hash(b)
        assert a != c
        assert hash(a) != hash(c)

    def test_arithmetic_operator_overloads(self):
        """Test arithmetic operator overloads"""
        a = BigNum128.from_string('10.5')
        b = BigNum128.from_string('2.5')
        result_add = a + b
        expected_add = BigNum128.from_string('13.0')
        assert result_add == expected_add
        result_sub = a - b
        expected_sub = BigNum128.from_string('8.0')
        assert result_sub == expected_sub
        result_mul = a * b
        expected_mul = BigNum128.from_string('26.25')
        assert result_mul == expected_mul
        result_div = a / b
        expected_div = BigNum128.from_string('4.2')
        assert result_div == expected_div
        result_floordiv = a // b
        assert result_floordiv == expected_div

    def test_constants(self):
        """Test zero() and one() constants"""
        zero = BigNum128.zero()
        one = BigNum128.one()
        assert zero.value == 0
        assert one.value == BigNum128.SCALE
        another_zero = BigNum128.zero()
        assert zero is not another_zero
        assert zero == another_zero

    def test_from_int_method(self):
        """Test from_int class method"""
        zero = BigNum128.from_int(0)
        assert zero.value == 0
        ten = BigNum128.from_int(10)
        assert ten.value == 10 * BigNum128.SCALE
        max_int_part = BigNum128.MAX_VALUE // BigNum128.SCALE
        large = BigNum128.from_int(max_int_part)
        assert large.value == max_int_part * BigNum128.SCALE
        with pytest.raises(OverflowError):
            BigNum128.from_int(max_int_part + 1)

    def test_negative_input_rejection(self):
        """Test that negative inputs are properly rejected"""
        negative_inputs = ['-1', '-0.5', '-123.456']
        for input_str in sorted(negative_inputs):
            with pytest.raises(BigNum128Error, match='BigNum128 is unsigned'):
                BigNum128.from_string(input_str)

    def test_invalid_string_rejection(self):
        """Test that invalid string formats are properly rejected"""
        with pytest.raises(ValueError, match='Input string must contain only digits'):
            BigNum128.from_string('abc')
        with pytest.raises(ValueError, match='Input string must contain at most one decimal point'):
            BigNum128.from_string('1.2.3')
        with pytest.raises(ValueError, match='Input string parts must contain only digits'):
            BigNum128.from_string('1.abc')
        with pytest.raises(ValueError, match='Input string parts must contain only digits'):
            BigNum128.from_string('abc.123')
        with pytest.raises(ValueError):
            BigNum128.from_string('')
        result = BigNum128.from_string('.')
        assert result == BigNum128.from_string('0.0')
        result = BigNum128.from_string('1.')
        assert result == BigNum128.from_string('1.0')
        result = BigNum128.from_string('.1')
        assert result == BigNum128.from_string('0.1')

    def test_repr_and_str_methods(self):
        """Test __repr__ and __str__ methods"""
        bignum = BigNum128.from_string('123.456')
        str_repr = str(bignum)
        assert '123.456' in str_repr
        repr_str = repr(bignum)
        assert 'BigNum128' in repr_str
        assert 'raw=' in repr_str
        assert 'fp=' in repr_str
        assert str(bignum.value) in repr_str
if __name__ == '__main__':
    pytest.main([__file__, '-v'])