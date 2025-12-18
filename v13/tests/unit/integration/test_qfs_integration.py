"""
Integration test suite for QFS V13 compliance.
Tests all components working together including PQC, DRV_Packet, and CertifiedMath.
"""
import json
try:
    from PQC import generate_keypair, sign_data, verify_signature, export_key_to_hex, import_key_from_hex
    from DRV_Packet import DRV_Packet, ValidationResult, ValidationErrorCode
    from CertifiedMath import CertifiedMath, BigNum128
except ImportError:
    from PQC import generate_keypair, sign_data, verify_signature, export_key_to_hex, import_key_from_hex
    from DRV_Packet import DRV_Packet, ValidationResult, ValidationErrorCode
    from CertifiedMath import CertifiedMath, BigNum128

def test_full_qfs_workflow():
    """Test the full QFS V13 workflow with all components."""
    print('Testing full QFS V13 workflow...')
    keypair = generate_keypair(pqc_cid='INTEGRATION_001')
    private_key = keypair['private_key']
    public_key = keypair['public_key']
    genesis_packet = DRV_Packet(ttsTimestamp=1700000000, sequence=0, seed='genesis_seed_12345', metadata={'source': 'integration_test', 'version': '1.0'}, previous_hash=None, pqc_cid='INTEGRATION_002')
    genesis_packet.sign(private_key, pqc_cid='INTEGRATION_003')
    genesis_validation = genesis_packet.is_valid(public_key, None, pqc_cid='INTEGRATION_004')
    assert genesis_validation.is_valid, f'Genesis packet validation failed: {genesis_validation.error_message}'
    second_packet = DRV_Packet(ttsTimestamp=1700000001, sequence=1, seed='second_seed_67890', metadata={'source': 'integration_test', 'version': '1.0'}, previous_hash=genesis_packet.get_hash(), pqc_cid='INTEGRATION_005')
    second_packet.sign(private_key, pqc_cid='INTEGRATION_006')
    second_validation = second_packet.is_valid(public_key, genesis_packet, pqc_cid='INTEGRATION_007')
    assert second_validation.is_valid, f'Second packet validation failed: {second_validation.error_message}'
    third_packet = DRV_Packet(ttsTimestamp=1700000002, sequence=2, seed='third_seed_abcde', metadata={'source': 'integration_test', 'version': '1.0'}, previous_hash=second_packet.get_hash(), pqc_cid='INTEGRATION_008')
    third_packet.sign(private_key, pqc_cid='INTEGRATION_009')
    third_validation = third_packet.is_valid(public_key, second_packet, pqc_cid='INTEGRATION_010')
    assert third_validation.is_valid, f'Third packet validation failed: {third_validation.error_message}'
    print('[PASS] Full QFS workflow test passed')

def test_certified_math_in_qfs():
    """Test CertifiedMath operations within QFS workflow."""
    print('Testing CertifiedMath operations within QFS workflow...')
    value_a = BigNum128.from_string('123.456789012345678')
    value_b = BigNum128.from_string('987.654321098765432')
    log = []
    math = CertifiedMath(log)
    sum_result = math.add(value_a, value_b, pqc_cid='MATH_001')
    product_result = math.mul(sum_result, value_a, pqc_cid='MATH_002')
    sqrt_result = math.sqrt(product_result, pqc_cid='MATH_003')
    assert len(log) == 3
    assert log[0]['pqc_cid'] == 'MATH_001'
    assert log[1]['pqc_cid'] == 'MATH_002'
    assert log[2]['pqc_cid'] == 'MATH_003'
    operations_hash = math.get_log_hash()
    assert isinstance(operations_hash, str)
    assert len(operations_hash) == 64
    print('[PASS] CertifiedMath operations test passed')

