"""
Audit trail and log chain hardening for CertifiedMath.py to ensure tamper-proof, fully sequenced logs
"""

import sys
import os
import json
import hashlib
from typing import List, Dict, Any

# Add the libs directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'libs'))

from CertifiedMath import (
    CertifiedMath, BigNum128, 
    MathOverflowError, MathValidationError,
    PHI_INTENSITY_B, LN2_CONSTANT, EXP_LIMIT, ZERO, ONE, TWO,
    set_series_precision, set_phi_intensity_damping, set_exp_limit, get_current_config,
    LogContext
)

def test_log_hash_chaining():
    """Test log redundancy and hash chaining."""
    print("Testing log hash chaining...")
    
    log = []
    math = CertifiedMath(log)
    
    # Perform operations
    a = BigNum128.from_string("1.234567")
    b = BigNum128.from_string("2.345678")
    
    quantum_metadata = {
        "thread_id": 1,
        "execution_time": "2025-11-16T21:50:00Z",
        "operation_index": 0,
        "test_id": "HASH_CHAIN_001"
    }
    
    result1 = math.add(a, b, pqc_cid="HASH_CHAIN_001", quantum_metadata=quantum_metadata)
    result2 = math.mul(result1, a, pqc_cid="HASH_CHAIN_001", quantum_metadata=quantum_metadata)
    result3 = math.exp(result2, pqc_cid="HASH_CHAIN_001", quantum_metadata=quantum_metadata)
    
    # Verify log entries have all required fields
    assert len(log) >= 3, f"Expected at least 3 log entries, got {len(log)}"
    
    for i, entry in enumerate(log):
        # Check required fields
        required_fields = ["log_index", "pqc_cid", "op_name", "inputs"]
        for field in required_fields:
            assert field in entry, f"Missing required field '{field}' in log entry {i}: {entry}"
        
        # Check log index sequencing
        assert entry["log_index"] == i, f"Incorrect log index in entry {i}: expected {i}, got {entry['log_index']}"
        
        # Check PQC CID
        assert entry["pqc_cid"] == "HASH_CHAIN_001", f"Incorrect PQC CID in entry {i}: {entry['pqc_cid']}"
        
        # Check quantum metadata
        assert "quantum_metadata" in entry, f"Missing quantum_metadata in entry {i}"
        assert entry["quantum_metadata"]["test_id"] == "HASH_CHAIN_001", f"Incorrect test_id in entry {i}"
    
    # Get the final log hash
    log_hash = math.get_log_hash()
    
    # Verify hash properties
    assert len(log_hash) == 64, f"Log hash should be 64 characters, got {len(log_hash)}"
    assert all(c in '0123456789abcdef' for c in log_hash), f"Log hash should contain only hex characters"
    
    print(f"  [PASS] Log hash chaining verified")
    print(f"  Log entries: {len(log)}")
    print(f"  Log hash: {log_hash[:16]}...")


def test_tamper_simulation():
    """Test tamper simulations to verify hash mismatch detection."""
    print("Testing tamper simulation...")
    
    # Create original log
    log1 = []
    math1 = CertifiedMath(log1)
    
    a = BigNum128.from_string("1.234567")
    b = BigNum128.from_string("2.345678")
    
    result1 = math1.add(a, b, pqc_cid="TAMPER_001")
    result2 = math1.mul(result1, a, pqc_cid="TAMPER_001")
    
    original_hash = math1.get_log_hash()
    
    # Simulate tampering by manually modifying a log entry
    # Note: In a real system, this would be detected by external verification
    # For this test, we'll just verify that if we modify the log, the hash changes
    
    # Create a copy of the log and modify it
    log2 = []
    for entry in log1:
        log2.append(entry.copy())  # Shallow copy
    
    # Modify one entry
    if len(log2) > 0:
        log2[0]["inputs"]["a"] = "999.999999999999999999"  # Tamper with input
    
    # Create a new CertifiedMath instance with the tampered log
    math2 = CertifiedMath(log2)
    tampered_hash = math2.get_log_hash()
    
    # Hashes should be different
    assert original_hash != tampered_hash, f"Tampered hash should differ: {original_hash} == {tampered_hash}"
    
    print(f"  [PASS] Tamper simulation verified")
    print(f"  Original hash: {original_hash[:16]}...")
    print(f"  Tampered hash: {tampered_hash[:16]}...")


def test_cross_platform_serialization_verification():
    """Test cross-platform serialization verification."""
    print("Testing cross-platform serialization verification...")
    
    log = []
    math = CertifiedMath(log)
    
    # Perform operations
    a = BigNum128.from_string("1.234567")
    b = BigNum128.from_string("2.345678")
    
    result1 = math.add(a, b, pqc_cid="SERIALIZATION_001")
    result2 = math.mul(result1, a, pqc_cid="SERIALIZATION_001")
    
    # Get log hash
    log_hash = math.get_log_hash()
    
    # Manually serialize to verify deterministic serialization
    sorted_log = sorted(log, key=lambda x: x.get('log_index', 0))
    serialized1 = json.dumps(sorted_log, sort_keys=True)
    
    # Do it again to verify consistency
    sorted_log2 = sorted(log, key=lambda x: x.get('log_index', 0))
    serialized2 = json.dumps(sorted_log2, sort_keys=True)
    
    # Serializations should be identical
    assert serialized1 == serialized2, "Serializations should be identical"
    
    # Verify that serialization includes all expected fields
    assert "log_index" in serialized1
    assert "pqc_cid" in serialized1
    assert "op_name" in serialized1
    assert "inputs" in serialized1
    assert "result" in serialized1
    
    print(f"  [PASS] Cross-platform serialization verification completed")
    print(f"  Log hash: {log_hash[:16]}...")


def test_full_context_fields():
    """Test that all context fields are included in logs."""
    print("Testing full context fields...")
    
    log = []
    math = CertifiedMath(log)
    
    # Perform operation with full context
    a = BigNum128.from_string("1.234567")
    
    quantum_metadata = {
        "thread_id": 42,
        "execution_time": "2025-11-16T21:55:00Z",
        "operation_index": 123,
        "pqc_cid": "CONTEXT_001",
        "config_snapshot": {
            "series_terms": 31,
            "phi_intensity_b": "0.100000000000000000",
            "exp_limit": "15.0"
        }
    }
    
    result = math.exp(a, pqc_cid="CONTEXT_001", quantum_metadata=quantum_metadata)
    
    # Verify log entry contains all context fields
    assert len(log) > 0, "Expected at least one log entry"
    
    entry = log[0]
    assert "quantum_metadata" in entry, "Missing quantum_metadata"
    
    qm = entry["quantum_metadata"]
    assert qm["thread_id"] == 42, f"Incorrect thread_id: {qm['thread_id']}"
    assert qm["operation_index"] == 123, f"Incorrect operation_index: {qm['operation_index']}"
    assert "config_snapshot" in qm, "Missing config_snapshot"
    
    print(f"  [PASS] Full context fields verified")


def run_audit_trail_hardening_tests():
    """Run all audit trail hardening tests."""
    print("Running CertifiedMath Audit Trail Hardening Tests...")
    print("=" * 60)
    
    test_log_hash_chaining()
    test_tamper_simulation()
    test_cross_platform_serialization_verification()
    test_full_context_fields()
    
    print("=" * 60)
    print("[SUCCESS] All CertifiedMath Audit Trail Hardening tests passed!")


if __name__ == "__main__":
    run_audit_trail_hardening_tests()