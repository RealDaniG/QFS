"""
Test cases for the _safe_ln function in CertifiedMath
"""
import math
from v13.libs.CertifiedMath import CertifiedMath, BigNum128

def test_ln_basic_values():
    """Test ln function with basic values"""
    with CertifiedMath.LogContext() as log:
        one = BigNum128.from_int(1)
        result = CertifiedMath.safe_ln(one, log)
        expected = BigNum128(0)
        assert result.value == expected.value, f'ln(1) should be 0, got {result.to_decimal_string()}'
        e_val = BigNum128(2718281828459045235)
        result = CertifiedMath.safe_ln(e_val, log)
        expected = BigNum128.from_int(1)
        assert abs(result.value - expected.value) < 1000000000000, f'ln(e) should be 1, got {result.to_decimal_string()}'

def test_ln_known_constants():
    """Test ln function with known mathematical constants"""
    with CertifiedMath.LogContext() as log:
        two = BigNum128.from_int(2)
        result = CertifiedMath.safe_ln(two, log)
        expected = BigNum128(693147180559945309)
        assert abs(result.value - expected.value) < 1000000000000, f'ln(2) should be ~0.693, got {result.to_decimal_string()}'
        ten = BigNum128.from_int(10)
        result = CertifiedMath.safe_ln(ten, log)
        expected = BigNum128(2302585092994045684)
        assert abs(result.value - expected.value) < 1000000000000, f'ln(10) should be ~2.303, got {result.to_decimal_string()}'

def test_ln_edge_cases():
    """Test ln function with edge cases"""
    with CertifiedMath.LogContext() as log:
        one = BigNum128.from_int(1)
        result = CertifiedMath.safe_ln(one, log)
        expected = BigNum128(0)
        assert result.value == expected.value, f'ln(1) should be 0, got {result.to_decimal_string()}'
        small_val = BigNum128(1)
        try:
            result = CertifiedMath.safe_ln(small_val, log)
            assert result.value < 0, f'ln(small) should be negative, got {result.to_decimal_string()}'
        except ValueError:
            pass
        two = BigNum128.from_int(2)
        result = CertifiedMath.safe_ln(two, log)
        expected = BigNum128(693147180559945309)
        assert abs(result.value - expected.value) < 1000000000000, f'ln(2) should be ~0.693, got {result.to_decimal_string()}'

def test_ln_randomized_deterministic():
    """Test that ln produces deterministic results"""
    with CertifiedMath.LogContext() as log1:
        val = BigNum128.from_int(5)
        result1 = CertifiedMath.safe_ln(val, log1)
        hash1 = CertifiedMath.get_log_hash(log1)
    with CertifiedMath.LogContext() as log2:
        val = BigNum128.from_int(5)
        result2 = CertifiedMath.safe_ln(val, log2)
        hash2 = CertifiedMath.get_log_hash(log2)
    assert result1.value == result2.value, 'ln should produce deterministic results'
    assert hash1 == hash2, 'Log hashes should be identical for deterministic operations'
if __name__ == '__main__':
    test_ln_basic_values()
    test_ln_known_constants()
    test_ln_edge_cases()
    test_ln_randomized_deterministic()
    print('All ln tests passed!')
