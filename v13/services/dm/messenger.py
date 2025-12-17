"""
messenger.py - Direct Messaging Service Logic
"""

import hashlib
from typing import Dict, List, Optional
from v13.services.dm.identity import IdentityManager
from v13.services.dm.crypto import DMCryptoEngine


class MessageSignal:
    def __init__(
        self,
        sender: str,
        recipient: str,
        storage_uri: str,
        content_hash: str,
        timestamp: int,
    ):
        self.sender = sender
        self.recipient = recipient
        self.storage_uri = storage_uri
        self.content_hash = content_hash
        self.timestamp = timestamp


class DirectMessagingService:
    def __init__(self):
        self.identity_mgr = IdentityManager()
        self.crypto = DMCryptoEngine()
        self.inboxes: Dict[str, List[MessageSignal]] = {}

    def send_message_signal(
        self, sender_id: str, recipient_id: str, storage_uri: str, content_hash: str
    ) -> bool:
        """
        Process a message signal from sender to recipient.
        Enforces:
        1. Recipient must exist.
        2. Sender meets coherence requirements (Mocked).
        3. Rate limits (Mocked).
        """
        recipient = self.identity_mgr.get_identity(recipient_id)
        if not recipient:
            raise ValueError(f"Recipient {recipient_id} not found")

        # Check blocking/coherence here
        # ...

        signal = MessageSignal(
            sender=sender_id,
            recipient=recipient_id,
            storage_uri=storage_uri,
            content_hash=content_hash,
            timestamp=0,  # TODO: use real clock passed from controller
        )

        if recipient_id not in self.inboxes:
            self.inboxes[recipient_id] = []

        self.inboxes[recipient_id].append(signal)

        # Emit to Ledger (Mocked)
        self._emit_ledger_event(signal)

        return True

    def get_inbox(self, user_id: str) -> List[MessageSignal]:
        return self.inboxes.get(user_id, [])

    def _emit_ledger_event(self, signal: MessageSignal):
        # Integration point with v13.ledger.writer
        pass
