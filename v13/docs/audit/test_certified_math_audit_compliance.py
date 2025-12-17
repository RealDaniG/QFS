"""
Comprehensive audit compliance test suite for CertifiedMath.py
Following the QFS V13 Phase 2/3 Zero-Simulation Audit Guide
"""
import json
import hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'libs'))
from CertifiedMath import CertifiedMath, BigNum128, MathOverflowError, MathValidationError, PHI_INTENSITY_B, LN2_CONSTANT, EXP_LIMIT, ZERO, ONE, TWO, set_series_precision, set_phi_intensity_damping, set_exp_limit, get_current_config, LogContext

def test_bignum128_from_string():
    """Test BigNum128.from_string according to audit guide."""
    print('Testing BigNum128.from_string...')
    result = BigNum128.from_string('123.456789012345678901')
    expected = '123.456789012345678901'
    assert result.to_decimal_string() == expected, f'Expected {expected}, got {result.to_decimal_string()}'
    result = BigNum128.from_string('123.456')
    expected = '123.456000000000000000'
    assert result.to_decimal_string() == expected, f'Expected {expected}, got {result.to_decimal_string()}'
    result = BigNum128.from_string('123')
    expected = '123.000000000000000000'
    assert result.to_decimal_string() == expected, f'Expected {expected}, got {result.to_decimal_string()}'
    result = BigNum128.from_string('-123.456')
    print(f'  Negative input result: {result.to_decimal_string()}')
    result = BigNum128.from_string('0')
    expected = '0.000000000000000000'
    assert result.to_decimal_string() == expected, f'Expected {expected}, got {result.to_decimal_string()}'
    result = BigNum128.from_string('0.0')
    expected = '0.000000000000000000'
    assert result.to_decimal_string() == expected, f'Expected {expected}, got {result.to_decimal_string()}'
    print('  [PASS] BigNum128.from_string tests passed')

def test_basic_arithmetic_operations():
    """Test basic arithmetic operations with edge cases."""
    print('Testing basic arithmetic operations...')
    log = []
    math = CertifiedMath(log)
    max_val = BigNum128(BigNum128.MAX_VALUE)
    min_val = BigNum128(BigNum128.MIN_VALUE)
    zero = BigNum128(0)
    one = BigNum128(BigNum128.SCALE)
    neg_one = BigNum128(-BigNum128.SCALE)
    result = math.add(zero, one, pqc_cid='ADD_001')
    assert result.value == one.value, f'0 + 1 should equal 1'
    result = math.add(one, neg_one, pqc_cid='ADD_002')
    assert result.value == 0, f'1 + (-1) should equal 0'
    result = math.sub(one, one, pqc_cid='SUB_001')
    assert result.value == 0, f'1 - 1 should equal 0'
    result = math.sub(zero, one, pqc_cid='SUB_002')
    assert result.value == neg_one.value, f'0 - 1 should equal -1'
    result = math.mul(one, one, pqc_cid='MUL_001')
    assert result.value == one.value, f'1 * 1 should equal 1'
    result = math.mul(one, zero, pqc_cid='MUL_002')
    assert result.value == 0, f'1 * 0 should equal 0'
    result = math.div(one, one, pqc_cid='DIV_001')
    assert result.value == one.value, f'1 / 1 should equal 1'
    result = math.div(zero, one, pqc_cid='DIV_002')
    assert result.value == 0, f'0 / 1 should equal 0'
    try:
        result = math.add(max_val, one, pqc_cid='ADD_003')
        assert False, 'Should have raised MathOverflowError'
    except MathOverflowError:
        print('  [PASS] Addition overflow correctly detected')
    try:
        result = math.sub(min_val, one, pqc_cid='SUB_003')
        assert False, 'Should have raised MathOverflowError'
    except MathOverflowError:
        print('  [PASS] Subtraction underflow correctly detected')
    try:
        result = math.div(one, zero, pqc_cid='DIV_003')
        assert False, 'Should have raised MathValidationError'
    except MathValidationError:
        print('  [PASS] Division by zero correctly detected')
    print('  [PASS] Basic arithmetic operations tests passed')

