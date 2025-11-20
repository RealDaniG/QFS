#!/usr/bin/env python3
"""
Test script to verify CertifiedMath integration with GenesisHarmonicState
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'libs'))

from libs.CertifiedMath import CertifiedMath, BigNum128
from libs.economics.GenesisHarmonicState import GENESIS_STATE

def test_verify_genesis_state():
    """Test the verify_genesis_state method"""
    print("Testing CertifiedMath.verify_genesis_state...")
    
    # Create a log list for audit trail
    log_list = []
    
    # Test the method
    result = CertifiedMath.verify_genesis_state(GENESIS_STATE, log_list)
    
    print(f"Verification result: {result['valid']}")
    print(f"Proofs generated: {list(result['proofs'].keys())}")
    print(f"Violations found: {result['violations']}")
    
    # Check specific proofs
    if 'token_conservation' in result['proofs']:
        print(f"Token conservation proof: {result['proofs']['token_conservation']}")
    
    if 'harmonic_bounds' in result['proofs']:
        print(f"Harmonic bounds proof: {result['proofs']['harmonic_bounds']}")
    
    return result['valid']

def test_basic_operations():
    """Test basic CertifiedMath operations"""
    print("\nTesting basic CertifiedMath operations...")
    
    # Create some test values
    a = BigNum128.from_int(1000000000)  # 1.0
    b = BigNum128.from_int(500000000)   # 0.5
    
    log_list = []
    
    # Test addition
    result_add = CertifiedMath.add(a, b, log_list)
    print(f"Addition: {a.to_decimal_string()} + {b.to_decimal_string()} = {result_add.to_decimal_string()}")
    
    # Test multiplication
    result_mul = CertifiedMath.mul(a, b, log_list)
    print(f"Multiplication: {a.to_decimal_string()} * {b.to_decimal_string()} = {result_mul.to_decimal_string()}")
    
    # Test comparison
    result_gte = CertifiedMath.gte(a, b, log_list)
    print(f"Comparison: {a.to_decimal_string()} >= {b.to_decimal_string()} = {result_gte}")
    
    return True

if __name__ == "__main__":
    print("Running CertifiedMath integration tests...")
    
    try:
        # Test basic operations
        test_basic_operations()
        
        # Test genesis state verification
        success = test_verify_genesis_state()
        
        if success:
            print("\n✅ All tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)