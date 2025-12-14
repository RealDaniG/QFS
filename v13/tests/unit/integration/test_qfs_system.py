"""
Test suite for the QFS System functionality.
"""

import sys
import os

# Add the libs directory to the path

from qfs_system import get_system_audit_hash, clear_all_audit_logs


def test_system_audit_hash():
    """Test system audit hash generation."""
    # Clear any existing audit logs
    clear_all_audit_logs()
    
    # Generate system audit hash with no activity
    system_hash1 = get_system_audit_hash()
    assert isinstance(system_hash1, str)
    assert len(system_hash1) == 64  # SHA-256 hash length
    
    # Generate system audit hash again - should be identical
    system_hash2 = get_system_audit_hash()
    assert system_hash1 == system_hash2
    
    print("[PASS] System audit hash test passed")


def test_system_audit_hash_with_certified_math_logs():
    """Test system audit hash generation with CertifiedMath logs."""
    # Clear any existing audit logs
    clear_all_audit_logs()
    
    # Generate system audit hash with CertifiedMath logs
    certified_math_logs = [
        {
            "log_index": 0,
            "pqc_cid": "test_001",
            "op_name": "add",
            "inputs": {"a": "1.0", "b": "2.0"},
            "result": "3.0"
        },
        {
            "log_index": 1,
            "pqc_cid": "test_001",
            "op_name": "mul",
            "inputs": {"a": "3.0", "b": "4.0"},
            "result": "12.0"
        }
    ]
    
    system_hash1 = get_system_audit_hash(certified_math_logs)
    assert isinstance(system_hash1, str)
    assert len(system_hash1) == 64  # SHA-256 hash length
    
    # Generate system audit hash again with same logs - should be identical
    system_hash2 = get_system_audit_hash(certified_math_logs)
    assert system_hash1 == system_hash2
    
    # Generate system audit hash with different logs - should be different
    different_logs = [
        {
            "log_index": 0,
            "pqc_cid": "test_002",
            "op_name": "sub",
            "inputs": {"a": "5.0", "b": "3.0"},
            "result": "2.0"
        }
    ]
    
    system_hash3 = get_system_audit_hash(different_logs)
    assert system_hash1 != system_hash3
    
    print("[PASS] System audit hash with CertifiedMath logs test passed")


def test_clear_all_audit_logs():
    """Test clearing all audit logs."""
    # This test just verifies the function can be called without error
    clear_all_audit_logs()
    print("[PASS] Clear all audit logs test passed")


def run_all_tests():
    """Run all QFS system tests."""
    print("Running QFS System tests...")
    
    test_system_audit_hash()
    test_system_audit_hash_with_certified_math_logs()
    test_clear_all_audit_logs()
    
    print("All QFS System tests passed!")


if __name__ == "__main__":
    run_all_tests()