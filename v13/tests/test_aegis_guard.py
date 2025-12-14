#!/usr/bin/env python3
"""
Test to debug AEGIS guard functionality
"""

import sys
import os


from v13.guards.AEGISGuard import AEGISGuard
from v13.libs.CertifiedMath import CertifiedMath, BigNum128
from v13.core.TokenStateBundle import create_token_state_bundle

def test_aegis_guard():
    """Test the AEGISGuard implementation."""
    print("Testing AEGISGuard...")
    
    # Create a CertifiedMath instance
    cm = CertifiedMath()
    
    # Create AEGISGuard
    aegis_guard = AEGISGuard(cm)
    
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
    
    # Test observing a safe interaction
    safe_inputs = {
        "user_id": "test_user",
        "target_id": "test_post",
        "content": "This is a safe, family-friendly comment about quantum computing.",
        "type": "comment"
    }
    
    observation1 = aegis_guard.observe_event(
        event_type="social_interaction",
        inputs=safe_inputs,
        token_bundle=token_bundle,
        deterministic_timestamp=1234567890
    )
    
    print(f"Safe interaction - Safety guard passed: {observation1.safety_guard_result.get('passed', False)}")
    print(f"Safe interaction - Economics guard passed: {observation1.economics_guard_result.get('passed', False)}")
    print(f"Safe interaction - AEGIS decision: {observation1.aegis_decision}")
    print(f"Safe interaction - Explanation: {observation1.explanation}")
    
    # Test observing an unsafe interaction
    unsafe_inputs = {
        "user_id": "test_user",
        "target_id": "test_post",
        "content": "This is explicit adult content that should be flagged.",
        "type": "comment"
    }
    
    observation2 = aegis_guard.observe_event(
        event_type="social_interaction",
        inputs=unsafe_inputs,
        token_bundle=token_bundle,
        deterministic_timestamp=1234567891
    )
    
    print(f"Unsafe interaction - Safety guard passed: {observation2.safety_guard_result.get('passed', False)}")
    print(f"Unsafe interaction - Economics guard passed: {observation2.economics_guard_result.get('passed', False)}")
    print(f"Unsafe interaction - AEGIS decision: {observation2.aegis_decision}")
    print(f"Unsafe interaction - Explanation: {observation2.explanation}")
    
    # Verify results
    safe_safety_passed = observation1.safety_guard_result.get('passed', False)
    unsafe_safety_passed = observation2.safety_guard_result.get('passed', False)
    
    if safe_safety_passed and not unsafe_safety_passed:
        print("✅ AEGIS GUARD TEST PASSED!")
        return True
    else:
        print("❌ AEGIS GUARD TEST FAILED!")
        return False

if __name__ == "__main__":
    success = test_aegis_guard()
    sys.exit(0 if success else 1)