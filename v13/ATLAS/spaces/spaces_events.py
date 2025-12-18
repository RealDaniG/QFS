"""
ATLAS Spaces Events - Economic Event Emission

Minimal implementation for test validation.
"""

from typing import Dict, Any, List
from dataclasses import dataclass

try:
    from ...libs.BigNum128 import BigNum128
    from ...libs.CertifiedMath import CertifiedMath
    from .spaces_manager import Space
    from ..economic_event import EconomicEvent
except ImportError:
    from v13.libs.BigNum128 import BigNum128
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.atlas.spaces.spaces_manager import Space
    from v13.atlas.economic_event import EconomicEvent


def emit_space_created(
    space: Space, cm: CertifiedMath, log_list: List[Dict[str, Any]], pqc_cid: str = ""
) -> EconomicEvent:
    """Emit space_created event"""
    event = EconomicEvent(
        event_id=f"space_created_{space.space_id}",
        event_type="space_created",
        wallet_id=space.host_wallet,
        token_type="CHR",
        amount="1000000000000000000",  # 1 CHR
        timestamp=space.created_at,
        metadata={"space_id": space.space_id, "pqc_cid": pqc_cid},
        pqc_signature="",
    )
    log_list.append({"operation": "event_emitted", "event_type": "space_created"})
    return event


def emit_space_joined(
    space_id: str,
    participant_wallet: str,
    timestamp: int,
    cm: CertifiedMath,
    log_list: List[Dict[str, Any]],
    pqc_cid: str = "",
) -> EconomicEvent:
    """Emit space_joined event"""
    event = EconomicEvent(
        event_id=f"space_joined_{space_id}_{participant_wallet}_{timestamp}",
        event_type="space_joined",
        wallet_id=participant_wallet,
        token_type="FLX",
        amount="100000000000000000",  # 0.1 FLX
        timestamp=timestamp,
        metadata={"space_id": space_id, "pqc_cid": pqc_cid},
        pqc_signature="",
    )
    log_list.append({"operation": "event_emitted", "event_type": "space_joined"})
    return event


def emit_space_spoke(
    space_id: str,
    participant_wallet: str,
    speak_duration_seconds: int,
    timestamp: int,
    cm: CertifiedMath,
    log_list: List[Dict[str, Any]],
    pqc_cid: str = "",
) -> EconomicEvent:
    """Emit space_spoke event"""
    minutes = speak_duration_seconds // 60
    reward_per_min = BigNum128.from_string("50000000000000000")  # 0.05 CHR/min
    speaker_reward = cm.imul(minutes, reward_per_min, log_list=log_list)

    event = EconomicEvent(
        event_id=f"space_spoke_{space_id}_{participant_wallet}_{timestamp}",
        event_type="space_spoke",
        wallet_id=participant_wallet,
        token_type="CHR",
        amount=speaker_reward.to_decimal_string(),
        timestamp=timestamp,
        metadata={"space_id": space_id, "pqc_cid": pqc_cid},
        pqc_signature="",
    )
    log_list.append({"operation": "event_emitted", "event_type": "space_spoke"})
    return event


def emit_space_ended(
    space: Space,
    end_timestamp: int,
    cm: CertifiedMath,
    log_list: List[Dict[str, Any]],
    pqc_cid: str = "",
) -> EconomicEvent:
    """Emit space_ended event"""
    duration_seconds = end_timestamp - space.created_at
    duration_minutes = duration_seconds // 60

    bonus_per_minute = BigNum128.from_string("10000000000000000")  # 0.01 CHR
    duration_bonus = cm.imul(
        min(duration_minutes, 1000), bonus_per_minute, log_list=log_list
    )

    event = EconomicEvent(
        event_id=f"space_ended_{space.space_id}_{end_timestamp}",
        event_type="space_ended",
        wallet_id=space.host_wallet,
        token_type="CHR",
        amount=duration_bonus.to_decimal_string(),
        timestamp=end_timestamp,
        metadata={"space_id": space.space_id, "pqc_cid": pqc_cid},
        pqc_signature="",
    )
    log_list.append({"operation": "event_emitted", "event_type": "space_ended"})
    return event
