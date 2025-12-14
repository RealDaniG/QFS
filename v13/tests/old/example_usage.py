#!/usr/bin/env python3
"""
Example usage of CertifiedMath.py demonstrating all key features
"""

import sys
import os

# Add the libs directory to the path so we can import CertifiedMath

from v13.libs.CertifiedMath import CertifiedMath, BigNum128

def main():
    print("CertifiedMath Example Usage")
    print("==============================")
    
    # Create BigNum128 instances with smaller values to avoid overflow
    a = BigNum128(1000000000000000000)  # 1.0
    b = BigNum128(2000000000000000000)  # 2.0
    c = BigNum128(500000000000000000)   # 0.5 instead of 500000000000000000000
    
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
    
    # Demonstrate quantum metadata handling (no filtering in core library)
    print("\n" + "=" * 30)
    print("Quantum Metadata Handling Example")
    
    quantum_metadata = {
        "quantum_seed": "qrng-001",
        "vdf_output_hash": "vdf-hash-7890",
        "entanglement_index": "ent-123",
        "quantum_source_id": "source-456",
        "quantum_entropy": "entropy-abc",
        "current_timestamp": "1234567890",  # This is logged as-is (filtering happens in SDK)
        "native_float": 3.14159,           # This is logged as-is (filtering happens in SDK)
        "random_value": "should_be_kept"   # This is logged as-is (filtering happens in SDK)
    }
    
    with CertifiedMath.LogContext() as session_log:
        result = CertifiedMath.add(a, b, session_log, 
                                 pqc_cid="quantum_test_001",
                                 quantum_metadata=quantum_metadata)
        
        print(f"Result: {result.value / 10**18}")
        logged_metadata = session_log[0]['quantum_metadata']
        print(f"Logged Metadata: {logged_metadata}")
        
        # Show that all keys are preserved (filtering is handled by SDK)
        if logged_metadata:
            print("All metadata keys preserved (filtering handled by SDK layer)")

if __name__ == "__main__":
    main()