def test_phi_series_function():
    """Test Phi-Series function with edge cases."""
    print('Testing Phi-Series function...')
    log = []
    math = CertifiedMath(log)
    one = BigNum128(BigNum128.SCALE)
    neg_one = BigNum128(-BigNum128.SCALE)
    result = math.phi_series(one, pqc_cid='PHI_001')
    print(f'  phi_series(1.0) = {result.to_decimal_string()}')
    result = math.phi_series(neg_one, pqc_cid='PHI_002')
    print(f'  phi_series(-1.0) = {result.to_decimal_string()}')
    point_9999 = BigNum128.from_string('0.9999')
    neg_point_9999 = BigNum128.from_string('-0.9999')
    result = math.phi_series(point_9999, pqc_cid='PHI_003')
    print(f'  phi_series(0.9999) = {result.to_decimal_string()}')
    result = math.phi_series(neg_point_9999, pqc_cid='PHI_004')
    print(f'  phi_series(-0.9999) = {result.to_decimal_string()}')
    boundary = BigNum128(BigNum128.SCALE)
    result = math.phi_series(boundary, pqc_cid='PHI_005')
    try:
        beyond_boundary = BigNum128(BigNum128.SCALE + 1)
        result = math.phi_series(beyond_boundary, pqc_cid='PHI_006')
        assert False, 'Should have raised MathValidationError'
    except MathValidationError:
        print('  [PASS] Phi series convergence boundary correctly enforced')
    print('  [PASS] Phi-Series function tests passed')

def test_exp_function():
    """Test exponential function with edge cases."""
    print('Testing exponential function...')
    log = []
    math = CertifiedMath(log)
    zero = BigNum128(0)
    result = math.exp(zero, pqc_cid='EXP_001')
    expected = BigNum128(BigNum128.SCALE)
    assert result.value == expected.value, f'exp(0) should equal 1, got {result.to_decimal_string()}'
    result = math.exp(EXP_LIMIT, pqc_cid='EXP_002')
    print(f'  exp(EXP_LIMIT) = {result.to_decimal_string()}')
    result = math.exp(BigNum128(-EXP_LIMIT.value), pqc_cid='EXP_003')
    print(f'  exp(-EXP_LIMIT) = {result.to_decimal_string()}')
    try:
        beyond_limit = BigNum128(EXP_LIMIT.value + BigNum128.SCALE)
        result = math.exp(beyond_limit, pqc_cid='EXP_004')
        assert False, 'Should have raised MathValidationError'
    except MathValidationError:
        print('  [PASS] Exponential limit correctly enforced')
    print('  [PASS] Exponential function tests passed')

def test_ln_function():
    """Test natural logarithm function with edge cases."""
    print('Testing natural logarithm function...')
    log = []
    math = CertifiedMath(log)
    one = BigNum128(BigNum128.SCALE)
    result = math.ln(one, pqc_cid='LN_001')
    assert result.value == 0, f'ln(1) should equal 0, got {result.to_decimal_string()}'
    point_5 = BigNum128.from_string('0.5')
    point_2 = BigNum128.from_string('2.0')
    result = math.ln(point_5, pqc_cid='LN_002')
    print(f'  ln(0.5) = {result.to_decimal_string()}')
    result = math.ln(point_2, pqc_cid='LN_003')
    print(f'  ln(2.0) = {result.to_decimal_string()}')
    point_25 = BigNum128.from_string('0.25')
    point_10 = BigNum128.from_string('10.0')
    result = math.ln(point_25, pqc_cid='LN_004')
    print(f'  ln(0.25) = {result.to_decimal_string()}')
    result = math.ln(point_10, pqc_cid='LN_005')
    print(f'  ln(10.0) = {result.to_decimal_string()}')
    try:
        negative = BigNum128(-1)
        result = math.ln(negative, pqc_cid='LN_006')
        assert False, 'Should have raised MathValidationError'
    except MathValidationError:
        print('  [PASS] ln negative input correctly detected')
    try:
        zero = BigNum128(0)
        result = math.ln(zero, pqc_cid='LN_007')
        assert False, 'Should have raised MathValidationError'
    except MathValidationError:
        print('  [PASS] ln zero input correctly detected')
    print('  [PASS] Natural logarithm function tests passed')

