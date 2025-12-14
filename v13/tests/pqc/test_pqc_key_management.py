"""
Test suite for PQC key management functionality including export/import and zeroization.
"""

import sys
import os
import json
import base64

# Add the libs directory to the path

# Import the PQC functions
try:
    from PQC import generate_keypair, export_key_to_hex, export_key_to_base64, export_key_to_json, import_key_from_hex, import_key_from_base64, import_keypair_from_json, zeroize_private_key, secure_zeroize_keypair
except ImportError:
    # Try alternative import path
    import PQC
    generate_keypair = PQC.generate_keypair
    export_private_key = PQC.export_private_key
    export_public_key = PQC.export_public_key
    import_private_key = PQC.import_private_key
    import_public_key = PQC.import_public_key
    zeroize_private_key = PQC.zeroize_private_key


def test_key_export_import_hex():
    """Test key export and import using hex format."""
    print("Testing key export/import using hex format...")
    
    # Generate a keypair
    keypair = generate_keypair(pqc_cid="KEY_TEST_001")
    original_private_key = keypair["private_key"]
    original_public_key = keypair["public_key"]
    
    # Export keys in hex format
    private_key_hex = export_key_to_hex(original_private_key)
    public_key_hex = export_key_to_hex(original_public_key)
    
    # Verify hex format
    assert isinstance(private_key_hex, str), "Private key hex should be a string"
    assert isinstance(public_key_hex, str), "Public key hex should be a string"
    assert all(c in '0123456789abcdef' for c in private_key_hex.lower()), "Private key hex should contain only hex characters"
    assert all(c in '0123456789abcdef' for c in public_key_hex.lower()), "Public key hex should contain only hex characters"
    
    # Import keys from hex format
    imported_private_key = import_key_from_hex(private_key_hex)
    imported_public_key = import_key_from_hex(public_key_hex)
    
    # Verify imported keys match original keys
    assert imported_private_key == original_private_key, "Imported private key should match original"
    assert imported_public_key == original_public_key, "Imported public key should match original"
    
    print("[PASS] Key export/import using hex format test passed")


def test_key_export_import_base64():
    """Test key export and import using base64 format."""
    print("Testing key export/import using base64 format...")
    
    # Generate a keypair
    keypair = generate_keypair(pqc_cid="KEY_TEST_002")
    original_private_key = keypair["private_key"]
    original_public_key = keypair["public_key"]
    
    # Export keys in base64 format
    private_key_b64 = export_key_to_base64(original_private_key)
    public_key_b64 = export_key_to_base64(original_public_key)
    
    # Verify base64 format
    assert isinstance(private_key_b64, str), "Private key base64 should be a string"
    assert isinstance(public_key_b64, str), "Public key base64 should be a string"
    
    # Import keys from base64 format
    imported_private_key = import_key_from_base64(private_key_b64)
    imported_public_key = import_key_from_base64(public_key_b64)
    
    # Verify imported keys match original keys
    assert imported_private_key == original_private_key, "Imported private key should match original"
    assert imported_public_key == original_public_key, "Imported public key should match original"
    
    print("[PASS] Key export/import using base64 format test passed")


def test_key_export_import_json():
    """Test key export and import using JSON format."""
    print("Testing key export/import using JSON format...")
    
    # Generate a keypair
    keypair = generate_keypair(pqc_cid="KEY_TEST_003")
    original_private_key = keypair["private_key"]
    original_public_key = keypair["public_key"]
    
    # Export keys in JSON format
    keypair_json = export_key_to_json(original_private_key, original_public_key)
    
    # Verify JSON format
    assert isinstance(keypair_json, str), "Keypair JSON should be a string"
    
    # Parse JSON to verify structure
    keypair_data = json.loads(keypair_json)
    
    assert "private_key" in keypair_data, "Keypair JSON should contain 'private_key' field"
    assert "public_key" in keypair_data, "Keypair JSON should contain 'public_key' field"
    assert "algorithm" in keypair_data, "Keypair JSON should contain 'algorithm' field"
    
    # Import keys from JSON format
    imported_keypair = import_keypair_from_json(keypair_json)
    imported_private_key = imported_keypair['private_key']
    imported_public_key = imported_keypair['public_key']
    
    # Verify imported keys match original keys
    assert imported_private_key == original_private_key, "Imported private key should match original"
    assert imported_public_key == original_public_key, "Imported public key should match original"
    
    print("[PASS] Key export/import using JSON format test passed")


def test_key_zeroization():
    """Test key zeroization functionality."""
    print("Testing key zeroization functionality...")
    
    # Generate a keypair
    keypair = generate_keypair(pqc_cid="KEY_TEST_004")
    original_private_key = keypair["private_key"]
    
    # Verify original key is not zero
    assert len(original_private_key) > 0, "Original private key should not be empty"
    assert any(b != 0 for b in original_private_key), "Original private key should contain non-zero bytes"
    
    # Zeroize the private key
    zeroized_key = zeroize_private_key(original_private_key)
    
    # Verify zeroized key is all zeros
    assert len(zeroized_key) == len(original_private_key), "Zeroized key should have same length as original"
    assert all(b == 0 for b in zeroized_key), "Zeroized key should contain only zero bytes"
    
    print("[PASS] Key zeroization test passed")


def test_key_format_validation():
    """Test key format validation."""
    print("Testing key format validation...")
    
    # Generate a keypair
    keypair = generate_keypair(pqc_cid="KEY_TEST_005")
    private_key = keypair["private_key"]
    public_key = keypair["public_key"]
    
    # Test invalid hex data for import
    try:
        import_key_from_hex("invalid_hex_data")
        assert False, "Should have raised ValueError for invalid hex data"
    except ValueError:
        print("[PASS] Invalid hex data validation passed")
    
    # Test invalid base64 data for import
    try:
        import_key_from_base64("invalid_base64!")
        assert False, "Should have raised ValueError for invalid base64 data"
    except ValueError:
        print("[PASS] Invalid base64 data validation passed")


def run_all_tests():
    """Run all PQC key management tests."""
    print("Running PQC Key Management Tests...")
    print("=" * 50)
    
    test_key_export_import_hex()
    test_key_export_import_base64()
    test_key_export_import_json()
    test_key_zeroization()
    test_key_format_validation()
    
    print("=" * 50)
    print("[SUCCESS] All PQC Key Management tests passed!")


if __name__ == "__main__":
    run_all_tests()