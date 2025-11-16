#!/usr/bin/env python3
"""
Example usage of CertifiedMath.py demonstrating all key features
"""

import sys
import os

# Add the libs directory to the path so we can import CertifiedMath
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from libs.CertifiedMath import CertifiedMath, BigNum128

def main():
    print("CertifiedMath Example Usage")
    print("=" * 30)
    
    # Create some fixed-point numbers (1.0 and 2.0)
    a = CertifiedMath.from_string("1000000000000000000")  # 1.0
    b = CertifiedMath.from_string("2000000000000000000")  # 2.0
    c = CertifiedMath.from_string("500000000000000000")   # 0.5
    
    print(f"a = {a.value / 10**18}")
    print(f"b = {b.value / 10**18}")
    print(f"c = {c.value / 10**18}")
    
    # Use the LogContext for thread-safe, isolated logging
    with CertifiedMath.LogContext() as session_log:
        # Perform arithmetic operations
        result1 = CertifiedMath.add(a, b, session_log, pqc_cid="operation_001")
        print(f"\nAddition: {a.value / 10**18} + {b.value / 10**18} = {result1.value / 10**18}")
        
        result2 = CertifiedMath.mul(result1, c, session_log, pqc_cid="operation_002")
        print(f"Multiplication: {result1.value / 10**18} * {c.value / 10**18} = {result2.value / 10**18}")
        
        result3 = CertifiedMath.fast_sqrt(result2, session_log, iterations=20, pqc_cid="operation_003")
        print(f"Square Root: sqrt({result2.value / 10**18}) = {result3.value / 10**18}")
        
        # Calculate phi series
        result4 = CertifiedMath.calculate_phi_series(result3, session_log, n=10, pqc_cid="operation_004")
        print(f"Phi Series: phi_series({result3.value / 10**18}, 10) = {result4.value / 10**18}")
        
        # Show log information
        print(f"\nLog Entries: {len(session_log)}")
        print(f"Log Hash: {CertifiedMath.get_log_hash(session_log)}")
        
        # Show log details
        print("\nLog Details:")
        for i, entry in enumerate(session_log):
            print(f"  {i+1}. {entry['op_name']}: {entry['inputs']} -> {entry['result']}")
            if entry['pqc_cid']:
                print(f"     PQC CID: {entry['pqc_cid']}")
            if entry['quantum_metadata']:
                print(f"     Quantum Metadata: {entry['quantum_metadata']}")
    
    # Demonstrate quantum metadata filtering
    print("\n" + "=" * 30)
    print("Quantum Metadata Filtering Example")
    
    quantum_metadata = {
        "quantum_seed": "qrng-001",
        "vdf_output_hash": "vdf-hash-7890",
        "entanglement_index": "ent-123",
        "quantum_source_id": "source-456",
        "quantum_entropy": "entropy-abc",
        "current_timestamp": "1234567890",  # This will be filtered out
        "native_float": 3.14159,           # This will be filtered out
        "random_value": "should_be_removed" # This will be filtered out
    }
    
    with CertifiedMath.LogContext() as session_log:
        result = CertifiedMath.add(a, b, session_log, 
                                 pqc_cid="quantum_test_001",
                                 quantum_metadata=quantum_metadata)
        
        print(f"Result: {result.value / 10**18}")
        logged_metadata = session_log[0]['quantum_metadata']
        print(f"Logged Metadata: {logged_metadata}")
        
        # Show that only allowed keys are present
        if logged_metadata:
            allowed_keys = {"quantum_seed", "vdf_output_hash", "entanglement_index", 
                           "quantum_source_id", "quantum_entropy"}
            logged_keys = set(logged_metadata.keys())
            print(f"Allowed keys preserved: {logged_keys}")
            print(f"Filtered out keys: {allowed_keys - logged_keys}")

if __name__ == "__main__":
    main()