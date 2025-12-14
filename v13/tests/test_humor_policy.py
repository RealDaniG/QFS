"""
Tests for the humor policy module
"""

import sys
import os
import pytest

from v13.policy.humor_policy import HumorSignalPolicy, HumorPolicyConfig


class TestHumorPolicy:
    """Test suite for the humor policy"""
    
    def setup_method(self):
        """Setup test environment"""
        self.humor_policy = HumorSignalPolicy()
    
    def test_normal_humor_bonus_calculation(self):
        """Test normal humor bonus calculation"""
        dimensions = {
            "chronos": 0.8,
            "lexicon": 0.6,
            "surreal": 0.4,
            "empathy": 0.9,
            "critique": 0.7,
            "slapstick": 0.3,
            "meta": 0.5
        }
        
        confidence = 0.85
        
        bonus_calc = self.humor_policy.calculate_humor_bonus(dimensions, confidence)
        
        # Verify calculation structure
        assert bonus_calc.bonus_factor >= 0.0
        assert bonus_calc.bonus_factor <= self.humor_policy.config.max_humor_bonus
        assert bonus_calc.dimensions_used == dimensions
        assert bonus_calc.weights_applied == self.humor_policy.config.dimension_weights
        assert bonus_calc.policy_version == "v1.0.0"
    
    def test_humor_disabled_returns_zero_bonus(self):
        """Test that disabled humor policy returns zero bonus"""
        # Disable humor
        self.humor_policy.config.enabled = False
        
        dimensions = {
            "chronos": 0.8,
            "lexicon": 0.6,
            "surreal": 0.4,
            "empathy": 0.9,
            "critique": 0.7,
            "slapstick": 0.3,
            "meta": 0.5
        }
        
        confidence = 0.85
        
        bonus_calc = self.humor_policy.calculate_humor_bonus(dimensions, confidence)
        
        # Verify zero bonus when disabled
        assert bonus_calc.bonus_factor == 0.0
    
    def test_humor_recognition_only_returns_zero_bonus(self):
        """Test that recognition-only humor policy returns zero bonus"""
        # Enable humor but set to recognition only
        self.humor_policy.config.enabled = True
        self.humor_policy.config.recognition_only = True
        
        dimensions = {
            "chronos": 0.8,
            "lexicon": 0.6,
            "surreal": 0.4,
            "empathy": 0.9,
            "critique": 0.7,
            "slapstick": 0.3,
            "meta": 0.5
        }
        
        confidence = 0.85
        
        bonus_calc = self.humor_policy.calculate_humor_bonus(dimensions, confidence)
        
        # Verify zero bonus when recognition only
        assert bonus_calc.bonus_factor == 0.0
    
    def test_humor_bonus_respects_cap(self):
        """Test that humor bonus respects the maximum cap"""
        # Set dimensions to maximum values
        dimensions = {
            "chronos": 1.0,
            "lexicon": 1.0,
            "surreal": 1.0,
            "empathy": 1.0,
            "critique": 1.0,
            "slapstick": 1.0,
            "meta": 1.0
        }
        
        confidence = 1.0
        
        bonus_calc = self.humor_policy.calculate_humor_bonus(dimensions, confidence)
        
        # Verify bonus is capped
        assert bonus_calc.bonus_factor <= self.humor_policy.config.max_humor_bonus
        if bonus_calc.bonus_factor == self.humor_policy.config.max_humor_bonus:
            assert bonus_calc.cap_applied == self.humor_policy.config.max_humor_bonus
    
    def test_deterministic_behavior(self):
        """Test that humor policy produces deterministic results"""
        dimensions = {
            "chronos": 0.8,
            "lexicon": 0.6,
            "surreal": 0.4,
            "empathy": 0.9,
            "critique": 0.7,
            "slapstick": 0.3,
            "meta": 0.5
        }
        
        confidence = 0.85
        
        # Calculate bonus twice with same input
        bonus_calc1 = self.humor_policy.calculate_humor_bonus(dimensions, confidence)
        bonus_calc2 = self.humor_policy.calculate_humor_bonus(dimensions, confidence)
        
        # Verify both results are identical
        assert bonus_calc1.bonus_factor == bonus_calc2.bonus_factor
        assert bonus_calc1.dimensions_used == bonus_calc2.dimensions_used
        assert bonus_calc1.weights_applied == bonus_calc2.weights_applied
        assert bonus_calc1.policy_version == bonus_calc2.policy_version
    
    def test_observability_stats_updated(self):
        """Test that observability statistics are updated correctly"""
        initial_stats = self.humor_policy.get_observability_stats()
        initial_count = initial_stats.total_signals_processed
        
        dimensions = {
            "chronos": 0.8,
            "lexicon": 0.6,
            "surreal": 0.4,
            "empathy": 0.9,
            "critique": 0.7,
            "slapstick": 0.3,
            "meta": 0.5
        }
        
        confidence = 0.85
        
        # Process multiple signals
        for i in range(5):
            self.humor_policy.calculate_humor_bonus(dimensions, confidence)
        
        # Check that stats were updated
        final_stats = self.humor_policy.get_observability_stats()
        assert final_stats.total_signals_processed == initial_count + 5
        
        # Check dimension distributions were updated
        for dimension in dimensions:
            assert len(final_stats.dimension_distributions[dimension]) == 5
    
    def test_policy_explanation_generation(self):
        """Test that policy explanation is generated correctly"""
        dimensions = {
            "chronos": 0.8,
            "lexicon": 0.6,
            "surreal": 0.4,
            "empathy": 0.9,
            "critique": 0.7,
            "slapstick": 0.3,
            "meta": 0.5
        }
        
        confidence = 0.85
        
        explanation = self.humor_policy.get_policy_explanation(dimensions, confidence)
        
        # Verify explanation structure
        assert "policy_version" in explanation
        assert "dimensions" in explanation
        assert "confidence" in explanation
        assert "weights" in explanation
        assert "weighted_scores" in explanation
        assert "final_bonus" in explanation
        assert "policy_settings" in explanation
        
        # Verify values
        assert explanation["dimensions"] == dimensions
        assert explanation["confidence"] == confidence
        assert explanation["final_bonus"] >= 0.0


if __name__ == "__main__":
    pytest.main([__file__])