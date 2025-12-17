"""
Tests for the humor explainability module
"""
import pytest
from v13.policy.humor_policy import HumorSignalPolicy
from v13.policy.humor_explainability import HumorExplainabilityHelper

class TestHumorExplainability:
    """Test suite for the humor explainability helper"""

    def setup_method(self):
        """Setup test environment"""
        humor_policy = HumorSignalPolicy()
        self.explain_helper = HumorExplainabilityHelper(humor_policy)

    def test_explain_humor_reward(self):
        """Test generating explanation for humor reward"""
        dimensions = {'chronos': 0.8, 'lexicon': 0.6, 'surreal': 0.4, 'empathy': 0.9, 'critique': 0.7, 'slapstick': 0.3, 'meta': 0.5}
        ledger_context = {'views': 1000, 'laughs': 800, 'saves': 200, 'replays': 150, 'author_reputation': 0.9}
        explanation = self.explain_helper.explain_humor_reward(content_id='content_123', user_id='user_456', reward_event_id='reward_789', dimensions=dimensions, confidence=0.85, ledger_context=ledger_context, timestamp=1234567890)
        assert explanation.content_id == 'content_123'
        assert explanation.user_id == 'user_456'
        assert explanation.reward_event_id == 'reward_789'
        assert explanation.dimensions == dimensions
        assert explanation.confidence == 0.85
        assert explanation.ledger_context == ledger_context
        assert explanation.final_bonus >= 0
        assert len(explanation.explanation_hash) > 0

    def test_explanation_deterministic_hash(self):
        """Test that explanations generate deterministic hashes"""
        dimensions = {'chronos': 0.8, 'lexicon': 0.6, 'surreal': 0.4, 'empathy': 0.9, 'critique': 0.7, 'slapstick': 0.3, 'meta': 0.5}
        ledger_context = {'views': 1000, 'laughs': 800, 'saves': 200, 'replays': 150, 'author_reputation': 0.9}
        explanation1 = self.explain_helper.explain_humor_reward(content_id='content_123', user_id='user_456', reward_event_id='reward_789', dimensions=dimensions, confidence=0.85, ledger_context=ledger_context, timestamp=1234567890)
        explanation2 = self.explain_helper.explain_humor_reward(content_id='content_123', user_id='user_456', reward_event_id='reward_789', dimensions=dimensions, confidence=0.85, ledger_context=ledger_context, timestamp=1234567890)
        assert explanation1.explanation_hash == explanation2.explanation_hash

    def test_explanation_consistency_verification(self):
        """Test explanation consistency verification"""
        dimensions = {'chronos': 0.8, 'lexicon': 0.6, 'surreal': 0.4, 'empathy': 0.9, 'critique': 0.7, 'slapstick': 0.3, 'meta': 0.5}
        ledger_context = {'views': 1000, 'laughs': 800, 'saves': 200, 'replays': 150, 'author_reputation': 0.9}
        explanation = self.explain_helper.explain_humor_reward(content_id='content_123', user_id='user_456', reward_event_id='reward_789', dimensions=dimensions, confidence=0.85, ledger_context=ledger_context, timestamp=1234567890)
        is_consistent = self.explain_helper.verify_explanation_consistency(explanation)
        assert is_consistent

    def test_simplified_explanation(self):
        """Test generating simplified explanation"""
        dimensions = {'chronos': 0.8, 'lexicon': 0.6, 'surreal': 0.4, 'empathy': 0.9, 'critique': 0.7, 'slapstick': 0.3, 'meta': 0.5}
        ledger_context = {'views': 1000, 'laughs': 800, 'saves': 200, 'replays': 150, 'author_reputation': 0.9}
        explanation = self.explain_helper.explain_humor_reward(content_id='content_123', user_id='user_456', reward_event_id='reward_789', dimensions=dimensions, confidence=0.85, ledger_context=ledger_context, timestamp=1234567890)
        simplified = self.explain_helper.get_simplified_explanation(explanation)
        assert 'summary' in simplified
        assert 'reason' in simplified
        assert 'reason_codes' in simplified
        assert 'breakdown' in simplified
        assert 'policy_info' in simplified
        assert 'verification' in simplified

    def test_explanation_reason_codes_humor_disabled(self):
        """Test that explanation includes HUMOR_DISABLED reason code when humor is disabled"""
        from v13.policy.humor_policy import HumorSignalPolicy, HumorPolicy
        disabled_policy = HumorSignalPolicy(policy=HumorPolicy(enabled=False, mode='rewarding', dimension_weights={'chronos': 0.15, 'lexicon': 0.1, 'surreal': 0.1, 'empathy': 0.2, 'critique': 0.15, 'slapstick': 0.1, 'meta': 0.2}, max_bonus_ratio=0.25, per_user_daily_cap_atr=1))
        disabled_explain_helper = HumorExplainabilityHelper(disabled_policy)
        dimensions = {'chronos': 0.8, 'lexicon': 0.6, 'surreal': 0.4, 'empathy': 0.9, 'critique': 0.7, 'slapstick': 0.3, 'meta': 0.5}
        ledger_context = {'views': 1000, 'laughs': 800, 'saves': 200, 'replays': 150, 'author_reputation': 0.9}
        explanation = disabled_explain_helper.explain_humor_reward(content_id='content_123', user_id='user_456', reward_event_id='reward_789', dimensions=dimensions, confidence=0.85, ledger_context=ledger_context, timestamp=1234567890)
        assert 'HUMOR_DISABLED' in explanation.reason_codes

    def test_explanation_reason_codes_recognition_only(self):
        """Test that explanation includes RECOGNITION_ONLY reason code when in recognition-only mode"""
        from v13.policy.humor_policy import HumorSignalPolicy, HumorPolicy
        recognition_policy = HumorSignalPolicy(policy=HumorPolicy(enabled=True, mode='recognition_only', dimension_weights={'chronos': 0.15, 'lexicon': 0.1, 'surreal': 0.1, 'empathy': 0.2, 'critique': 0.15, 'slapstick': 0.1, 'meta': 0.2}, max_bonus_ratio=0.25, per_user_daily_cap_atr=1))
        recognition_explain_helper = HumorExplainabilityHelper(recognition_policy)
        dimensions = {'chronos': 0.8, 'lexicon': 0.6, 'surreal': 0.4, 'empathy': 0.9, 'critique': 0.7, 'slapstick': 0.3, 'meta': 0.5}
        ledger_context = {'views': 1000, 'laughs': 800, 'saves': 200, 'replays': 150, 'author_reputation': 0.9}
        explanation = recognition_explain_helper.explain_humor_reward(content_id='content_123', user_id='user_456', reward_event_id='reward_789', dimensions=dimensions, confidence=0.85, ledger_context=ledger_context, timestamp=1234567890)
        assert 'RECOGNITION_ONLY' in explanation.reason_codes

    def test_explanation_reason_codes_humor_cap_applied(self):
        """Test that explanation includes HUMOR_CAP_APPLIED reason code when cap is applied"""
        from v13.policy.humor_policy import HumorSignalPolicy, HumorPolicy
        capped_policy = HumorSignalPolicy(policy=HumorPolicy(enabled=True, mode='rewarding', dimension_weights={'chronos': 1, 'lexicon': 1, 'surreal': 1, 'empathy': 1, 'critique': 1, 'slapstick': 1, 'meta': 1}, max_bonus_ratio=0.01, per_user_daily_cap_atr=1))
        capped_explain_helper = HumorExplainabilityHelper(capped_policy)
        dimensions = {'chronos': 1, 'lexicon': 1, 'surreal': 1, 'empathy': 1, 'critique': 1, 'slapstick': 1, 'meta': 1}
        ledger_context = {'views': 1000, 'laughs': 800, 'saves': 200, 'replays': 150, 'author_reputation': 0.9}
        explanation = capped_explain_helper.explain_humor_reward(content_id='content_123', user_id='user_456', reward_event_id='reward_789', dimensions=dimensions, confidence=1, ledger_context=ledger_context, timestamp=1234567890)
        assert 'HUMOR_CAP_APPLIED' in explanation.reason_codes

    def test_batch_explain_rewards(self):
        """Test batch explanation generation"""
        batch_data = [{'content_id': f'content_{i}', 'user_id': f'user_{i}', 'reward_event_id': f'reward_{i}', 'dimensions': {'chronos': 0.5 + i * 0.1, 'lexicon': 0.5, 'surreal': 0.5, 'empathy': 0.5, 'critique': 0.5, 'slapstick': 0.5, 'meta': 0.5}, 'confidence': 0.85 - i * 0.05, 'ledger_context': {'views': 100 + i * 10, 'laughs': 50 + i * 5, 'saves': 20 + i * 2, 'replays': 30 + i * 3, 'author_reputation': 0.5 + i * 0.1}, 'timestamp': 1234567890 + i} for i in range(3)]
        explanations = self.explain_helper.batch_explain_rewards(batch_data)
        assert len(explanations) == 3
        for i, explanation in enumerate(explanations):
            assert explanation.content_id == f'content_{i}'
            assert explanation.user_id == f'user_{i}'
            assert explanation.reward_event_id == f'reward_{i}'

    def test_reason_code_combinations(self):
        """Test various reason-code combinations (e.g., disabled + recognition, cap + daily limit)"""
        from v13.policy.humor_policy import HumorSignalPolicy, HumorPolicy
        disabled_policy = HumorSignalPolicy(policy=HumorPolicy(enabled=False, mode='recognition_only', dimension_weights={'chronos': 0.15, 'lexicon': 0.1, 'surreal': 0.1, 'empathy': 0.2, 'critique': 0.15, 'slapstick': 0.1, 'meta': 0.2}, max_bonus_ratio=0.25, per_user_daily_cap_atr=1))
        disabled_explain_helper = HumorExplainabilityHelper(disabled_policy)
        dimensions = {'chronos': 0.8, 'lexicon': 0.6, 'surreal': 0.4, 'empathy': 0.9, 'critique': 0.7, 'slapstick': 0.3, 'meta': 0.5}
        ledger_context = {'views': 1000, 'laughs': 800, 'saves': 200, 'replays': 150, 'author_reputation': 0.9}
        explanation = disabled_explain_helper.explain_humor_reward(content_id='content_123', user_id='user_456', reward_event_id='reward_789', dimensions=dimensions, confidence=0.85, ledger_context=ledger_context, timestamp=1234567890)
        assert 'HUMOR_DISABLED' in explanation.reason_codes
        assert len(explanation.reason_codes) == 1
        recognition_policy = HumorSignalPolicy(policy=HumorPolicy(enabled=True, mode='recognition_only', dimension_weights={'chronos': 0.15, 'lexicon': 0.1, 'surreal': 0.1, 'empathy': 0.2, 'critique': 0.15, 'slapstick': 0.1, 'meta': 0.2}, max_bonus_ratio=0.25, per_user_daily_cap_atr=1))
        recognition_explain_helper = HumorExplainabilityHelper(recognition_policy)
        explanation2 = recognition_explain_helper.explain_humor_reward(content_id='content_123', user_id='user_456', reward_event_id='reward_789', dimensions=dimensions, confidence=0.85, ledger_context=ledger_context, timestamp=1234567890)
        assert 'RECOGNITION_ONLY' in explanation2.reason_codes
        assert len(explanation2.reason_codes) == 1

    def test_explanation_hash_stability(self):
        """Test stability of explanation hashes under replay"""
        dimensions = {'chronos': 0.8, 'lexicon': 0.6, 'surreal': 0.4, 'empathy': 0.9, 'critique': 0.7, 'slapstick': 0.3, 'meta': 0.5}
        ledger_context = {'views': 1000, 'laughs': 800, 'saves': 200, 'replays': 150, 'author_reputation': 0.9}
        hashes = []
        for i in range(5):
            explanation = self.explain_helper.explain_humor_reward(content_id='content_123', user_id='user_456', reward_event_id='reward_789', dimensions=dimensions, confidence=0.85, ledger_context=ledger_context, timestamp=1234567890)
            hashes.append(explanation.explanation_hash)
        assert len(set(hashes)) == 1
        assert len(hashes[0]) == 64
        assert all((c in '0123456789abcdef' for c in hashes[0]))

    def test_api_response_shapes(self):
        """Test API response shapes for humor-explanation endpoints"""
        dimensions = {'chronos': 0.8, 'lexicon': 0.6, 'surreal': 0.4, 'empathy': 0.9, 'critique': 0.7, 'slapstick': 0.3, 'meta': 0.5}
        ledger_context = {'views': 1000, 'laughs': 800, 'saves': 200, 'replays': 150, 'author_reputation': 0.9}
        explanation = self.explain_helper.explain_humor_reward(content_id='content_123', user_id='user_456', reward_event_id='reward_789', dimensions=dimensions, confidence=0.85, ledger_context=ledger_context, timestamp=1234567890)
        assert hasattr(explanation, 'content_id')
        assert hasattr(explanation, 'user_id')
        assert hasattr(explanation, 'reward_event_id')
        assert hasattr(explanation, 'timestamp')
        assert hasattr(explanation, 'dimensions')
        assert hasattr(explanation, 'confidence')
        assert hasattr(explanation, 'ledger_context')
        assert hasattr(explanation, 'policy_version')
        assert hasattr(explanation, 'policy_hash')
        assert hasattr(explanation, 'dimension_weights')
        assert hasattr(explanation, 'weighted_scores')
        assert hasattr(explanation, 'weighted_sum')
        assert hasattr(explanation, 'confidence_factor')
        assert hasattr(explanation, 'base_bonus')
        assert hasattr(explanation, 'cap_applied')
        assert hasattr(explanation, 'final_bonus')
        assert hasattr(explanation, 'policy_settings')
        assert hasattr(explanation, 'explanation_hash')
        assert hasattr(explanation, 'reason_codes')
        simplified = self.explain_helper.get_simplified_explanation(explanation)
        required_keys = ['summary', 'reason', 'reason_codes', 'breakdown', 'policy_info', 'verification']
        for key in sorted(required_keys):
            assert key in simplified
        assert 'dimensions' in simplified['breakdown']
        assert 'confidence' in simplified['breakdown']
        assert 'final_bonus' in simplified['breakdown']
        assert 'version' in simplified['policy_info']
        assert 'hash' in simplified['policy_info']
        assert 'was_capped' in simplified['policy_info']
        assert 'hash' in simplified['verification']
        assert 'consistent' in simplified['verification']
if __name__ == '__main__':
    pytest.main([__file__])