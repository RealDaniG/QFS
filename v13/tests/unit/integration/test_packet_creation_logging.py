"""
Test to verify that packet creation is logged deterministically for cross-check with SDK.
"""
import json
import hashlib
try:
    from PQC import generate_keypair
    from DRV_Packet import DRV_Packet, get_drv_packet_audit_log, get_drv_packet_audit_hash, clear_drv_packet_audit_log, ValidationResult, ValidationErrorCode
    from CertifiedMath import CertifiedMath, BigNum128
except ImportError:
    from PQC import generate_keypair
    from DRV_Packet import DRV_Packet, get_drv_packet_audit_log, get_drv_packet_audit_hash, clear_drv_packet_audit_log, ValidationResult, ValidationErrorCode
    from CertifiedMath import CertifiedMath, BigNum128

def test_packet_creation_logging():
    """Test that packet creation is logged deterministically."""
    print('Testing packet creation logging...')
    clear_drv_packet_audit_log()
    tts_timestamp = 1700000000
    sequence = 1
    seed = 'test_seed_12345'
    metadata = {'source': 'logging_test', 'version': '1.0'}
    previous_hash = '0000000000000000000000000000000000000000000000000000000000000000'
    pqc_cid = 'LOG_TEST_001'
    quantum_metadata = {'quantum_source_id': 'QSO-2025-11-16-001', 'vdf_output_hash': 'abcdef1234567890', 'entropy_pool': 'pool_data_12345', 'timestamp': 1700000000}
    packet = DRV_Packet(ttsTimestamp=tts_timestamp, sequence=sequence, seed=seed, metadata=metadata, previous_hash=previous_hash, pqc_cid=pqc_cid, quantum_metadata=quantum_metadata)
    audit_log = get_drv_packet_audit_log()
    assert len(audit_log) == 1, f'Audit log should contain one entry, got {len(audit_log)}'
    entry = audit_log[0]
    assert entry['operation'] == 'create', f"Operation should be 'create', got {entry['operation']}"
    assert entry['pqc_cid'] == pqc_cid, f"PQC CID should match, got {entry['pqc_cid']}"
    assert entry['quantum_metadata'] == quantum_metadata, f'Quantum metadata should match'
    details = entry['details']
    assert details['ttsTimestamp'] == tts_timestamp
    assert details['sequence'] == sequence
    assert details['seed'] == seed
    assert details['metadata'] == metadata
    assert details['previous_hash'] == previous_hash
    print('  [PASS] Packet creation logging structure verified')

def test_deterministic_audit_log():
    """Test that identical packet creations produce identical audit logs."""
    print('Testing deterministic audit log...')
    tts_timestamp = 1700000000
    sequence = 1
    seed = 'test_seed_12345'
    metadata = {'source': 'determinism_test', 'version': '1.0'}
    previous_hash = '0000000000000000000000000000000000000000000000000000000000000000'
    pqc_cid = 'DETERMINISM_TEST_001'
    quantum_metadata = {'quantum_source_id': 'QSO-2025-11-16-001', 'vdf_output_hash': 'abcdef1234567890', 'entropy_pool': 'pool_data_12345', 'timestamp': 1700000000}
    clear_drv_packet_audit_log()
    packet1 = DRV_Packet(ttsTimestamp=tts_timestamp, sequence=sequence, seed=seed, metadata=metadata, previous_hash=previous_hash, pqc_cid=pqc_cid, quantum_metadata=quantum_metadata)
    audit_log1 = get_drv_packet_audit_log()
    audit_hash1 = get_drv_packet_audit_hash()
    clear_drv_packet_audit_log()
    packet2 = DRV_Packet(ttsTimestamp=tts_timestamp, sequence=sequence, seed=seed, metadata=metadata, previous_hash=previous_hash, pqc_cid=pqc_cid, quantum_metadata=quantum_metadata)
    audit_log2 = get_drv_packet_audit_log()
    audit_hash2 = get_drv_packet_audit_hash()
    assert audit_log1 == audit_log2, 'Audit logs should be identical for identical operations'
    assert audit_hash1 == audit_hash2, 'Audit hashes should be identical for identical operations'
    print('  [PASS] Deterministic audit log verified')

def test_audit_log_serialization():
    """Test that audit log serialization is deterministic."""
    print('Testing audit log serialization...')
    clear_drv_packet_audit_log()
    packet = DRV_Packet(ttsTimestamp=1700000000, sequence=1, seed='serialization_test', metadata={'test': 'serialization'}, previous_hash='1111111111111111111111111111111111111111111111111111111111111111', pqc_cid='SERIAL_TEST_001')
    audit_log = get_drv_packet_audit_log()
    audit_hash = get_drv_packet_audit_hash()
    serialized_log = json.dumps(audit_log, sort_keys=True, separators=(',', ':'))
    manual_hash = hashlib.sha256(serialized_log.encode('utf-8')).hexdigest()
    assert audit_hash == manual_hash, f'Audit hash should match manual hash: {audit_hash} != {manual_hash}'
    print('  [PASS] Audit log serialization verified')

