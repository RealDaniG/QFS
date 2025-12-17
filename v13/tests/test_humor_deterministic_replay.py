"""
Meta-test to verify deterministic replay tests on fixed fixtures for humor modules.
"""
import pytest
import json
import hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from v13.ATLAS.src.signals.humor import HumorSignalAddon
from v13.policy.humor_policy import HumorSignalPolicy, HumorPolicy
from v13.policy.humor_observatory import HumorSignalObservatory, HumorSignalSnapshot
from v13.policy.humor_explainability import HumorExplainabilityHelper

class TestHumorDeterministicReplay:
    """Meta-test suite for deterministic replay of humor modules"""

    def setup_method(self):
        """Setup test environment with fixed fixtures"""
        self.fixed_content = "Why don't scientists trust atoms? Because they make up everything!"
        self.fixed_context = {'views': 1000, 'laughs': 800, 'saves': 200, 'replays': 150, 'author_reputation': 800000000000000000}
        self.humor_addon = HumorSignalAddon()
        self.humor_policy = HumorSignalPolicy(policy=HumorPolicy(enabled=True, mode='rewarding', dimension_weights={'chronos': 0.15, 'lexicon': 0.1, 'surreal': 0.1, 'empathy': 0.2, 'critique': 0.15, 'slapstick': 0.1, 'meta': 0.2}, max_bonus_ratio=0.25, per_user_daily_cap_atr=1))
        self.observatory = HumorSignalObservatory()
        self.explainability = HumorExplainabilityHelper(self.humor_policy)

    def test_humor_signal_deterministic_replay(self):
        """Test that HumorSignalAddon produces identical results for identical inputs"""
        results = []
        for i in range(5):
            result = self.humor_addon.evaluate(self.fixed_content, self.fixed_context)
            results.append(result)
        for i in range(1, len(results)):
            assert abs(results[0].confidence - results[i].confidence) < 1e-10
            dims1 = results[0].metadata.get('dimensions', {})
            dims2 = results[i].metadata.get('dimensions', {})
            assert dims1 == dims2
            assert results[0].result_hash == results[i].result_hash
            assert results[0].content_hash == results[i].content_hash
            assert results[0].context_hash == results[i].context_hash

    def test_humor_policy_deterministic_replay(self):
        """Test that HumorSignalPolicy produces identical results for identical inputs"""
        signal_result = self.humor_addon.evaluate(self.fixed_content, self.fixed_context)
        dimensions = signal_result.metadata.get('dimensions', {})
        confidence = signal_result.confidence
        calculations = []
        for i in range(5):
            calc = self.humor_policy.calculate_humor_bonus(dimensions, confidence)
            calculations.append(calc)
        for i in range(1, len(calculations)):
            assert abs(calculations[0].bonus_factor - calculations[i].bonus_factor) < 1e-10
            assert calculations[0].dimensions_used == calculations[i].dimensions_used
            assert calculations[0].weights_applied == calculations[i].weights_applied
            assert calculations[0].policy_version == calculations[i].policy_version

    def test_humor_observatory_deterministic_replay(self):
        """Test that HumorSignalObservatory produces identical reports for identical inputs"""
        timestamp = 1234567890
        for i in range(3):
            signal_result = self.humor_addon.evaluate(self.fixed_content, self.fixed_context)
            dimensions = signal_result.metadata.get('dimensions', {})
            confidence = signal_result.confidence
            bonus_calc = self.humor_policy.calculate_humor_bonus(dimensions, confidence)
            snapshot = HumorSignalSnapshot(timestamp=timestamp + i, content_id=f'content_{i}', dimensions=dimensions, confidence=confidence, bonus_factor=bonus_calc.bonus_factor, policy_version=bonus_calc.policy_version)
            self.observatory.record_signal(snapshot)
        reports = []
        for i in range(3):
            report = self.observatory.get_observability_report(policy_version=self.humor_policy.policy.version, policy_hash=self.humor_policy.policy.hash)
            reports.append(report)
        for i in range(1, len(reports)):
            assert reports[0].total_signals_processed == reports[i].total_signals_processed
            assert abs(reports[0].average_confidence - reports[i].average_confidence) < 1e-10
            assert reports[0].dimension_averages == reports[i].dimension_averages
            assert reports[0].bonus_statistics == reports[i].bonus_statistics

    def test_humor_explainability_deterministic_replay(self):
        """Test that HumorExplainabilityHelper produces identical explanations for identical inputs"""
        signal_result = self.humor_addon.evaluate(self.fixed_content, self.fixed_context)
        dimensions = signal_result.metadata.get('dimensions', {})
        confidence = signal_result.confidence
        explanation_data = {'content_id': 'test_content_123', 'user_id': 'test_user_456', 'reward_event_id': 'test_reward_789', 'dimensions': dimensions, 'confidence': confidence, 'ledger_context': self.fixed_context, 'timestamp': 1234567890}
        explanations = []
        for i in range(5):
            explanation = self.explainability.explain_humor_reward(**explanation_data)
            explanations.append(explanation)
        for i in range(1, len(explanations)):
            assert explanations[0].content_id == explanations[i].content_id
            assert explanations[0].user_id == explanations[i].user_id
            assert explanations[0].reward_event_id == explanations[i].reward_event_id
            assert abs(explanations[0].final_bonus - explanations[i].final_bonus) < 1e-10
            assert explanations[0].dimensions == explanations[i].dimensions
            assert explanations[0].dimension_weights == explanations[i].dimension_weights
            assert explanations[0].explanation_hash == explanations[i].explanation_hash
            assert explanations[0].reason_codes == explanations[i].reason_codes

    def test_cross_module_deterministic_consistency(self):
        """Test that all humor modules work consistently together"""
        signal_result = self.humor_addon.evaluate(self.fixed_content, self.fixed_context)
        dimensions = signal_result.metadata.get('dimensions', {})
        confidence = signal_result.confidence
        bonus_calc = self.humor_policy.calculate_humor_bonus(dimensions, confidence)
        snapshot = HumorSignalSnapshot(timestamp=1234567890, content_id='consistency_test_content', dimensions=dimensions, confidence=confidence, bonus_factor=bonus_calc.bonus_factor, policy_version=bonus_calc.policy_version)
        self.observatory.record_signal(snapshot)
        explanation = self.explainability.explain_humor_reward(content_id='consistency_test_content', user_id='consistency_test_user', reward_event_id='consistency_test_reward', dimensions=dimensions, confidence=confidence, ledger_context=self.fixed_context, timestamp=1234567890)
        report = self.observatory.get_observability_report(policy_version=self.humor_policy.policy.version, policy_hash=self.humor_policy.policy.hash)
        assert report.policy_version == bonus_calc.policy_version
        assert report.policy_version == explanation.policy_version
        assert len(report.dimension_averages) == 7
if __name__ == '__main__':
    pytest.main([__file__])