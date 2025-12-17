"""
Test to verify SafetyGuard integration in AtlasAPIGateway
"""
from libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
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
    print('Testing safe content interaction...')
    gateway = AtlasAPIGateway()
    drv_packet = create_test_drv_packet()
    gateway.set_drv_packet(drv_packet)
    interaction_request = InteractionRequest(user_id='test_user_123', target_id='test_post_456', content='This is a safe, family-friendly comment about quantum computing.')
    interaction_response = gateway.post_interaction('comment', interaction_request)
    safety_passed = interaction_response.guard_results.safety_guard_passed if interaction_response.guard_results else False
    economics_passed = interaction_response.guard_results.economics_guard_passed if interaction_response.guard_results else False
    print(f'Safe content - Safety guard passed: {safety_passed}')
    print(f'Safe content - Economics guard passed: {economics_passed}')
    return (safety_passed, economics_passed)

def test_unsafe_content():
    """Test interaction with unsafe content"""
    print('Testing unsafe content interaction...')
    gateway = AtlasAPIGateway()
    drv_packet = create_test_drv_packet()
    gateway.set_drv_packet(drv_packet)
    interaction_request = InteractionRequest(user_id='test_user_123', target_id='test_post_456', content='This is explicit adult content that should be flagged.')
    interaction_response = gateway.post_interaction('comment', interaction_request)
    safety_passed = interaction_response.guard_results.safety_guard_passed if interaction_response.guard_results else False
    economics_passed = interaction_response.guard_results.economics_guard_passed if interaction_response.guard_results else False
    print(f'Unsafe content - Safety guard passed: {safety_passed}')
    print(f'Unsafe content - Economics guard passed: {economics_passed}')
    return (safety_passed, economics_passed)

def main():
    """Main test function"""
    print('Starting SafetyGuard integration test...')
    safe_safety, safe_economics = test_safe_content()
    unsafe_safety, unsafe_economics = test_unsafe_content()
    if safe_safety and (not unsafe_safety):
        print('✅ SAFETY GUARD INTEGRATION TEST PASSED!')
        print(f'  Safe content correctly passed safety check: {safe_safety}')
        print(f'  Unsafe content correctly failed safety check: {unsafe_safety}')
        return True
    else:
        print('❌ SAFETY GUARD INTEGRATION TEST FAILED!')
        print(f'  Safe content safety check result: {safe_safety}')
        print(f'  Unsafe content safety check result: {unsafe_safety}')
        return False
if __name__ == '__main__':
    success = main()
    raise ZeroSimAbort(0 if success else 1)