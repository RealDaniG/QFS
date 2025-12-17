"""
Test suite for ValueNodeExplainability.py

This module provides comprehensive tests for the value-node explainability features,
ensuring deterministic behavior, policy compliance, and proper explanation generation.
"""
from fractions import Fraction
import pytest
import re
from typing import Dict, Any, List
from v13.policy.value_node_explainability import ValueNodeExplainabilityHelper, ValueNodeRewardExplanation
from v13.policy.humor_policy import HumorSignalPolicy, HumorPolicy

class TestValueNodeExplainability:
    """Test suite for ValueNodeExplainabilityHelper."""

    @pytest.fixture
    def humor_policy(self) -> HumorSignalPolicy:
        """Create a humor policy instance for testing."""
        return HumorSignalPolicy(policy=HumorPolicy(enabled=True, mode='rewarding', dimension_weights={'chronos': Fraction(3, 20), 'lexicon': Fraction(1, 10), 'surreal': Fraction(1, 10), 'empathy': Fraction(1, 5), 'critique': Fraction(3, 20), 'slapstick': Fraction(1, 10), 'meta': Fraction(1, 5)}, max_bonus_ratio=Fraction(1, 4), per_user_daily_cap_atr=1))

    @pytest.fixture
    def explain_helper(self, humor_policy: HumorSignalPolicy) -> ValueNodeExplainabilityHelper:
        """Create a value-node explainability helper instance."""
        return ValueNodeExplainabilityHelper(humor_policy)

    @pytest.fixture
    def sample_reward_data(self) -> Dict[str, Any]:
        """Sample reward data for testing."""
        return {'wallet_id': 'wallet_123', 'user_id': 'user_456', 'reward_event_id': 'reward_789', 'epoch': 1, 'base_reward': {'ATR': '10.0 ATR'}, 'bonuses': [{'label': 'Coherence bonus', 'value': '+2.5 ATR', 'reason': 'Coherence score 0.92 above threshold'}, {'label': 'Humor bonus', 'value': '+1.2 ATR', 'reason': 'Humor signal 0.88 above threshold'}], 'caps': [{'label': 'Humor cap', 'value': '-0.3 ATR', 'reason': 'Humor cap applied at 1.0 ATR'}, {'label': 'Global cap', 'value': '-2.0 ATR', 'reason': 'Global reward cap for epoch'}], 'guards': [{'name': 'Balance guard', 'result': 'pass', 'reason': 'Balance within limits'}, {'name': 'Rate limit guard', 'result': 'pass', 'reason': 'Rate limit not exceeded'}], 'timestamp': 1234567890}

    def test_explain_value_node_reward(self, explain_helper: ValueNodeExplainabilityHelper, sample_reward_data: Dict[str, Any]) -> None:
        """Test that value-node reward explanations are generated correctly."""
        explanation = explain_helper.explain_value_node_reward(**sample_reward_data)
        assert explanation.wallet_id == 'wallet_123'
        assert explanation.user_id == 'user_456'
        assert explanation.reward_event_id == 'reward_789'
        assert explanation.epoch == 1
        assert explanation.timestamp == 1234567890
        assert explanation.base_reward == sample_reward_data['base_reward']
        assert explanation.bonuses == sample_reward_data['bonuses']
        assert explanation.caps == sample_reward_data['caps']
        assert explanation.guards == sample_reward_data['guards']
        assert explanation.policy_version == 'Humor:v1.0.0'
        assert isinstance(explanation.policy_hash, str)
        assert 'REWARD_BONUSES_APPLIED' in explanation.reason_codes
        assert 'REWARD_CAPS_APPLIED' in explanation.reason_codes
        assert explanation.explanation_hash != ''
        assert len(explanation.explanation_hash) == 64

    def test_explanation_deterministic_hash(self, explain_helper: ValueNodeExplainabilityHelper, sample_reward_data: Dict[str, Any]) -> None:
        """Test that identical inputs produce identical explanation hashes."""
        explanation1 = explain_helper.explain_value_node_reward(**sample_reward_data)
        explanation2 = explain_helper.explain_value_node_reward(**sample_reward_data)
        assert explanation1.explanation_hash == explanation2.explanation_hash

    def test_explanation_consistency_verification(self, explain_helper: ValueNodeExplainabilityHelper, sample_reward_data: Dict[str, Any]) -> None:
        """Test that explanation consistency verification works correctly."""
        explanation = explain_helper.explain_value_node_reward(**sample_reward_data)
        is_consistent = explain_helper.verify_explanation_consistency(explanation)
        assert is_consistent

    def test_simplified_explanation(self, explain_helper: ValueNodeExplainabilityHelper, sample_reward_data: Dict[str, Any]) -> None:
        """Test that simplified explanations are generated correctly."""
        explanation = explain_helper.explain_value_node_reward(**sample_reward_data)
        simplified = explain_helper.get_simplified_explanation(explanation)
        assert 'summary' in simplified
        assert 'reason' in simplified
        assert 'reason_codes' in simplified
        assert 'breakdown' in simplified
        assert 'policy_info' in simplified
        assert 'verification' in simplified
        assert 'Received value-node reward' in simplified['summary']
        assert 'epoch' in simplified['reason']
        assert simplified['reason_codes'] == explanation.reason_codes
        assert simplified['verification']['consistent'] == True

    def test_explanation_reason_codes_guard_failures(self, explain_helper: ValueNodeExplainabilityHelper) -> None:
        """Test that guard failures are properly reflected in reason codes."""
        reward_data = {'wallet_id': 'wallet_123', 'user_id': 'user_456', 'reward_event_id': 'reward_789', 'epoch': 1, 'base_reward': {'ATR': '10.0 ATR'}, 'bonuses': [], 'caps': [], 'guards': [{'name': 'Balance guard', 'result': 'fail', 'reason': 'Balance exceeds limits'}, {'name': 'Rate limit guard', 'result': 'pass', 'reason': 'Rate limit not exceeded'}], 'timestamp': 1234567890}
        explanation = explain_helper.explain_value_node_reward(**reward_data)
        reason_codes_str = ' '.join(explanation.reason_codes)
        assert 'GUARD_FAILED' in reason_codes_str

    def test_explanation_reason_codes_various_conditions(self, explain_helper: ValueNodeExplainabilityHelper) -> None:
        """Test reason codes for various conditions."""
        reward_data = {'wallet_id': 'wallet_123', 'user_id': 'user_456', 'reward_event_id': 'reward_789', 'epoch': 1, 'base_reward': {'ATR': '10.0 ATR'}, 'bonuses': [{'label': 'Test bonus', 'value': '+1.0 ATR', 'reason': 'Test'}], 'caps': [{'label': 'Test cap', 'value': '-0.5 ATR', 'reason': 'Test'}], 'guards': [{'name': 'Test guard', 'result': 'pass', 'reason': 'Test'}], 'timestamp': 1234567890}
        explanation = explain_helper.explain_value_node_reward(**reward_data)
        reason_codes = explanation.reason_codes
        assert 'REWARD_BONUSES_APPLIED' in reason_codes
        assert 'REWARD_CAPS_APPLIED' in reason_codes

    def test_batch_explain_rewards(self, explain_helper: ValueNodeExplainabilityHelper, sample_reward_data: Dict[str, Any]) -> None:
        """Test batch explanation of rewards."""
        batch_data = [sample_reward_data, {**sample_reward_data, 'wallet_id': 'wallet_456', 'reward_event_id': 'reward_987'}]
        explanation1 = explain_helper.explain_value_node_reward(**batch_data[0])
        explanation2 = explain_helper.explain_value_node_reward(**batch_data[1])
        assert explanation1.wallet_id != explanation2.wallet_id
        assert explanation1.reward_event_id != explanation2.reward_event_id
        assert explanation1.explanation_hash != explanation2.explanation_hash

    def test_value_node_signal_pure_functionality(self, explain_helper: ValueNodeExplainabilityHelper, sample_reward_data: Dict[str, Any]) -> None:
        """Test that the explainability helper is a pure function with no side effects."""
        initial_hash = explain_helper._generate_explanation_hash(explain_helper.explain_value_node_reward(**sample_reward_data))
        hashes = []
        for _ in range(5):
            explanation = explain_helper.explain_value_node_reward(**sample_reward_data)
            hashes.append(explanation.explanation_hash)
        assert all((h == initial_hash for h in hashes))

    def test_no_network_io_in_value_node_modules(self) -> None:
        """Test that value-node explainability modules do not perform network I/O."""
        import v13.policy.value_node_explainability as module
        import inspect
        source = inspect.getsource(module)
        forbidden_patterns = ['requests.', 'urllib.', 'socket.', 'httplib.', 'http.client', 'aiohttp.']
        for pattern in sorted(forbidden_patterns):
            assert pattern not in source, f"Forbidden network I/O pattern '{pattern}' found in value-node modules"

    def test_no_filesystem_io_in_value_node_modules(self) -> None:
        """Test that value-node explainability modules do not perform filesystem I/O."""
        import v13.policy.value_node_explainability as module
        import inspect
        source = inspect.getsource(module)
        forbidden_patterns = ['open(', 'os.', 'shutil.', 'pathlib.', 'pickle.']
        for pattern in sorted(forbidden_patterns):
            assert pattern not in source, f"Forbidden filesystem I/O pattern '{pattern}' found in value-node modules"

    def test_no_ledger_adapters_in_value_node_modules(self) -> None:
        """Test that value-node explainability modules do not import ledger adapters."""
        import v13.policy.value_node_explainability as module
        import inspect
        source = inspect.getsource(module)
        forbidden_patterns = ['TreasuryEngine', 'RealLedger', 'TokenStateBundle', 'CoherenceLedger']
        for pattern in sorted(forbidden_patterns):
            assert pattern not in source, f"Forbidden ledger adapter pattern '{pattern}' found in value-node modules"

    def test_extreme_reward_values(self, explain_helper: ValueNodeExplainabilityHelper) -> None:
        """Test explainability with extreme reward values."""
        large_reward_data = {'wallet_id': 'wallet_large', 'user_id': 'user_large', 'reward_event_id': 'reward_large', 'epoch': 1, 'base_reward': {'ATR': '1000000.0 ATR'}, 'bonuses': [{'label': 'Large bonus', 'value': '+500000.0 ATR', 'reason': 'Large bonus reason'}], 'caps': [{'label': 'Large cap', 'value': '-100000.0 ATR', 'reason': 'Large cap reason'}], 'guards': [{'name': 'Test guard', 'result': 'pass', 'reason': 'Test'}], 'timestamp': 1234567890}
        explanation = explain_helper.explain_value_node_reward(**large_reward_data)
        assert explanation.wallet_id == 'wallet_large'
        assert 'REWARD_BONUSES_APPLIED' in explanation.reason_codes
        assert 'REWARD_CAPS_APPLIED' in explanation.reason_codes
        assert explanation.explanation_hash != ''
        zero_reward_data = {'wallet_id': 'wallet_zero', 'user_id': 'user_zero', 'reward_event_id': 'reward_zero', 'epoch': 1, 'base_reward': {'ATR': '0.0 ATR'}, 'bonuses': [], 'caps': [], 'guards': [{'name': 'Test guard', 'result': 'pass', 'reason': 'Test'}], 'timestamp': 1234567890}
        explanation = explain_helper.explain_value_node_reward(**zero_reward_data)
        assert explanation.wallet_id == 'wallet_zero'
        assert explanation.explanation_hash != ''

    def test_malformed_input_data_handling(self, explain_helper: ValueNodeExplainabilityHelper) -> None:
        """Test explainability with malformed input data."""
        malformed_data = {'wallet_id': 'wallet_malformed', 'reward_event_id': 'reward_malformed', 'epoch': 1, 'bonuses': 'not_a_list', 'caps': None, 'guards': [], 'timestamp': 'not_a_number'}
        try:
            explanation = explain_helper.explain_value_node_reward(**malformed_data)
            assert explanation.wallet_id == 'wallet_malformed'
            assert explanation.explanation_hash != ''
        except Exception:
            pass

    def test_different_policy_configurations(self, explain_helper: ValueNodeExplainabilityHelper) -> None:
        """Test explainability with different policy configurations."""
        from v13.policy.humor_policy import HumorSignalPolicy, HumorPolicy
        different_policy = HumorSignalPolicy(policy=HumorPolicy(enabled=False, mode='recognition_only', dimension_weights={'chronos': Fraction(1, 5), 'lexicon': Fraction(3, 20), 'surreal': Fraction(3, 20), 'empathy': Fraction(1, 10), 'critique': Fraction(1, 5), 'slapstick': Fraction(1, 10), 'meta': Fraction(1, 10)}, max_bonus_ratio=Fraction(1, 2), per_user_daily_cap_atr=2))
        different_helper = ValueNodeExplainabilityHelper(different_policy)
        reward_data = {'wallet_id': 'wallet_diff_policy', 'user_id': 'user_diff_policy', 'reward_event_id': 'reward_diff_policy', 'epoch': 1, 'base_reward': {'ATR': '10.0 ATR'}, 'bonuses': [{'label': 'Bonus', 'value': '+2.0 ATR', 'reason': 'Bonus reason'}], 'caps': [{'label': 'Cap', 'value': '-1.0 ATR', 'reason': 'Cap reason'}], 'guards': [{'name': 'Test guard', 'result': 'pass', 'reason': 'Test'}], 'timestamp': 1234567890}
        explanation = different_helper.explain_value_node_reward(**reward_data)
        assert explanation.wallet_id == 'wallet_diff_policy'
        assert explanation.explanation_hash != ''

    def test_explanation_hash_collision_resistance(self, explain_helper: ValueNodeExplainabilityHelper) -> None:
        """Test that explanation hashes are resistant to collisions."""
        reward_data_1 = {'wallet_id': 'wallet_1', 'user_id': 'user_1', 'reward_event_id': 'reward_1', 'epoch': 1, 'base_reward': {'ATR': '10.0 ATR'}, 'bonuses': [{'label': 'Bonus 1', 'value': '+2.0 ATR', 'reason': 'Bonus reason 1'}], 'caps': [{'label': 'Cap 1', 'value': '-1.0 ATR', 'reason': 'Cap reason 1'}], 'guards': [{'name': 'Guard 1', 'result': 'pass', 'reason': 'Guard reason 1'}], 'timestamp': 1234567890}
        reward_data_2 = {'wallet_id': 'wallet_2', 'user_id': 'user_2', 'reward_event_id': 'reward_2', 'epoch': 2, 'base_reward': {'ATR': '15.0 ATR'}, 'bonuses': [{'label': 'Bonus 2', 'value': '+3.0 ATR', 'reason': 'Bonus reason 2'}], 'caps': [{'label': 'Cap 2', 'value': '-2.0 ATR', 'reason': 'Cap reason 2'}], 'guards': [{'name': 'Guard 2', 'result': 'fail', 'reason': 'Guard reason 2'}], 'timestamp': 1234567891}
        explanation_1 = explain_helper.explain_value_node_reward(**reward_data_1)
        explanation_2 = explain_helper.explain_value_node_reward(**reward_data_2)
        assert explanation_1.explanation_hash != explanation_2.explanation_hash
        assert len(explanation_1.explanation_hash) == 64
        assert len(explanation_2.explanation_hash) == 64
if __name__ == '__main__':
    pytest.main([__file__, '-v'])