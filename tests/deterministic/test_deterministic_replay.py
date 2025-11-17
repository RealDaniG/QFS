"""
Deterministic Replay Test for QFS V13
Verifies that identical inputs produce identical outputs across runs.
"""

import sys
import os
import json
import hashlib

# Add src/libs to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'libs'))

def test_deterministic_replay():
    """
    Test that the same operations produce the same results when replayed.
    """
    try:
        from CertifiedMath import CertifiedMath, BigNum128
        
        # Test data
        a = BigNum128.from_int(10)
        b = BigNum128.from_int(5)
        
        # Run the same operation multiple times
        results = []
        logs = []
        
        for i in range(3):
            with CertifiedMath.LogContext() as log:
                result = CertifiedMath.add(a, b, log, pqc_cid=f"test_add_{i}")
                log_hash = CertifiedMath.get_log_hash(log)
                results.append(result)
                logs.append(log_hash)
                print(f"Run {i+1}: Result = {result.to_decimal_string()}, Log Hash = {log_hash}")
        
        # Check if all results are identical
        result_values = [r.value for r in results]
        if len(set(result_values)) == 1:
            print("✅ Deterministic results test PASSED")
        else:
            print("❌ Deterministic results test FAILED")
            return False
        
        # Check if all log hashes are identical
        if len(set(logs)) == 1:
            print("✅ Deterministic log hash test PASSED")
        else:
            print("❌ Deterministic log hash test FAILED")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error during deterministic replay test: {e}")
        return False

def main():
    """
    Main test function.
    """
    print("Running Deterministic Replay Test...")
    
    if test_deterministic_replay():
        print("✅ Deterministic Replay Test PASSED")
        return 0
    else:
        print("❌ Deterministic Replay Test FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())