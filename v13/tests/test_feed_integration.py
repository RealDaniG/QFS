"""
Test script to verify policy engine integration in feed generation
"""
import sys
import os


# Import required modules
from v13.atlas_api.models import FeedRequest
from v13.atlas_api.gateway import AtlasAPIGateway
from unittest.mock import Mock

def test_feed_generation_with_policy_hints():
    """Test that feed generation includes policy hints"""
    print("Testing feed generation with policy hints...")
    
    # Create gateway instance
    gateway = AtlasAPIGateway()
    
    
    gateway.storage_client = Mock()
    gateway.ledger_economics_service = Mock()
    
    
    mock_candidates = [
        {
            'content_id': 'post_1',
            'content_cid': 'cid_1',
            'author_id': 'user_1',
            'text': 'Test post 1'
        },
        {
            'content_id': 'post_2', 
            'content_cid': 'cid_2',
            'author_id': 'user_2',
            'text': 'Test post 2'
        }
    ]
    
    
    gateway._fetch_content_candidates = Mock(return_value=mock_candidates)
    gateway._get_user_token_bundle = Mock(return_value={})
    gateway._get_deterministic_timestamp = Mock(return_value=1234567890)
    gateway._validate_request_shape = Mock(return_value=True)
    gateway._build_coherence_input = Mock(return_value={
        'content_id': 'test_content',
        'features': ['feature1', 'feature2']
    })
    gateway._build_feature_vector = Mock(return_value=['feature1', 'feature2'])
    gateway.coherence_engine.update_omega = Mock(return_value=[1, 2, 3])
    gateway._calculate_coherence_score = Mock(return_value=100)
    
    
    def mock_observe_event(*args, **kwargs):
        mock_observation = Mock()
        mock_observation.block_suggested = False
        mock_observation.severity = "info"
        mock_observation.safety_guard_result = {"passed": True, "risk_score": "0", "explanation": "Safe"}
        mock_observation.economics_guard_result = {"passed": True, "explanation": "Economically sound"}
        mock_observation.explanation = "No issues detected"
        return mock_observation
    
    gateway.aegis_guard.observe_event = Mock(side_effect=mock_observe_event)
    
    # Create feed request
    request = FeedRequest(user_id="test_user", limit=10)
    
    # Generate feed
    response = gateway.get_feed(request)
    
    # Verify response structure
    assert response is not None, "Response should not be None"
    assert hasattr(response, 'posts'), "Response should have posts"
    assert hasattr(response, 'policy_metadata'), "Response should have policy_metadata"
    
    # Verify posts have policy hints
    assert len(response.posts) > 0, "Should have at least one post"
    
    for post in response.posts:
        print(f"Post ID: {post.post_id}")
        print(f"AEGIS Advisory: {post.aegis_advisory}")
        print(f"Policy Hints: {post.policy_hints}")
        
        # Verify policy hints structure
        assert hasattr(post, 'policy_hints'), "Post should have policy_hints field"
        assert post.policy_hints is not None, "Policy hints should not be None"
        
        # Verify policy hints contain expected fields
        expected_fields = ['visibility_level', 'warning_banner', 'requires_click_through', 'client_tags']
        for field in expected_fields:
            assert field in post.policy_hints, f"Policy hints should contain {field}"
    
    print("✅ Feed generation with policy hints test passed!")

if __name__ == "__main__":
    try:
        test_feed_generation_with_policy_hints()
        print("\n🎉 All integration tests passed!")
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)