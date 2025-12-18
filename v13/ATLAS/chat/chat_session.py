"""
ATLAS Secure Chat Logic
Core session management for Zero-Sim compliant secure chat.
"""

from typing import Dict, List, Any, Optional
import time

try:
    from ...libs.CertifiedMath import CertifiedMath
    from ...libs.deterministic_helpers import DeterministicID
    from .chat_models import ChatSessionState, ChatParticipant, ChatMessage
    from .chat_events import emit_chat_created, emit_message_sent
except ImportError:
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.libs.deterministic_helpers import DeterministicID
    from v13.atlas.chat.chat_models import (
        ChatSessionState,
        ChatParticipant,
        ChatMessage,
    )
    from v13.atlas.chat.chat_events import emit_chat_created, emit_message_sent


class ChatSessionManager:
    """
    Manages secure chat sessions with strict determinism.
    """

    def __init__(self, cm: CertifiedMath):
        self.cm = cm
        self.active_sessions: Dict[str, ChatSessionState] = {}

    def create_session(
        self,
        owner_wallet: str,
        timestamp: int,
        log_list: List[Dict[str, Any]],
        pqc_cid: str = "",
        initial_members: Optional[List[str]] = None,
        ttl_seconds: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChatSessionState:
        """
        Create a new deterministic chat session.
        """
        # Deterministic ID: owner:timestamp:QFS_CHAT
        seed = f"{owner_wallet}:{timestamp}:QFS_CHAT"
        session_id = DeterministicID.from_string(seed)

        if session_id in self.active_sessions:
            return self.active_sessions[session_id]

        # invoke economic cost
        emit_chat_created(
            session_id, owner_wallet, timestamp, self.cm, log_list, pqc_cid
        )

        owner_participant = ChatParticipant(
            wallet_id=owner_wallet, joined_at=timestamp, role="owner"
        )

        participants = {owner_wallet: owner_participant}

        # Add initial members if any
        if initial_members:
            for member_wallet in initial_members:
                if member_wallet == owner_wallet:
                    continue
                participants[member_wallet] = ChatParticipant(
                    wallet_id=member_wallet, joined_at=timestamp, role="member"
                )

        session = ChatSessionState(
            session_id=session_id,
            created_at=timestamp,
            owner_wallet=owner_wallet,
            participants=participants,
            ttl_seconds=ttl_seconds,
            metadata=metadata or {},
        )

        self.active_sessions[session_id] = session
        log_list.append(
            {
                "operation": "chat_session_created",
                "session_id": session_id,
                "owner": owner_wallet,
                "timestamp": timestamp,
                "ttl_seconds": ttl_seconds,
                "initial_member_count": len(participants),
            }
        )
        return session

    def remove_participant(
        self,
        session_id: str,
        target_wallet: str,
        req_wallet: str,
        log_list: List[Dict[str, Any]],
    ) -> None:
        """
        Remove a participant from the session. Only owner can remove others.
        Participant can remove themselves (leave).
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.active_sessions[session_id]
        if session.status != "active":
            raise ValueError(f"Session {session_id} is not active")

        if target_wallet not in session.participants:
            raise ValueError(f"Participant {target_wallet} not in session")

        # Permission check
        # 1. Owner can remove anyone
        # 2. User can remove themselves
        if req_wallet != session.owner_wallet and req_wallet != target_wallet:
            raise PermissionError("Only owner can remove other participants")

        if target_wallet == session.owner_wallet:
            raise ValueError(
                "Owner cannot be removed from session (must end session instead)"
            )

        session.participants.pop(target_wallet)
        log_list.append(
            {
                "operation": "chat_participant_removed",
                "session_id": session_id,
                "wallet_id": target_wallet,
                "removed_by": req_wallet,
            }
        )

    def join_session(
        self,
        session_id: str,
        participant_wallet: str,
        timestamp: int,
        log_list: List[Dict[str, Any]],
        session_key_handle: Optional[str] = None,
    ) -> ChatParticipant:
        """
        Add a participant to a chat session. Idempotent.
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.active_sessions[session_id]
        if session.status != "active":
            raise ValueError(f"Session {session_id} is not active")

        if participant_wallet in session.participants:
            return session.participants[participant_wallet]

        participant = ChatParticipant(
            wallet_id=participant_wallet,
            joined_at=timestamp,
            role="member",
            session_key_handle=session_key_handle,
        )
        session.participants[participant_wallet] = participant

        log_list.append(
            {
                "operation": "chat_participant_joined",
                "session_id": session_id,
                "wallet_id": participant_wallet,
            }
        )
        return participant

    def send_message(
        self,
        session_id: str,
        sender_wallet: str,
        content_encrypted: str,
        timestamp: int,
        pqc_signature: str,
        log_list: List[Dict[str, Any]],
        pqc_cid: str = "",
        references: Optional[List[str]] = None,
    ) -> ChatMessage:
        """
        Send a message to the chat.
        Requires sender to be a participant.
        """
        if references is None:
            references = []

        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.active_sessions[session_id]
        if session.status != "active":
            raise ValueError(f"Session {session_id} is not active")

        if sender_wallet not in session.participants:
            raise ValueError(
                f"User {sender_wallet} is not a participant in session {session_id}"
            )

        # TTL Enforcement
        if session.ttl_seconds > 0:
            if timestamp > session.created_at + session.ttl_seconds:
                raise ValueError("Session has expired (TTL)")

        # TTL Enforcement
        if session.ttl_seconds > 0:
            if timestamp > session.created_at + session.ttl_seconds:
                raise ValueError("Session has expired (TTL)")

        # Deterministic Message ID: session_id:sender:sequence:timestamp
        seq_num = len(session.messages) + 1
        msg_seed = f"{session_id}:{sender_wallet}:{seq_num}:{timestamp}"
        message_id = DeterministicID.from_string(msg_seed)

        # Economic Event
        emit_message_sent(
            message_id, session_id, sender_wallet, timestamp, self.cm, log_list, pqc_cid
        )

        msg = ChatMessage(
            message_id=message_id,
            session_id=session_id,
            author_wallet=sender_wallet,
            timestamp=timestamp,
            sequence_number=seq_num,
            content_encrypted=content_encrypted,
            pqc_signature=pqc_signature,
            references=references,
        )

        session.messages.append(msg)
        log_list.append(
            {
                "operation": "chat_message_dist",
                "session_id": session_id,
                "message_id": message_id,
                "references": references,
            }
        )
        return msg

    def end_session(
        self,
        session_id: str,
        requester_wallet: str,
        timestamp: int,
        log_list: List[Dict[str, Any]],
    ):
        """
        End a chat session. Only owner can end.
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.active_sessions[session_id]
        if session.owner_wallet != requester_wallet:
            raise PermissionError("Only owner can end session")

        session.status = "ended"
        log_list.append(
            {
                "operation": "chat_session_ended",
                "session_id": session_id,
                "timestamp": timestamp,
            }
        )
