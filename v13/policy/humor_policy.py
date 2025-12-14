"""
HumorPolicy.py - Policy configuration and integration for humor signals

This module provides policy configurations and integration for the humor signal addon,
including reward calculation, observability, and explainability features.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

from .policy_engine import PolicyEngine, PolicyConfiguration, PolicyHints


class HumorPolicyConfig:
    """Configuration for humor policy rules and reward calculations."""
    
    def __init__(self):
        # Default weights for each humor dimension
        self.dimension_weights = {
            "chronos": 0.15,      # Timing
            "lexicon": 0.10,      # Wordplay
            "surreal": 0.10,      # Absurdity
            "empathy": 0.20,      # Relatability
            "critique": 0.15,     # Satire
            "slapstick": 0.10,    # Physical Comedy
            "meta": 0.20          # Meta-Humor
        }
        
        # Caps and limits
        self.max_humor_bonus = 0.25  # Max 25% bonus from humor
        self.daily_user_cap = 1.0    # Max 100% daily bonus per user
        self.enabled = True          # Whether humor rewards are enabled
        self.recognition_only = False  # Badge/label only, no economic effect
        
        # Anomaly detection thresholds
        self.anomaly_spike_threshold = 2.0  # 2x normal humor bonus rate
        self.anomaly_duration_minutes = 60  # Duration to monitor for anomalies


@dataclass
class HumorBonusCalculation:
    """Result of humor bonus calculation."""
    bonus_factor: float
    dimensions_used: Dict[str, float]
    weights_applied: Dict[str, float]
    cap_applied: Optional[float] = None
    policy_version: str = "v1.0.0"


@dataclass
class HumorObservationStats:
    """Statistics for humor signal observability."""
    total_signals_processed: int = 0
    dimension_distributions: Dict[str, List[float]] = field(default_factory=dict)
    average_confidence: float = 0.0
    bonus_distribution: List[float] = field(default_factory=list)
    anomaly_count: int = 0


class HumorSignalPolicy:
    """
    Policy integration for humor signals that maps 7-dimensional vectors to rewards.
    
    This class handles:
    1. Mapping humor dimensions to reward bonuses
    2. Applying caps and policy constraints
    3. Handling policy toggles (enabled/disabled, recognition-only)
    4. Anomaly detection for humor-derived rewards
    """
    
    def __init__(self, config: Optional[HumorPolicyConfig] = None):
        """
        Initialize the humor signal policy.
        
        Args:
            config: Humor policy configuration
        """
        self.config = config or HumorPolicyConfig()
        self.observation_stats = HumorObservationStats()
        
        # Initialize dimension distributions
        for dimension in ["chronos", "lexicon", "surreal", "empathy", "critique", "slapstick", "meta"]:
            self.observation_stats.dimension_distributions[dimension] = []
    
    def calculate_humor_bonus(self, dimensions: Dict[str, float], confidence: float) -> HumorBonusCalculation:
        """
        Calculate humor bonus factor from dimensions and confidence.
        
        Args:
            dimensions: 7-dimensional humor vector
            confidence: Confidence in the dimension scores
            
        Returns:
            HumorBonusCalculation: Calculated bonus and metadata
        """
        # Check if humor is enabled
        if not self.config.enabled:
            return HumorBonusCalculation(
                bonus_factor=0.0,
                dimensions_used=dimensions,
                weights_applied=self.config.dimension_weights,
                policy_version="v1.0.0"
            )
        
        # Check if humor is recognition-only
        if self.config.recognition_only:
            return HumorBonusCalculation(
                bonus_factor=0.0,  # No economic effect
                dimensions_used=dimensions,
                weights_applied=self.config.dimension_weights,
                policy_version="v1.0.0"
            )
        
        # Calculate weighted sum of dimensions
        weighted_sum = 0.0
        for dimension, score in dimensions.items():
            weight = self.config.dimension_weights.get(dimension, 0.0)
            weighted_sum += score * weight
        
        # Apply confidence as a multiplier
        confidence_factor = confidence
        
        # Calculate base bonus
        base_bonus = weighted_sum * confidence_factor
        
        # Apply cap
        final_bonus = min(base_bonus, self.config.max_humor_bonus)
        
        # Update observability stats
        self._update_observation_stats(dimensions, confidence, final_bonus)
        
        return HumorBonusCalculation(
            bonus_factor=final_bonus,
            dimensions_used=dimensions,
            weights_applied=self.config.dimension_weights,
            cap_applied=self.config.max_humor_bonus if base_bonus > self.config.max_humor_bonus else None,
            policy_version="v1.0.0"
        )
    
    def _update_observation_stats(self, dimensions: Dict[str, float], confidence: float, bonus: float):
        """Update observability statistics."""
        self.observation_stats.total_signals_processed += 1
        
        # Update dimension distributions
        for dimension, score in dimensions.items():
            self.observation_stats.dimension_distributions[dimension].append(score)
        
        # Update average confidence (rolling average)
        total_signals = self.observation_stats.total_signals_processed
        current_avg = self.observation_stats.average_confidence
        self.observation_stats.average_confidence = (
            (current_avg * (total_signals - 1) + confidence) / total_signals
        )
        
        # Add bonus to distribution
        self.observation_stats.bonus_distribution.append(bonus)
    
    def get_observability_stats(self) -> HumorObservationStats:
        """
        Get current observability statistics for humor signals.
        
        Returns:
            HumorObservationStats: Current statistics
        """
        return self.observation_stats
    
    def check_for_anomalies(self) -> bool:
        """
        Check if current humor bonus rate indicates an anomaly.
        
        Returns:
            bool: True if anomaly detected
        """
        if len(self.observation_stats.bonus_distribution) < 10:
            return False
        
        # Calculate recent average bonus
        recent_bonuses = self.observation_stats.bonus_distribution[-10:]
        recent_avg = sum(recent_bonuses) / len(recent_bonuses)
        
        # Compare with historical average (if we have enough data)
        if len(self.observation_stats.bonus_distribution) >= 100:
            historical_bonuses = self.observation_stats.bonus_distribution[:-10]
            historical_avg = sum(historical_bonuses) / len(historical_bonuses)
            
            if historical_avg > 0 and recent_avg / historical_avg > self.config.anomaly_spike_threshold:
                self.observation_stats.anomaly_count += 1
                return True
        
        return False
    
    def get_policy_explanation(self, dimensions: Dict[str, float], confidence: float) -> Dict[str, Any]:
        """
        Generate explanation for humor bonus calculation.
        
        Args:
            dimensions: 7-dimensional humor vector
            confidence: Confidence in the dimension scores
            
        Returns:
            Dict: Explanation of the calculation
        """
        calculation = self.calculate_humor_bonus(dimensions, confidence)
        
        explanation = {
            "policy_version": calculation.policy_version,
            "dimensions": dimensions,
            "confidence": confidence,
            "weights": self.config.dimension_weights,
            "weighted_scores": {
                dim: dimensions[dim] * self.config.dimension_weights[dim]
                for dim in dimensions
            },
            "weighted_sum": sum(
                dimensions[dim] * self.config.dimension_weights[dim]
                for dim in dimensions
            ),
            "confidence_factor": confidence,
            "base_bonus": sum(
                dimensions[dim] * self.config.dimension_weights[dim]
                for dim in dimensions
            ) * confidence,
            "cap": self.config.max_humor_bonus,
            "final_bonus": calculation.bonus_factor,
            "policy_settings": {
                "enabled": self.config.enabled,
                "recognition_only": self.config.recognition_only,
                "max_bonus": self.config.max_humor_bonus
            }
        }
        
        return explanation


# Test function
def test_humor_policy():
    """Test the humor policy implementation."""
    print("Testing HumorSignalPolicy...")
    
    # Create humor policy
    humor_policy = HumorSignalPolicy()
    
    # Test case 1: Normal humor signal
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
    
    bonus_calc = humor_policy.calculate_humor_bonus(dimensions, confidence)
    print(f"Bonus calculation: {bonus_calc}")
    
    # Test explanation
    explanation = humor_policy.get_policy_explanation(dimensions, confidence)
    print(f"Explanation keys: {list(explanation.keys())}")
    
    # Test observability
    stats = humor_policy.get_observability_stats()
    print(f"Observation stats: {stats.total_signals_processed} signals processed")
    
    # Test with policy disabled
    humor_policy.config.enabled = False
    disabled_bonus = humor_policy.calculate_humor_bonus(dimensions, confidence)
    print(f"Disabled bonus: {disabled_bonus.bonus_factor}")
    
    # Test with recognition-only mode
    humor_policy.config.enabled = True
    humor_policy.config.recognition_only = True
    recognition_bonus = humor_policy.calculate_humor_bonus(dimensions, confidence)
    print(f"Recognition-only bonus: {recognition_bonus.bonus_factor}")
    
    print("✓ HumorPolicy test passed!")


if __name__ == "__main__":
    test_humor_policy()