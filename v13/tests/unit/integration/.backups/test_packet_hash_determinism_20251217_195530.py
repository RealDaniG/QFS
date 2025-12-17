"""
Test to verify that each DRV_Packet generates a SHA256 hash deterministically from its contents.
"""
import json
import hashlib
try:
    from PQC import generate_keypair
    from DRV_Packet import DRV_Packet, get_drv_packet_audit_log, get_drv_packet_audit_hash, clear_drv_packet_audit_log
    from CertifiedMath import CertifiedMath, BigNum128
except ImportError:
    from PQC import generate_keypair
    from DRV_Packet import DRV_Packet, get_drv_packet_audit_log, get_drv_packet_audit_hash, clear_drv_packet_audit_log
    from CertifiedMath import CertifiedMath, BigNum128

def test_packet_hash_determinism():
    """Test that identical packets generate identical SHA256 hashes."""
    print('Testing packet hash determinism...')
    clear_drv_packet_audit_log()
    tts_timestamp = 1700000000
    sequence = 1
    seed = 'test_seed_12345'
    metadata = {'source': 'hash_test', 'version': '1.0'}
    previous_hash = '0000000000000000000000000000000000000000000000000000000000000000'
    pqc_cid = 'HASH_TEST_001'
    quantum_metadata = {'quantum_source_id': 'QSO-2025-11-16-001', 'vdf_output_hash': 'abcdef1234567890', 'entropy_pool': 'pool_data_12345', 'timestamp': 1700000000}
    packet1 = DRV_Packet(ttsTimestamp=tts_timestamp, sequence=sequence, seed=seed, metadata=metadata, previous_hash=previous_hash, pqc_cid=pqc_cid, quantum_metadata=quantum_metadata)
    hash1 = packet1.get_hash()
    clear_drv_packet_audit_log()
    packet2 = DRV_Packet(ttsTimestamp=tts_timestamp, sequence=sequence, seed=seed, metadata=metadata, previous_hash=previous_hash, pqc_cid=pqc_cid, quantum_metadata=quantum_metadata)
    hash2 = packet2.get_hash()
    assert hash1 == hash2, f'Packet hashes should be identical: {hash1} != {hash2}'
    assert isinstance(hash1, str), 'Hash should be a string'
    assert len(hash1) == 64, f'SHA256 hash should be 64 characters long, got {len(hash1)}'
    print('[PASS] Packet hash determinism test passed')

def test_packet_hash_uniqueness():
    """Test that different packet contents generate different SHA256 hashes."""
    print('Testing packet hash uniqueness...')
    clear_drv_packet_audit_log()
    packet1 = DRV_Packet(ttsTimestamp=1700000000, sequence=1, seed='seed_1', metadata={'source': 'test1'}, previous_hash='0000000000000000000000000000000000000000000000000000000000000000', pqc_cid='UNIQUE_TEST_001')
    hash1 = packet1.get_hash()
    clear_drv_packet_audit_log()
    packet2 = DRV_Packet(ttsTimestamp=1700000001, sequence=1, seed='seed_1', metadata={'source': 'test1'}, previous_hash='0000000000000000000000000000000000000000000000000000000000000000', pqc_cid='UNIQUE_TEST_002')
    hash2 = packet2.get_hash()
    assert hash1 != hash2, f'Packet hashes should be different: {hash1} == {hash2}'
    clear_drv_packet_audit_log()
    packet3 = DRV_Packet(ttsTimestamp=1700000000, sequence=2, seed='seed_1', metadata={'source': 'test1'}, previous_hash='0000000000000000000000000000000000000000000000000000000000000000', pqc_cid='UNIQUE_TEST_003')
    hash3 = packet3.get_hash()
    assert hash1 != hash3, f'Packet hashes should be different: {hash1} == {hash3}'
    assert hash2 != hash3, f'Packet hashes should be different: {hash2} == {hash3}'
    print('[PASS] Packet hash uniqueness test passed')

