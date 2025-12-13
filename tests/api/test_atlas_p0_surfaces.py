"""
Tests for ATLAS x QFS P0 API surfaces
"""
import pytest
from src.atlas_api.router import AtlasAPIRouter
from src.atlas_api.models import FeedRequest, InteractionRequest


class TestAtlasP0Surfaces:
    """Test suite for ATLAS P0 API surface stubs"""

    def test_feed_endpoint_exists(self):
        """Test that the feed endpoint exists in the router"""
        router = AtlasAPIRouter()
        assert hasattr(router, 'route_get_feed')
        
        # Test that it accepts the expected parameters
        response = router.route_get_feed(user_id="test_user")
        assert isinstance(response, dict)
        assert "policy_metadata" in response

    def test_interaction_endpoint_exists(self):
        """Test that the interaction endpoint exists in the router"""
        router = AtlasAPIRouter()
        assert hasattr(router, 'route_post_interaction')
        
        # Test that it accepts the expected parameters
        response = router.route_post_interaction(
            interaction_type="like",
            user_id="test_user",
            target_id="test_post"
        )
        assert isinstance(response, dict)
        assert "success" in response

    def test_feed_response_schema(self):
        """Test that feed response conforms to documented schema"""
        router = AtlasAPIRouter()
        response = router.route_get_feed(user_id="test_user")
        
        # Check required fields
        assert "posts" in response
        assert "policy_metadata" in response
        
        # Check policy metadata structure
        policy_meta = response["policy_metadata"]
        assert isinstance(policy_meta, dict)
        assert "version" in policy_meta
        assert "status" in policy_meta

    def test_interaction_response_schema(self):
        """Test that interaction response conforms to documented schema"""
        router = AtlasAPIRouter()
        response = router.route_post_interaction(
            interaction_type="like",
            user_id="test_user",
            target_id="test_post"
        )
        
        # Check required fields
        assert "success" in response
        assert isinstance(response["success"], bool)

    def test_deterministic_responses(self):
        """Test that responses are deterministic given same inputs"""
        router1 = AtlasAPIRouter()
        router2 = AtlasAPIRouter()
        
        # Same inputs should produce same outputs
        response1 = router1.route_get_feed(user_id="test_user")
        response2 = router2.route_get_feed(user_id="test_user")
        
        assert response1 == response2

    def test_request_models_exist(self):
        """Test that request models are properly defined"""
        # Test FeedRequest
        feed_request = FeedRequest(user_id="test_user")
        assert feed_request.user_id == "test_user"
        assert feed_request.limit == 20
        assert feed_request.mode == "coherence"
        
        # Test InteractionRequest
        interaction_request = InteractionRequest(
            user_id="test_user",
            target_id="test_target"
        )
        assert interaction_request.user_id == "test_user"
        assert interaction_request.target_id == "test_target"


if __name__ == "__main__":
    pytest.main([__file__])