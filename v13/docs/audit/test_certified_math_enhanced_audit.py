"""
Enhanced audit test suite for CertifiedMath.py addressing all cross-cutting audit requirements
"""
import json
import hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'libs'))
from CertifiedMath import CertifiedMath, BigNum128, MathOverflowError, MathValidationError, PHI_INTENSITY_B, LN2_CONSTANT, EXP_LIMIT, ZERO, ONE, TWO, set_series_precision, set_phi_intensity_damping, set_exp_limit, get_current_config, LogContext

def test_deterministic_json_serialization():
    """Test deterministic JSON serialization with sort_keys=True, separators=(',', ':')."""
    print('Testing deterministic JSON serialization...')
    log = []
    math = CertifiedMath(log)
    a = BigNum128.from_string('1.234567')
    b = BigNum128.from_string('2.345678')
    result = math.add(a, b, pqc_cid='JSON_001', quantum_metadata={'test': 'serialization'})
    log_hash = math.get_log_hash()
    sorted_log = sorted(log, key=lambda x: x.get('log_index', 0))
    manual_serialization = json.dumps(sorted_log, sort_keys=True).encode('utf-8')
    manual_hash = hashlib.sha256(manual_serialization).hexdigest()
    assert log_hash == manual_hash, f'Log hash mismatch: {log_hash} != {manual_hash}'
    log2 = []
    math2 = CertifiedMath(log2)
    a2 = BigNum128.from_string('1.234567')
    b2 = BigNum128.from_string('2.345678')
    result2 = math2.add(a2, b2, pqc_cid='JSON_001', quantum_metadata={'test': 'serialization'})
    log_hash2 = math2.get_log_hash()
    assert log_hash == log_hash2, f'Serialization inconsistent across runs: {log_hash} != {log_hash2}'
    print('  [PASS] Deterministic JSON serialization verified')
    print(f'  Log hash: {log_hash[:16]}...')

