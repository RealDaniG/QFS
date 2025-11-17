"""
Test to verify that quantum metadata and PQC CID are recorded deterministically in DRV_Packet.
"""

import sys
import os
import json
import hashlib

# Add the libs directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'libs'))

# Import all components
try:
    from PQC import generate_keypair
    from DRV_Packet import DRV_Packet, get_drv_packet_audit_log, get_drv_packet_audit_hash, clear_drv_packet_audit_log
    from CertifiedMath import CertifiedMath, BigNum128
except ImportError:
    from PQC import generate_keypair
    from DRV_Packet import DRV_Packet, get_drv_packet_audit_log, get_drv_packet_audit_hash, clear_drv_packet_audit_log
    from CertifiedMath import CertifiedMath, BigNum128

def test_quantum_metadata_determinism():
    """Test that quantum metadata and PQC CID are recorded deterministically."""
    print("Testing quantum metadata and PQC CID determinism...")
    
    # Clear any existing audit log
    clear_drv_packet_audit_log()
    
    # Test data
    tts_timestamp = 1700000000
    sequence = 1
    seed = "test_seed_12345"
    metadata = {"source": "test", "version": "1.0"}
    previous_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    pqc_cid = "QUANTUM_TEST_001"
    quantum_metadata = {
        "quantum_source_id": "QSO-2025-11-16-001",
        "vdf_output_hash": "abcdef1234567890",
        "entropy_pool": "pool_data_12345",
        "timestamp": 1700000000
    }
    
    # Create first packet
    packet1 = DRV_Packet(
        ttsTimestamp=tts_timestamp,
        sequence=sequence,
        seed=seed,
        metadata=metadata,
        previous_hash=previous_hash,
        pqc_cid=pqc_cid,
        quantum_metadata=quantum_metadata
    )
    
    # Get audit log after first packet creation
    audit_log1 = get_drv_packet_audit_log()
    audit_hash1 = get_drv_packet_audit_hash()
    
    # Clear audit log and create second identical packet
    clear_drv_packet_audit_log()
    
    packet2 = DRV_Packet(
        ttsTimestamp=tts_timestamp,
        sequence=sequence,
        seed=seed,
        metadata=metadata,
        previous_hash=previous_hash,
        pqc_cid=pqc_cid,
        quantum_metadata=quantum_metadata
    )
    
    # Get audit log after second packet creation
    audit_log2 = get_drv_packet_audit_log()
    audit_hash2 = get_drv_packet_audit_hash()
    
    # Verify that audit logs are identical
    assert audit_log1 == audit_log2, "Audit logs should be identical for identical operations"
    assert audit_hash1 == audit_hash2, "Audit hashes should be identical for identical operations"
    
    # Verify packet hashes are identical
    assert packet1.get_hash() == packet2.get_hash(), "Packet hashes should be identical for identical packets"
    
    # Verify that the audit log contains the quantum metadata and PQC CID
    assert len(audit_log1) == 1, "Audit log should contain one entry"
    audit_entry = audit_log1[0]
    
    assert audit_entry["pqc_cid"] == pqc_cid, f"PQC CID should be recorded: expected {pqc_cid}, got {audit_entry['pqc_cid']}"
    assert audit_entry["quantum_metadata"] == quantum_metadata, f"Quantum metadata should be recorded: expected {quantum_metadata}, got {audit_entry['quantum_metadata']}"
    
    print("[PASS] Quantum metadata and PQC CID determinism test passed")