def test_cross_check_with_sdk_compatibility():
    """Test that audit log format is compatible for cross-check with SDK."""
    print('Testing cross-check with SDK compatibility...')
    clear_drv_packet_audit_log()
    packet = DRV_Packet(ttsTimestamp=1700000000, sequence=1, seed='sdk_compatibility_test', metadata={'source': 'sdk_test', 'version': '1.0', 'test_id': 'CROSS_CHECK_001'}, previous_hash='2222222222222222222222222222222222222222222222222222222222222222', pqc_cid='SDK_TEST_001', quantum_metadata={'quantum_source_id': 'QSO-2025-11-16-SDK-001', 'vdf_output_hash': 'sdk_vdf_hash_1234567890', 'entropy_pool': 'sdk_entropy_pool_data', 'timestamp': 1700000000, 'sdk_version': '1.0.0'})
    audit_log = get_drv_packet_audit_log()
    assert len(audit_log) == 1
    entry = audit_log[0]
    required_fields = ['operation', 'timestamp', 'details', 'pqc_cid', 'quantum_metadata']
    for field in sorted(required_fields):
        assert field in entry, f"Required field '{field}' missing from audit entry"
    details = entry['details']
    required_details = ['ttsTimestamp', 'sequence', 'seed', 'metadata', 'previous_hash']
    for field in sorted(required_details):
        assert field in details, f"Required detail field '{field}' missing from audit entry details"
    reconstructed_packet = DRV_Packet(ttsTimestamp=details['ttsTimestamp'], sequence=details['sequence'], seed=details['seed'], metadata=details['metadata'], previous_hash=details['previous_hash'])
    assert reconstructed_packet.ttsTimestamp == packet.ttsTimestamp
    assert reconstructed_packet.sequence == packet.sequence
    assert reconstructed_packet.seed == packet.seed
    assert reconstructed_packet.metadata == packet.metadata
    assert reconstructed_packet.previous_hash == packet.previous_hash
    print('  [PASS] SDK cross-check compatibility verified')

def test_audit_log_chain_validation():
    """Test that audit log includes chain validation operations."""
    print('Testing audit log chain validation...')
    keypair = generate_keypair(pqc_cid='CHAIN_LOG_001')
    private_key = keypair['private_key']
    public_key = keypair['public_key']
    clear_drv_packet_audit_log()
    genesis_packet = DRV_Packet(ttsTimestamp=1700000000, sequence=0, seed='genesis', pqc_cid='CHAIN_LOG_002')
    second_packet = DRV_Packet(ttsTimestamp=1700000001, sequence=1, seed='second', previous_hash=genesis_packet.get_hash(), pqc_cid='CHAIN_LOG_003')
    genesis_packet.sign(private_key, pqc_cid='CHAIN_LOG_004')
    second_packet.sign(private_key, pqc_cid='CHAIN_LOG_005')
    validation_result = second_packet.is_valid(public_key, genesis_packet, pqc_cid='CHAIN_LOG_006')
    audit_log = get_drv_packet_audit_log()
    operations = [entry['operation'] for entry in audit_log]
    expected_operations = ['create', 'create', 'sign', 'sign', 'validate_chain']
    for op in sorted(expected_operations):
        assert op in operations, f"Expected operation '{op}' not found in audit log"
    print('  [PASS] Audit log chain validation verified')

def test_audit_log_clearing():
    """Test that audit log can be cleared and starts fresh."""
    print('Testing audit log clearing...')
    clear_drv_packet_audit_log()
    audit_log = get_drv_packet_audit_log()
    assert len(audit_log) == 0, f'Audit log should be empty after clearing, got {len(audit_log)}'
    packet = DRV_Packet(ttsTimestamp=1700000000, sequence=1, seed='clear_test', pqc_cid='CLEAR_TEST_001')
    audit_log = get_drv_packet_audit_log()
    assert len(audit_log) == 1, f'Audit log should have one entry, got {len(audit_log)}'
    clear_drv_packet_audit_log()
    audit_log = get_drv_packet_audit_log()
    assert len(audit_log) == 0, f'Audit log should be empty after clearing, got {len(audit_log)}'
    print('  [PASS] Audit log clearing verified')

def run_all_tests():
    """Run all packet creation logging tests."""
    print('Running Packet Creation Logging Tests...')
    print('=' * 50)
    test_packet_creation_logging()
    test_deterministic_audit_log()
    test_audit_log_serialization()
    test_cross_check_with_sdk_compatibility()
    test_audit_log_chain_validation()
    test_audit_log_clearing()
    print('=' * 50)
    print('[SUCCESS] All Packet Creation Logging tests passed!')
if __name__ == '__main__':
    run_all_tests()
