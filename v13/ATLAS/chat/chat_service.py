"""
chat_service.py - ATLAS Chat Service

Manages conversations and messages with deterministic ordering and E2EE support.
Zero-Sim compliant with CertifiedMath and deterministic ID generation.
"""

from typing import Dict, List, Optional
from v13.libs.CertifiedMath import CertifiedMath
from v13.libs.deterministic_helpers import DeterministicID
from .chat_models import Conversation, Message, ConversationType, MessageStatus


class ChatService:
    """
    Service for managing secure conversations and messages.

    Provides deterministic conversation creation, message sending, and status updates.
    All operations are Zero-Sim compliant with sorted iterations and deterministic IDs.
    """

    def __init__(self, cm: CertifiedMath, max_participants: int = 100):
        """
        Initialize ChatService.

        Args:
            cm: CertifiedMath instance for deterministic operations
            max_participants: Maximum participants per group conversation
        """
        self.cm = cm
        self.max_participants = max_participants
        self.conversations: Dict[str, Conversation] = {}
        self.messages: Dict[str, List[Message]] = {}

    def create_conversation(
        self,
        creator_wallet: str,
        participants: List[str],
        conversation_type: ConversationType,
        timestamp: int,
        encryption_metadata: Optional[Dict[str, str]] = None,
        log_list: Optional[List] = None,
    ) -> Conversation:
        """
        Create a new conversation with deterministic ID.

        Args:
            creator_wallet: Wallet ID of conversation creator
            participants: List of participant wallet IDs (including creator)
            conversation_type: ONE_ON_ONE or GROUP
            timestamp: Creation timestamp
            encryption_metadata: E2EE key exchange metadata
            log_list: Optional audit log

        Returns:
            Conversation: Created conversation

        Raises:
            ValueError: If validation fails
        """
        if log_list is None:
            log_list = []

        # Validate participants
        if creator_wallet not in participants:
            raise ValueError(f"Creator {creator_wallet} must be in participants")

        if conversation_type == ConversationType.ONE_ON_ONE and len(participants) != 2:
            raise ValueError(
                f"One-on-one conversation must have exactly 2 participants, got {len(participants)}"
            )

        if len(participants) > self.max_participants:
            raise ValueError(
                f"Conversation exceeds max participants ({self.max_participants})"
            )

        # Generate deterministic conversation ID
        sorted_participants = sorted(participants)
        id_string = f"{creator_wallet}:{':'.join(sorted_participants)}:{timestamp}"
        conversation_id = DeterministicID.from_string(id_string)

        # Create conversation
        conversation = Conversation(
            conversation_id=conversation_id,
            conversation_type=conversation_type,
            participants=sorted_participants,
            created_at=timestamp,
            created_by=creator_wallet,
            last_message_at=timestamp,
            message_count=0,
            encryption_metadata=encryption_metadata or {},
        )

        self.conversations[conversation_id] = conversation
        self.messages[conversation_id] = []

        log_list.append(
            {
                "operation": "conversation_created",
                "conversation_id": conversation_id,
                "type": conversation_type.value,
                "participant_count": len(participants),
            }
        )

        return conversation

    def send_message(
        self,
        conversation_id: str,
        sender_wallet: str,
        content_cid: str,
        timestamp: int,
        reply_to: Optional[str] = None,
        encryption_metadata: Optional[Dict[str, str]] = None,
        log_list: Optional[List] = None,
    ) -> Message:
        """
        Send a message in a conversation.

        Args:
            conversation_id: Target conversation ID
            sender_wallet: Sender wallet ID
            content_cid: IPFS CID of encrypted content
            timestamp: Message timestamp
            reply_to: Optional message ID to reply to
            encryption_metadata: E2EE metadata for this message
            log_list: Optional audit log

        Returns:
            Message: Created message

        Raises:
            ValueError: If validation fails
        """
        if log_list is None:
            log_list = []

        # Validate conversation exists
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")

        conversation = self.conversations[conversation_id]

        # Validate sender is participant
        if sender_wallet not in conversation.participants:
            raise ValueError(
                f"Sender {sender_wallet} is not a participant in conversation {conversation_id}"
            )

        # Generate deterministic message ID
        id_string = f"{conversation_id}:{sender_wallet}:{timestamp}:{content_cid}"
        message_id = DeterministicID.from_string(id_string)

        # Create message
        message = Message(
            message_id=message_id,
            conversation_id=conversation_id,
            sender_wallet=sender_wallet,
            content_cid=content_cid,
            timestamp=timestamp,
            status=MessageStatus.SENT,
            reply_to_message_id=reply_to,
            encryption_metadata=encryption_metadata or {},
        )

        # Add to conversation
        self.messages[conversation_id].append(message)

        # Update conversation metadata
        conversation.last_message_at = timestamp
        conversation.message_count += 1

        log_list.append(
            {
                "operation": "message_sent",
                "message_id": message_id,
                "conversation_id": conversation_id,
                "sender": sender_wallet,
            }
        )

        return message

    def mark_as_read(
        self,
        message_id: str,
        conversation_id: str,
        reader_wallet: str,
        timestamp: int,
        log_list: Optional[List] = None,
    ) -> Message:
        """
        Mark a message as read.

        Args:
            message_id: Message ID to mark as read
            conversation_id: Conversation ID
            reader_wallet: Reader wallet ID
            timestamp: Read timestamp
            log_list: Optional audit log

        Returns:
            Message: Updated message

        Raises:
            ValueError: If validation fails
        """
        if log_list is None:
            log_list = []

        # Validate conversation exists
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")

        conversation = self.conversations[conversation_id]

        # Validate reader is participant
        if reader_wallet not in conversation.participants:
            raise ValueError(
                f"Reader {reader_wallet} is not a participant in conversation {conversation_id}"
            )

        # Find message
        message = None
        for msg in self.messages[conversation_id]:
            if msg.message_id == message_id:
                message = msg
                break

        if message is None:
            raise ValueError(
                f"Message {message_id} not found in conversation {conversation_id}"
            )

        # Update status
        message.status = MessageStatus.READ

        log_list.append(
            {
                "operation": "message_read",
                "message_id": message_id,
                "reader": reader_wallet,
                "timestamp": timestamp,
            }
        )

        return message

    def get_conversation_messages(
        self,
        conversation_id: str,
        limit: int = 50,
        before_timestamp: Optional[int] = None,
    ) -> List[Message]:
        """
        Get messages from a conversation in deterministic order.

        Args:
            conversation_id: Conversation ID
            limit: Maximum messages to return
            before_timestamp: Optional timestamp for pagination

        Returns:
            List[Message]: Messages sorted by timestamp ASC, message_id ASC
        """
        if conversation_id not in self.messages:
            return []

        messages = self.messages[conversation_id]

        # Filter by timestamp if provided
        if before_timestamp is not None:
            messages = [m for m in messages if m.timestamp < before_timestamp]

        # Sort deterministically: timestamp ASC, message_id ASC
        sorted_messages = sorted(messages, key=lambda m: (m.timestamp, m.message_id))

        # Apply limit
        return (
            sorted_messages[-limit:]
            if len(sorted_messages) > limit
            else sorted_messages
        )
