#!/usr/bin/env python3
"""
Test to verify SafetyGuard integration in AtlasAPIGateway
"""

import sys
import os
import json
import hashlib


from v13.atlas_api.gateway import AtlasAPIGateway
from v13.atlas_api.models import InteractionRequest

def create_test_drv_packet():
    """Create a deterministic DRV packet for testing"""
    class MockDRVPacket:
        def __init__(self):
            self.ttsTimestamp = 1234567890
    
    return MockDRVPacket()

def test_safe_content():
    """Test interaction with safe content"""
    print("Testing safe content interaction...")
    
    # Create gateway instance
    gateway = AtlasAPIGateway()
    
    # Set deterministic DRV packet
    drv_packet = create_test_drv_packet()
    gateway.set_drv_packet(drv_packet)
    
    # Test interaction request with safe content
    interaction_request = InteractionRequest(
        user_id="test_user_123",
        target_id="test_post_456",
        content="This is a safe, family-friendly comment about quantum computing."
    )
    
    # Post interaction
    interaction_response = gateway.post_interaction("comment", interaction_request)
    
    # Check results
    safety_passed = interaction_response.guard_results.safety_guard_passed if interaction_response.guard_results else False
    economics_passed = interaction_response.guard_results.economics_guard_passed if interaction_response.guard_results else False
    
    print(f"Safe content - Safety guard passed: {safety_passed}")
    print(f"Safe content - Economics guard passed: {economics_passed}")
    
    return safety_passed, economics_passed

def test_unsafe_content():
    """Test interaction with unsafe content"""
    print("Testing unsafe content interaction...")
    
    # Create gateway instance
    gateway = AtlasAPIGateway()
    
    # Set deterministic DRV packet
    drv_packet = create_test_drv_packet()
    gateway.set_drv_packet(drv_packet)
    
    # Test interaction request with unsafe content
    interaction_request = InteractionRequest(
        user_id="test_user_123",
        target_id="test_post_456",
        content="This is explicit adult content that should be flagged."
    )
    
    # Post interaction
    interaction_response = gateway.post_interaction("comment", interaction_request)
    
    # Check results
    safety_passed = interaction_response.guard_results.safety_guard_passed if interaction_response.guard_results else False
    economics_passed = interaction_response.guard_results.economics_guard_passed if interaction_response.guard_results else False
    
    print(f"Unsafe content - Safety guard passed: {safety_passed}")
    print(f"Unsafe content - Economics guard passed: {economics_passed}")
    
    return safety_passed, economics_passed

def main():
    """Main test function"""
    print("Starting SafetyGuard integration test...")
    
    # Test safe content
    safe_safety, safe_economics = test_safe_content()
    
    # Test unsafe content
    unsafe_safety, unsafe_economics = test_unsafe_content()
    
    # Verify results
    if safe_safety and not unsafe_safety:
        print("✅ SAFETY GUARD INTEGRATION TEST PASSED!")
        print(f"  Safe content correctly passed safety check: {safe_safety}")
        print(f"  Unsafe content correctly failed safety check: {unsafe_safety}")
        return True
    else:
        print("❌ SAFETY GUARD INTEGRATION TEST FAILED!")
        print(f"  Safe content safety check result: {safe_safety}")
        print(f"  Unsafe content safety check result: {unsafe_safety}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)