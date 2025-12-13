"""
Tests for Notification Service implementation
"""
import pytest
from src.services.notification_service import NotificationService, Notification, NotificationCategory
from src.libs.CertifiedMath import CertifiedMath
from src.core.TokenStateBundle import create_token_state_bundle, BigNum128


class TestNotificationService:
    """Test suite for Notification Service"""

    def test_notification_service_initialization(self):
        """Test that Notification Service initializes correctly"""
        cm = CertifiedMath()
        notification_service = NotificationService(cm)
        
        assert notification_service is not None
        assert notification_service.cm == cm
        assert notification_service.notifications == []

    def test_process_ledger_entry_creates_notification(self):
        """Test that processing a ledger entry creates appropriate notifications"""
        cm = CertifiedMath()
        notification_service = NotificationService(cm)
        
        # Create mock ledger entry class for testing
        class MockLedgerEntry:
            def __init__(self, entry_id, timestamp, entry_type, data):
                self.entry_id = entry_id
                self.timestamp = timestamp
                self.entry_type = entry_type
                self.data = data
                self.entry_hash = "test_hash_" + entry_id

        # Test token state entry (should create social notification)
        token_state_entry = MockLedgerEntry(
            entry_id="token_state_001",
            timestamp=1234567890,
            entry_type="token_state",
            data={"test": "data"}
        )
        
        notification = notification_service.process_ledger_entry(token_state_entry)
        
        assert notification is not None
        assert isinstance(notification, Notification)
        assert notification.category == NotificationCategory.SOCIAL
        assert notification.event_id == "token_state_001"
        assert notification.timestamp == 1234567890
        assert notification.is_read == False
        assert len(notification_service.notifications) == 1

    def test_get_notifications_by_category(self):
        """Test that notifications can be filtered by category"""
        cm = CertifiedMath()
        notification_service = NotificationService(cm)
        
        # Create mock ledger entry class for testing
        class MockLedgerEntry:
            def __init__(self, entry_id, timestamp, entry_type, data):
                self.entry_id = entry_id
                self.timestamp = timestamp
                self.entry_type = entry_type
                self.data = data
                self.entry_hash = "test_hash_" + entry_id

        # Create different types of entries
        token_state_entry = MockLedgerEntry(
            entry_id="token_state_001",
            timestamp=1234567890,
            entry_type="token_state",
            data={"test": "data"}
        )
        
        reward_allocation_entry = MockLedgerEntry(
            entry_id="reward_alloc_001",
            timestamp=1234567891,
            entry_type="reward_allocation",
            data={"test": "data"}
        )
        
        # Process entries
        notification_service.process_ledger_entry(token_state_entry)
        notification_service.process_ledger_entry(reward_allocation_entry)
        
        # Test filtering
        social_notifications = notification_service.get_notifications(NotificationCategory.SOCIAL)
        economic_notifications = notification_service.get_notifications(NotificationCategory.ECONOMIC)
        
        assert len(social_notifications["notifications"]) == 1
        assert social_notifications["notifications"][0]["category"] == "social"
        
        assert len(economic_notifications["notifications"]) == 1
        assert economic_notifications["notifications"][0]["category"] == "economic"

    def test_get_unread_counts(self):
        """Test that unread counts are calculated correctly"""
        cm = CertifiedMath()
        notification_service = NotificationService(cm)
        
        # Create mock ledger entry class for testing
        class MockLedgerEntry:
            def __init__(self, entry_id, timestamp, entry_type, data):
                self.entry_id = entry_id
                self.timestamp = timestamp
                self.entry_type = entry_type
                self.data = data
                self.entry_hash = "test_hash_" + entry_id

        # Create entries
        entry1 = MockLedgerEntry("entry_001", 1234567890, "token_state", {"test": "data"})
        entry2 = MockLedgerEntry("entry_002", 1234567891, "reward_allocation", {"test": "data"})
        
        # Process entries
        notification_service.process_ledger_entry(entry1)
        notification_service.process_ledger_entry(entry2)
        
        # Test initial unread counts
        unread_counts = notification_service.get_unread_counts()
        assert unread_counts["social"] == 1
        assert unread_counts["economic"] == 1
        assert unread_counts["governance"] == 0

    def test_mark_as_read(self):
        """Test that notifications can be marked as read"""
        cm = CertifiedMath()
        notification_service = NotificationService(cm)
        
        # Create mock ledger entry class for testing
        class MockLedgerEntry:
            def __init__(self, entry_id, timestamp, entry_type, data):
                self.entry_id = entry_id
                self.timestamp = timestamp
                self.entry_type = entry_type
                self.data = data
                self.entry_hash = "test_hash_" + entry_id

        # Create entry
        entry = MockLedgerEntry("entry_001", 1234567890, "token_state", {"test": "data"})
        
        # Process entry
        notification = notification_service.process_ledger_entry(entry)
        
        # Verify initial state
        assert notification.is_read == False
        
        # Mark as read
        result = notification_service.mark_as_read(notification.notification_id)
        assert result == True
        
        # Verify state change
        unread_counts = notification_service.get_unread_counts()
        assert unread_counts["social"] == 0

    def test_deterministic_notification_generation(self):
        """Test that notifications are generated deterministically"""
        cm = CertifiedMath()
        
        # Create two service instances
        service1 = NotificationService(cm)
        service2 = NotificationService(cm)
        
        # Create mock ledger entry class for testing
        class MockLedgerEntry:
            def __init__(self, entry_id, timestamp, entry_type, data):
                self.entry_id = entry_id
                self.timestamp = timestamp
                self.entry_type = entry_type
                self.data = data
                self.entry_hash = "test_hash_" + entry_id

        # Create identical entry
        entry = MockLedgerEntry("entry_001", 1234567890, "token_state", {"test": "data"})
        
        # Process identical entries
        notification1 = service1.process_ledger_entry(entry)
        notification2 = service2.process_ledger_entry(entry)
        
        # Verify deterministic behavior
        assert notification1.notification_id == notification2.notification_id
        assert notification1.timestamp == notification2.timestamp
        assert notification1.category == notification2.category


if __name__ == "__main__":
    pytest.main([__file__])