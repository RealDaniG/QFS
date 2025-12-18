"""
Tests for interaction safety validation in AtlasAPIGateway
"""
import pytest
from v13.atlas_api.gateway import AtlasAPIGateway
from v13.atlas_api.models import InteractionRequest

class TestInteractionSafety:
    """Test suite for interaction safety validation"""

    def test_safe_content_interaction(self):
        """Test interaction with safe content passes safety guard"""
        gateway = AtlasAPIGateway()
        request = InteractionRequest(user_id='test_user', target_id='test_post', content='This is a safe, family-friendly comment about quantum computing.')
        response = gateway.post_interaction('comment', request)
        assert hasattr(response, 'success')
        assert hasattr(response, 'event_id')
        assert hasattr(response, 'guard_results')
        assert response.guard_results is not None
        guard_results = response.guard_results
        assert guard_results.safety_guard_passed == True
        assert 'passed with risk score' in guard_results.explanation.lower()

    def test_unsafe_content_interaction(self):
        """Test interaction with unsafe content fails safety guard"""
        gateway = AtlasAPIGateway()
        request = InteractionRequest(user_id='test_user', target_id='test_post', content='This is explicit adult content that should be flagged.')
        response = gateway.post_interaction('comment', request)
        assert hasattr(response, 'success')
        assert hasattr(response, 'event_id')
        assert hasattr(response, 'guard_results')
        assert response.guard_results is not None
        guard_results = response.guard_results
        assert guard_results.safety_guard_passed == False
        assert 'failed with risk score' in guard_results.explanation.lower()
        assert 'threshold' in guard_results.explanation.lower()

    def test_high_risk_spam_content_interaction(self):
        """Test interaction with high-risk spam content fails safety guard"""
        gateway = AtlasAPIGateway()
        request = InteractionRequest(user_id='test_user', target_id='test_post', content='Buy now! Click here for free money and urgent offers! Limited time deal! Act now! Buy now! Click here for free money and urgent offers! Limited time deal! Act now! Buy now! Click here for free money and urgent offers! Limited time deal! Act now! Buy now! Click here for free money and urgent offers! Limited time deal! Act now! Buy now! Click here for free money and urgent offers! Limited time deal! Act now!')
        response = gateway.post_interaction('comment', request)
        assert hasattr(response, 'success')
        assert hasattr(response, 'event_id')
        assert hasattr(response, 'guard_results')
        assert response.guard_results is not None
        guard_results = response.guard_results
        assert guard_results.safety_guard_passed == False
        assert 'failed with risk score' in guard_results.explanation.lower()

    def test_deterministic_timestamp_behavior(self):
        """Test that timestamps are deterministic across calls"""
        gateway1 = AtlasAPIGateway()
        gateway2 = AtlasAPIGateway()
        ts1_first = gateway1._get_deterministic_timestamp()
        ts1_second = gateway1._get_deterministic_timestamp()
        ts1_third = gateway1._get_deterministic_timestamp()
        ts2_first = gateway2._get_deterministic_timestamp()
        ts2_second = gateway2._get_deterministic_timestamp()
        assert ts1_second == ts1_first + 1
        assert ts1_third == ts1_first + 2
        assert ts2_first == ts1_first
        assert ts2_second == ts1_second

    def test_like_interaction_without_content(self):
        """Test like interaction (no content) passes safety guard"""
        gateway = AtlasAPIGateway()
        request = InteractionRequest(user_id='test_user', target_id='test_post')
        response = gateway.post_interaction('like', request)
        assert hasattr(response, 'success')
        assert hasattr(response, 'event_id')
        assert hasattr(response, 'guard_results')
        assert response.guard_results is not None
        guard_results = response.guard_results
        assert guard_results.safety_guard_passed == True
if __name__ == '__main__':
    pytest.main([__file__])
