"""
Debug test to see what's happening in the gateway
"""
from v13.atlas_api.gateway import AtlasAPIGateway
from v13.atlas_api.models import InteractionRequest

def create_test_drv_packet():
    """Create a deterministic DRV packet for testing"""

    class MockDRVPacket:

        def __init__(self):
            self.ttsTimestamp = 1234567890
    return MockDRVPacket()

def debug_test():
    """Debug test to see what's happening"""
    print('Starting debug test...')
    gateway = AtlasAPIGateway()
    drv_packet = create_test_drv_packet()
    gateway.set_drv_packet(drv_packet)
    interaction_request = InteractionRequest(user_id='test_user_123', target_id='test_post_456', content='This is a safe, family-friendly comment about quantum computing.')
    interaction_response = gateway.post_interaction('comment', interaction_request)
    print(f'Response success: {interaction_response.success}')
    print(f'Event ID: {interaction_response.event_id}')
    if interaction_response.guard_results:
        print(f'Guard results safety: {interaction_response.guard_results.safety_guard_passed}')
        print(f'Guard results economics: {interaction_response.guard_results.economics_guard_passed}')
        print(f'Guard results explanation: {interaction_response.guard_results.explanation}')
    else:
        print('No guard results')
if __name__ == '__main__':
    debug_test()
