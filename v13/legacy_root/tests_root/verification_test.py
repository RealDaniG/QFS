sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from v13.libs.CertifiedMath import CertifiedMath, BigNum128

def test_deterministic_replay():
    """Test deterministic replay of a sequence of operations"""
    with CertifiedMath.LogContext() as log1:
        val = BigNum128.from_int(2)
        result1 = CertifiedMath.safe_ln(val, log1)
        result1 = CertifiedMath.safe_exp(result1, log1)
        hash1 = CertifiedMath.get_log_hash(log1)
        result1_str = result1.to_decimal_string()
    with CertifiedMath.LogContext() as log2:
        val = BigNum128.from_int(2)
        result2 = CertifiedMath.safe_ln(val, log2)
        result2 = CertifiedMath.safe_exp(result2, log2)
        hash2 = CertifiedMath.get_log_hash(log2)
        result2_str = result2.to_decimal_string()
    print(f'Result 1: {result1_str}')
    print(f'Result 2: {result2_str}')
    print(f'Hash 1: {hash1}')
    print(f'Hash 2: {hash2}')
    assert result1.value == result2.value, 'Sequence should produce deterministic results'
    assert hash1 == hash2, 'Log hashes should be identical for deterministic operations'
    print('Deterministic replay test passed!')

def test_phi_series():
    """Test phi series with a few values"""
    with CertifiedMath.LogContext() as log:
        one = BigNum128.from_int(1)
        result = CertifiedMath.safe_phi_series(one, log, n=5)
        print(f'φ(1) with 5 terms: {result.to_decimal_string()}')
        assert result.value > 0, f'φ(1) should be positive, got {result.to_decimal_string()}'
if __name__ == '__main__':
    test_deterministic_replay()
    test_phi_series()
    print('All verification tests passed!')
