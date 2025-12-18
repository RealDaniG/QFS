"""
ATLAS Chat Module

Secure 1-on-1 and group conversations with E2EE metadata support.
Zero-Sim compliant with deterministic message ordering and economic events.
"""

from .chat_models import Conversation, Message, ConversationType, MessageStatus
from .chat_service import ChatService
from .chat_events import (
    EconomicEvent,
    emit_conversation_created,
    emit_message_sent,
    emit_message_read,
)

__all__ = [
    "Conversation",
    "Message",
    "ConversationType",
    "MessageStatus",
    "ChatService",
    "EconomicEvent",
    "emit_conversation_created",
    "emit_message_sent",
    "emit_message_read",
]
