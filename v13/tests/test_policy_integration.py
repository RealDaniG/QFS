"""
Test suite for policy engine integration with Atlas API Gateway
"""
import sys
import os
import unittest
from unittest.mock import Mock, patch


from v13.atlas_api.gateway import AtlasAPIGateway
from v13.atlas_api.models import FeedRequest, FeedPost
from v13.policy.policy_engine import PolicyEngine, PolicyConfiguration, VisibilityLevel, WarningBannerType


class TestPolicyIntegration(unittest.TestCase):
    """Test policy engine integration with feed generation"""

    def setUp(self):
        """Set up test fixtures"""
        self.gateway = AtlasAPIGateway()
        
        
        self.gateway.storage_client = Mock()
        self.gateway.ledger_economics_service = Mock()
        
        
        self.mock_candidates = [
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
        
        
        self.gateway._fetch_content_candidates = Mock(return_value=self.mock_candidates)
        
        
        self.gateway._get_user_token_bundle = Mock(return_value={})
        
        
        self.gateway._get_deterministic_timestamp = Mock(return_value=1234567890)
        
        
        self.gateway._validate_request_shape = Mock(return_value=True)
        
        
        self.gateway._build_coherence_input = Mock(return_value={
            'content_id': 'test_content',
            'features': ['feature1', 'feature2']
        })
        
        
        self.gateway._build_feature_vector = Mock(return_value=['feature1', 'feature2'])
        
        
        self.gateway.coherence_engine.update_omega = Mock(return_value=[1, 2, 3])
        self.gateway._calculate_coherence_score = Mock(return_value=100)
        
        
        mock_aegis_observation = Mock()
        mock_aegis_observation.block_suggested = False
        mock_aegis_observation.severity = "info"
        mock_aegis_observation.safety_guard_result = {"passed": True, "risk_score": "0", "explanation": "Safe"}
        mock_aegis_observation.economics_guard_result = {"passed": True, "explanation": "Economically sound"}
        mock_aegis_observation.explanation = "No issues detected"
        
        self.gateway.aegis_guard.observe_event = Mock(return_value=mock_aegis_observation)

    def test_feed_generation_with_policy_hints(self):
        """Test that feed generation includes policy hints"""
        # Create a feed request
        request = FeedRequest(user_id="test_user", limit=10)
        
        # Generate feed
        response = self.gateway.get_feed(request)
        
        # Verify response structure
        self.assertIsNotNone(response)
        self.assertTrue(hasattr(response, 'posts'))
        self.assertTrue(hasattr(response, 'policy_metadata'))
        
        # Verify posts have policy hints
        self.assertGreater(len(response.posts), 0)
        for post in response.posts:
            self.assertTrue(hasattr(post, 'policy_hints'))
            self.assertIsNotNone(post.policy_hints)
            
            # Verify policy hints structure
            policy_hints = post.policy_hints
            self.assertIn('visibility_level', policy_hints)
            self.assertIn('warning_banner', policy_hints)
            self.assertIn('requires_click_through', policy_hints)
            self.assertIn('client_tags', policy_hints)

    def test_policy_hints_for_different_severities(self):
        """Test that policy hints vary based on AEGIS advisory severity"""
        # Test with info level advisory
        info_observation = Mock()
        info_observation.block_suggested = False
        info_observation.severity = "info"
        info_observation.safety_guard_result = {"passed": True, "risk_score": "0", "explanation": "Safe"}
        info_observation.economics_guard_result = {"passed": True, "explanation": "Economically sound"}
        info_observation.explanation = "No issues detected"
        
        self.gateway.aegis_guard.observe_event.return_value = info_observation
        
        request = FeedRequest(user_id="test_user", limit=1)
        response = self.gateway.get_feed(request)
        
        # Verify info level policy hints
        post = response.posts[0]
        self.assertEqual(post.policy_hints['visibility_level'], 'visible')
        self.assertEqual(post.policy_hints['warning_banner'], 'none')
        self.assertFalse(post.policy_hints['requires_click_through'])
        self.assertEqual(post.policy_hints['client_tags'], [])
        
        # Test with warning level advisory
        warning_observation = Mock()
        warning_observation.block_suggested = True
        warning_observation.severity = "warning"
        warning_observation.safety_guard_result = {"passed": False, "risk_score": "50", "explanation": "Moderate risk"}
        warning_observation.economics_guard_result = {"passed": True, "explanation": "Economically sound"}
        warning_observation.explanation = "Potential safety concerns"
        
        self.gateway.aegis_guard.observe_event.return_value = warning_observation
        
        response = self.gateway.get_feed(request)
        
        # Verify warning level policy hints
        post = response.posts[0]
        self.assertEqual(post.policy_hints['visibility_level'], 'warned')
        self.assertEqual(post.policy_hints['warning_banner'], 'general')
        self.assertFalse(post.policy_hints['requires_click_through'])  # Default config
        self.assertIn('aegis_severity_warning', post.policy_hints['client_tags'])
        self.assertIn('aegis_block_suggested', post.policy_hints['client_tags'])

    def test_backwards_compatibility(self):
        """Test that responses remain backwards compatible"""
        request = FeedRequest(user_id="test_user", limit=1)
        response = self.gateway.get_feed(request)
        
        # Verify all existing fields are still present
        post = response.posts[0]
        self.assertTrue(hasattr(post, 'post_id'))
        self.assertTrue(hasattr(post, 'coherence_score'))
        self.assertTrue(hasattr(post, 'policy_version'))
        self.assertTrue(hasattr(post, 'why_this_ranking'))
        self.assertTrue(hasattr(post, 'timestamp'))
        self.assertTrue(hasattr(post, 'aegis_advisory'))
        
        # Verify new policy_hints field is optional but present
        self.assertTrue(hasattr(post, 'policy_hints'))
        self.assertIsNotNone(post.policy_hints)


if __name__ == '__main__':
    unittest.main()