#!/usr/bin/env python3
"""
Simple test to verify SafetyGuard functionality
"""

import sys
import os


from v13.libs.core.SafetyGuard import SafetyGuard
from v13.libs.CertifiedMath import CertifiedMath, BigNum128
from v13.core.TokenStateBundle import create_token_state_bundle

def test_safety_guard():
    """Test the SafetyGuard implementation."""
    print("Testing SafetyGuard...")
    
    # Create a CertifiedMath instance
    cm = CertifiedMath()
    
    # Create SafetyGuard
    safety_guard = SafetyGuard(cm)
    
    # Create a simple token bundle for testing
    token_bundle = create_token_state_bundle(
        chr_state={"balance": "100.0"},
        flx_state={"balance": "50.0"},
        psi_sync_state={"balance": "25.0"},
        atr_state={"balance": "30.0"},
        res_state={"balance": "40.0"},
        nod_state={"balance": "20.0"},
        lambda1=BigNum128.from_int(1),
        lambda2=BigNum128.from_int(1),
        c_crit=BigNum128.from_int(1),
        pqc_cid="test_safety_001",
        timestamp=1234567890
    )
    
    log_list = []
    
    # Test content validation - safe content
    safe_content = "This is a safe, family-friendly post about quantum computing."
    safe_metadata = {
        "author": "user_123",
        "community": "technology",
        "timestamp": 1234567890
    }
    
    result1 = safety_guard.validate_content(
        content_text=safe_content,
        content_metadata=safe_metadata,
        token_bundle=token_bundle,
        log_list=log_list,
        pqc_cid="test_safety_001",
        deterministic_timestamp=1234567890
    )
    
    print(f"Safe content validation: {result1.passed}")
    print(f"Risk score: {result1.risk_score.to_decimal_string()}")
    print(f"Explanation: {result1.explanation}")
    
    # Test content validation - unsafe content
    unsafe_content = "This is explicit adult content that should be flagged."
    unsafe_metadata = {
        "author": "user_456",
        "community": "general",
        "timestamp": 1234567891
    }
    
    result2 = safety_guard.validate_content(
        content_text=unsafe_content,
        content_metadata=unsafe_metadata,
        token_bundle=token_bundle,
        log_list=log_list,
        pqc_cid="test_safety_002",
        deterministic_timestamp=1234567891
    )
    
    print(f"Unsafe content validation: {result2.passed}")
    print(f"Risk score: {result2.risk_score.to_decimal_string()}")
    print(f"Explanation: {result2.explanation}")
    
    # Verify results
    if result1.passed and not result2.passed:
        print("✅ SAFETY GUARD TEST PASSED!")
        return True
    else:
        print("❌ SAFETY GUARD TEST FAILED!")
        return False

if __name__ == "__main__":
    success = test_safety_guard()
    sys.exit(0 if success else 1)