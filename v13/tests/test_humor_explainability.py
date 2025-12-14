"""
Tests for the humor explainability module
"""

import sys
import os
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
        dimensions = {
            "chronos": 0.8,
            "lexicon": 0.6,
            "surreal": 0.4,
            "empathy": 0.9,
            "critique": 0.7,
            "slapstick": 0.3,
            "meta": 0.5
        }
        
        ledger_context = {
            "views": 1000,
            "laughs": 800,
            "saves": 200,
            "replays": 150,
            "author_reputation": 0.9
        }
        
        explanation = self.explain_helper.explain_humor_reward(
            content_id="content_123",
            user_id="user_456",
            reward_event_id="reward_789",
            dimensions=dimensions,
            confidence=0.85,
            ledger_context=ledger_context,
            timestamp=1234567890
        )
        
        # Verify explanation structure
        assert explanation.content_id == "content_123"
        assert explanation.user_id == "user_456"
        assert explanation.reward_event_id == "reward_789"
        assert explanation.dimensions == dimensions
        assert explanation.confidence == 0.85
        assert explanation.ledger_context == ledger_context
        assert explanation.final_bonus >= 0.0
        assert len(explanation.explanation_hash) > 0
    
    def test_explanation_deterministic_hash(self):
        """Test that explanations generate deterministic hashes"""
        dimensions = {
            "chronos": 0.8,
            "lexicon": 0.6,
            "surreal": 0.4,
            "empathy": 0.9,
            "critique": 0.7,
            "slapstick": 0.3,
            "meta": 0.5
        }
        
        ledger_context = {
            "views": 1000,
            "laughs": 800,
            "saves": 200,
            "replays": 150,
            "author_reputation": 0.9
        }
        
        # Generate two explanations with identical inputs
        explanation1 = self.explain_helper.explain_humor_reward(
            content_id="content_123",
            user_id="user_456",
            reward_event_id="reward_789",
            dimensions=dimensions,
            confidence=0.85,
            ledger_context=ledger_context,
            timestamp=1234567890
        )
        
        explanation2 = self.explain_helper.explain_humor_reward(
            content_id="content_123",
            user_id="user_456",
            reward_event_id="reward_789",
            dimensions=dimensions,
            confidence=0.85,
            ledger_context=ledger_context,
            timestamp=1234567890
        )
        
        # Verify identical hashes
        assert explanation1.explanation_hash == explanation2.explanation_hash
    
    def test_explanation_consistency_verification(self):
        """Test explanation consistency verification"""
        dimensions = {
            "chronos": 0.8,
            "lexicon": 0.6,
            "surreal": 0.4,
            "empathy": 0.9,
            "critique": 0.7,
            "slapstick": 0.3,
            "meta": 0.5
        }
        
        ledger_context = {
            "views": 1000,
            "laughs": 800,
            "saves": 200,
            "replays": 150,
            "author_reputation": 0.9
        }
        
        explanation = self.explain_helper.explain_humor_reward(
            content_id="content_123",
            user_id="user_456",
            reward_event_id="reward_789",
            dimensions=dimensions,
            confidence=0.85,
            ledger_context=ledger_context,
            timestamp=1234567890
        )
        
        # Verify consistency
        is_consistent = self.explain_helper.verify_explanation_consistency(explanation)
        assert is_consistent
    
    def test_simplified_explanation(self):
        """Test generating simplified explanation"""
        dimensions = {
            "chronos": 0.8,
            "lexicon": 0.6,
            "surreal": 0.4,
            "empathy": 0.9,
            "critique": 0.7,
            "slapstick": 0.3,
            "meta": 0.5
        }
        
        ledger_context = {
            "views": 1000,
            "laughs": 800,
            "saves": 200,
            "replays": 150,
            "author_reputation": 0.9
        }
        
        explanation = self.explain_helper.explain_humor_reward(
            content_id="content_123",
            user_id="user_456",
            reward_event_id="reward_789",
            dimensions=dimensions,
            confidence=0.85,
            ledger_context=ledger_context,
            timestamp=1234567890
        )
        
        simplified = self.explain_helper.get_simplified_explanation(explanation)
        
        # Verify simplified structure
        assert "summary" in simplified
        assert "reason" in simplified
        assert "breakdown" in simplified
        assert "policy_info" in simplified
        assert "verification" in simplified
    
    def test_batch_explain_rewards(self):
        """Test batch explanation generation"""
        batch_data = [
            {
                "content_id": f"content_{i}",
                "user_id": f"user_{i}",
                "reward_event_id": f"reward_{i}",
                "dimensions": {
                    "chronos": 0.5 + i * 0.1,
                    "lexicon": 0.5,
                    "surreal": 0.5,
                    "empathy": 0.5,
                    "critique": 0.5,
                    "slapstick": 0.5,
                    "meta": 0.5
                },
                "confidence": 0.85 - i * 0.05,
                "ledger_context": {
                    "views": 100 + i * 10,
                    "laughs": 50 + i * 5,
                    "saves": 20 + i * 2,
                    "replays": 30 + i * 3,
                    "author_reputation": 0.5 + i * 0.1
                },
                "timestamp": 1234567890 + i
            }
            for i in range(3)
        ]
        
        explanations = self.explain_helper.batch_explain_rewards(batch_data)
        
        # Verify batch results
        assert len(explanations) == 3
        for i, explanation in enumerate(explanations):
            assert explanation.content_id == f"content_{i}"
            assert explanation.user_id == f"user_{i}"
            assert explanation.reward_event_id == f"reward_{i}"


if __name__ == "__main__":
    pytest.main([__file__])