"""
Test cases for the _safe_phi_series function in CertifiedMath
"""
from v13.libs.CertifiedMath import CertifiedMath, BigNum128

def test_phi_series_basic_values():
    """Test phi_series function with basic values"""
    with CertifiedMath.LogContext() as log:
        zero = BigNum128(0)
        result = CertifiedMath.safe_phi_series(zero, log)
        expected = BigNum128(0)
        assert result.value == expected.value, f'φ(0) should be 0, got {result.to_decimal_string()}'
        one = BigNum128.from_int(1)
        result = CertifiedMath.safe_phi_series(one, log, n=10)
        assert result.value > 0, f'φ(1) should be positive, got {result.to_decimal_string()}'

def test_phi_series_negative_values():
    """Test phi_series function with negative values"""
    with CertifiedMath.LogContext() as log:
        neg_one = BigNum128.from_int(-1)
        result = CertifiedMath.safe_phi_series(neg_one, log, n=10)
        assert result.value < 0, f'φ(-1) should be negative, got {result.to_decimal_string()}'

def test_phi_series_half_values():
    """Test phi_series function with 0.5"""
    with CertifiedMath.LogContext() as log:
        half = BigNum128(500000000000000000)
        result = CertifiedMath.safe_phi_series(half, log, n=20)
        assert result.value > 0, f'φ(0.5) should be positive, got {result.to_decimal_string()}'
        assert result.value < BigNum128.from_int(1).value, f'φ(0.5) should be less than 1, got {result.to_decimal_string()}'

def test_phi_series_deterministic():
    """Test that phi_series produces deterministic results"""
    with CertifiedMath.LogContext() as log1:
        val = BigNum128.from_int(1)
        result1 = CertifiedMath.safe_phi_series(val, log1, n=15)
        hash1 = CertifiedMath.get_log_hash(log1)
    with CertifiedMath.LogContext() as log2:
        val = BigNum128.from_int(1)
        result2 = CertifiedMath.safe_phi_series(val, log2, n=15)
        hash2 = CertifiedMath.get_log_hash(log2)
    assert result1.value == result2.value, 'phi_series should produce deterministic results'
    assert hash1 == hash2, 'Log hashes should be identical for deterministic operations'

def test_phi_series_convergence():
    """Test that increasing terms improves convergence"""
    with CertifiedMath.LogContext() as log10:
        val = BigNum128.from_int(1)
        result10 = CertifiedMath.safe_phi_series(val, log10, n=10)
    with CertifiedMath.LogContext() as log20:
        val = BigNum128.from_int(1)
        result20 = CertifiedMath.safe_phi_series(val, log20, n=20)
    diff = abs(result10.value - result20.value)
    assert diff < 10000000000000, f'Results should converge with more terms, diff: {diff}'
if __name__ == '__main__':
    test_phi_series_basic_values()
    test_phi_series_negative_values()
    test_phi_series_half_values()
    test_phi_series_deterministic()
    test_phi_series_convergence()
    print('All phi_series tests passed!')