def test_tampered_data_detection():
    """Test that tampered data is properly detected."""
    print('Testing tampered data detection...')
    keypair = generate_keypair(pqc_cid='TAMPER_001')
    private_key = keypair['private_key']
    public_key = keypair['public_key']
    original_data = {'amount': '1000000000000000000', 'recipient': 'user123', 'timestamp': 1700000000}
    signature = sign_data(original_data, private_key, pqc_cid='TAMPER_002')
    is_valid = verify_signature(original_data, signature, public_key, pqc_cid='TAMPER_003')
    assert is_valid, 'Original signature should be valid'
    tampered_data = {**original_data, 'amount': '2000000000000000000'}
    is_valid_tampered = verify_signature(tampered_data, signature, public_key, pqc_cid='TAMPER_004')
    assert not is_valid_tampered, 'Tampered data should not pass verification'
    print('[PASS] Tampered data detection test passed')

def test_invalid_chain_detection():
    """Test that invalid packet chains are properly detected."""
    print('Testing invalid chain detection...')
    keypair = generate_keypair(pqc_cid='CHAIN_001')
    private_key = keypair['private_key']
    public_key = keypair['public_key']
    packet1 = DRV_Packet(ttsTimestamp=1700000000, sequence=0, seed='packet1_seed', metadata={'test': 'chain'})
    packet1.sign(private_key, pqc_cid='CHAIN_002')
    packet2 = DRV_Packet(ttsTimestamp=1700000001, sequence=1, seed='packet2_seed', metadata={'test': 'chain'}, previous_hash='0000000000000000000000000000000000000000000000000000000000000000')
    packet2.sign(private_key, pqc_cid='CHAIN_003')
    validation_result = packet2.is_valid(public_key, packet1, pqc_cid='CHAIN_004')
    assert not validation_result.is_valid
    assert validation_result.error_code == ValidationErrorCode.INVALID_CHAIN
    assert 'Chain hash mismatch' in validation_result.error_message
    print('[PASS] Invalid chain detection test passed')

def test_sequence_validation():
    """Test sequence number validation."""
    print('Testing sequence validation...')
    keypair = generate_keypair(pqc_cid='SEQUENCE_001')
    private_key = keypair['private_key']
    public_key = keypair['public_key']
    packet1 = DRV_Packet(ttsTimestamp=1700000000, sequence=0, seed='packet1_seed')
    packet1.sign(private_key, pqc_cid='SEQUENCE_002')
    packet2 = DRV_Packet(ttsTimestamp=1700000001, sequence=5, seed='packet2_seed', previous_hash=packet1.get_hash())
    packet2.sign(private_key, pqc_cid='SEQUENCE_003')
    validation_result = packet2.is_valid(public_key, packet1, pqc_cid='SEQUENCE_004')
    assert not validation_result.is_valid
    assert validation_result.error_code == ValidationErrorCode.INVALID_SEQUENCE
    assert 'Sequence non-monotonic' in validation_result.error_message
    print('[PASS] Sequence validation test passed')

def test_key_export_import_integration():
    """Test key export/import integration with signing."""
    print('Testing key export/import integration...')
    original_keypair = generate_keypair(pqc_cid='EXPORT_001')
    original_private_key = original_keypair['private_key']
    original_public_key = original_keypair['public_key']
    private_key_hex = export_key_to_hex(original_private_key)
    public_key_hex = export_key_to_hex(original_public_key)
    imported_private_key = import_key_from_hex(private_key_hex)
    imported_public_key = import_key_from_hex(public_key_hex)
    assert imported_private_key == original_private_key
    assert imported_public_key == original_public_key
    data = {'test': 'data', 'value': 100}
    signature = sign_data(data, imported_private_key, pqc_cid='EXPORT_002')
    is_valid = verify_signature(data, signature, imported_public_key, pqc_cid='EXPORT_003')
    assert is_valid, 'Signature should be valid with imported keys'
    print('[PASS] Key export/import integration test passed')

def run_all_tests():
    """Run all integration tests."""
    print('Running QFS V13 Integration Tests...')
    print('=' * 50)
    test_full_qfs_workflow()
    test_certified_math_in_qfs()
    test_tampered_data_detection()
    test_invalid_chain_detection()
    test_sequence_validation()
    test_key_export_import_integration()
    print('=' * 50)
    print('[SUCCESS] All QFS V13 Integration tests passed!')
if __name__ == '__main__':
    run_all_tests()
