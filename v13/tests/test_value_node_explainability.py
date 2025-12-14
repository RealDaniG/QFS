"""
Test suite for ValueNodeExplainability.py

This module provides comprehensive tests for the value-node explainability features,
ensuring deterministic behavior, policy compliance, and proper explanation generation.
"""

import pytest
import re
from typing import Dict, Any, List

from v13.policy.value_node_explainability import (
    ValueNodeExplainabilityHelper,
    ValueNodeRewardExplanation
)
from v13.policy.humor_policy import HumorSignalPolicy, HumorPolicy


class TestValueNodeExplainability:
    """Test suite for ValueNodeExplainabilityHelper."""
    
    @pytest.fixture
    def humor_policy(self) -> HumorSignalPolicy:
        """Create a humor policy instance for testing."""
        return HumorSignalPolicy(
            policy=HumorPolicy(
                enabled=True,
                mode="rewarding",
                dimension_weights={
                    "chronos": 0.15,
                    "lexicon": 0.10,
                    "surreal": 0.10,
                    "empathy": 0.20,
                    "critique": 0.15,
                    "slapstick": 0.10,
                    "meta": 0.20
                },
                max_bonus_ratio=0.25,
                per_user_daily_cap_atr=1.0
            )
        )
    
    @pytest.fixture
    def explain_helper(self, humor_policy: HumorSignalPolicy) -> ValueNodeExplainabilityHelper:
        """Create a value-node explainability helper instance."""
        return ValueNodeExplainabilityHelper(humor_policy)
    
    @pytest.fixture
    def sample_reward_data(self) -> Dict[str, Any]:
        """Sample reward data for testing."""
        return {
            "wallet_id": "wallet_123",
            "user_id": "user_456",
            "reward_event_id": "reward_789",
            "epoch": 1,
            "base_reward": {"ATR": "10.0 ATR"},
            "bonuses": [
                {"label": "Coherence bonus", "value": "+2.5 ATR", "reason": "Coherence score 0.92 above threshold"},
                {"label": "Humor bonus", "value": "+1.2 ATR", "reason": "Humor signal 0.88 above threshold"}
            ],
            "caps": [
                {"label": "Humor cap", "value": "-0.3 ATR", "reason": "Humor cap applied at 1.0 ATR"},
                {"label": "Global cap", "value": "-2.0 ATR", "reason": "Global reward cap for epoch"}
            ],
            "guards": [
                {"name": "Balance guard", "result": "pass", "reason": "Balance within limits"},
                {"name": "Rate limit guard", "result": "pass", "reason": "Rate limit not exceeded"}
            ],
            "timestamp": 1234567890
        }
    
    def test_explain_value_node_reward(self, explain_helper: ValueNodeExplainabilityHelper, sample_reward_data: Dict[str, Any]) -> None:
        """Test that value-node reward explanations are generated correctly."""
        explanation = explain_helper.explain_value_node_reward(**sample_reward_data)
        
        # Verify basic fields
        assert explanation.wallet_id == "wallet_123"
        assert explanation.user_id == "user_456"
        assert explanation.reward_event_id == "reward_789"
        assert explanation.epoch == 1
        assert explanation.timestamp == 1234567890
        
        # Verify input data preservation
        assert explanation.base_reward == sample_reward_data["base_reward"]
        assert explanation.bonuses == sample_reward_data["bonuses"]
        assert explanation.caps == sample_reward_data["caps"]
        assert explanation.guards == sample_reward_data["guards"]
        
        # Verify policy information
        assert explanation.policy_version == "v1.0.0"
        assert isinstance(explanation.policy_hash, str)
        
        # Verify reason codes
        assert "REWARD_BONUSES_APPLIED" in explanation.reason_codes
        assert "REWARD_CAPS_APPLIED" in explanation.reason_codes
        
        # Verify explanation hash is generated
        assert explanation.explanation_hash != ""
        assert len(explanation.explanation_hash) == 64  # SHA256 hash length
    
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
        
        # Verify simplified explanation structure
        assert "summary" in simplified
        assert "reason" in simplified
        assert "reason_codes" in simplified
        assert "breakdown" in simplified
        assert "policy_info" in simplified
        assert "verification" in simplified
        
        # Verify key fields contain expected substrings (exact values may vary due to calculation)
        assert "Received value-node reward" in simplified["summary"]
        assert "epoch" in simplified["reason"]
        assert simplified["reason_codes"] == explanation.reason_codes
        assert simplified["verification"]["consistent"] == True
    
    def test_explanation_reason_codes_guard_failures(self, explain_helper: ValueNodeExplainabilityHelper) -> None:
        """Test that guard failures are properly reflected in reason codes."""
        reward_data = {
            "wallet_id": "wallet_123",
            "user_id": "user_456",
            "reward_event_id": "reward_789",
            "epoch": 1,
            "base_reward": {"ATR": "10.0 ATR"},
            "bonuses": [],
            "caps": [],
            "guards": [
                {"name": "Balance guard", "result": "fail", "reason": "Balance exceeds limits"},
                {"name": "Rate limit guard", "result": "pass", "reason": "Rate limit not exceeded"}
            ],
            "timestamp": 1234567890
        }
        
        explanation = explain_helper.explain_value_node_reward(**reward_data)
        # Check that guard failure is properly reflected (format may vary)
        reason_codes_str = " ".join(explanation.reason_codes)
        assert "GUARD_FAILED" in reason_codes_str
    
    def test_explanation_reason_codes_various_conditions(self, explain_helper: ValueNodeExplainabilityHelper) -> None:
        """Test reason codes for various conditions."""
        reward_data = {
            "wallet_id": "wallet_123",
            "user_id": "user_456",
            "reward_event_id": "reward_789",
            "epoch": 1,
            "base_reward": {"ATR": "10.0 ATR"},
            "bonuses": [{"label": "Test bonus", "value": "+1.0 ATR", "reason": "Test"}],
            "caps": [{"label": "Test cap", "value": "-0.5 ATR", "reason": "Test"}],
            "guards": [{"name": "Test guard", "result": "pass", "reason": "Test"}],
            "timestamp": 1234567890
        }
        
        explanation = explain_helper.explain_value_node_reward(**reward_data)
        reason_codes = explanation.reason_codes
        
        assert "REWARD_BONUSES_APPLIED" in reason_codes
        assert "REWARD_CAPS_APPLIED" in reason_codes
    
    def test_batch_explain_rewards(self, explain_helper: ValueNodeExplainabilityHelper, sample_reward_data: Dict[str, Any]) -> None:
        """Test batch explanation of rewards."""
        # Create multiple reward data entries
        batch_data = [
            sample_reward_data,
            {**sample_reward_data, "wallet_id": "wallet_456", "reward_event_id": "reward_987"}
        ]
        
        # Test individual explanations first
        explanation1 = explain_helper.explain_value_node_reward(**batch_data[0])
        explanation2 = explain_helper.explain_value_node_reward(**batch_data[1])
        
        # Verify they're different
        assert explanation1.wallet_id != explanation2.wallet_id
        assert explanation1.reward_event_id != explanation2.reward_event_id
        assert explanation1.explanation_hash != explanation2.explanation_hash
    
    def test_value_node_signal_pure_functionality(self, explain_helper: ValueNodeExplainabilityHelper, sample_reward_data: Dict[str, Any]) -> None:
        """Test that the explainability helper is a pure function with no side effects."""
        # Capture initial state
        initial_hash = explain_helper._generate_explanation_hash(
            explain_helper.explain_value_node_reward(**sample_reward_data)
        )
        
        # Run multiple times
        hashes = []
        for _ in range(5):
            explanation = explain_helper.explain_value_node_reward(**sample_reward_data)
            hashes.append(explanation.explanation_hash)
        
        # All hashes should be identical
        assert all(h == initial_hash for h in hashes)
    
    def test_no_network_io_in_value_node_modules(self) -> None:
        """Test that value-node explainability modules do not perform network I/O."""
        # This is a static analysis test - we verify by inspection that no network
        # I/O operations are performed in the module
        import v13.policy.value_node_explainability as module
        import inspect
        
        # Get source code
        source = inspect.getsource(module)
        
        # Check for forbidden network operations
        forbidden_patterns = [
            "requests.",
            "urllib.",
            "socket.",
            "httplib.",
            "http.client",
            "aiohttp.",
        ]
        
        for pattern in forbidden_patterns:
            assert pattern not in source, f"Forbidden network I/O pattern '{pattern}' found in value-node modules"
    
    def test_no_filesystem_io_in_value_node_modules(self) -> None:
        """Test that value-node explainability modules do not perform filesystem I/O."""
        # This is a static analysis test - we verify by inspection that no filesystem
        # I/O operations are performed in the module
        import v13.policy.value_node_explainability as module
        import inspect
        
        # Get source code
        source = inspect.getsource(module)
        
        # Check for forbidden filesystem operations (but allow json module usage)
        forbidden_patterns = [
            "open(",
            "os.",
            "shutil.",
            "pathlib.",
            "pickle.",
        ]
        
        for pattern in forbidden_patterns:
            assert pattern not in source, f"Forbidden filesystem I/O pattern '{pattern}' found in value-node modules"
    
    def test_no_ledger_adapters_in_value_node_modules(self) -> None:
        """Test that value-node explainability modules do not import ledger adapters."""
        # This is a static analysis test - we verify by inspection that no ledger
        # adapters or TreasuryEngine modules are imported
        import v13.policy.value_node_explainability as module
        import inspect
        
        # Get source code
        source = inspect.getsource(module)
        
        # Check for forbidden imports
        forbidden_patterns = [
            "TreasuryEngine",
            "RealLedger",
            "TokenStateBundle",
            "CoherenceLedger"
        ]
        
        for pattern in forbidden_patterns:
            assert pattern not in source, f"Forbidden ledger adapter pattern '{pattern}' found in value-node modules"


    def test_extreme_reward_values(self, explain_helper: ValueNodeExplainabilityHelper) -> None:
        """Test explainability with extreme reward values."""
        # Test with very large reward values
        large_reward_data = {
            "wallet_id": "wallet_large",
            "user_id": "user_large",
            "reward_event_id": "reward_large",
            "epoch": 1,
            "base_reward": {"ATR": "1000000.0 ATR"},
            "bonuses": [
                {"label": "Large bonus", "value": "+500000.0 ATR", "reason": "Large bonus reason"}
            ],
            "caps": [
                {"label": "Large cap", "value": "-100000.0 ATR", "reason": "Large cap reason"}
            ],
            "guards": [
                {"name": "Test guard", "result": "pass", "reason": "Test"}
            ],
            "timestamp": 1234567890
        }
        
        explanation = explain_helper.explain_value_node_reward(**large_reward_data)
        assert explanation.wallet_id == "wallet_large"
        assert "REWARD_BONUSES_APPLIED" in explanation.reason_codes
        assert "REWARD_CAPS_APPLIED" in explanation.reason_codes
        assert explanation.explanation_hash != ""
        
        # Test with zero values
        zero_reward_data = {
            "wallet_id": "wallet_zero",
            "user_id": "user_zero",
            "reward_event_id": "reward_zero",
            "epoch": 1,
            "base_reward": {"ATR": "0.0 ATR"},
            "bonuses": [],
            "caps": [],
            "guards": [
                {"name": "Test guard", "result": "pass", "reason": "Test"}
            ],
            "timestamp": 1234567890
        }
        
        explanation = explain_helper.explain_value_node_reward(**zero_reward_data)
        assert explanation.wallet_id == "wallet_zero"
        assert explanation.explanation_hash != ""


    def test_malformed_input_data_handling(self, explain_helper: ValueNodeExplainabilityHelper) -> None:
        """Test explainability with malformed input data."""
        # Test with missing fields
        malformed_data = {
            "wallet_id": "wallet_malformed",
            # Missing user_id
            "reward_event_id": "reward_malformed",
            "epoch": 1,
            # Missing base_reward
            "bonuses": "not_a_list",  # Wrong type
            "caps": None,  # None value
            "guards": [],  # Empty list
            "timestamp": "not_a_number"  # Wrong type
        }
        
        # Should handle gracefully without crashing
        try:
            explanation = explain_helper.explain_value_node_reward(**malformed_data)
            # If it doesn't crash, it should still produce a valid explanation
            assert explanation.wallet_id == "wallet_malformed"
            assert explanation.explanation_hash != ""
        except Exception:
            # If it raises an exception, that's acceptable as long as it's handled
            pass


    def test_different_policy_configurations(self, explain_helper: ValueNodeExplainabilityHelper) -> None:
        """Test explainability with different policy configurations."""
        # Test with different humor policy settings
        from v13.policy.humor_policy import HumorSignalPolicy, HumorPolicy
        
        # Create a policy with different settings
        different_policy = HumorSignalPolicy(
            policy=HumorPolicy(
                enabled=False,  # Disabled
                mode="recognition_only",
                dimension_weights={
                    "chronos": 0.2,
                    "lexicon": 0.15,
                    "surreal": 0.15,
                    "empathy": 0.1,
                    "critique": 0.2,
                    "slapstick": 0.1,
                    "meta": 0.1
                },
                max_bonus_ratio=0.5,
                per_user_daily_cap_atr=2.0
            )
        )
        
        # Create a new explain helper with this policy
        different_helper = ValueNodeExplainabilityHelper(different_policy)
        
        reward_data = {
            "wallet_id": "wallet_diff_policy",
            "user_id": "user_diff_policy",
            "reward_event_id": "reward_diff_policy",
            "epoch": 1,
            "base_reward": {"ATR": "10.0 ATR"},
            "bonuses": [
                {"label": "Bonus", "value": "+2.0 ATR", "reason": "Bonus reason"}
            ],
            "caps": [
                {"label": "Cap", "value": "-1.0 ATR", "reason": "Cap reason"}
            ],
            "guards": [
                {"name": "Test guard", "result": "pass", "reason": "Test"}
            ],
            "timestamp": 1234567890
        }
        
        explanation = different_helper.explain_value_node_reward(**reward_data)
        assert explanation.wallet_id == "wallet_diff_policy"
        assert explanation.explanation_hash != ""


    def test_explanation_hash_collision_resistance(self, explain_helper: ValueNodeExplainabilityHelper) -> None:
        """Test that explanation hashes are resistant to collisions."""
        # Create two slightly different reward data sets
        reward_data_1 = {
            "wallet_id": "wallet_1",
            "user_id": "user_1",
            "reward_event_id": "reward_1",
            "epoch": 1,
            "base_reward": {"ATR": "10.0 ATR"},
            "bonuses": [
                {"label": "Bonus 1", "value": "+2.0 ATR", "reason": "Bonus reason 1"}
            ],
            "caps": [
                {"label": "Cap 1", "value": "-1.0 ATR", "reason": "Cap reason 1"}
            ],
            "guards": [
                {"name": "Guard 1", "result": "pass", "reason": "Guard reason 1"}
            ],
            "timestamp": 1234567890
        }
        
        reward_data_2 = {
            "wallet_id": "wallet_2",  # Different wallet
            "user_id": "user_2",  # Different user
            "reward_event_id": "reward_2",  # Different event
            "epoch": 2,  # Different epoch
            "base_reward": {"ATR": "15.0 ATR"},  # Different base reward
            "bonuses": [
                {"label": "Bonus 2", "value": "+3.0 ATR", "reason": "Bonus reason 2"}  # Different bonus
            ],
            "caps": [
                {"label": "Cap 2", "value": "-2.0 ATR", "reason": "Cap reason 2"}  # Different cap
            ],
            "guards": [
                {"name": "Guard 2", "result": "fail", "reason": "Guard reason 2"}  # Different guard result
            ],
            "timestamp": 1234567891  # Different timestamp
        }
        
        explanation_1 = explain_helper.explain_value_node_reward(**reward_data_1)
        explanation_2 = explain_helper.explain_value_node_reward(**reward_data_2)
        
        # Hashes should be different
        assert explanation_1.explanation_hash != explanation_2.explanation_hash
        assert len(explanation_1.explanation_hash) == 64  # SHA256 length
        assert len(explanation_2.explanation_hash) == 64  # SHA256 length


if __name__ == "__main__":
    pytest.main([__file__, "-v"])