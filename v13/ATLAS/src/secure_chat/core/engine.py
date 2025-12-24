"""
ATLAS Secure Chat Engine

Core engine for managing secure chat threads and messages with deterministic behavior.
"""

import hashlib
import hmac
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class ThreadStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"


@dataclass
class Thread:
    thread_id: str
    creator_id: str
    participants: List[str]
    created_at: str
    status: ThreadStatus = ThreadStatus.DRAFT
    metadata: Dict = field(default_factory=dict)
    version: str = "1.0"


@dataclass
class Message:
    message_id: str
    thread_id: str
    sender_id: str
    content_hash: str
    content_size: int
    timestamp: str
    message_type: str = "text"
    metadata: Dict = field(default_factory=dict)


class SecureChatEngine:
    MAX_MESSAGE_SIZE = 1 * 1024 * 1024
    MAX_PARTICIPANTS = 100

    def __init__(self, storage, atr_engine, clock=None):
        self.storage = storage
        self.atr_engine = atr_engine
        self.threads: Dict[str, Thread] = {}
        self.messages: Dict[str, List[Message]] = {}
        # Zero-Sim: Default clock returns genesis string
        self._clock = clock or (lambda: "2024-01-01T00:00:00+00:00")

    def _generate_id(self, *parts: str) -> str:
        """Generate a deterministic ID from input parts"""
        seed = ":".join((str(p) for p in parts)).encode()
        return hmac.new(b"ATLAS_SECURE_CHAT", seed, "sha256").hexdigest()

    def _validate_participants(self, participants: List[str]) -> None:
        """Validate participant list"""
        if not participants:
            raise ValueError("At least one participant is required")
        if len(participants) > self.MAX_PARTICIPANTS:
            raise ValueError(f"Maximum {self.MAX_PARTICIPANTS} participants allowed")
        if len(set(participants)) != len(participants):
            raise ValueError("Duplicate participants not allowed")

    def _validate_message_content(self, content: bytes) -> None:
        """Validate message content"""
        if not content:
            raise ValueError("Message content cannot be empty")
        if len(content) > self.MAX_MESSAGE_SIZE:
            raise ValueError(
                f"Message exceeds maximum size of {self.MAX_MESSAGE_SIZE} bytes"
            )

    def create_thread(
        self,
        creator_id: str,
        participants: List[str],
        metadata: Optional[Dict] = None,
        timestamp: Optional[str] = None,
    ) -> Tuple[Thread, List[Dict]]:
        """Create a new secure chat thread"""
        if not creator_id:
            raise ValueError("Creator ID is required")
        if creator_id not in participants:
            participants = [creator_id] + [p for p in participants if p != creator_id]
        self._validate_participants(participants)

        timestamp_str = timestamp or self._clock()

        thread_id = self._generate_id(
            "thread", creator_id, timestamp_str, ",".join(sorted(participants))
        )
        thread = Thread(
            thread_id=thread_id,
            creator_id=creator_id,
            participants=participants,
            created_at=timestamp_str,
            status=ThreadStatus.ACTIVE,
            metadata=metadata or {},
        )
        self.threads[thread_id] = thread
        self.messages[thread_id] = []
        event = {
            "event_type": "THREAD_CREATED",
            "thread_id": thread_id,
            "creator_id": creator_id,
            "timestamp": timestamp_str,
            "participants": participants,
            "metadata": thread.metadata,
        }
        return (thread, [event])

    async def post_message(
        self,
        thread_id: str,
        sender_id: str,
        content: bytes,
        content_type: str = "text/plain",
        message_type: str = "text",
        metadata: Optional[Dict] = None,
        timestamp: Optional[str] = None,
    ) -> Tuple[Message, List[Dict]]:
        """Post a message to a thread"""
        if not thread_id:
            raise ValueError("Thread ID is required")
        if not sender_id:
            raise ValueError("Sender ID is required")
        thread = self.threads.get(thread_id)
        if not thread:
            raise ValueError("Thread not found")
        if thread.status != ThreadStatus.ACTIVE:
            raise ValueError(f"Cannot post to {thread.status.value} thread")
        if sender_id not in thread.participants:
            raise PermissionError("Sender is not a participant in this thread")
        self._validate_message_content(content)
        content_hash = await self.storage.store(content)

        timestamp_str = timestamp or self._clock()

        message_id = self._generate_id(
            "message", thread_id, sender_id, content_hash, timestamp_str
        )
        message = Message(
            message_id=message_id,
            thread_id=thread_id,
            sender_id=sender_id,
            content_hash=content_hash,
            content_size=len(content),
            timestamp=timestamp_str,
            message_type=message_type,
            metadata={"content_type": content_type, **(metadata or {})},
        )
        self.messages[thread_id].append(message)
        if hasattr(self.atr_engine, "charge_fee"):
            await self.atr_engine.charge_fee(
                account_id=sender_id,
                amount=1,
                description=f"Secure chat message in thread {thread_id[:8]}...",
            )
        event = {
            "event_type": "MESSAGE_POSTED",
            "thread_id": thread_id,
            "message_id": message_id,
            "sender_id": sender_id,
            "content_hash": content_hash,
            "content_size": len(content),
            "timestamp": timestamp_str,
            "message_type": message_type,
        }
        return (message, [event])

    def get_thread(self, thread_id: str, user_id: str) -> Optional[Thread]:
        """Get thread metadata if user is a participant"""
        if not thread_id or not user_id:
            return None
        thread = self.threads.get(thread_id)
        if not thread or user_id not in thread.participants:
            return None
        return thread

    def list_threads(self, user_id: str) -> List[Thread]:
        """List all threads for a user"""
        if not user_id:
            return []
        return [
            thread
            for thread in self.threads.values()
            if user_id in thread.participants and thread.status != ThreadStatus.DELETED
        ]

    def get_messages(
        self,
        thread_id: str,
        user_id: str,
        limit: int = 100,
        before: Optional[str] = None,
    ) -> List[Message]:
        """Get messages from a thread"""
        if not thread_id or not user_id:
            return []
        thread = self.threads.get(thread_id)
        if not thread or user_id not in thread.participants:
            return []
        if thread.status == ThreadStatus.DELETED:
            return []
        messages = self.messages.get(thread_id, [])
        if before:
            messages = [m for m in messages if m.timestamp < before]
        return messages[-limit:]

    async def update_thread_status(
        self,
        thread_id: str,
        user_id: str,
        status: ThreadStatus,
        metadata: Optional[Dict] = None,
    ) -> Tuple[Optional[Thread], List[Dict]]:
        """Update thread status (archive, delete, etc.)"""
        if not thread_id or not user_id:
            raise ValueError("Thread ID and user ID are required")
        thread = self.threads.get(thread_id)
        if not thread:
            raise ValueError("Thread not found")
        if thread.creator_id != user_id:
            raise PermissionError("Only thread creator can update thread status")
        if thread.status == ThreadStatus.DELETED:
            raise ValueError("Cannot modify deleted thread")
        if thread.status == status:
            return (thread, [])
        old_status = thread.status
        thread.status = status
        if metadata:
            thread.metadata.update(metadata)
        event = {
            "event_type": "THREAD_UPDATED",
            "thread_id": thread_id,
            "user_id": user_id,
            "old_status": old_status.value,
            "new_status": status.value,
            "timestamp": self._clock(),
            "metadata": metadata or {},
        }
        return (thread, [event])
