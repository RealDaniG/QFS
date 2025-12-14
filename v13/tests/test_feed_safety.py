#!/usr/bin/env python3
"""
Test to verify feed ranking safety checks in AtlasAPIGateway
"""

import sys
import os

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
    print("Testing feed ranking with safety checks...")
    
    # Create gateway instance
    gateway = AtlasAPIGateway()
    
    # Set deterministic DRV packet
    drv_packet = create_test_drv_packet()
    gateway.set_drv_packet(drv_packet)
    
    # Create feed request
    feed_request = FeedRequest(
        user_id="test_user_123",
        limit=5,
        mode="coherence"
    )
    
    # Get feed
    feed_response = gateway.get_feed(feed_request)
    
    print(f"Feed response status: {feed_response.policy_metadata.get('status', 'UNKNOWN')}")
    print(f"Number of posts: {len(feed_response.posts)}")
    
    # Check if we got posts
    if feed_response.posts:
        print("\nPost details:")
        for i, post in enumerate(feed_response.posts):
            print(f"  Post {i+1}: ID={post.post_id}, Score={post.coherence_score.to_decimal_string()}")
    
    # The test passes if we get a successful response
    success = feed_response.policy_metadata.get('status') == 'SUCCESS'
    return success

def main():
    """Main test function"""
    print("Starting feed safety test...")
    
    success = test_feed_safety()
    
    if success:
        print("✅ FEED SAFETY TEST PASSED!")
        return True
    else:
        print("❌ FEED SAFETY TEST FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)