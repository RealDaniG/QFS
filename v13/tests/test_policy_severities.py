"""
Test script to verify policy engine handles different advisory severities correctly
"""
from v13.libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
from v13.atlas_api.models import FeedRequest
from v13.atlas_api.gateway import AtlasAPIGateway
from unittest.mock import Mock

def test_policy_hints_for_different_severities():
    """Test that policy hints vary based on AEGIS advisory severity"""
    print('Testing policy hints for different advisory severities...')
    gateway = AtlasAPIGateway()
    gateway.storage_client = Mock()
    gateway.ledger_economics_service = Mock()
    mock_candidates = [{'content_id': 'test_post', 'content_cid': 'test_cid', 'author_id': 'test_user', 'text': 'Test post'}]
    gateway._fetch_content_candidates = Mock(return_value=mock_candidates)
    gateway._get_user_token_bundle = Mock(return_value={})
    gateway._get_deterministic_timestamp = Mock(return_value=1234567890)
    gateway._validate_request_shape = Mock(return_value=True)
    gateway._build_coherence_input = Mock(return_value={'content_id': 'test_content', 'features': ['feature1', 'feature2']})
    gateway._build_feature_vector = Mock(return_value=['feature1', 'feature2'])
    gateway.coherence_engine.update_omega = Mock(return_value=[1, 2, 3])
    gateway._calculate_coherence_score = Mock(return_value=100)
    test_cases = [{'name': 'Info Advisory', 'block_suggested': False, 'severity': 'info', 'expected_visibility': 'visible', 'expected_banner': 'none', 'expected_click_through': False}, {'name': 'Warning Advisory', 'block_suggested': True, 'severity': 'warning', 'expected_visibility': 'warned', 'expected_banner': 'general', 'expected_click_through': False}, {'name': 'Critical Advisory', 'block_suggested': True, 'severity': 'critical', 'expected_visibility': 'hidden', 'expected_banner': 'safety', 'expected_click_through': True}]
    for test_case in sorted(test_cases):
        print(f"\nTesting {test_case['name']}...")

        def mock_observe_event(*args, **kwargs):
            mock_observation = Mock()
            mock_observation.block_suggested = test_case['block_suggested']
            mock_observation.severity = test_case['severity']
            mock_observation.safety_guard_result = {'passed': not test_case['block_suggested'], 'risk_score': '50' if test_case['block_suggested'] else '0', 'explanation': 'Test explanation'}
            mock_observation.economics_guard_result = {'passed': True, 'explanation': 'Economically sound'}
            mock_observation.explanation = 'Test explanation'
            return mock_observation
        gateway.aegis_guard.observe_event = Mock(side_effect=mock_observe_event)
        request = FeedRequest(user_id='test_user', limit=1)
        response = gateway.get_feed(request)
        post = response.posts[0]
        policy_hints = post.policy_hints
        print(f'  AEGIS Advisory: {post.aegis_advisory}')
        print(f'  Policy Hints: {policy_hints}')
        assert policy_hints['visibility_level'] == test_case['expected_visibility'], f"Expected visibility '{test_case['expected_visibility']}', got '{policy_hints['visibility_level']}'"
        assert policy_hints['warning_banner'] == test_case['expected_banner'], f"Expected banner '{test_case['expected_banner']}', got '{policy_hints['warning_banner']}'"
        assert policy_hints['requires_click_through'] == test_case['expected_click_through'], f"Expected click_through '{test_case['expected_click_through']}', got '{policy_hints['requires_click_through']}'"
        print(f"  ✅ {test_case['name']} test passed!")
    print('\n✅ All severity tests passed!')
if __name__ == '__main__':
    try:
        test_policy_hints_for_different_severities()
        print('\n🎉 All severity integration tests passed!')
    except Exception as e:
        print(f'\n❌ Severity integration test failed: {e}')
        import traceback
        traceback.print_exc()
        raise ZeroSimAbort(1)
