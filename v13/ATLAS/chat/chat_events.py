"""
chat_events.py - ATLAS Chat Economic Events

Emits economic events for chat actions with CHR/FLX rewards.
Zero-Sim compliant with BigNum128 precision and deterministic calculations.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from v13.libs.CertifiedMath import CertifiedMath, BigNum128
from .chat_models import Conversation, Message


@dataclass
class EconomicEvent:
    """Economic event for QFS ledger integration"""

    event_id: str
    event_type: str
    wallet_id: str
    token_type: str
    amount: str
    timestamp: int
    metadata: Dict[str, Any]
    pqc_signature: str


def emit_conversation_created(
    conversation: Conversation, cm: CertifiedMath, log_list: List, pqc_cid: str = ""
) -> EconomicEvent:
    """
    Emit conversation_created event with CHR reward.

    Reward: 0.3 CHR to conversation creator

    Args:
        conversation: Created conversation
        cm: CertifiedMath instance
        log_list: Audit log
        pqc_cid: PQC correlation ID

    Returns:
        EconomicEvent: Event with reward details
    """
    # 0.3 CHR reward for creating conversation
    reward = BigNum128.from_string("300000000000000000")

    event = EconomicEvent(
        event_id=f"conversation_created_{conversation.conversation_id}",
        event_type="conversation_created",
        wallet_id=conversation.created_by,
        token_type="CHR",
        amount=reward.to_decimal_string(),
        timestamp=conversation.created_at,
        metadata={
            "conversation_id": conversation.conversation_id,
            "conversation_type": conversation.conversation_type.value,
            "participant_count": len(conversation.participants),
            "pqc_cid": pqc_cid,
        },
        pqc_signature="",
    )

    log_list.append(
        {
            "operation": "event_emitted",
            "event_type": "conversation_created",
            "reward_chr": reward.to_decimal_string(),
            "conversation_id": conversation.conversation_id,
        }
    )

    return event


def emit_message_sent(
    message: Message, cm: CertifiedMath, log_list: List, pqc_cid: str = ""
) -> EconomicEvent:
    """
    Emit message_sent event with CHR reward.

    Reward: 0.1 CHR to message sender

    Args:
        message: Sent message
        cm: CertifiedMath instance
        log_list: Audit log
        pqc_cid: PQC correlation ID

    Returns:
        EconomicEvent: Event with reward details
    """
    # 0.1 CHR reward for sending message
    reward = BigNum128.from_string("100000000000000000")

    event = EconomicEvent(
        event_id=f"message_sent_{message.message_id}",
        event_type="message_sent",
        wallet_id=message.sender_wallet,
        token_type="CHR",
        amount=reward.to_decimal_string(),
        timestamp=message.timestamp,
        metadata={
            "message_id": message.message_id,
            "conversation_id": message.conversation_id,
            "is_reply": message.reply_to_message_id is not None,
            "pqc_cid": pqc_cid,
        },
        pqc_signature="",
    )

    log_list.append(
        {
            "operation": "event_emitted",
            "event_type": "message_sent",
            "reward_chr": reward.to_decimal_string(),
            "message_id": message.message_id,
        }
    )

    return event


def emit_message_read(
    message: Message,
    reader_wallet: str,
    timestamp: int,
    cm: CertifiedMath,
    log_list: List,
    pqc_cid: str = "",
) -> EconomicEvent:
    """
    Emit message_read event with FLX reward.

    Reward: 0.01 FLX to message reader

    Args:
        message: Read message
        reader_wallet: Wallet ID of reader
        timestamp: Read timestamp
        cm: CertifiedMath instance
        log_list: Audit log
        pqc_cid: PQC correlation ID

    Returns:
        EconomicEvent: Event with reward details
    """
    # 0.01 FLX reward for reading message
    reward = BigNum128.from_string("10000000000000000")

    event = EconomicEvent(
        event_id=f"message_read_{message.message_id}_{reader_wallet}_{timestamp}",
        event_type="message_read",
        wallet_id=reader_wallet,
        token_type="FLX",
        amount=reward.to_decimal_string(),
        timestamp=timestamp,
        metadata={
            "message_id": message.message_id,
            "conversation_id": message.conversation_id,
            "sender_wallet": message.sender_wallet,
            "pqc_cid": pqc_cid,
        },
        pqc_signature="",
    )

    log_list.append(
        {
            "operation": "event_emitted",
            "event_type": "message_read",
            "reward_flx": reward.to_decimal_string(),
            "message_id": message.message_id,
            "reader": reader_wallet,
        }
    )

    return event
