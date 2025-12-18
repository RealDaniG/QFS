"""
ATLAS Wall Posts Module - Economic Events

Event emission for wall post actions with CHR/FLX rewards.
"""

from typing import Dict, Any, List
from dataclasses import dataclass

try:
    from ...libs.BigNum128 import BigNum128
    from ...libs.CertifiedMath import CertifiedMath
    from .wall_models import Post
except ImportError:
    from v13.libs.BigNum128 import BigNum128
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.atlas.wall.wall_models import Post


@dataclass
class EconomicEvent:
    """Economic event for QFS integration"""

    event_id: str
    event_type: str
    wallet_id: str
    token_type: str
    amount: str
    timestamp: int
    metadata: Dict[str, Any]
    pqc_signature: str


def emit_post_created(
    post: Post, cm: CertifiedMath, log_list: List[Dict[str, Any]], pqc_cid: str = ""
) -> EconomicEvent:
    """Emit post_created event with CHR reward"""
    # 0.5 CHR for creating a post
    reward = BigNum128.from_string("500000000000000000")  # 0.5 CHR

    event = EconomicEvent(
        event_id=f"post_created_{post.post_id}",
        event_type="post_created",
        wallet_id=post.author_wallet,
        token_type="CHR",
        amount=reward.to_decimal_string(),
        timestamp=post.created_at,
        metadata={
            "post_id": post.post_id,
            "space_id": post.space_id,
            "pqc_cid": pqc_cid,
        },
        pqc_signature="",
    )
    log_list.append({"operation": "event_emitted", "event_type": "post_created"})
    return event


def emit_post_quoted(
    post: Post,
    parent_post: Post,
    cm: CertifiedMath,
    log_list: List[Dict[str, Any]],
    pqc_cid: str = "",
) -> EconomicEvent:
    """Emit post_quoted event with CHR reward"""
    # 0.3 CHR for quoting a post
    reward = BigNum128.from_string("300000000000000000")  # 0.3 CHR

    event = EconomicEvent(
        event_id=f"post_quoted_{post.post_id}_{parent_post.post_id}",
        event_type="post_quoted",
        wallet_id=post.author_wallet,
        token_type="CHR",
        amount=reward.to_decimal_string(),
        timestamp=post.created_at,
        metadata={
            "post_id": post.post_id,
            "parent_post_id": parent_post.post_id,
            "pqc_cid": pqc_cid,
        },
        pqc_signature="",
    )
    log_list.append({"operation": "event_emitted", "event_type": "post_quoted"})
    return event


def emit_post_pinned(
    post: Post,
    pinner_wallet: str,
    cm: CertifiedMath,
    log_list: List[Dict[str, Any]],
    pqc_cid: str = "",
) -> EconomicEvent:
    """Emit post_pinned event with CHR reward"""
    # 0.2 CHR for pinning a post (host only)
    reward = BigNum128.from_string("200000000000000000")  # 0.2 CHR

    event = EconomicEvent(
        event_id=f"post_pinned_{post.post_id}_{post.pin_timestamp}",
        event_type="post_pinned",
        wallet_id=pinner_wallet,
        token_type="CHR",
        amount=reward.to_decimal_string(),
        timestamp=post.pin_timestamp or post.created_at,
        metadata={
            "post_id": post.post_id,
            "space_id": post.space_id,
            "pqc_cid": pqc_cid,
        },
        pqc_signature="",
    )
    log_list.append({"operation": "event_emitted", "event_type": "post_pinned"})
    return event


def emit_post_reacted(
    post_id: str,
    reactor_wallet: str,
    emoji: str,
    timestamp: int,
    cm: CertifiedMath,
    log_list: List[Dict[str, Any]],
    pqc_cid: str = "",
) -> EconomicEvent:
    """Emit post_reacted event with FLX reward"""
    # 0.01 FLX for adding a reaction
    reward = BigNum128.from_string("10000000000000000")  # 0.01 FLX

    event = EconomicEvent(
        event_id=f"post_reacted_{post_id}_{reactor_wallet}_{timestamp}",
        event_type="post_reacted",
        wallet_id=reactor_wallet,
        token_type="FLX",
        amount=reward.to_decimal_string(),
        timestamp=timestamp,
        metadata={"post_id": post_id, "emoji": emoji, "pqc_cid": pqc_cid},
        pqc_signature="",
    )
    log_list.append({"operation": "event_emitted", "event_type": "post_reacted"})
    return event


def emit_recap_generated(
    post: Post, cm: CertifiedMath, log_list: List[Dict[str, Any]], pqc_cid: str = ""
) -> EconomicEvent:
    """Emit recap_generated event with CHR reward (advisory only)"""
    # 0.1 CHR for AI recap (advisory, not deterministic)
    reward = BigNum128.from_string("100000000000000000")  # 0.1 CHR

    event = EconomicEvent(
        event_id=f"recap_generated_{post.post_id}",
        event_type="recap_generated",
        wallet_id=post.author_wallet,
        token_type="CHR",
        amount=reward.to_decimal_string(),
        timestamp=post.created_at,
        metadata={
            "post_id": post.post_id,
            "space_id": post.space_id,
            "advisory_only": True,
            "pqc_cid": pqc_cid,
        },
        pqc_signature="",
    )
    log_list.append({"operation": "event_emitted", "event_type": "recap_generated"})
    return event
