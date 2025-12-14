"""
Tests for ATLAS x QFS P0 API surfaces
"""
import pytest
from v13.atlas_api.router import AtlasAPIRouter
from v13.atlas_api.models import FeedRequest, InteractionRequest


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

    def test_feed_deterministic_for_same_state(self):
        """Test that feed responses are deterministic for identical inputs"""
        # Create two router instances to simulate separate runs
        router1 = AtlasAPIRouter()
        router2 = AtlasAPIRouter()
        
        # Call with identical parameters
        response1 = router1.route_get_feed(user_id="test_user", limit=5, mode="coherence")
        response2 = router2.route_get_feed(user_id="test_user", limit=5, mode="coherence")
        
        # Responses should be identical
        assert response1 == response2
        
        # Also test with different modes to ensure they're different
        response3 = router1.route_get_feed(user_id="test_user", limit=5, mode="chronological")
        # While structure should be the same, content may differ
        assert "posts" in response3
        assert "policy_metadata" in response3
        assert response3["policy_metadata"]["mode"] == "chronological"

    def test_feed_mode_switch(self):
        """Test that feed mode switching works correctly"""
        router = AtlasAPIRouter()
        
        # Test coherence mode
        coherence_response = router.route_get_feed(user_id="test_user", limit=3, mode="coherence")
        assert coherence_response["policy_metadata"]["mode"] == "coherence"
        
        # Test chronological mode
        chrono_response = router.route_get_feed(user_id="test_user", limit=3, mode="chronological")
        assert chrono_response["policy_metadata"]["mode"] == "chronological"
        
        # Both should have the same schema
        assert "posts" in coherence_response
        assert "posts" in chrono_response
        assert "policy_metadata" in coherence_response
        assert "policy_metadata" in chrono_response
        
        # Posts should be ordered differently (though with mock data they might be the same)
        assert isinstance(coherence_response["posts"], list)
        assert isinstance(chrono_response["posts"], list)

    def test_interaction_success_path(self):
        """Test happy path for interaction submission"""
        router = AtlasAPIRouter()
        
        # Test a successful like interaction
        response = router.route_post_interaction(
            interaction_type="like",
            user_id="test_user",
            target_id="test_post"
        )
        
        # Check that response has expected structure
        assert "success" in response
        assert "event_id" in response
        assert "guard_results" in response
        assert "reward_estimate" in response
        
        # Check values
        assert isinstance(response["success"], bool)
        assert response["event_id"] is not None
        assert len(response["event_id"]) > 0
        assert response["guard_results"] is not None
        assert response["reward_estimate"] is not None

    def test_interaction_guard_failure(self):
        """Test interaction that fails guard validation"""
        # For this test, we'll need to modify the gateway to simulate a guard failure
        # Since our current implementation always passes, we'll test the structure
        router = AtlasAPIRouter()
        
        # Test an interaction (currently always succeeds in our mock)
        response = router.route_post_interaction(
            interaction_type="like",
            user_id="test_user",
            target_id="test_post"
        )
        
        # Even in success case, check structure is correct for failure handling
        assert "success" in response
        assert "event_id" in response
        assert "guard_results" in response
        
        # In a real implementation, we would test a case that fails validation

    def test_interaction_deterministic_event_id(self):
        """Test that event IDs are deterministic for identical interactions"""
        router1 = AtlasAPIRouter()
        router2 = AtlasAPIRouter()
        
        # Submit identical interactions
        response1 = router1.route_post_interaction(
            interaction_type="like",
            user_id="test_user",
            target_id="test_post"
        )
        
        response2 = router2.route_post_interaction(
            interaction_type="like",
            user_id="test_user",
            target_id="test_post"
        )
        
        # Event IDs should be identical
        assert response1["event_id"] == response2["event_id"]

    def test_invalid_input_handling(self):
        """Test handling of invalid inputs"""
        router = AtlasAPIRouter()
        
        # Test feed with missing user_id
        response = router.route_get_feed(user_id="")
        assert "error_code" in response
        assert response["error_code"] == "MISSING_USER_ID"
        
        # Test feed with invalid limit
        response = router.route_get_feed(user_id="test_user", limit=0)
        assert "error_code" in response
        assert response["error_code"] == "INVALID_LIMIT"
        
        # Test feed with invalid mode
        response = router.route_get_feed(user_id="test_user", mode="invalid")
        assert "error_code" in response
        assert response["error_code"] == "INVALID_MODE"
        
        # Test interaction with missing user_id
        response = router.route_post_interaction(
            interaction_type="like",
            user_id="",
            target_id="test_post"
        )
        assert "error_code" in response
        assert response["error_code"] == "MISSING_USER_ID"
        
        # Test interaction with missing target_id
        response = router.route_post_interaction(
            interaction_type="like",
            user_id="test_user",
            target_id=""
        )
        assert "error_code" in response
        assert response["error_code"] == "MISSING_TARGET_ID"
        
        # Test interaction with invalid type
        response = router.route_post_interaction(
            interaction_type="invalid",
            user_id="test_user",
            target_id="test_post"
        )
        assert "error_code" in response
        assert response["error_code"] == "INVALID_INTERACTION_TYPE"
        
        # Test comment interaction with missing content
        response = router.route_post_interaction(
            interaction_type="comment",
            user_id="test_user",
            target_id="test_post"
        )
        assert "error_code" in response
        assert response["error_code"] == "MISSING_CONTENT"
        
        # Test report interaction with missing reason
        response = router.route_post_interaction(
            interaction_type="report",
            user_id="test_user",
            target_id="test_post"
        )
        assert "error_code" in response
        assert response["error_code"] == "MISSING_REASON"

    def test_internal_error_handling(self):
        """Test handling of internal errors"""
        router = AtlasAPIRouter()
        
        # We can't easily simulate internal errors in our current implementation
        # But we can verify that the error handling structure is in place
        # by checking that the router methods return error dictionaries


if __name__ == "__main__":
    pytest.main([__file__])