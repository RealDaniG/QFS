sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from libs.CertifiedMath import CertifiedMath, BigNum128

def test_ln_one():
    with CertifiedMath.LogContext() as log:
        one = BigNum128.from_int(1)
        result = CertifiedMath.safe_ln(one, log)
        print(f'ln(1) = {result.to_decimal_string()}')
        assert result.value == 0, f'ln(1) should be 0, got {result.to_decimal_string()}'

def test_phi_zero():
    with CertifiedMath.LogContext() as log:
        zero = BigNum128(0)
        result = CertifiedMath.safe_phi_series(zero, log)
        print(f'φ(0) = {result.to_decimal_string()}')
        assert result.value == 0, f'φ(0) should be 0, got {result.to_decimal_string()}'
if __name__ == '__main__':
    test_ln_one()
    test_phi_zero()
    print('All simple tests passed!')