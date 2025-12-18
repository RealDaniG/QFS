"""
notification_service.py - Segmented notification service for ATLAS x QFS

Implements a NotificationService module that listens to QFS/ledger events,
categorizes them into Social, Economic, and Governance queues,
and provides deterministic read APIs.
"""
import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from ..libs.CertifiedMath import BigNum128, CertifiedMath
from ..core.CoherenceLedger import CoherenceLedger, LedgerEntry

class NotificationCategory(Enum):
    """Categories for notifications."""
    SOCIAL = 'social'
    ECONOMIC = 'economic'
    GOVERNANCE = 'governance'

@dataclass
class Notification:
    """Represents a notification in the system."""
    notification_id: str
    timestamp: int
    category: NotificationCategory
    title: str
    message: str
    event_id: str
    is_read: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    pqc_cid: str = ''
    quantum_metadata: Dict[str, Any] = field(default_factory=dict)

class NotificationService:
    """
    Segmented notification service for ATLAS x QFS.

    Listens to QFS/ledger events, categorizes them into queues,
    and provides deterministic read APIs.
    """

    def __init__(self, cm_instance: CertifiedMath):
        """
        Initialize the Notification Service.

        Args:
            cm_instance: CertifiedMath instance for deterministic operations
        """
        self.cm = cm_instance
        self.notifications: List[Notification] = []
        self.quantum_metadata = {'component': 'NotificationService', 'version': 'QFS-V13-P1-2', 'pqc_scheme': 'Dilithium-5'}

    def process_ledger_entry(self, ledger_entry: LedgerEntry) -> Optional[Notification]:
        """
        Process a ledger entry and create appropriate notifications.

        Args:
            ledger_entry: Ledger entry to process

        Returns:
            Notification: Created notification or None if no notification needed
        """
        category = self._categorize_entry(ledger_entry)
        if category is None:
            return None
        title, message = self._generate_notification_content(ledger_entry, category)
        notification_data = {'event_id': ledger_entry.entry_id, 'category': category.value, 'timestamp': ledger_entry.timestamp}
        notification_json = json.dumps(notification_data, sort_keys=True)
        notification_id = hashlib.sha256(notification_json.encode('utf-8')).hexdigest()[:32]
        pqc_cid = self._generate_pqc_cid(notification_data, ledger_entry.timestamp)
        notification = Notification(notification_id=notification_id, timestamp=ledger_entry.timestamp, category=category, title=title, message=message, event_id=ledger_entry.entry_id, is_read=False, metadata={'entry_type': ledger_entry.entry_type, 'entry_hash': ledger_entry.entry_hash + '...'}, pqc_cid=pqc_cid, quantum_metadata=self.quantum_metadata.copy())
        self.notifications.append(notification)
        return notification

    def get_notifications(self, category: Optional[NotificationCategory]=None, limit: int=20, cursor: Optional[str]=None) -> Dict[str, Any]:
        """
        Get notifications with optional filtering by category.

        Args:
            category: Optional category to filter by
            limit: Maximum number of notifications to return
            cursor: Pagination cursor for next page

        Returns:
            Dict: Notifications and pagination info
        """
        filtered_notifications = self.notifications
        if category:
            filtered_notifications = [n for n in self.notifications if n.category == category]
        filtered_notifications.sort(key=lambda x: x.timestamp, reverse=True)
        if limit > 0:
            filtered_notifications = filtered_notifications[:limit]
        notifications_data = []
        for notification in sorted(filtered_notifications):
            notifications_data.append({'notification_id': notification.notification_id, 'timestamp': notification.timestamp, 'category': notification.category.value, 'title': notification.title, 'message': notification.message, 'event_id': notification.event_id, 'is_read': notification.is_read, 'metadata': notification.metadata})
        next_cursor = None
        if len(filtered_notifications) == limit and self.notifications:
            oldest_timestamp = filtered_notifications[-1].timestamp
            next_cursor = f'cursor_{oldest_timestamp}'
        return {'notifications': notifications_data, 'next_cursor': next_cursor, 'unread_counts': self._get_unread_counts()}

    def get_unread_counts(self) -> Dict[str, int]:
        """
        Get unread notification counts per category.

        Returns:
            Dict: Unread counts per category
        """
        return self._get_unread_counts()

    def mark_as_read(self, notification_id: str) -> bool:
        """
        Mark a notification as read.

        Args:
            notification_id: ID of notification to mark as read

        Returns:
            bool: True if notification was found and marked as read
        """
        for notification in sorted(self.notifications):
            if notification.notification_id == notification_id:
                notification.is_read = True
                return True
        return False

    def _categorize_entry(self, ledger_entry: LedgerEntry) -> Optional[NotificationCategory]:
        """
        Categorize a ledger entry into a notification category.

        Args:
            ledger_entry: Ledger entry to categorize

        Returns:
            NotificationCategory: Category or None if no notification needed
        """
        entry_type = ledger_entry.entry_type
        if entry_type in ['token_state']:
            return NotificationCategory.SOCIAL
        elif entry_type in ['reward_allocation', 'hsmf_metrics']:
            return NotificationCategory.ECONOMIC
        elif entry_type in ['hsmf_metrics']:
            return NotificationCategory.GOVERNANCE
        return None

    def _generate_notification_content(self, ledger_entry: LedgerEntry, category: NotificationCategory) -> tuple[str, str]:
        """
        Generate notification title and message based on ledger entry.

        Args:
            ledger_entry: Ledger entry to generate content for
            category: Category of the notification

        Returns:
            tuple: (title, message)
        """
        entry_type = ledger_entry.entry_type
        data = ledger_entry.data
        is_safety_alert = False
        safety_explanation = ''
        if 'guards' in data and 'safety' in data['guards']:
            safety_info = data['guards']['safety']
            if not safety_info.get('passed', True):
                is_safety_alert = True
                safety_explanation = safety_info.get('explanation', '')
                category = NotificationCategory.SOCIAL
        if category == NotificationCategory.SOCIAL:
            if entry_type == 'token_state':
                if is_safety_alert:
                    return ('⚠️ Safety Alert: Content Flagged', f'Unsafe content detected: {safety_explanation[:100]}...')
                else:
                    return ('Token State Updated', f'Your token state has been updated. View details in the ledger.')
        elif category == NotificationCategory.ECONOMIC:
            if entry_type == 'reward_allocation':
                reward_info = data.get('rewards', {})
                reward_count = len(reward_info)
                if is_safety_alert:
                    return ('⚠️ Safety Alert: Reward Allocation Issue', f'Unsafe content detected in reward allocation: {safety_explanation[:100]}...')
                else:
                    return ('Reward Allocation', f'{reward_count} reward(s) allocated. Check your balance.')
            elif entry_type == 'hsmf_metrics':
                if is_safety_alert:
                    return ('⚠️ Safety Alert: System Metrics Issue', f'Safety check failed during metrics update: {safety_explanation[:100]}...')
                else:
                    return ('System Metrics Updated', 'HSMF metrics have been calculated and recorded.')
        elif category == NotificationCategory.GOVERNANCE:
            if entry_type == 'hsmf_metrics':
                if is_safety_alert:
                    return ('⚠️ Safety Alert: Governance Issue', f'Safety check failed during governance update: {safety_explanation[:100]}...')
                else:
                    return ('Governance Update', 'System governance metrics updated.')
        if is_safety_alert:
            return ('⚠️ Safety Alert', f'Safety check failed: {safety_explanation[:100]}...')
        else:
            return (f'Ledger Event: {entry_type}', f'A new {entry_type} event has been recorded in the ledger.')

    def _generate_pqc_cid(self, notification_data: Dict[str, Any], timestamp: int) -> str:
        """Generate deterministic PQC correlation ID."""
        data_to_hash = {'notification_data': notification_data, 'timestamp': timestamp}
        data_json = json.dumps(data_to_hash, sort_keys=True)
        return hashlib.sha256(data_json.encode()).hexdigest()[:32]

    def _get_unread_counts(self) -> Dict[str, int]:
        """Get unread notification counts per category."""
        counts = {'social': 0, 'economic': 0, 'governance': 0}
        for notification in sorted(self.notifications):
            if not notification.is_read:
                counts[notification.category.value] += 1
        return counts