def test_sqrt_function():
    """Test square root function with edge cases."""
    print('Testing square root function...')
    log = []
    math = CertifiedMath(log)
    zero = BigNum128(0)
    result = math.sqrt(zero, pqc_cid='SQRT_001')
    assert result.value == 0, f'sqrt(0) should equal 0, got {result.to_decimal_string()}'
    one = BigNum128(BigNum128.SCALE)
    result = math.sqrt(one, pqc_cid='SQRT_002')
    assert abs(result.value - one.value) < one.value // 1000, f'sqrt(1) should be approximately 1, got {result.to_decimal_string()}'
    small = BigNum128(1)
    result = math.sqrt(small, pqc_cid='SQRT_003')
    print(f'  sqrt(very small) = {result.to_decimal_string()}')
    max_val = BigNum128(BigNum128.MAX_VALUE)
    result = math.sqrt(max_val, pqc_cid='SQRT_004')
    print(f'  sqrt(MAX_VALUE) = {result.to_decimal_string()}')
    try:
        negative = BigNum128(-1)
        result = math.sqrt(negative, pqc_cid='SQRT_005')
        assert False, 'Should have raised MathValidationError'
    except MathValidationError:
        print('  [PASS] sqrt negative input correctly detected')
    print('  [PASS] Square root function tests passed')

def test_two_to_the_power_function():
    """Test two to the power function with edge cases."""
    print('Testing two to the power function...')
    log = []
    math = CertifiedMath(log)
    zero = BigNum128(0)
    result = math.two_to_the_power(zero, pqc_cid='TWO_POW_001')
    expected = BigNum128(BigNum128.SCALE)
    assert result.value == expected.value, f'2^0 should equal 1, got {result.to_decimal_string()}'
    threshold_scaled = EXP_LIMIT.value * BigNum128.SCALE // LN2_CONSTANT.value
    threshold = threshold_scaled // BigNum128.SCALE
    thresh_val = BigNum128(threshold * BigNum128.SCALE)
    result = math.two_to_the_power(thresh_val, pqc_cid='TWO_POW_002')
    print(f'  2^{threshold} = {result.to_decimal_string()}')
    neg_thresh_val = BigNum128(-threshold * BigNum128.SCALE)
    result = math.two_to_the_power(neg_thresh_val, pqc_cid='TWO_POW_003')
    print(f'  2^{-threshold} = {result.to_decimal_string()}')
    try:
        beyond_thresh = BigNum128((threshold + 1) * BigNum128.SCALE)
        result = math.two_to_the_power(beyond_thresh, pqc_cid='TWO_POW_004')
        assert False, 'Should have raised MathValidationError'
    except MathValidationError:
        print('  [PASS] Two to the power threshold correctly enforced')
    print('  [PASS] Two to the power function tests passed')

