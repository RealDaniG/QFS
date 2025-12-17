from libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_bignum_to_decimal_string():
    """Test the fixed BigNum128.to_decimal_string method"""
    try:
        from libs.BigNum128 import BigNum128
        print('Testing BigNum128.to_decimal_string fix...')
        bn1 = BigNum128(100)
        result1 = bn1.to_decimal_string()
        print(f'BigNum128(100) -> {result1}')
        assert result1 == '0.0000000000000001', f"Expected '0.0000000000000001', got '{result1}'"
        bn2 = BigNum128(1000000000000000000)
        result2 = bn2.to_decimal_string()
        print(f'BigNum128(1000000000000000000) -> {result2}')
        assert result2 == '1.0', f"Expected '1.0', got '{result2}'"
        bn3 = BigNum128(0)
        result3 = bn3.to_decimal_string()
        print(f'BigNum128(0) -> {result3}')
        assert result3 == '0.0', f"Expected '0.0', got '{result3}'"
        bn4 = BigNum128(1234567890123456789012345)
        result4 = bn4.to_decimal_string()
        print(f'BigNum128(1234567890123456789012345) -> {result4}')
        assert result4 == '1234567.890123456789012345', f"Expected '1234567.890123456789012345', got '{result4}'"
        print('✅ All BigNum128.to_decimal_string tests passed!')
        return True
    except Exception as e:
        print(f'❌ Error testing BigNum128.to_decimal_string: {e}')
        return False

def test_certified_math_bignum_to_decimal_string():
    """Test the fixed BigNum128.to_decimal_string method in CertifiedMath"""
    try:
        from libs.CertifiedMath import BigNum128
        print('Testing CertifiedMath BigNum128.to_decimal_string fix...')
        bn1 = BigNum128(100)
        result1 = bn1.to_decimal_string()
        print(f'BigNum128(100) -> {result1}')
        assert result1 == '0.0000000000000001', f"Expected '0.0000000000000001', got '{result1}'"
        bn2 = BigNum128(1000000000000000000)
        result2 = bn2.to_decimal_string()
        print(f'BigNum128(1000000000000000000) -> {result2}')
        assert result2 == '1.0', f"Expected '1.0', got '{result2}'"
        bn3 = BigNum128(0)
        result3 = bn3.to_decimal_string()
        print(f'BigNum128(0) -> {result3}')
        assert result3 == '0.0', f"Expected '0.0', got '{result3}'"
        print('✅ All CertifiedMath BigNum128.to_decimal_string tests passed!')
        return True
    except Exception as e:
        print(f'❌ Error testing CertifiedMath BigNum128.to_decimal_string: {e}')
        return False
if __name__ == '__main__':
    success1 = test_bignum_to_decimal_string()
    success2 = test_certified_math_bignum_to_decimal_string()
    if success1 and success2:
        print('\n🎉 All BigNum128 fixes verified successfully!')
    else:
        print('\n❌ Some tests failed.')
        raise ZeroSimAbort(1)