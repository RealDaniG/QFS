"""
Test suite for QFS V13 serialization, log export, and hash replay functionality.
"""
import json
import hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'libs'))
try:
    from PQC import generate_keypair, sign_data, verify_signature, get_pqc_audit_log, get_pqc_audit_hash, clear_pqc_audit_log
    from DRV_Packet import DRV_Packet, get_drv_packet_audit_log, get_drv_packet_audit_hash, clear_drv_packet_audit_log
    from CertifiedMath import CertifiedMath, BigNum128
except ImportError:
    import PQC
    import DRV_Packet
    import CertifiedMath
    from PQC import generate_keypair, sign_data, verify_signature, get_pqc_audit_log, get_pqc_audit_hash, clear_pqc_audit_log
    from DRV_Packet import DRV_Packet, get_drv_packet_audit_log, get_drv_packet_audit_hash, clear_drv_packet_audit_log
    from CertifiedMath import CertifiedMath, BigNum128

def test_deterministic_serialization():
    """Test that identical data produces identical serialization."""
    print('Testing deterministic serialization...')
    data1 = {'a': 1, 'b': 2, 'c': {'nested': 'value'}}
    data2 = {'b': 2, 'a': 1, 'c': {'nested': 'value'}}
    serialized1 = json.dumps(data1, sort_keys=True, separators=(',', ':'))
    serialized2 = json.dumps(data2, sort_keys=True, separators=(',', ':'))
    assert serialized1 == serialized2, 'Serialization should be canonical'
    print('[PASS] Deterministic serialization test passed')

def test_pqc_audit_log_export():
    """Test PQC audit log export and hashing."""
    print('Testing PQC audit log export and hashing...')
    clear_pqc_audit_log()
    keypair = generate_keypair(pqc_cid='AUDIT_001', quantum_metadata={'test': 'pqc'})
    private_key = keypair['private_key']
    public_key = keypair['public_key']
    data = {'message': 'test', 'value': 123}
    signature = sign_data(data, private_key, pqc_cid='AUDIT_002', quantum_metadata={'test': 'sign'})
    is_valid = verify_signature(data, signature, public_key, pqc_cid='AUDIT_003', quantum_metadata={'test': 'verify'})
    audit_log = get_pqc_audit_log()
    assert len(audit_log) == 3, f'Expected 3 audit entries, got {len(audit_log)}'
    assert audit_log[0]['operation'] == 'keygen'
    assert audit_log[0]['pqc_cid'] == 'AUDIT_001'
    assert audit_log[1]['operation'] == 'sign'
    assert audit_log[1]['pqc_cid'] == 'AUDIT_002'
    assert audit_log[2]['operation'] == 'verify'
    assert audit_log[2]['pqc_cid'] == 'AUDIT_003'
    audit_hash = get_pqc_audit_hash()
    assert isinstance(audit_hash, str), 'Audit hash should be a string'
    assert len(audit_hash) == 64, f'Audit hash should be 64 characters, got {len(audit_hash)}'
    print('[PASS] PQC audit log export test passed')

def test_drv_packet_audit_log_export():
    """Test DRV_Packet audit log export and hashing."""
    print('Testing DRV_Packet audit log export and hashing...')
    clear_drv_packet_audit_log()
    keypair = generate_keypair(pqc_cid='DRV_AUDIT_001')
    private_key = keypair['private_key']
    public_key = keypair['public_key']
    packet = DRV_Packet(ttsTimestamp=1700000000, sequence=1, seed='test_seed', metadata={'test': 'drv'}, previous_hash='0000000000000000000000000000000000000000000000000000000000000000', pqc_cid='DRV_AUDIT_002', quantum_metadata={'test': 'create'})
    packet.sign(private_key, pqc_cid='DRV_AUDIT_003', quantum_metadata={'test': 'sign'})
    is_valid = packet.verify_signature(public_key, pqc_cid='DRV_AUDIT_004', quantum_metadata={'test': 'verify'})
    validation_result = packet.is_valid(public_key, None, pqc_cid='DRV_AUDIT_005', quantum_metadata={'test': 'validate'})
    audit_log = get_drv_packet_audit_log()
    assert len(audit_log) >= 4, f'Expected at least 4 audit entries, got {len(audit_log)}'
    operations = [entry['operation'] for entry in audit_log]
    assert 'create' in operations
    assert 'sign' in operations
    assert 'verify' in operations
    assert 'validate' in operations
    audit_hash = get_drv_packet_audit_hash()
    assert isinstance(audit_hash, str), 'Audit hash should be a string'
    assert len(audit_hash) == 64, f'Audit hash should be 64 characters, got {len(audit_hash)}'
    print('[PASS] DRV_Packet audit log export test passed')

