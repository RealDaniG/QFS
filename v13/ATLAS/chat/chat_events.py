"""
ATLAS Secure Chat Events
Economic event emission for chat actions.
"""

from typing import Dict, Any, List

try:
    from ...atlas.economic_event import EconomicEvent
    from ...libs.BigNum128 import BigNum128
    from ...libs.CertifiedMath import CertifiedMath
except ImportError:
    from v13.atlas.economic_event import EconomicEvent
    from v13.libs.BigNum128 import BigNum128
    from v13.libs.CertifiedMath import CertifiedMath


def emit_chat_created(
    session_id: str,
    owner_wallet: str,
    timestamp: int,
    cm: CertifiedMath,
    log_list: List[Dict[str, Any]],
    pqc_cid: str = "",
) -> EconomicEvent:
    """
    Emit event for chat creation.
    Cost: 1.0 FLX (Creation Stake)
    """
    cost = BigNum128.from_string("1000000000000000000")  # 1.0 FLX

    event = EconomicEvent(
        event_id=f"chat_created_{session_id}",
        event_type="chat_created",
        wallet_id=owner_wallet,
        token_type="FLX",
        amount=cost.to_decimal_string(),
        timestamp=timestamp,
        metadata={"session_id": session_id, "pqc_cid": pqc_cid},
        pqc_signature="",
    )
    log_list.append(
        {
            "operation": "event_emitted",
            "event_type": "chat_created",
            "session_id": session_id,
        }
    )
    return event


def emit_message_sent(
    message_id: str,
    session_id: str,
    sender_wallet: str,
    timestamp: int,
    cm: CertifiedMath,
    log_list: List[Dict[str, Any]],
    pqc_cid: str = "",
) -> EconomicEvent:
    """
    Emit event for sending a message.
    Cost: 0.01 FLX (Anti-Spam / Transmission Cost)
    """
    cost = BigNum128.from_string("10000000000000000")  # 0.01 FLX

    event = EconomicEvent(
        event_id=f"msg_sent_{message_id}",
        event_type="message_sent",
        wallet_id=sender_wallet,
        token_type="FLX",
        amount=cost.to_decimal_string(),
        timestamp=timestamp,
        metadata={
            "session_id": session_id,
            "message_id": message_id,
            "pqc_cid": pqc_cid,
        },
        pqc_signature="",
    )
    log_list.append(
        {
            "operation": "event_emitted",
            "event_type": "message_sent",
            "message_id": message_id,
        }
    )
    return event