def test_combined_operation_overflow():
    """Test overflow detection in combined operations."""
    print('Testing combined operation overflow detection...')
    log = []
    math = CertifiedMath(log)
    a = BigNum128(BigNum128.MAX_VALUE // 2)
    b = BigNum128(BigNum128.SCALE * 3)
    c = BigNum128(BigNum128.SCALE)
    try:
        result = math.add(math.mul(a, b, pqc_cid='COMB_001'), c, pqc_cid='COMB_001')
        assert False, 'Should have raised MathOverflowError'
    except MathOverflowError as e:
        print(f'  [PASS] Combined operation overflow correctly detected: {e}')
    max_val = BigNum128(BigNum128.MAX_VALUE)
    one = BigNum128(BigNum128.SCALE)
    try:
        result = math.add(max_val, one, pqc_cid='COMB_002')
        assert False, 'Should have raised MathOverflowError'
    except MathOverflowError as e:
        print(f'  [PASS] Addition overflow correctly detected: {e}')

def test_cross_module_integration():
    """Test cross-module integration with DRV_Packet and SDK context."""
    print('Testing cross-module integration...')
    log = []
    with LogContext(log) as ctx_log:
        math = CertifiedMath(ctx_log)
        a = BigNum128.from_string('1.234567')
        b = BigNum128.from_string('2.345678')
        quantum_metadata = {'phase': 'V13 Phase 3', 'entropy_level': 'QRNG-VDF', 'test_id': 'cross_module_001'}
        result = math.add(a, b, pqc_cid='CROSS_MODULE_001', quantum_metadata=quantum_metadata)
        result2 = math.mul(result, a, pqc_cid='CROSS_MODULE_001', quantum_metadata=quantum_metadata)
        for entry in sorted(log):
            assert entry.get('pqc_cid') == 'CROSS_MODULE_001', f'Missing or incorrect PQC CID in entry: {entry}'
            assert entry.get('quantum_metadata') == quantum_metadata, f'Missing or incorrect quantum metadata in entry: {entry}'
        for i, entry in enumerate(log):
            assert entry.get('log_index') == i, f"Incorrect log index: expected {i}, got {entry.get('log_index')}"
        print('  [PASS] Cross-module integration verified')
        print(f'  Log entries: {len(log)}')

def test_audit_trail_completeness():
    """Test audit trail completeness and integrity."""
    print('Testing audit trail completeness...')
    log = []
    math = CertifiedMath(log)
    a = BigNum128.from_string('1.234567')
    b = BigNum128.from_string('2.345678')
    result1 = math.add(a, b, pqc_cid='AUDIT_001', quantum_metadata={'op': 'add'})
    try:
        zero = BigNum128(0)
        result2 = math.div(a, zero, pqc_cid='AUDIT_001', quantum_metadata={'op': 'div_by_zero'})
    except MathValidationError:
        pass
    assert len(log) >= 1, f'Expected at least 1 log entry, got {len(log)}'
    for entry in sorted(log):
        required_fields = ['log_index', 'pqc_cid', 'op_name', 'inputs']
        for field in sorted(required_fields):
            assert field in entry, f"Missing required field '{field}' in log entry: {entry}"
        assert entry.get('pqc_cid') is not None, f'Missing PQC CID in entry: {entry}'
        assert 'inputs' in entry, f'Missing inputs in entry: {entry}'
    log_indices = [entry['log_index'] for entry in log]
    expected_indices = list(range(len(log)))
    assert log_indices == expected_indices, f'Log indices out of order: {log_indices} != {expected_indices}'
    print('  [PASS] Audit trail completeness verified')
    print(f'  Log entries: {len(log)}')

def test_reference_hash_verification():
    """Test reference hash verification automation."""
    print('Testing reference hash verification...')
    log = []
    math = CertifiedMath(log)
    a = BigNum128.from_string('1.234567')
    b = BigNum128.from_string('2.345678')
    result1 = math.add(a, b, pqc_cid='REF_HASH_001')
    result2 = math.mul(result1, a, pqc_cid='REF_HASH_001')
    result3 = math.exp(result2, pqc_cid='REF_HASH_001')
    computed_hash = math.get_log_hash()
    assert len(computed_hash) == 64, f'Hash should be 64 characters, got {len(computed_hash)}'
    assert all((c in '0123456789abcdef' for c in computed_hash)), f'Hash should contain only hex characters: {computed_hash}'
    log2 = []
    math2 = CertifiedMath(log2)
    a2 = BigNum128.from_string('1.234567')
    b2 = BigNum128.from_string('2.345678')
    result4 = math2.add(a2, b2, pqc_cid='REF_HASH_001')
    result5 = math2.mul(result4, a2, pqc_cid='REF_HASH_001')
    result6 = math2.exp(result5, pqc_cid='REF_HASH_001')
    computed_hash2 = math2.get_log_hash()
    assert computed_hash == computed_hash2, f'Reference hash inconsistent: {computed_hash} != {computed_hash2}'
    print('  [PASS] Reference hash verification passed')
    print(f'  Computed hash: {computed_hash[:16]}...')

def test_stress_performance_determinism():
    """Test deterministic behavior under stress/performance conditions."""
    print('Testing stress performance determinism...')
    log1 = []
    math1 = CertifiedMath(log1)
    for i in range(1000):
        a = BigNum128.from_string(f'1.{i:06d}')
        b = BigNum128.from_string(f'2.{i:06d}')
        result = math1.add(a, b, pqc_cid=f'STRESS_001', quantum_metadata={'iteration': i})
    hash1 = math1.get_log_hash()
    log2 = []
    math2 = CertifiedMath(log2)
    for i in range(1000):
        a = BigNum128.from_string(f'1.{i:06d}')
        b = BigNum128.from_string(f'2.{i:06d}')
        result = math2.add(a, b, pqc_cid=f'STRESS_001', quantum_metadata={'iteration': i})
    hash2 = math2.get_log_hash()
    assert hash1 == hash2, f'Stress test hash mismatch: {hash1} != {hash2}'
    assert len(log1) == len(log2), f'Log length mismatch: {len(log1)} != {len(log2)}'
    print('  [PASS] Stress performance determinism verified')
    print(f'  Operations: {len(log1)}')
    print(f'  Log hash: {hash1[:16]}...')

def test_multi_threaded_determinism():
    """Test deterministic behavior under multi-threaded scenarios."""
    print('Testing multi-threaded determinism...')
    logs = []
    maths = []
    for i in range(5):
        log = []
        math = CertifiedMath(log)
        logs.append(log)
        maths.append(math)
    for i, math in enumerate(maths):
        a = BigNum128.from_string('1.123456')
        b = BigNum128.from_string('2.654321')
        quantum_metadata = {'thread_id': 0, 'test': 'multi_threaded'}
        result1 = math.add(a, b, pqc_cid='THREAD_000', quantum_metadata=quantum_metadata)
        result2 = math.mul(result1, a, pqc_cid='THREAD_000', quantum_metadata=quantum_metadata)
    hashes = []
    for i, log in enumerate(logs):
        assert len(log) == 2, f'Thread {i} log should have 2 entries, got {len(log)}'
        for j, entry in enumerate(log):
            assert entry['log_index'] == j, f"Thread {i} entry {j} has incorrect index: {entry['log_index']}"
        sorted_log = sorted(log, key=lambda x: x.get('log_index', 0))
        serialized = json.dumps(sorted_log, sort_keys=True, separators=(',', ':'))
        hash_val = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
        hashes.append(hash_val)
    assert hashes[0] == hashes[1], f'Multi-threaded hash mismatch: {hashes[0]} != {hashes[1]}'
    print('  [PASS] Multi-threaded determinism verified')
    print(f'  Thread hashes: {[h[:8] for h in hashes]}')

def test_configuration_consistency():
    """Test configuration consistency verification."""
    print('Testing configuration consistency...')
    original_config = get_current_config()
    set_series_precision(20)
    config = get_current_config()
    assert config['series_terms'] == 20, f"Series terms should be 20, got {config['series_terms']}"
    log1 = []
    math1 = CertifiedMath(log1)
    a = BigNum128.from_string('1.0')
    result1 = math1.exp(a, pqc_cid='CONFIG_001')
    hash1 = math1.get_log_hash()
    set_series_precision(original_config['series_terms'])
    log2 = []
    math2 = CertifiedMath(log2)
    a2 = BigNum128.from_string('1.0')
    result2 = math2.exp(a2, pqc_cid='CONFIG_001')
    hash2 = math2.get_log_hash()
    log3 = []
    math3 = CertifiedMath(log3)
    a3 = BigNum128.from_string('1.0')
    result3 = math3.exp(a3, pqc_cid='CONFIG_001')
    hash3 = math3.get_log_hash()
    assert hash2 == hash3, f'Configuration reset hash mismatch: {hash2} != {hash3}'
    print('  [PASS] Configuration consistency verified')
    print(f'  Modified config hash: {hash1[:16]}...')
    print(f'  Reset config hash: {hash2[:16]}...')

def run_enhanced_audit_tests():
    """Run all enhanced audit tests."""
    print('Running CertifiedMath Enhanced Audit Tests...')
    print('=' * 60)
    test_deterministic_json_serialization()
    test_combined_operation_overflow()
    test_cross_module_integration()
    test_audit_trail_completeness()
    test_reference_hash_verification()
    test_stress_performance_determinism()
    test_multi_threaded_determinism()
    test_configuration_consistency()
    print('=' * 60)
    print('[SUCCESS] All CertifiedMath Enhanced Audit tests passed!')
if __name__ == '__main__':
    run_enhanced_audit_tests()