def test_packet_hash_serialization_consistency():
    """Test that packet hash is consistent with serialization."""
    print('Testing packet hash serialization consistency...')
    clear_drv_packet_audit_log()
    packet = DRV_Packet(ttsTimestamp=1700000000, sequence=1, seed='test_seed_12345', metadata={'source': 'serialization_test', 'version': '1.0'}, previous_hash='1111111111111111111111111111111111111111111111111111111111111111', pqc_cid='SERIAL_TEST_001')
    direct_hash = packet.get_hash()
    serialized = packet.serialize(include_signature=True)
    manual_hash = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
    assert direct_hash == manual_hash, f'Direct hash should match manual hash: {direct_hash} != {manual_hash}'
    print('[PASS] Packet hash serialization consistency test passed')

def test_packet_hash_with_signature():
    """Test that packet hash includes signature when present."""
    print('Testing packet hash with signature...')
    clear_drv_packet_audit_log()
    keypair = generate_keypair(pqc_cid='SIGNATURE_TEST_001')
    private_key = keypair['private_key']
    packet = DRV_Packet(ttsTimestamp=1700000000, sequence=1, seed='test_seed_with_signature', metadata={'source': 'signature_test'}, previous_hash='2222222222222222222222222222222222222222222222222222222222222222', pqc_cid='SIGNATURE_TEST_002')
    hash_before = packet.get_hash()
    packet.sign(private_key, pqc_cid='SIGNATURE_TEST_003')
    hash_after = packet.get_hash()
    assert hash_before != hash_after, f'Hash should change after signing: {hash_before} == {hash_after}'
    clear_drv_packet_audit_log()
    packet2 = DRV_Packet(ttsTimestamp=1700000000, sequence=1, seed='test_seed_with_signature', metadata={'source': 'signature_test'}, previous_hash='2222222222222222222222222222222222222222222222222222222222222222', pqc_cid='SIGNATURE_TEST_004')
    packet2.sign(private_key, pqc_cid='SIGNATURE_TEST_005')
    hash_after2 = packet2.get_hash()
    assert hash_after == hash_after2, f'Signed packet hashes should be identical: {hash_after} != {hash_after2}'
    print('[PASS] Packet hash with signature test passed')

def test_packet_hash_chain_consistency():
    """Test that packet hash chain is consistent."""
    print('Testing packet hash chain consistency...')
    clear_drv_packet_audit_log()
    genesis_packet = DRV_Packet(ttsTimestamp=1700000000, sequence=0, seed='genesis_seed', metadata={'source': 'chain_test'}, previous_hash=None, pqc_cid='CHAIN_TEST_001')
    genesis_hash = genesis_packet.get_hash()
    second_packet = DRV_Packet(ttsTimestamp=1700000001, sequence=1, seed='second_seed', metadata={'source': 'chain_test'}, previous_hash=genesis_hash, pqc_cid='CHAIN_TEST_002')
    assert second_packet.previous_hash == genesis_hash, f'Previous hash should match genesis hash: {second_packet.previous_hash} != {genesis_hash}'
    clear_drv_packet_audit_log()
    genesis_packet2 = DRV_Packet(ttsTimestamp=1700000000, sequence=0, seed='genesis_seed', metadata={'source': 'chain_test'}, previous_hash=None, pqc_cid='CHAIN_TEST_003')
    genesis_hash2 = genesis_packet2.get_hash()
    second_packet2 = DRV_Packet(ttsTimestamp=1700000001, sequence=1, seed='second_seed', metadata={'source': 'chain_test'}, previous_hash=genesis_hash2, pqc_cid='CHAIN_TEST_004')
    assert genesis_hash == genesis_hash2, f'Genesis hashes should be identical: {genesis_hash} != {genesis_hash2}'
    assert second_packet.get_hash() == second_packet2.get_hash(), f'Second packet hashes should be identical'
    assert second_packet.previous_hash == second_packet2.previous_hash, f'Previous hashes should be identical'
    print('[PASS] Packet hash chain consistency test passed')

def run_all_tests():
    """Run all packet hash determinism tests."""
    print('Running Packet Hash Determinism Tests...')
    print('=' * 50)
    test_packet_hash_determinism()
    test_packet_hash_uniqueness()
    test_packet_hash_serialization_consistency()
    test_packet_hash_with_signature()
    test_packet_hash_chain_consistency()
    print('=' * 50)
    print('[SUCCESS] All Packet Hash Determinism tests passed!')
if __name__ == '__main__':
    run_all_tests()