"""
Test to verify feed ranking safety checks in AtlasAPIGateway
"""
from v13.libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
from v13.atlas_api.gateway import AtlasAPIGateway
from v13.atlas_api.models import FeedRequest

def create_test_drv_packet():
    """Create a deterministic DRV packet for testing"""

    class MockDRVPacket:

        def __init__(self):
            self.ttsTimestamp = 1234567890
    return MockDRVPacket()

def test_feed_safety():
    """Test feed ranking with safety checks"""
    print('Testing feed ranking with safety checks...')
    gateway = AtlasAPIGateway()
    drv_packet = create_test_drv_packet()
    gateway.set_drv_packet(drv_packet)
    feed_request = FeedRequest(user_id='test_user_123', limit=5, mode='coherence')
    feed_response = gateway.get_feed(feed_request)
    print(f"Feed response status: {feed_response.policy_metadata.get('status', 'UNKNOWN')}")
    print(f'Number of posts: {len(feed_response.posts)}')
    if feed_response.posts:
        print('\nPost details:')
        for i, post in enumerate(feed_response.posts):
            print(f'  Post {i + 1}: ID={post.post_id}, Score={post.coherence_score.to_decimal_string()}')
    success = feed_response.policy_metadata.get('status') == 'SUCCESS'
    return success

def main():
    """Main test function"""
    print('Starting feed safety test...')
    success = test_feed_safety()
    if success:
        print('✅ FEED SAFETY TEST PASSED!')
        return True
    else:
        print('❌ FEED SAFETY TEST FAILED!')
        return False
if __name__ == '__main__':
    success = main()
    raise ZeroSimAbort(0 if success else 1)
