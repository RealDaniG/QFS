from CertifiedMath import CertifiedMath, BigNum128, MathOverflowError, MathValidationError

def test_comprehensive_log_consistency():
    """Comprehensive test for log consistency, sequencing, and determinism."""
    print('=== Comprehensive Log Consistency Test ===')
    print('\n1. Testing basic operation sequence determinism...')
    log_list1 = []
    cm1 = CertifiedMath(log_list1)
    a1 = BigNum128.from_string('10.5')
    b1 = BigNum128.from_string('5.25')
    result1_1 = cm1.add(a1, b1, 'test_pqc_1', {'source': 'test'})
    result2_1 = cm1.mul(result1_1, BigNum128.from_string('0.5'), 'test_pqc_2', {'source': 'test'})
    result3_1 = cm1.exp(result2_1, 'test_pqc_3', {'source': 'test'})
    hash1 = cm1.get_log_hash()
    log_list2 = []
    cm2 = CertifiedMath(log_list2)
    a2 = BigNum128.from_string('10.5')
    b2 = BigNum128.from_string('5.25')
    result1_2 = cm2.add(a2, b2, 'test_pqc_1', {'source': 'test'})
    result2_2 = cm2.mul(result1_2, BigNum128.from_string('0.5'), 'test_pqc_2', {'source': 'test'})
    result3_2 = cm2.exp(result2_2, 'test_pqc_3', {'source': 'test'})
    hash2 = cm2.get_log_hash()
    result1_deterministic = result1_1.value == result1_2.value
    result2_deterministic = result2_1.value == result2_2.value
    result3_deterministic = result3_1.value == result3_2.value
    hash_deterministic = hash1 == hash2
    print(f'  Result1 determinism: {result1_deterministic}')
    print(f'  Result2 determinism: {result2_deterministic}')
    print(f'  Result3 determinism: {result3_deterministic}')
    print(f'  Hash determinism: {hash_deterministic}')
    print('\n2. Testing log entry structure...')
    structure_valid = False
    pqc_correct = False
    op_name_correct = False
    inputs_correct = False
    result_correct = False
    quantum_metadata_present = False
    if log_list1:
        entry = log_list1[0]
        required_keys = ['log_index', 'pqc_cid', 'op_name', 'inputs', 'result']
        structure_valid = all((key in entry for key in required_keys))
        pqc_correct = entry.get('pqc_cid') == 'test_pqc_1'
        op_name_correct = entry.get('op_name') == 'add'
        inputs_correct = 'a' in entry.get('inputs', {}) and 'b' in entry.get('inputs', {})
        result_correct = entry.get('result') is not None
        quantum_metadata_present = 'quantum_metadata' in entry and entry['quantum_metadata'] == {'source': 'test'}
        print(f'  Required keys present: {structure_valid}')
        print(f'  PQC CID correct: {pqc_correct}')
        print(f'  Operation name correct: {op_name_correct}')
        print(f'  Inputs structure correct: {inputs_correct}')
        print(f'  Result present: {result_correct}')
        print(f'  Quantum metadata present: {quantum_metadata_present}')
    print('\n3. Testing sequential log indexing...')
    log_indices = [entry.get('log_index') for entry in log_list1]
    expected_indices = list(range(len(log_list1)))
    sequential_indexing = log_indices == expected_indices
    print(f"  Log indices: {log_indices[:10]}{('...' if len(log_indices) > 10 else '')}")
    print(f'  Sequential indexing: {sequential_indexing}')
    print('\n4. Testing PQC/Quantum metadata propagation...')
    metadata_consistent = True
    for entry in sorted(log_list1):
        if 'quantum_metadata' not in entry or entry['quantum_metadata'] != {'source': 'test'}:
            metadata_consistent = False
            break
    print(f'  Metadata consistency: {metadata_consistent}')
    print('\n5. Testing edge cases...')
    none_pqc_handled = False
    none_metadata_handled = False
    log_list3 = []
    cm3 = CertifiedMath(log_list3)
    a3 = BigNum128.from_string('3.0')
    b3 = BigNum128.from_string('4.0')
    result_none = cm3.add(a3, b3, None, None)
    if log_list3:
        entry_none = log_list3[0]
        none_pqc_handled = entry_none.get('pqc_cid') is None
        none_metadata_handled = entry_none.get('quantum_metadata') is None
        print(f'  None PQC CID handled: {none_pqc_handled}')
        print(f'  None quantum metadata handled: {none_metadata_handled}')
    print('\n6. Testing error handling...')
    log_list4 = []
    cm4 = CertifiedMath(log_list4)
    try:
        a4 = BigNum128.from_string('10.0')
        b4 = BigNum128.from_string('0.0')
        result_error = cm4.div(a4, b4, 'error_test', {'test': 'div_by_zero'})
        error_logged = False
    except MathValidationError:
        error_logged = len(log_list4) == 0
    print(f'  Error not logged on failure: {error_logged}')
    print('\n7. Testing transcendental functions...')
    transcendental_logged = False
    sqrt_correct = False
    ln_correct = False
    phi_correct = False
    log_list5 = []
    cm5 = CertifiedMath(log_list5)
    x = BigNum128.from_string('0.5')
    result_sqrt = cm5.sqrt(x, 'sqrt_test', {'func': 'sqrt'})
    result_ln = cm5.ln(x, 'ln_test', {'func': 'ln'})
    result_phi = cm5.phi_series(x, 'phi_test', {'func': 'phi_series'})
    transcendental_logged = len(log_list5) > 3
    print(f'  Transcendental functions logged: {transcendental_logged}')
    if log_list5:
        sqrt_entries = [e for e in log_list5 if e.get('op_name') in ['sqrt', 'sqrt_final']]
        ln_entries = [e for e in log_list5 if e.get('op_name') in ['ln', 'ln_final']]
        phi_entries = [e for e in log_list5 if e.get('op_name') in ['phi_series', 'phi_series_final']]
        sqrt_correct = len(sqrt_entries) > 0
        ln_correct = len(ln_entries) > 0
        phi_correct = len(phi_entries) > 0
        print(f'  Sqrt operation logged correctly: {sqrt_correct}')
        print(f'  Ln operation logged correctly: {ln_correct}')
        print(f'  Phi series operation logged correctly: {phi_correct}')
    print('\n=== Test Summary ===')
    all_tests_passed = result1_deterministic and result2_deterministic and result3_deterministic and hash_deterministic and structure_valid and pqc_correct and op_name_correct and inputs_correct and result_correct and quantum_metadata_present and sequential_indexing and metadata_consistent and none_pqc_handled and none_metadata_handled and error_logged and transcendental_logged and sqrt_correct and ln_correct and phi_correct
    print(f'All tests passed: {all_tests_passed}')
    return all_tests_passed
if __name__ == '__main__':
    test_comprehensive_log_consistency()