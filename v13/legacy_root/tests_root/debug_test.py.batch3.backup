sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from libs.CertifiedMath import CertifiedMath, BigNum128

def debug_exp_ln():
    with CertifiedMath.LogContext() as log:
        two = BigNum128.from_int(2)
        print(f'Input: {two.to_decimal_string()}')
        ln_two = CertifiedMath.safe_ln(two, log)
        print(f'ln(2): {ln_two.to_decimal_string()}')
        exp_ln_two = CertifiedMath.safe_exp(ln_two, log)
        print(f'exp(ln(2)): {exp_ln_two.to_decimal_string()}')
        diff = abs(exp_ln_two.value - two.value)
        print(f'Difference: {diff}')
if __name__ == '__main__':
    debug_exp_ln()