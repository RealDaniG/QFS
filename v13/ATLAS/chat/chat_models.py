"""
ATLAS Secure Chat Models
Strict data structures for Zero-Sim compliant chat sessions.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator


class ChatParticipant(BaseModel):
    """Participant in a secure chat session."""

    wallet_id: str
    joined_at: int
    role: str = "member"  # 'owner', 'member', 'observer'
    session_key_handle: Optional[str] = None  # PQC public key handle for this session
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatMessage(BaseModel):
    """Strictly typed chat message."""

    message_id: str
    session_id: str
    author_wallet: str
    timestamp: int
    sequence_number: int
    content_encrypted: str  # Hex-encoded ciphertext
    pqc_signature: str  # Signature over (session_id+seq+content_encrypted)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatSessionState(BaseModel):
    """Full state of a chat session."""

    session_id: str
    created_at: int
    owner_wallet: str
    status: str = "active"  # 'active', 'ended', 'archived'
    participants: Dict[str, ChatParticipant] = Field(default_factory=dict)
    messages: List[ChatMessage] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def message_count(self) -> int:
        return len(self.messages)

    def get_participant(self, wallet_id: str) -> Optional[ChatParticipant]:
        return self.participants.get(wallet_id)
