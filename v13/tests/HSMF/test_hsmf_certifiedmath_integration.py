"""
Test script for HSMF.py and CertifiedMath.py to verify the implementations work correctly.
"""
from v13.libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
import json
try:
    from v13.libs.BigNum128 import BigNum128
    from v13.libs.CertifiedMath import CertifiedMath
    from core.TokenStateBundle import TokenStateBundle, create_token_state_bundle
    from handlers.CIR302_Handler import CIR302_Handler
    from core.HSMF import HSMF
except ImportError:
    try:
        from v13.libs.BigNum128 import BigNum128
        from v13.libs.CertifiedMath import CertifiedMath
        from v13.core.TokenStateBundle import TokenStateBundle, create_token_state_bundle
        from v13.handlers.CIR302_Handler import CIR302_Handler
        from v13.core.HSMF import HSMF
    except ImportError:
        from v13.libs.BigNum128 import BigNum128
        from v13.libs.CertifiedMath import CertifiedMath
        from v13.core.TokenStateBundle import TokenStateBundle, create_token_state_bundle
        from v13.handlers.CIR302_Handler import CIR302_Handler
        from v13.core.HSMF import HSMF

def test_hsmf_with_certified_math():
    """Test the HSMF implementation with CertifiedMath."""
    print('Testing HSMF with CertifiedMath...')
    log_list = []
    cm = CertifiedMath(log_list)
    cir302_handler = CIR302_Handler(cm)
    hsmf = HSMF(cm, cir302_handler)
    chr_state = {'coherence_metric': '0.98'}
    flx_state = {'magnitudes': [BigNum128.from_string('1.0'), BigNum128.from_string('1.618'), BigNum128.from_string('2.618')]}
    psi_sync_state = {'current_sequence': BigNum128.from_int(100)}
    atr_state = {'atr_magnitude': BigNum128.from_string('1.0')}
    res_state = {'inertial_metric': '0.05'}
    lambda1 = BigNum128.from_string('1.618033988749894848')
    lambda2 = BigNum128.from_string('0.95')
    c_crit = BigNum128.from_string('0.9')
    token_bundle = create_token_state_bundle(chr_state=chr_state, flx_state=flx_state, psi_sync_state=psi_sync_state, atr_state=atr_state, res_state=res_state, lambda1=lambda1, lambda2=lambda2, c_crit=c_crit, pqc_cid='TEST_PQC', timestamp=1234567890)
    f_atr = BigNum128.from_string('0.005')
    try:
        result = hsmf.validate_action_bundle(token_bundle, f_atr, pqc_cid='TEST_PQC')
        print(f'Validation successful: {result.is_valid}')
        print(f'DEZ OK: {result.dez_ok}')
        print(f'Survival OK: {result.survival_ok}')
        print(f'Errors: {result.errors}')
        print('Metrics:')
        for name, value in result.metrics_str.items():
            print(f'  {name}: {value}')
        print(f'Total log entries: {len(log_list)}')
        print('\nFirst 5 log entries:')
        for i, entry in enumerate(log_list[:5]):
            print(f'  {i}: {entry}')
        log_hash = cm.get_log_hash()
        print(f'\nLog hash: {log_hash}')
        return True
    except Exception as e:
        print(f'Validation failed with exception: {e}')
        import traceback
        traceback.print_exc()
        return False

def test_public_api():
    """Test the CertifiedMath public API methods."""
    print('\nTesting CertifiedMath public API...')
    log_list = []
    cm = CertifiedMath(log_list)
    a = BigNum128.from_string('10.5')
    b = BigNum128.from_string('5.25')
    result_add = cm.add(a, b, pqc_cid='TEST_ADD')
    result_sub = cm.sub(a, b, pqc_cid='TEST_SUB')
    result_mul = cm.mul(a, b, pqc_cid='TEST_MUL')
    result_div = cm.div(a, b, pqc_cid='TEST_DIV')
    print(f'Add: {a.to_decimal_string()} + {b.to_decimal_string()} = {result_add.to_decimal_string()}')
    print(f'Sub: {a.to_decimal_string()} - {b.to_decimal_string()} = {result_sub.to_decimal_string()}')
    print(f'Mul: {a.to_decimal_string()} * {b.to_decimal_string()} = {result_mul.to_decimal_string()}')
    print(f'Div: {a.to_decimal_string()} / {b.to_decimal_string()} = {result_div.to_decimal_string()}')
    result_gt = cm.gt(a, b, pqc_cid='TEST_GT')
    result_lt = cm.lt(a, b, pqc_cid='TEST_LT')
    result_gte = cm.gte(a, b, pqc_cid='TEST_GTE')
    result_lte = cm.lte(a, b, pqc_cid='TEST_LTE')
    result_eq = cm.eq(a, b, pqc_cid='TEST_EQ')
    result_ne = cm.ne(a, b, pqc_cid='TEST_NE')
    print(f'GT: {a.to_decimal_string()} > {b.to_decimal_string()} = {result_gt}')
    print(f'LT: {a.to_decimal_string()} < {b.to_decimal_string()} = {result_lt}')
    print(f'GTE: {a.to_decimal_string()} >= {b.to_decimal_string()} = {result_gte}')
    print(f'LTE: {a.to_decimal_string()} <= {b.to_decimal_string()} = {result_lte}')
    print(f'EQ: {a.to_decimal_string()} == {b.to_decimal_string()} = {result_eq}')
    print(f'NE: {a.to_decimal_string()} != {b.to_decimal_string()} = {result_ne}')
    c = BigNum128.from_string('-7.5')
    result_abs = cm.abs(c, pqc_cid='TEST_ABS')
    print(f'Abs: |{c.to_decimal_string()}| = {result_abs.to_decimal_string()}')
    d = BigNum128.from_string('0.5')
    result_exp = cm.exp(d, pqc_cid='TEST_EXP')
    result_ln = cm.ln(d, pqc_cid='TEST_LN')
    result_sqrt = cm.sqrt(d, pqc_cid='TEST_SQRT')
    print(f'Exp: e^{d.to_decimal_string()} = {result_exp.to_decimal_string()}')
    print(f'Ln: ln({d.to_decimal_string()}) = {result_ln.to_decimal_string()}')
    print(f'Sqrt: sqrt({d.to_decimal_string()}) = {result_sqrt.to_decimal_string()}')
    base = BigNum128.from_string('2.0')
    exponent = BigNum128.from_string('3.0')
    result_pow = cm.pow(base, exponent, pqc_cid='TEST_POW')
    result_two_power = cm.two_to_the_power(exponent, pqc_cid='TEST_TWO_POWER')
    print(f'Pow: {base.to_decimal_string()}^{exponent.to_decimal_string()} = {result_pow.to_decimal_string()}')
    print(f'Two to the power: 2^{exponent.to_decimal_string()} = {result_two_power.to_decimal_string()}')
    print(f'Total log entries: {len(log_list)}')
    return True
if __name__ == '__main__':
    print('=== QFS V13 HSMF & CertifiedMath Integration Test ===')
    api_success = test_public_api()
    hsmf_success = test_hsmf_with_certified_math()
    if api_success and hsmf_success:
        print('\n=== ALL TESTS PASSED ===')
        raise ZeroSimAbort(0)
    else:
        print('\n=== SOME TESTS FAILED ===')
        raise ZeroSimAbort(1)
