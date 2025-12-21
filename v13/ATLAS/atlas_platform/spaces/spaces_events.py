"""
ATLAS Spaces Events - Economic Event Emission

Emits QFS EconomicEvents for all space-related actions.
All events are deterministic and replayable.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

try:
    from ...libs.BigNum128 import BigNum128
    from ...libs.CertifiedMath import CertifiedMath
    from ...libs.canonical.events import EconomicEvent
    from .spaces_manager import Space, Participant, ParticipantRole
except ImportError:
    from v13.libs.BigNum128 import BigNum128
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.libs.canonical.events import EconomicEvent
    from v13.atlas.spaces.spaces_manager import Space, Participant, ParticipantRole


# Reward constants (BigNum128 strings for exact arithmetic)
HOST_BASE_REWARD = "1000000000000000000"  # 1 CHR
PARTICIPATION_REWARD = "100000000000000000"  # 0.1 FLX
SPEAKER_REWARD_PER_MINUTE = "50000000000000000"  # 0.05 CHR/FLX per minute


def emit_space_created(
    space: Space, cm: CertifiedMath, log_list: List[Dict[str, Any]], pqc_cid: str = ""
) -> EconomicEvent:
    """
    Emit space_created event with CHR reward for host.

    Args:
        space: Created space
        cm: CertifiedMath instance
        log_list: Audit log list
        pqc_cid: PQC correlation ID

    Returns:
        EconomicEvent for space creation
    """
    # Calculate host reward (base CHR)
    host_reward = BigNum128.from_string(HOST_BASE_REWARD)

    # Create event
    event = EconomicEvent(
        event_id=f"space_created_{space.space_id}",
        event_type="space_created",
        wallet_id=space.host_wallet,
        token_type="CHR",
        amount=host_reward.to_decimal_string(),
        timestamp=space.created_at,
        metadata={
            "space_id": space.space_id,
            "title": space.title,
            "host_wallet": space.host_wallet,
            "reward_type": "host_base",
            "pqc_cid": pqc_cid,
        },
        pqc_signature="",
    )

    # Log event emission
    log_list.append(
        {
            "operation": "event_emitted",
            "event_type": "space_created",
            "event_id": event.event_id,
            "wallet_id": space.host_wallet,
            "amount": event.amount,
            "timestamp": space.created_at,
        }
    )

    return event


def emit_space_joined(
    space_id: str,
    participant_wallet: str,
    timestamp: int,
    cm: CertifiedMath,
    log_list: List[Dict[str, Any]],
    pqc_cid: str = "",
) -> EconomicEvent:
    """
    Emit space_joined event with FLX reward for participant.

    Args:
        space_id: Space ID
        participant_wallet: Participant wallet
        timestamp: Join timestamp
        cm: CertifiedMath instance
        log_list: Audit log list
        pqc_cid: PQC correlation ID

    Returns:
        EconomicEvent for joining space
    """
    # Calculate participation reward
    participation_reward = BigNum128.from_string(PARTICIPATION_REWARD)

    # Create event
    event = EconomicEvent(
        event_id=f"space_joined_{space_id}_{participant_wallet}_{timestamp}",
        event_type="space_joined",
        wallet_id=participant_wallet,
        token_type="FLX",
        amount=participation_reward.to_decimal_string(),
        timestamp=timestamp,
        metadata={
            "space_id": space_id,
            "participant_wallet": participant_wallet,
            "reward_type": "participation",
            "pqc_cid": pqc_cid,
        },
        pqc_signature="",
    )

    # Log event emission
    log_list.append(
        {
            "operation": "event_emitted",
            "event_type": "space_joined",
            "event_id": event.event_id,
            "wallet_id": participant_wallet,
            "amount": event.amount,
            "timestamp": timestamp,
        }
    )

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
    """
    Emit space_spoke event with CHR/FLX reward based on speaking duration.

    Args:
        space_id: Space ID
        participant_wallet: Speaker wallet
        speak_duration_seconds: Speaking duration in seconds
        timestamp: Event timestamp
        cm: CertifiedMath instance
        log_list: Audit log list
        pqc_cid: PQC correlation ID

    Returns:
        EconomicEvent for speaking in space
    """
    # Calculate reward based on duration (per minute)
    minutes = speak_duration_seconds // 60
    base_reward_per_min = BigNum128.from_string(SPEAKER_REWARD_PER_MINUTE)

    # Use CertifiedMath for exact multiplication
    speaker_reward = cm.imul(base_reward_per_min, minutes, log_list=log_list)

    # Create event
    event = EconomicEvent(
        event_id=f"space_spoke_{space_id}_{participant_wallet}_{timestamp}",
        event_type="space_spoke",
        wallet_id=participant_wallet,
        token_type="CHR",  # CHR for quality contribution
        amount=speaker_reward.to_decimal_string(),
        timestamp=timestamp,
        metadata={
            "space_id": space_id,
            "participant_wallet": participant_wallet,
            "speak_duration_seconds": speak_duration_seconds,
            "speak_duration_minutes": minutes,
            "reward_type": "speaker",
            "pqc_cid": pqc_cid,
        },
        pqc_signature="",
    )

    # Log event emission
    log_list.append(
        {
            "operation": "event_emitted",
            "event_type": "space_spoke",
            "event_id": event.event_id,
            "wallet_id": participant_wallet,
            "amount": event.amount,
            "duration_seconds": speak_duration_seconds,
            "timestamp": timestamp,
        }
    )

    return event


def emit_space_ended(
    space: Space,
    end_timestamp: int,
    cm: CertifiedMath,
    log_list: List[Dict[str, Any]],
    pqc_cid: str = "",
) -> EconomicEvent:
    """
    Emit space_ended event with duration bonus for host.

    Args:
        space: Ended space
        end_timestamp: End timestamp
        cm: CertifiedMath instance
        log_list: Audit log list
        pqc_cid: PQC correlation ID

    Returns:
        EconomicEvent for ending space
    """
    # Calculate duration bonus (CHR based on space duration)
    duration_seconds = end_timestamp - space.created_at
    duration_minutes = duration_seconds // 60

    # Bonus: 0.01 CHR per minute (up to max of 10 CHR for 1000 minutes)
    bonus_per_minute = BigNum128.from_string("10000000000000000")  # 0.01 CHR
    max_bonus = BigNum128.from_string("10000000000000000000")  # 10 CHR

    # Calculate bonus with cap
    duration_bonus = cm.imul(
        bonus_per_minute, min(duration_minutes, 1000), log_list=log_list
    )

    # Create event
    event = EconomicEvent(
        event_id=f"space_ended_{space.space_id}_{end_timestamp}",
        event_type="space_ended",
        wallet_id=space.host_wallet,
        token_type="CHR",
        amount=duration_bonus.to_decimal_string(),
        timestamp=end_timestamp,
        metadata={
            "space_id": space.space_id,
            "host_wallet": space.host_wallet,
            "duration_seconds": duration_seconds,
            "duration_minutes": duration_minutes,
            "final_participant_count": space.get_participant_count(),
            "reward_type": "duration_bonus",
            "pqc_cid": pqc_cid,
        },
        pqc_signature="",
    )

    # Log event emission
    log_list.append(
        {
            "operation": "event_emitted",
            "event_type": "space_ended",
            "event_id": event.event_id,
            "wallet_id": space.host_wallet,
            "amount": event.amount,
            "duration_minutes": duration_minutes,
            "timestamp": end_timestamp,
        }
    )

    return event
