"""
chat_models.py - ATLAS Chat Models

Defines data models for secure 1-on-1 and group conversations with E2EE metadata.
Zero-Sim compliant with deterministic IDs and BigNum128 precision.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict


class ConversationType(Enum):
    """Type of conversation"""

    ONE_ON_ONE = "one_on_one"
    GROUP = "group"


class MessageStatus(Enum):
    """Message delivery status"""

    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"


@dataclass
class Conversation:
    """
    Conversation between participants with E2EE metadata.

    Attributes:
        conversation_id: Deterministic unique identifier
        conversation_type: ONE_ON_ONE or GROUP
        participants: List of participant wallet IDs (sorted for determinism)
        created_at: Creation timestamp
        created_by: Creator wallet ID
        last_message_at: Timestamp of last message
        message_count: Total messages in conversation
        encryption_metadata: E2EE key exchange information
    """

    conversation_id: str
    conversation_type: ConversationType
    participants: List[str]
    created_at: int
    created_by: str
    last_message_at: int
    message_count: int
    encryption_metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Ensure participants are sorted for determinism"""
        self.participants = sorted(self.participants)


@dataclass
class Message:
    """
    Encrypted message in a conversation.

    Attributes:
        message_id: Deterministic unique identifier
        conversation_id: Parent conversation ID
        sender_wallet: Sender wallet ID
        content_cid: IPFS CID of encrypted content
        timestamp: Message timestamp
        status: Delivery status
        reply_to_message_id: Optional parent message for threading
        encryption_metadata: E2EE metadata for this message
    """

    message_id: str
    conversation_id: str
    sender_wallet: str
    content_cid: str
    timestamp: int
    status: MessageStatus
    reply_to_message_id: Optional[str] = None
    encryption_metadata: Dict[str, str] = field(default_factory=dict)
