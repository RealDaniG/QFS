import json
try:
    from PQC import generate_keypair, sign_data, verify_signature
except ImportError:
    import PQC
    generate_keypair = PQC.generate_keypair
    sign_data = PQC.sign_data
    verify_signature = PQC.verify_signature

def test_pqc_sign_verify():
    """Test basic PQC signing and verification."""
    keypair = generate_keypair(pqc_cid='TEST_001')
    private_key = keypair['private_key']
    public_key = keypair['public_key']
    data = {'message': 'Test message for PQC', 'timestamp': 1700000000, 'value': 1000000000000000000}
    signature = sign_data(data, private_key, pqc_cid='TEST_002')
    is_valid = verify_signature(data, signature, public_key, pqc_cid='TEST_003')
    assert is_valid, 'Signature verification failed'
    print('[PASS] Basic PQC signing and verification test passed')

def test_pqc_tamper_detection():
    """Test that PQC detects tampered data."""
    keypair = generate_keypair(pqc_cid='TEST_004')
    private_key = keypair['private_key']
    public_key = keypair['public_key']
    original_data = {'message': 'Original message', 'timestamp': 1700000000, 'value': 1000000000000000000}
    signature = sign_data(original_data, private_key, pqc_cid='TEST_005')
    tampered_data = {**original_data, 'value': 2000000000000000000}
    is_valid = verify_signature(tampered_data, signature, public_key, pqc_cid='TEST_006')
    assert not is_valid, 'Tampered data should not pass verification'
    print('[PASS] PQC tamper detection test passed')

def test_pqc_serialization():
    """Test that PQC correctly serializes data."""
    data1 = {'a': 1, 'b': 2}
    data2 = {'b': 2, 'a': 1}
    serialized1 = json.dumps(data1, sort_keys=True, separators=(',', ':'))
    serialized2 = json.dumps(data2, sort_keys=True, separators=(',', ':'))
    assert serialized1 == serialized2, 'Serialization should be canonical'
    print('[PASS] PQC serialization test passed')

def test_pqc_signature_format():
    """Test PQC signature format validation."""
    keypair = generate_keypair(pqc_cid='TEST_007')
    private_key = keypair['private_key']
    public_key = keypair['public_key']
    data = {'test': 'data'}
    signature = sign_data(data, private_key, pqc_cid='TEST_008')
    assert isinstance(signature, bytes), 'Signature should be bytes'
    assert len(signature) > 0, 'Signature should not be empty'
    is_valid = verify_signature(data, signature, public_key, pqc_cid='TEST_009')
    assert is_valid, 'Signature should be valid'
    print('[PASS] PQC signature format validation test passed')

def test_pqc_audit_trail():
    """Test PQC audit trail functionality."""
    from PQC import clear_pqc_audit_log, get_pqc_audit_log, get_pqc_audit_hash
    clear_pqc_audit_log()
    keypair = generate_keypair(pqc_cid='AUDIT_001', quantum_metadata={'test': 'metadata'})
    private_key = keypair['private_key']
    public_key = keypair['public_key']
    data = {'test': 'data'}
    signature = sign_data(data, private_key, pqc_cid='AUDIT_002', quantum_metadata={'test': 'metadata'})
    is_valid = verify_signature(data, signature, public_key, pqc_cid='AUDIT_003', quantum_metadata={'test': 'metadata'})
    audit_log = get_pqc_audit_log()
    assert len(audit_log) == 3, f'Expected 3 audit entries, got {len(audit_log)}'
    assert audit_log[0]['operation'] == 'keygen'
    assert audit_log[0]['pqc_cid'] == 'AUDIT_001'
    assert audit_log[0]['quantum_metadata'] == {'test': 'metadata'}
    assert audit_log[1]['operation'] == 'sign'
    assert audit_log[1]['pqc_cid'] == 'AUDIT_002'
    assert audit_log[1]['quantum_metadata'] == {'test': 'metadata'}
    assert audit_log[2]['operation'] == 'verify'
    assert audit_log[2]['pqc_cid'] == 'AUDIT_003'
    assert audit_log[2]['quantum_metadata'] == {'test': 'metadata'}
    audit_hash = get_pqc_audit_hash()
    assert isinstance(audit_hash, str), 'Audit hash should be a string'
    assert len(audit_hash) == 64, f'Audit hash should be 64 characters, got {len(audit_hash)}'
    print('[PASS] PQC audit trail test passed')

def run_all_tests():
    """Run all PQC tests."""
    print('Running PQC tests...')
    test_pqc_sign_verify()
    test_pqc_tamper_detection()
    test_pqc_serialization()
    test_pqc_signature_format()
    test_pqc_audit_trail()
    print('All PQC tests passed!')
if __name__ == '__main__':
    run_all_tests()