def test_certified_math_log_export():
    """Test CertifiedMath log export and hashing."""
    print('Testing CertifiedMath log export and hashing...')
    log = []
    math = CertifiedMath(log)
    a = BigNum128.from_string('10.0')
    b = BigNum128.from_string('5.0')
    sum_result = math.add(a, b, pqc_cid='MATH_AUDIT_001')
    mul_result = math.mul(sum_result, a, pqc_cid='MATH_AUDIT_002')
    sqrt_result = math.sqrt(mul_result, pqc_cid='MATH_AUDIT_003')
    assert len(log) == 3, f'Expected 3 log entries, got {len(log)}'
    assert log[0]['pqc_cid'] == 'MATH_AUDIT_001'
    assert log[1]['pqc_cid'] == 'MATH_AUDIT_002'
    assert log[2]['pqc_cid'] == 'MATH_AUDIT_003'
    log_hash = math.get_log_hash()
    assert isinstance(log_hash, str), 'Log hash should be a string'
    assert len(log_hash) == 64, f'Log hash should be 64 characters, got {len(log_hash)}'
    log2 = []
    math2 = CertifiedMath(log2)
    a2 = BigNum128.from_string('10.0')
    b2 = BigNum128.from_string('5.0')
    sum_result2 = math2.add(a2, b2, pqc_cid='MATH_AUDIT_001')
    mul_result2 = math2.mul(sum_result2, a2, pqc_cid='MATH_AUDIT_002')
    sqrt_result2 = math2.sqrt(mul_result2, pqc_cid='MATH_AUDIT_003')
    log_hash2 = math2.get_log_hash()
    assert log_hash == log_hash2, 'Identical operations should produce identical log hashes'
    print('[PASS] CertifiedMath log export test passed')

def test_system_hash_replay():
    """Test system hash generation and replay capability."""
    print('Testing system hash generation and replay...')
    clear_pqc_audit_log()
    clear_drv_packet_audit_log()
    keypair = generate_keypair(pqc_cid='REPLAY_001')
    private_key = keypair['private_key']
    public_key = keypair['public_key']
    data = {'test': 'replay', 'value': 42}
    signature = sign_data(data, private_key, pqc_cid='REPLAY_002')
    is_valid = verify_signature(data, signature, public_key, pqc_cid='REPLAY_003')
    packet = DRV_Packet(ttsTimestamp=1700000000, sequence=1, seed='replay_seed', metadata={'test': 'replay'}, pqc_cid='REPLAY_004')
    packet.sign(private_key, pqc_cid='REPLAY_005')
    is_valid_packet = packet.verify_signature(public_key, pqc_cid='REPLAY_006')
    math_log = []
    math = CertifiedMath(math_log)
    x = BigNum128.from_string('2.5')
    y = BigNum128.from_string('3.0')
    result = math.add(x, y, pqc_cid='REPLAY_007')
    pqc_hash = get_pqc_audit_hash()
    drv_hash = get_drv_packet_audit_hash()
    math_hash = math.get_log_hash()
    system_components = {'pqc_audit_hash': pqc_hash, 'drv_audit_hash': drv_hash, 'math_log_hash': math_hash}
    system_serialized = json.dumps(system_components, sort_keys=True, separators=(',', ':'))
    system_hash = hashlib.sha256(system_serialized.encode('utf-8')).hexdigest()
    assert isinstance(system_hash, str), 'System hash should be a string'
    assert len(system_hash) == 64, f'System hash should be 64 characters, got {len(system_hash)}'
    print('[PASS] System hash replay test passed')

def run_all_tests():
    """Run all serialization and audit tests."""
    print('Running Serialization and Audit Tests...')
    print('=' * 50)
    test_deterministic_serialization()
    test_pqc_audit_log_export()
    test_drv_packet_audit_log_export()
    test_certified_math_log_export()
    test_system_hash_replay()
    print('=' * 50)
    print('[SUCCESS] All Serialization and Audit tests passed!')
if __name__ == '__main__':
    run_all_tests()
