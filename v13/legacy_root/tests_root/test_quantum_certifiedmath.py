"""
Test file for CertifiedMath with Quantum Integration
"""
import sys
import os

# Add the libs directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

from CertifiedMath import CertifiedMath, BigNum128

def test_quantum_metadata_logging():
    """Test that CertifiedMath correctly logs quantum metadata"""
    print("Testing CertifiedMath with Quantum Metadata...")
    
    # Create test BigNum128 values
    a = CertifiedMath.from_string("1000000000000000000")  # 1.0 in fixed-point
    b = CertifiedMath.from_string("2000000000000000000")  # 2.0 in fixed-point
    
    # Create quantum metadata
    quantum_metadata = {
        "quantum_source_id": "qrng-001",
        "quantum_entropy": "a1b2c3d4e5f6",
        "vdf_output_hash": "vdf-hash-7890"
    }
    
    # Perform addition with quantum metadata
    result = CertifiedMath.add(a, b, "test-pqc-cid-001", quantum_metadata)
    print(f"Addition result: {result.value / 10**18}")
    
    # Check the log
    log_hash = CertifiedMath.get_log_hash()
    print(f"Log hash: {log_hash}")
    
    # Export log to see the quantum metadata
    CertifiedMath.export_log("test_quantum_log.json")
    print("Log exported to test_quantum_log.json")
    
    # Verify quantum metadata was logged
    import json
    with open("test_quantum_log.json", "r") as f:
        log_data = json.load(f)
    
    if log_data and "quantum_metadata" in log_data[0]:
        print("Quantum metadata successfully logged:")
        print(f"  Source ID: {log_data[0]['quantum_metadata']['quantum_source_id']}")
        print(f"  Entropy: {log_data[0]['quantum_metadata']['quantum_entropy']}")
        print(f"  VDF Hash: {log_data[0]['quantum_metadata']['vdf_output_hash']}")
    else:
        print("ERROR: Quantum metadata not found in log")
    
    print("Test completed successfully!")

def test_fixed_point_safety():
    """Test fixed-point safety features"""
    print("\nTesting Fixed-Point Safety...")
    
    # Test overflow in addition
    print("Testing addition overflow...")
    try:
        a = BigNum128(BigNum128.MAX_VALUE)
        b = BigNum128(1)
        result = CertifiedMath.add(a, b)
        print("ERROR: Overflow should have been detected!")
    except OverflowError as e:
        print(f"Correctly caught overflow: {e}")
    
    # Test underflow in subtraction
    print("Testing subtraction underflow...")
    try:
        a = BigNum128(BigNum128.MIN_VALUE)
        b = BigNum128(1)
        result = CertifiedMath.sub(a, b)
        print("ERROR: Underflow should have been detected!")
    except OverflowError as e:
        print(f"Correctly caught underflow: {e}")
    
    # Test division by zero
    print("Testing division by zero...")
    try:
        a = BigNum128(1000000000000000000)
        b = BigNum128(0)
        result = CertifiedMath.div(a, b)
        print("ERROR: Division by zero should have been detected!")
    except ZeroDivisionError as e:
        print(f"Correctly caught division by zero: {e}")
    
    print("Fixed-point safety tests completed!")

if __name__ == "__main__":
    test_quantum_metadata_logging()
    test_fixed_point_safety()