"""
Tests for end-to-end unsafe interaction flow:
API response → ledger entry → notification with safety context
"""
import sys
import os
import pytest


from v13.atlas_api.gateway import AtlasAPIGateway
from v13.atlas_api.models import InteractionRequest


class TestUnsafeInteractionFlow:
    """Test suite for end-to-end unsafe interaction flow"""

    def test_unsafe_interaction_flow(self):
        """Test unsafe interaction propagates through API → ledger → notification"""
        gateway = AtlasAPIGateway()
        
        # Test an interaction with unsafe content
        request = InteractionRequest(
            user_id="test_user",
            target_id="test_post",
            content="This is explicit adult content that should be flagged."
        )
        
        # 1. API Response Check
        response = gateway.post_interaction("comment", request)
        
        # Check that response has expected structure
        assert hasattr(response, 'success')
        assert hasattr(response, 'event_id')
        assert hasattr(response, 'guard_results')
        assert response.guard_results is not None
        
        # Check that safety guard failed
        guard_results = response.guard_results
        assert guard_results.safety_guard_passed == False
        assert "failed with risk score" in guard_results.explanation.lower()
        assert "threshold" in guard_results.explanation.lower()
        
        # Get the event ID for ledger lookup
        event_id = response.event_id
        assert event_id is not None
        
        # 2. Ledger Entry Check
        # Find the ledger entry for this event
        ledger_entries = gateway.coherence_ledger.ledger_entries
        ledger_entry = None
        for entry in ledger_entries:
            # Look for entries with rewards containing our event_id
            if "rewards" in entry.data and "event_id" in entry.data["rewards"]:
                if entry.data["rewards"]["event_id"] == event_id:
                    ledger_entry = entry
                    break
        
        assert ledger_entry is not None, "Could not find ledger entry for event"
        
        # Check that ledger entry contains guard information
        assert "guards" in ledger_entry.data
        assert "safety" in ledger_entry.data["guards"]
        safety_info = ledger_entry.data["guards"]["safety"]
        assert safety_info["passed"] == False
        assert "risk score" in safety_info["explanation"].lower()
        
        # 3. Notification Check
        # Find notifications related to this event
        notifications = gateway.notification_service.notifications
        notification = None
        for note in notifications:
            if note.event_id == ledger_entry.entry_id:
                notification = note
                break
        
        assert notification is not None, "Could not find notification for ledger entry"
        
        # Check that notification indicates a safety issue
        assert "⚠️ safety alert" in notification.title.lower()
        assert "safety check failed" in notification.message.lower()


if __name__ == "__main__":
    pytest.main([__file__])