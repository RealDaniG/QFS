"""
Audit Verification Script for QFS V13 Compliance & Determinism
"""
from v13.libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
import json
sys.path.insert(0, 'libs')
from CertifiedMath import CertifiedMath, BigNum128, LogContext, MathOverflowError
from HSMF import HSMF
from TokenStateBundle import TokenStateBundle, create_token_state_bundle

def test_zero_simulation_compliance():
    """Test that all core files pass Zero-Simulation compliance checks."""
    print('=== Phase 1: Zero-Simulation Compliance Check ===')
    from AST_ZeroSimChecker import AST_ZeroSimChecker
    checker = AST_ZeroSimChecker()
    core_files = ['libs/CertifiedMath.py', 'libs/HSMF.py', 'libs/TokenStateBundle.py']
    all_passed = True
    for file_path in sorted(core_files):
        violations = checker.scan_file(file_path)
        if violations:
            print(f'❌ {file_path} has {len(violations)} violations:')
            for v in sorted(violations):
                print(f'  Line {v.line_number}: {v.violation_type} - {v.message}')
            all_passed = False
        else:
            print(f'✅ {file_path} passed Zero-Simulation compliance check')
    return all_passed

def test_deterministic_behavior():
    """Test that identical inputs produce identical outputs."""
    print('\n=== Phase 2: Deterministic Behavior Verification ===')
    log_list1 = []
    cm1 = CertifiedMath(log_list1)
    result1 = cm1.add(BigNum128.from_string('1.5'), BigNum128.from_string('2.5'), 'test_pqc', {'test': 'metadata'})
    log_list2 = []
    cm2 = CertifiedMath(log_list2)
    result2 = cm2.add(BigNum128.from_string('1.5'), BigNum128.from_string('2.5'), 'test_pqc', {'test': 'metadata'})
    results_identical = result1.value == result2.value
    hashes_identical = cm1.get_log_hash() == cm2.get_log_hash()
    print(f'✅ CertifiedMath deterministic results: {results_identical}')
    print(f'✅ CertifiedMath deterministic logs: {hashes_identical}')
    log_list3 = []
    cm3 = CertifiedMath(log_list3)
    result3 = cm3.add(BigNum128.from_string('3.0'), BigNum128.from_string('4.0'), 'pqc_test_456', {'source': 'QRNG'})
    metadata_propagated = False
    if log_list3:
        entry = log_list3[0]
        if entry.get('pqc_cid') == 'pqc_test_456' and entry.get('quantum_metadata', {}).get('source') == 'QRNG':
            metadata_propagated = True
    print(f'✅ PQC/Quantum metadata propagation: {metadata_propagated}')
    chr_state = {'coherence_metric': '0.95'}
    flx_state = {'scaling_metric': '1.2'}
    psi_sync_state = {'frequency_metric': '0.8'}
    atr_state = {'directional_metric': '0.1'}
    res_state = {'inertial_metric': '0.3'}
    lambda1 = BigNum128.from_string('1.618033988749894848')
    lambda2 = BigNum128.from_string('0.95')
    c_crit = BigNum128.from_string('1.0')
    bundle1 = create_token_state_bundle(chr_state, flx_state, psi_sync_state, atr_state, res_state, lambda1, lambda2, c_crit, 'pqc_1', 1234567890)
    bundle2 = create_token_state_bundle(chr_state, flx_state, psi_sync_state, atr_state, res_state, lambda1, lambda2, c_crit, 'pqc_1', 1234567890)
    hash1 = bundle1.get_deterministic_hash()
    hash2 = bundle2.get_deterministic_hash()
    bundle_hashes_identical = hash1 == hash2
    print(f'✅ TokenStateBundle deterministic hashing: {bundle_hashes_identical}')
    return results_identical and hashes_identical and metadata_propagated and bundle_hashes_identical

def test_error_handling():
    """Test that error conditions are handled correctly."""
    print('\n=== Phase 2: Error Handling Verification ===')
    log_list = []
    cm = CertifiedMath(log_list)
    try:
        result = cm.add(BigNum128(BigNum128.MAX_VALUE), BigNum128(1), 'test_pqc', {})
        overflow_handled = False
    except MathOverflowError:
        overflow_handled = True
    except Exception as e:
        print(f'Unexpected error: {e}')
        overflow_handled = False
    print(f'✅ Overflow error handling: {overflow_handled}')
    return overflow_handled

def test_v13_plan_alignment():
    """Test that implementation aligns with V13 plans."""
    print('\n=== Phase 3: V13 Plan Alignment Verification ===')
    cm = CertifiedMath([])
    required_methods = ['add', 'sub', 'mul', 'div', 'abs', 'gt', 'lt', 'gte', 'lte', 'eq', 'ne', 'sqrt', 'phi_series', 'exp', 'ln', 'pow', 'two_to_the_power']
    api_complete = True
    for method in sorted(required_methods):
        if not hasattr(cm, method):
            print(f'❌ Missing required method: {method}')
            api_complete = False
    print(f'✅ CertifiedMath public API completeness: {api_complete}')
    log_list = []
    cm = CertifiedMath(log_list)
    hsmf = HSMF(cm)
    hsmf_methods = ['validate_action_bundle', '_calculate_I_eff', '_calculate_delta_lambda', '_calculate_delta_h']
    hsmf_complete = True
    for method in sorted(hsmf_methods):
        if not hasattr(hsmf, method):
            print(f'❌ Missing required HSMF method: {method}')
            hsmf_complete = False
    print(f'✅ HSMF method completeness: {hsmf_complete}')
    return api_complete and hsmf_complete

def main():
    """Run all audit verification tests."""
    print('QFS V13 Audit Verification')
    print('=' * 50)
    phase1_pass = test_zero_simulation_compliance()
    phase2_pass = test_deterministic_behavior()
    phase2_error_pass = test_error_handling()
    phase3_pass = test_v13_plan_alignment()
    print('\n' + '=' * 50)
    print('AUDIT VERIFICATION SUMMARY')
    print('=' * 50)
    print(f"Phase 1 - Zero-Simulation Compliance: {('✅ PASS' if phase1_pass else '❌ FAIL')}")
    print(f"Phase 2 - Deterministic Behavior: {('✅ PASS' if phase2_pass else '❌ FAIL')}")
    print(f"Phase 2 - Error Handling: {('✅ PASS' if phase2_error_pass else '❌ FAIL')}")
    print(f"Phase 3 - V13 Plan Alignment: {('✅ PASS' if phase3_pass else '❌ FAIL')}")
    overall_pass = phase1_pass and phase2_pass and phase2_error_pass and phase3_pass
    print(f"\nOverall Audit Status: {('✅ ALL TESTS PASSED' if overall_pass else '❌ SOME TESTS FAILED')}")
    return overall_pass
if __name__ == '__main__':
    success = main()
    raise ZeroSimAbort(0 if success else 1)
