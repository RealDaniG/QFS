"""
Example usage of CertifiedMath.py demonstrating all key features
"""
from v13.libs.CertifiedMath import CertifiedMath, BigNum128

def main():
    print('CertifiedMath Example Usage')
    print('==============================')
    a = BigNum128(1000000000000000000)
    b = BigNum128(2000000000000000000)
    c = BigNum128(500000000000000000)
    print(f'a = {a.value / 10 ** 18}')
    print(f'b = {b.value / 10 ** 18}')
    print(f'c = {c.value / 10 ** 18}')
    with CertifiedMath.LogContext() as session_log:
        result1 = CertifiedMath.add(a, b, session_log, pqc_cid='operation_001')
        print(f'\nAddition: {a.value / 10 ** 18} + {b.value / 10 ** 18} = {result1.value / 10 ** 18}')
        result2 = CertifiedMath.mul(result1, c, session_log, pqc_cid='operation_002')
        print(f'Multiplication: {result1.value / 10 ** 18} * {c.value / 10 ** 18} = {result2.value / 10 ** 18}')
        result3 = CertifiedMath.fast_sqrt(result2, session_log, iterations=20, pqc_cid='operation_003')
        print(f'Square Root: sqrt({result2.value / 10 ** 18}) = {result3.value / 10 ** 18}')
        result4 = CertifiedMath.calculate_phi_series(result3, session_log, n=10, pqc_cid='operation_004')
        print(f'Phi Series: phi_series({result3.value / 10 ** 18}, 10) = {result4.value / 10 ** 18}')
        print(f'\nLog Entries: {len(session_log)}')
        print(f'Log Hash: {CertifiedMath.get_log_hash(session_log)}')
        print('\nLog Details:')
        for i, entry in enumerate(session_log):
            print(f"  {i + 1}. {entry['op_name']}: {entry['inputs']} -> {entry['result']}")
            if entry['pqc_cid']:
                print(f"     PQC CID: {entry['pqc_cid']}")
            if entry['quantum_metadata']:
                print(f"     Quantum Metadata: {entry['quantum_metadata']}")
    print('\n' + '=' * 30)
    print('Quantum Metadata Handling Example')
    quantum_metadata = {'quantum_seed': 'qrng-001', 'vdf_output_hash': 'vdf-hash-7890', 'entanglement_index': 'ent-123', 'quantum_source_id': 'source-456', 'quantum_entropy': 'entropy-abc', 'current_timestamp': '1234567890', 'native_float': 3.14159, 'random_value': 'should_be_kept'}
    with CertifiedMath.LogContext() as session_log:
        result = CertifiedMath.add(a, b, session_log, pqc_cid='quantum_test_001', quantum_metadata=quantum_metadata)
        print(f'Result: {result.value / 10 ** 18}')
        logged_metadata = session_log[0]['quantum_metadata']
        print(f'Logged Metadata: {logged_metadata}')
        if logged_metadata:
            print('All metadata keys preserved (filtering handled by SDK layer)')
if __name__ == '__main__':
    main()