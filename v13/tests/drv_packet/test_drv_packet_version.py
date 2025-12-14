"""
Test suite for DRV_Packet version compatibility checking.
"""

import sys
import os

# Add the libs directory to the path

# Import DRV_Packet
try:
    from DRV_Packet import DRV_Packet
except ImportError:
    # Try alternative import path
    import DRV_Packet
    DRV_Packet = getattr(DRV_Packet, 'DRV_Packet', DRV_Packet)


def test_valid_version():
    """Test DRV packet creation with valid version."""
    print("Testing DRV packet creation with valid version...")
    
    valid_data = {
        "version": "1.0",
        "ttsTimestamp": 1700000000,
        "sequence": 1,
        "seed": "test_seed",
        "previous_hash": "0000000000000000000000000000000000000000000000000000000000000000"
    }
    
    packet = DRV_Packet.from_dict(valid_data)
    assert packet.version == "1.0"
    print("[PASS] Valid version test passed")


def test_invalid_version():
    """Test DRV packet creation with invalid version."""
    print("Testing DRV packet creation with invalid version...")
    
    invalid_data = {
        "version": "0.9",
        "ttsTimestamp": 1700000000,
        "sequence": 1,
        "seed": "test_seed",
        "previous_hash": "0000000000000000000000000000000000000000000000000000000000000000"
    }
    
    try:
        packet = DRV_Packet.from_dict(invalid_data)
        assert False, "Should have raised ValueError for invalid version"
    except ValueError as e:
        assert "Unsupported DRV_Packet version" in str(e)
        print("[PASS] Invalid version test passed")


def test_missing_version():
    """Test DRV packet creation with missing version (should default to 1.0)."""
    print("Testing DRV packet creation with missing version...")
    
    missing_data = {
        "ttsTimestamp": 1700000000,
        "sequence": 1,
        "seed": "test_seed",
        "previous_hash": "0000000000000000000000000000000000000000000000000000000000000000"
    }
    
    packet = DRV_Packet.from_dict(missing_data)
    assert packet.version == "1.0"
    print("[PASS] Missing version test passed")


def test_future_version():
    """Test DRV packet creation with future version."""
    print("Testing DRV packet creation with future version...")
    
    future_data = {
        "version": "2.0",
        "ttsTimestamp": 1700000000,
        "sequence": 1,
        "seed": "test_seed",
        "previous_hash": "0000000000000000000000000000000000000000000000000000000000000000"
    }
    
    try:
        packet = DRV_Packet.from_dict(future_data)
        assert False, "Should have raised ValueError for future version"
    except ValueError as e:
        assert "Unsupported DRV_Packet version" in str(e)
        print("[PASS] Future version test passed")


def run_all_tests():
    """Run all DRV packet version tests."""
    print("Running DRV Packet Version Tests...")
    print("=" * 50)
    
    test_valid_version()
    test_invalid_version()
    test_missing_version()
    test_future_version()
    
    print("=" * 50)
    print("[SUCCESS] All DRV Packet Version tests passed!")


if __name__ == "__main__":
    run_all_tests()