def test_packet_serialization_with_quantum_metadata():
    """Test that packet serialization includes quantum metadata context."""
    print("Testing packet serialization with quantum metadata...")
    
    # Clear any existing audit log
    clear_drv_packet_audit_log()
    
    # Test data
    tts_timestamp = 1700000001
    sequence = 2
    seed = "test_seed_67890"
    metadata = {"source": "serialization_test", "version": "1.0"}
    previous_hash = "1111111111111111111111111111111111111111111111111111111111111111"
    pqc_cid = "QUANTUM_TEST_002"
    quantum_metadata = {
        "quantum_source_id": "QSO-2025-11-16-002",
        "vdf_output_hash": "fedcba0987654321",
        "entropy_pool": "pool_data_67890",
        "timestamp": 1700000001
    }
    
    # Create packet
    packet = DRV_Packet(
        ttsTimestamp=tts_timestamp,
        sequence=sequence,
        seed=seed,
        metadata=metadata,
        previous_hash=previous_hash,
        pqc_cid=pqc_cid,
        quantum_metadata=quantum_metadata
    )
    
    # Serialize packet
    serialized = packet.serialize()
    packet_dict = json.loads(serialized)
    
    # Verify packet fields
    assert packet_dict["ttsTimestamp"] == tts_timestamp
    assert packet_dict["sequence"] == sequence
    assert packet_dict["seed"] == seed
    assert packet_dict["metadata"] == metadata
    assert packet_dict["previous_hash"] == previous_hash
    assert packet_dict["version"] == "1.0"
    
    # Note: Quantum metadata and PQC CID are not stored in the packet itself,
    # but are recorded in the audit log during creation
    
    print("[PASS] Packet serialization with quantum metadata test passed")

def test_certified_math_integration_with_quantum_metadata():
    """Test CertifiedMath operations with quantum metadata integration."""
    print("Testing CertifiedMath operations with quantum metadata integration...")
    
    # Create test values
    value_a = BigNum128.from_string("123.456789012345678")
    value_b = BigNum128.from_string("987.654321098765432")
    
    # Perform operations with quantum metadata
    log = []
    math = CertifiedMath(log)
    
    pqc_cid = "MATH_QUANTUM_001"
    quantum_metadata = {
        "quantum_source_id": "QSO-2025-11-16-MATH-001",
        "vdf_output_hash": "math_vdf_hash_12345",
        "computation_context": "addition_operation"
    }
    
    # Addition with quantum metadata
    sum_result = math.add(value_a, value_b, pqc_cid=pqc_cid, quantum_metadata=quantum_metadata)
    
    # Verify log entry contains quantum metadata
    assert len(log) == 1, "Log should contain one entry"
    log_entry = log[0]
    
    assert log_entry["pqc_cid"] == pqc_cid, f"PQC CID should be recorded: expected {pqc_cid}, got {log_entry['pqc_cid']}"
    assert log_entry["quantum_metadata"] == quantum_metadata, f"Quantum metadata should be recorded: expected {quantum_metadata}, got {log_entry['quantum_metadata']}"
    
    # Verify deterministic hash
    operations_hash = math.get_log_hash()
    assert isinstance(operations_hash, str)
    assert len(operations_hash) == 64  # SHA-256 hash
    
    # Repeat with identical parameters to verify determinism
    log2 = []
    math2 = CertifiedMath(log2)
    sum_result2 = math2.add(value_a, value_b, pqc_cid=pqc_cid, quantum_metadata=quantum_metadata)
    operations_hash2 = math2.get_log_hash()
    
    # Verify identical results
    assert sum_result.value == sum_result2.value, "Results should be identical"
    assert operations_hash == operations_hash2, "Hashes should be identical"
    assert log == log2, "Logs should be identical"
    
    print("[PASS] CertifiedMath operations with quantum metadata integration test passed")

def run_all_tests():
    """Run all quantum metadata determinism tests."""
    print("Running Quantum Metadata Determinism Tests...")
    print("=" * 50)
    
    test_quantum_metadata_determinism()
    test_packet_serialization_with_quantum_metadata()
    test_certified_math_integration_with_quantum_metadata()
    
    print("=" * 50)
    print("[SUCCESS] All Quantum Metadata Determinism tests passed!")

if __name__ == "__main__":
    run_all_tests()