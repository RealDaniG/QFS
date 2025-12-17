"""
Tests for the humor policy module
"""
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from v13.policy.humor_policy import HumorSignalPolicy, HumorPolicyConfig, HumorPolicy

class TestHumorPolicy:
    """Test suite for the humor policy"""

    def setup_method(self):
        """Setup test environment"""
        self.humor_policy = HumorSignalPolicy(policy=HumorPolicy(enabled=True, mode='rewarding', dimension_weights={'chronos': 0.15, 'lexicon': 0.1, 'surreal': 0.1, 'empathy': 0.2, 'critique': 0.15, 'slapstick': 0.1, 'meta': 0.2}, max_bonus_ratio=0.25, per_user_daily_cap_atr=1.0))

    def test_humor_policy_struct_creation(self):
        """Test that HumorPolicy struct is created correctly"""
        policy = HumorPolicy(enabled=True, mode='rewarding', dimension_weights={'chronos': 0.15, 'lexicon': 0.1, 'surreal': 0.1, 'empathy': 0.2, 'critique': 0.15, 'slapstick': 0.1, 'meta': 0.2}, max_bonus_ratio=0.25, per_user_daily_cap_atr=1.0)
        assert policy.enabled == True
        assert policy.mode == 'rewarding'
        assert policy.max_bonus_ratio == 0.25
        assert policy.per_user_daily_cap_atr == 1.0
        assert len(policy.dimension_weights) == 7
        assert policy.hash != ''

    def test_normal_humor_bonus_calculation(self):
        """Test normal humor bonus calculation"""
        dimensions = {'chronos': 0.8, 'lexicon': 0.6, 'surreal': 0.4, 'empathy': 0.9, 'critique': 0.7, 'slapstick': 0.3, 'meta': 0.5}
        confidence = 0.85
        bonus_calc = self.humor_policy.calculate_humor_bonus(dimensions, confidence)
        assert bonus_calc.bonus_factor >= 0.0
        assert bonus_calc.bonus_factor <= self.humor_policy.policy.max_bonus_ratio
        assert bonus_calc.dimensions_used == dimensions
        assert bonus_calc.weights_applied == self.humor_policy.policy.dimension_weights
        assert bonus_calc.policy_version == self.humor_policy.policy.version

    def test_humor_disabled_returns_zero_bonus(self):
        """Test that disabled humor policy returns zero bonus"""
        self.humor_policy.policy.enabled = False
        dimensions = {'chronos': 0.8, 'lexicon': 0.6, 'surreal': 0.4, 'empathy': 0.9, 'critique': 0.7, 'slapstick': 0.3, 'meta': 0.5}
        confidence = 0.85
        bonus_calc = self.humor_policy.calculate_humor_bonus(dimensions, confidence)
        assert bonus_calc.bonus_factor == 0.0

    def test_humor_recognition_only_returns_zero_bonus(self):
        """Test that recognition-only humor policy returns zero bonus"""
        self.humor_policy.policy.enabled = True
        self.humor_policy.policy.mode = 'recognition_only'
        dimensions = {'chronos': 0.8, 'lexicon': 0.6, 'surreal': 0.4, 'empathy': 0.9, 'critique': 0.7, 'slapstick': 0.3, 'meta': 0.5}
        confidence = 0.85
        bonus_calc = self.humor_policy.calculate_humor_bonus(dimensions, confidence)
        assert bonus_calc.bonus_factor == 0.0

    def test_humor_bonus_respects_cap(self):
        """Test that humor bonus respects the maximum cap"""
        dimensions = {'chronos': 1.0, 'lexicon': 1.0, 'surreal': 1.0, 'empathy': 1.0, 'critique': 1.0, 'slapstick': 1.0, 'meta': 1.0}
        confidence = 1.0
        bonus_calc = self.humor_policy.calculate_humor_bonus(dimensions, confidence)
        assert bonus_calc.bonus_factor <= self.humor_policy.policy.max_bonus_ratio
        if bonus_calc.bonus_factor == self.humor_policy.policy.max_bonus_ratio:
            assert bonus_calc.cap_applied == self.humor_policy.policy.max_bonus_ratio

    def test_daily_cap_field_exists(self):
        """Test that daily cap field exists in policy struct"""
        policy_with_cap = HumorPolicy(enabled=True, mode='rewarding', dimension_weights={'chronos': 0.15, 'lexicon': 0.1, 'surreal': 0.1, 'empathy': 0.2, 'critique': 0.15, 'slapstick': 0.1, 'meta': 0.2}, max_bonus_ratio=0.25, per_user_daily_cap_atr=1.0)
        assert hasattr(policy_with_cap, 'per_user_daily_cap_atr')
        assert policy_with_cap.per_user_daily_cap_atr == 1.0

    def test_deterministic_behavior(self):
        """Test that humor policy produces deterministic results"""
        dimensions = {'chronos': 0.8, 'lexicon': 0.6, 'surreal': 0.4, 'empathy': 0.9, 'critique': 0.7, 'slapstick': 0.3, 'meta': 0.5}
        confidence = 0.85
        bonus_calc1 = self.humor_policy.calculate_humor_bonus(dimensions, confidence)
        bonus_calc2 = self.humor_policy.calculate_humor_bonus(dimensions, confidence)
        assert bonus_calc1.bonus_factor == bonus_calc2.bonus_factor
        assert bonus_calc1.dimensions_used == bonus_calc2.dimensions_used
        assert bonus_calc1.weights_applied == bonus_calc2.weights_applied
        assert bonus_calc1.policy_version == bonus_calc2.policy_version

    def test_negative_or_malformed_vectors_safely_handled(self):
        """Test that negative or malformed vectors are safely handled"""
        negative_dimensions = {'chronos': -0.5, 'lexicon': 0.6, 'surreal': 1.5, 'empathy': 0.9, 'critique': -0.2, 'slapstick': 0.3, 'meta': 1.2}
        confidence = 0.85
        bonus_calc = self.humor_policy.calculate_humor_bonus(negative_dimensions, confidence)
        assert bonus_calc.bonus_factor >= 0.0
        assert bonus_calc.bonus_factor <= self.humor_policy.policy.max_bonus_ratio
        incomplete_dimensions = {'chronos': 0.8, 'lexicon': 0.6}
        bonus_calc_incomplete = self.humor_policy.calculate_humor_bonus(incomplete_dimensions, confidence)
        assert bonus_calc_incomplete.bonus_factor >= 0.0
        try:
            invalid_dimensions = {'chronos': 'invalid', 'lexicon': 0.6, 'surreal': 0.4, 'empathy': 0.9, 'critique': 0.7, 'slapstick': 0.3, 'meta': 0.5}
        except Exception:
            pass

    def test_observability_stats_updated(self):
        """Test that observability statistics are updated correctly"""
        initial_stats = self.humor_policy.get_observability_stats()
        initial_count = initial_stats.total_signals_processed
        dimensions = {'chronos': 0.8, 'lexicon': 0.6, 'surreal': 0.4, 'empathy': 0.9, 'critique': 0.7, 'slapstick': 0.3, 'meta': 0.5}
        confidence = 0.85
        for i in range(5):
            self.humor_policy.calculate_humor_bonus(dimensions, confidence)
        final_stats = self.humor_policy.get_observability_stats()
        assert final_stats.total_signals_processed == initial_count + 5
        for dimension in sorted(dimensions):
            assert len(final_stats.dimension_distributions[dimension]) == 5

    def test_policy_explanation_generation(self):
        """Test that policy explanation is generated correctly"""
        dimensions = {'chronos': 0.8, 'lexicon': 0.6, 'surreal': 0.4, 'empathy': 0.9, 'critique': 0.7, 'slapstick': 0.3, 'meta': 0.5}
        confidence = 0.85
        explanation = self.humor_policy.get_policy_explanation(dimensions, confidence)
        assert 'policy_version' in explanation
        assert 'policy_hash' in explanation
        assert 'dimensions' in explanation
        assert 'confidence' in explanation
        assert 'weights' in explanation
        assert 'weighted_scores' in explanation
        assert 'final_bonus' in explanation
        assert 'policy_settings' in explanation
        assert explanation['dimensions'] == dimensions
        assert explanation['confidence'] == confidence
        assert explanation['final_bonus'] >= 0.0

    def test_humor_rewarding_mode_produces_nonzero_bonus(self):
        """Test that rewarding mode produces nonzero bonus when enabled"""
        self.humor_policy.policy.enabled = True
        self.humor_policy.policy.mode = 'rewarding'
        dimensions = {'chronos': 0.8, 'lexicon': 0.6, 'surreal': 0.4, 'empathy': 0.9, 'critique': 0.7, 'slapstick': 0.3, 'meta': 0.5}
        confidence = 0.85
        bonus_calc = self.humor_policy.calculate_humor_bonus(dimensions, confidence)
        assert bonus_calc.bonus_factor > 0.0
        assert bonus_calc.bonus_factor <= self.humor_policy.policy.max_bonus_ratio

    def test_all_mode_combinations_with_boundary_values(self):
        """Test all mode combinations with boundary values (very small and near-cap bonuses)"""
        dimensions = {'chronos': 0.8, 'lexicon': 0.6, 'surreal': 0.4, 'empathy': 0.9, 'critique': 0.7, 'slapstick': 0.3, 'meta': 0.5}
        small_confidence = 0.001
        bonus_calc_small = self.humor_policy.calculate_humor_bonus(dimensions, small_confidence)
        assert bonus_calc_small.bonus_factor >= 0.0
        max_confidence = 1.0
        bonus_calc_max = self.humor_policy.calculate_humor_bonus(dimensions, max_confidence)
        assert bonus_calc_max.bonus_factor <= self.humor_policy.policy.max_bonus_ratio
        modes = ['recognition_only', 'rewarding']
        for mode in sorted(modes):
            test_policy = HumorSignalPolicy(policy=HumorPolicy(enabled=True, mode=mode, dimension_weights={'chronos': 0.15, 'lexicon': 0.1, 'surreal': 0.1, 'empathy': 0.2, 'critique': 0.15, 'slapstick': 0.1, 'meta': 0.2}, max_bonus_ratio=0.25, per_user_daily_cap_atr=1.0))
            bonus_calc = test_policy.calculate_humor_bonus(dimensions, 0.85)
            if mode == 'rewarding':
                assert bonus_calc.bonus_factor > 0.0
                assert bonus_calc.bonus_factor <= test_policy.policy.max_bonus_ratio
            else:
                assert bonus_calc.bonus_factor == 0.0
        disabled_policy = HumorSignalPolicy(policy=HumorPolicy(enabled=False, mode='rewarding', dimension_weights={'chronos': 0.15, 'lexicon': 0.1, 'surreal': 0.1, 'empathy': 0.2, 'critique': 0.15, 'slapstick': 0.1, 'meta': 0.2}, max_bonus_ratio=0.25, per_user_daily_cap_atr=1.0))
        bonus_calc_disabled = disabled_policy.calculate_humor_bonus(dimensions, 0.85)
        assert bonus_calc_disabled.bonus_factor == 0.0
        high_weight_policy = HumorSignalPolicy(policy=HumorPolicy(enabled=True, mode='rewarding', dimension_weights={'chronos': 1.0, 'lexicon': 1.0, 'surreal': 1.0, 'empathy': 1.0, 'critique': 1.0, 'slapstick': 1.0, 'meta': 1.0}, max_bonus_ratio=0.25, per_user_daily_cap_atr=1.0))
        max_dimensions = {'chronos': 1.0, 'lexicon': 1.0, 'surreal': 1.0, 'empathy': 1.0, 'critique': 1.0, 'slapstick': 1.0, 'meta': 1.0}
        bonus_calc_high = high_weight_policy.calculate_humor_bonus(max_dimensions, 1.0)
        assert bonus_calc_high.bonus_factor <= high_weight_policy.policy.max_bonus_ratio
if __name__ == '__main__':
    pytest.main([__file__])