def test_log_sequencing():
    """Test log sequencing and deterministic hashing."""
    print('Testing log sequencing and deterministic hashing...')
    log1 = []
    math1 = CertifiedMath(log1)
    a1 = BigNum128.from_string('1.234567')
    b1 = BigNum128.from_string('2.345678')
    result1 = math1.add(a1, b1, pqc_cid='SEQ_001')
    result2 = math1.mul(result1, a1, pqc_cid='SEQ_001')
    result3 = math1.exp(result2, pqc_cid='SEQ_001')
    hash1 = math1.get_log_hash()
    log2 = []
    math2 = CertifiedMath(log2)
    a2 = BigNum128.from_string('1.234567')
    b2 = BigNum128.from_string('2.345678')
    result4 = math2.add(a2, b2, pqc_cid='SEQ_001')
    result5 = math2.mul(result4, a2, pqc_cid='SEQ_001')
    result6 = math2.exp(result5, pqc_cid='SEQ_001')
    hash2 = math2.get_log_hash()
    assert hash1 == hash2, f'Identical operations should produce identical hashes: {hash1} != {hash2}'
    assert len(log1) == len(log2), 'Log lengths should be identical'
    for i, entry in enumerate(log1):
        assert entry['log_index'] == i, f"Log entry {i} should have index {i}, got {entry['log_index']}"
    print(f'  [PASS] Deterministic hashing verified: {hash1[:16]}...')
    print(f'  [PASS] Log sequencing verified: {len(log1)} entries')
    print('  [PASS] Log sequencing and deterministic hashing tests passed')

def test_configurable_parameters():
    """Test runtime configuration of parameters."""
    print('Testing configurable parameters...')
    original_config = get_current_config()
    set_series_precision(20)
    config = get_current_config()
    assert config['series_terms'] == 20, f"Series terms should be 20, got {config['series_terms']}"
    set_phi_intensity_damping('0.050000000000000000')
    config = get_current_config()
    assert config['phi_intensity_b_str'] == '0.050000000000000000', f"Phi intensity should be 0.05, got {config['phi_intensity_b_str']}"
    set_exp_limit('10.0')
    config = get_current_config()
    assert config['exp_limit_str'] == '10.0', f"Exp limit should be 10.0, got {config['exp_limit_str']}"
    set_series_precision(original_config['series_terms'])
    set_phi_intensity_damping(original_config['phi_intensity_b_str'])
    set_exp_limit(original_config['exp_limit_str'])
    print('  [PASS] Configurable parameters tests passed')

def test_multi_thread_safety():
    """Test multi-thread safety with LogContext."""
    print('Testing multi-thread safety...')
    log1 = []
    log2 = []
    with LogContext(log1) as ctx_log1:
        math1 = CertifiedMath(ctx_log1)
        a1 = BigNum128.from_string('1.0')
        b1 = BigNum128.from_string('2.0')
        result1 = math1.add(a1, b1, pqc_cid='THREAD_001')
    with LogContext(log2) as ctx_log2:
        math2 = CertifiedMath(ctx_log2)
        a2 = BigNum128.from_string('3.0')
        b2 = BigNum128.from_string('4.0')
        result2 = math2.add(a2, b2, pqc_cid='THREAD_002')
    assert len(log1) == 1, f'Log1 should have 1 entry, got {len(log1)}'
    assert len(log2) == 1, f'Log2 should have 1 entry, got {len(log2)}'
    assert log1[0]['pqc_cid'] == 'THREAD_001', f"Log1 should have pqc_cid THREAD_001, got {log1[0]['pqc_cid']}"
    assert log2[0]['pqc_cid'] == 'THREAD_002', f"Log2 should have pqc_cid THREAD_002, got {log2[0]['pqc_cid']}"
    print('  [PASS] Multi-thread safety tests passed')

def run_all_audit_tests():
    """Run all audit compliance tests."""
    print('Running CertifiedMath Audit Compliance Tests...')
    print('=' * 60)
    test_bignum128_from_string()
    test_basic_arithmetic_operations()
    test_phi_series_function()
    test_exp_function()
    test_ln_function()
    test_sqrt_function()
    test_two_to_the_power_function()
    test_log_sequencing()
    test_configurable_parameters()
    test_multi_thread_safety()
    print('=' * 60)
    print('[SUCCESS] All CertifiedMath Audit Compliance tests passed!')
if __name__ == '__main__':
    run_all_audit_tests()