def test_notification_service():
    """Test the NotificationService implementation."""
    log_list = []
    with CertifiedMath.LogContext() as log_list:
        cm = CertifiedMath()
    notification_service = NotificationService(cm)
    from ..core.TokenStateBundle import TokenStateBundle
    chr_state = {'coherence_metric': '0.98', 'c_holo_proxy': '0.99', 'resonance_metric': '0.05', 'flux_metric': '0.15', 'psi_sync_metric': '0.08', 'atr_metric': '0.85'}
    parameters = {'beta_penalty': BigNum128.from_int(100000000), 'phi': BigNum128.from_int(1618033988749894848)}
    token_bundle = TokenStateBundle(chr_state=chr_state, flx_state={'flux_metric': '0.15'}, psi_sync_state={'psi_sync_metric': '0.08'}, atr_state={'atr_metric': '0.85'}, res_state={'resonance_metric': '0.05'}, nod_state={'nod_metric': '0.5'}, signature='test_signature', timestamp=1234567890, bundle_id='test_bundle_id', pqc_cid='test_pqc_cid', quantum_metadata={'test': 'data'}, lambda1=BigNum128.from_int(300000000000000000), lambda2=BigNum128.from_int(200000000000000000), c_crit=BigNum128.from_int(900000000000000000), parameters=parameters)

    class MockLedgerEntry:

        def __init__(self, entry_id, timestamp, entry_type, data):
            self.entry_id = entry_id
            self.timestamp = timestamp
            self.entry_type = entry_type
            self.data = data
            self.entry_hash = hashlib.sha256(entry_id.encode()).hexdigest()
    token_state_entry = MockLedgerEntry(entry_id='token_state_001', timestamp=1234567890, entry_type='token_state', data={'token_bundle': token_bundle.to_dict()})
    notification1 = notification_service.process_ledger_entry(token_state_entry)
    reward_allocation_entry = MockLedgerEntry(entry_id='reward_alloc_001', timestamp=1234567891, entry_type='reward_allocation', data={'rewards': {'CHR': {'amount': '100.0', 'token_name': 'CHR'}, 'FLX': {'amount': '50.0', 'token_name': 'FLX'}}})
    notification2 = notification_service.process_ledger_entry(reward_allocation_entry)
    social_notifications = notification_service.get_notifications(NotificationCategory.SOCIAL)
    economic_notifications = notification_service.get_notifications(NotificationCategory.ECONOMIC)
    unread_counts = notification_service.get_unread_counts()
    if notification1:
        marked = notification_service.mark_as_read(notification1.notification_id)
        unread_counts_after = notification_service.get_unread_counts()
if __name__ == '__main__':
    test_notification_service()
