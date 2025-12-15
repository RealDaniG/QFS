"""
Tests for AtlasAPIGateway integration with AEGIS advisory gate
"""
import sys
import os
import pytest
from unittest.mock import Mock, patch


from v13.atlas_api.gateway import AtlasAPIGateway
from v13.atlas_api.models import InteractionRequest
from v13.libs.CertifiedMath import CertifiedMath, BigNum128


class TestGatewayAEGISIntegration:
    """Test suite for AtlasAPIGateway integration with AEGIS advisory gate"""

    def setup_method(self):
        """Setup test environment"""
        # Create gateway instance
        self.gateway = AtlasAPIGateway()
        
        
        mock_drv_packet = Mock()
        mock_drv_packet.ttsTimestamp = 1234567890
        self.gateway.set_drv_packet(mock_drv_packet)

    def test_safe_interaction_passes_through(self):
        """Test that safe interactions pass through normally"""
        # Create interaction request with safe content
        request = InteractionRequest(
            user_id="test_user",
            target_id="test_target",
            content="This is a safe, family-friendly comment about quantum computing.",
            reason="Interesting post"
        )
        
        # Process the interaction
        response = self.gateway.post_interaction("comment", request)
        
        # Check that the interaction was successful
        assert response.success is True
        assert response.event_id is not None
        assert response.reward_estimate is not None
        assert response.guard_results.safety_guard_passed is True
        assert response.guard_results.economics_guard_passed is True

    def test_unsafe_interaction_is_blocked(self):
        """Test that unsafe interactions are blocked by AEGIS advisory gate"""
        # Create interaction request with unsafe content
        request = InteractionRequest(
            user_id="test_user",
            target_id="test_target",
            content="This is explicit adult content that should be flagged.",
            reason="Inappropriate comment"
        )
        
        # Process the interaction
        response = self.gateway.post_interaction("comment", request)
        
        # Check that the interaction was blocked
        assert response.success is False
        assert response.event_id is not None
        assert response.reward_estimate is None  # No reward for blocked interactions
        assert response.guard_results.safety_guard_passed is False
        assert "AEGIS advisory gate blocked interaction" in response.guard_results.explanation

    def test_spam_interaction_is_blocked(self):
        """Test that spam interactions are blocked by AEGIS advisory gate"""
        # Create interaction request with spam content
        request = InteractionRequest(
            user_id="test_user",
            target_id="test_target",
            content="Buy now! Click here for free money! Urgent limited time offer! Act now!",
            reason="Spam comment"
        )
        
        # Process the interaction
        response = self.gateway.post_interaction("comment", request)
        
        # Check that the interaction was blocked
        assert response.success is False
        assert response.event_id is not None
        assert response.reward_estimate is None  # No reward for blocked interactions
        assert response.guard_results.safety_guard_passed is False
        assert "AEGIS advisory gate blocked interaction" in response.guard_results.explanation

    def test_ledger_entry_created_for_blocked_interaction(self):
        """Test that ledger entries are created for blocked interactions"""
        # Create interaction request with unsafe content
        request = InteractionRequest(
            user_id="test_user",
            target_id="test_target",
            content="This is explicit adult content that should be flagged.",
            reason="Inappropriate comment"
        )
        
        # Store initial ledger entry count
        initial_entry_count = len(self.gateway.coherence_ledger.ledger_entries)
        
        # Process the interaction
        response = self.gateway.post_interaction("comment", request)
        
        # Check that a ledger entry was created for the blocked interaction
        final_entry_count = len(self.gateway.coherence_ledger.ledger_entries)
        assert final_entry_count == initial_entry_count + 1
        
        # Check that the ledger entry contains AEGIS advisory information
        latest_entry = self.gateway.coherence_ledger.ledger_entries[-1]
        assert "guards" in latest_entry.data
        guard_results = latest_entry.data["guards"]
        assert "aegis_advisory" in guard_results
        assert guard_results["aegis_advisory"]["block_suggested"] is True
        assert guard_results["aegis_advisory"]["severity"] == "critical"

    def test_normal_interaction_creates_ledger_entry_with_advisory_info(self):
        """Test that normal interactions create ledger entries with AEGIS advisory information"""
        # Create interaction request with safe content
        request = InteractionRequest(
            user_id="test_user",
            target_id="test_target",
            content="This is a safe, educational comment.",
            reason="Helpful comment"
        )
        
        # Store initial ledger entry count
        initial_entry_count = len(self.gateway.coherence_ledger.ledger_entries)
        
        # Process the interaction
        response = self.gateway.post_interaction("comment", request)
        
        # Check that a ledger entry was created
        final_entry_count = len(self.gateway.coherence_ledger.ledger_entries)
        assert final_entry_count == initial_entry_count + 1
        
        # Check that the ledger entry contains AEGIS advisory information
        latest_entry = self.gateway.coherence_ledger.ledger_entries[-1]
        assert "guards" in latest_entry.data
        guard_results = latest_entry.data["guards"]
        assert "aegis_advisory" in guard_results
        assert guard_results["aegis_advisory"]["block_suggested"] is False
        assert guard_results["aegis_advisory"]["severity"] == "info"


if __name__ == "__main__":
    pytest.main([__file__])