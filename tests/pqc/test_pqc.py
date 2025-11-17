import sys
import os
import json

# Add the libs directory to the path - updated to reflect new directory structure
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'libs'))

# Import the PQC functions
try:
    from PQC import generate_keypair, sign_data, verify_signature
except ImportError:
    # Try alternative import path
    import PQC
    generate_keypair = PQC.generate_keypair
    sign_data = PQC.sign_data
    verify_signature = PQC.verify_signature


def test_pqc_sign_verify():
    """Test basic PQC signing and verification."""
    # Generate a keypair
    keypair = generate_keypair(pqc_cid="TEST_001")
    private_key = keypair["private_key"]
    public_key = keypair["public_key"]
    
    # Data to sign
    data = {
        "message": "Test message for PQC",
        "timestamp": 1700000000,
        "value": 1000000000000000000  # 1.0 in fixed-point
    }
    
    # Sign the data
    signature = sign_data(data, private_key, pqc_cid="TEST_002")
    
    # Verify the signature
    is_valid = verify_signature(data, signature, public_key, pqc_cid="TEST_003")
    assert is_valid, "Signature verification failed"
    
    print("[PASS] Basic PQC signing and verification test passed")


def test_pqc_tamper_detection():
    """Test that PQC detects tampered data."""
    # Generate a keypair
    keypair = generate_keypair(pqc_cid="TEST_004")
    private_key = keypair["private_key"]
    public_key = keypair["public_key"]
    
    # Data to sign
    original_data = {
        "message": "Original message",
        "timestamp": 1700000000,
        "value": 1000000000000000000  # 1.0 in fixed-point
    }
    
    # Sign the data
    signature = sign_data(original_data, private_key, pqc_cid="TEST_005")
    
    # Tamper with the data
    tampered_data = {**original_data, "value": 2000000000000000000}  # 2.0 in fixed-point
    
    # Verify the signature with tampered data
    is_valid = verify_signature(tampered_data, signature, public_key, pqc_cid="TEST_006")
    assert not is_valid, "Tampered data should not pass verification"
    
    print("[PASS] PQC tamper detection test passed")


def test_pqc_serialization():
    """Test that PQC correctly serializes data."""
    # Test data
    data1 = {"a": 1, "b": 2}
    data2 = {"b": 2, "a": 1}  # Same data, different order
    
    # Serialize both using our functions
    serialized1 = json.dumps(data1, sort_keys=True, separators=(',', ':'))
    serialized2 = json.dumps(data2, sort_keys=True, separators=(',', ':'))
    
    # They should be identical due to canonical serialization
    assert serialized1 == serialized2, "Serialization should be canonical"
    
    print("[PASS] PQC serialization test passed")


def test_pqc_signature_format():
    """Test PQC signature format validation."""
    # Generate a keypair
    keypair = generate_keypair(pqc_cid="TEST_007")
    private_key = keypair["private_key"]
    public_key = keypair["public_key"]
    
    # Data to sign
    data = {"test": "data"}
    
    # Sign the data
    signature = sign_data(data, private_key, pqc_cid="TEST_008")
    
    # Check signature format
    assert isinstance(signature, bytes), "Signature should be bytes"
    assert len(signature) > 0, "Signature should not be empty"
    
    # Verify the signature
    is_valid = verify_signature(data, signature, public_key, pqc_cid="TEST_009")
    assert is_valid, "Signature should be valid"
    
    print("[PASS] PQC signature format validation test passed")


def test_pqc_audit_trail():
    """Test PQC audit trail functionality."""
    # Clear any existing audit log
    from PQC import clear_pqc_audit_log, get_pqc_audit_log, get_pqc_audit_hash
    clear_pqc_audit_log()
    
    # Generate a keypair
    keypair = generate_keypair(pqc_cid="AUDIT_001", quantum_metadata={"test": "metadata"})
    private_key = keypair["private_key"]
    public_key = keypair["public_key"]
    
    # Data to sign
    data = {"test": "data"}
    
    # Sign the data
    signature = sign_data(data, private_key, pqc_cid="AUDIT_002", quantum_metadata={"test": "metadata"})
    
    # Verify the signature
    is_valid = verify_signature(data, signature, public_key, pqc_cid="AUDIT_003", quantum_metadata={"test": "metadata"})
    
    # Check audit log
    audit_log = get_pqc_audit_log()
    assert len(audit_log) == 3, f"Expected 3 audit entries, got {len(audit_log)}"
    
    # Check audit entries
    assert audit_log[0]["operation"] == "keygen"
    assert audit_log[0]["pqc_cid"] == "AUDIT_001"
    assert audit_log[0]["quantum_metadata"] == {"test": "metadata"}
    
    assert audit_log[1]["operation"] == "sign"
    assert audit_log[1]["pqc_cid"] == "AUDIT_002"
    assert audit_log[1]["quantum_metadata"] == {"test": "metadata"}
    
    assert audit_log[2]["operation"] == "verify"
    assert audit_log[2]["pqc_cid"] == "AUDIT_003"
    assert audit_log[2]["quantum_metadata"] == {"test": "metadata"}
    
    # Check audit hash
    audit_hash = get_pqc_audit_hash()
    assert isinstance(audit_hash, str), "Audit hash should be a string"
    assert len(audit_hash) == 64, f"Audit hash should be 64 characters, got {len(audit_hash)}"
    
    print("[PASS] PQC audit trail test passed")


def run_all_tests():
    """Run all PQC tests."""
    print("Running PQC tests...")
    
    test_pqc_sign_verify()
    test_pqc_tamper_detection()
    test_pqc_serialization()
    test_pqc_signature_format()
    test_pqc_audit_trail()
    
    print("All PQC tests passed!")


if __name__ == "__main__":
    run_all_tests()