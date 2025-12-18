"""
ATLAS Wall Post Events - Economic Event Emission

Handles rewards and economic tracking for Wall Post engagements.
"""

from typing import Dict, Any, List
from dataclasses import dataclass

try:
    from ...libs.BigNum128 import BigNum128
    from ...libs.CertifiedMath import CertifiedMath
    from .wall_posts import WallPost
    from ..economic_event import EconomicEvent
except ImportError:
    from v13.libs.BigNum128 import BigNum128
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.atlas.spaces.wall_posts import WallPost
    from v13.atlas.economic_event import EconomicEvent


def emit_post_created(
    post: WallPost, cm: CertifiedMath, log_list: List[Dict[str, Any]], pqc_cid: str = ""
) -> EconomicEvent:
    """Emit wall_post_created event - Reward author"""
    # Reward for creating content: e.g., 0.5 FLX
    reward_amount = "500000000000000000"  # 0.5 FLX

    event = EconomicEvent(
        event_id=f"post_created_{post.post_id}",
        event_type="wall_post_created",
        wallet_id=post.author_wallet,
        token_type="FLX",
        amount=reward_amount,
        timestamp=post.timestamp,
        metadata={
            "space_id": post.space_id,
            "post_id": post.post_id,
            "pqc_cid": pqc_cid,
        },
        pqc_signature="",
    )
    log_list.append(
        {
            "operation": "event_emitted",
            "event_type": "wall_post_created",
            "amount": reward_amount,
        }
    )
    return event


def emit_post_liked(
    post_id: str,
    liker_wallet: str,
    author_wallet: str,
    timestamp: int,
    cm: CertifiedMath,
    log_list: List[Dict[str, Any]],
    pqc_cid: str = "",
) -> EconomicEvent:
    """Emit wall_post_liked event - Micro-reward to author"""
    # Author gets CHR micro-reward for engagement
    reward_amount = "1000000000000000"  # 0.001 CHR

    event = EconomicEvent(
        event_id=f"post_liked_{post_id}_{liker_wallet}_{timestamp}",
        event_type="wall_post_liked",
        wallet_id=author_wallet,  # Reward goes to author
        token_type="CHR",
        amount=reward_amount,
        timestamp=timestamp,
        metadata={"post_id": post_id, "liker": liker_wallet, "pqc_cid": pqc_cid},
        pqc_signature="",
    )
    log_list.append(
        {
            "operation": "event_emitted",
            "event_type": "wall_post_liked",
            "amount": reward_amount,
        }
    )
    return event


def emit_post_replied(
    reply_post: WallPost,
    parent_author_wallet: str,
    cm: CertifiedMath,
    log_list: List[Dict[str, Any]],
    pqc_cid: str = "",
) -> List[EconomicEvent]:
    """Emit events for a reply: Reward replier (creation) and Parent Author (engagement)"""

    events = []

    # 1. Replier gets creation reward (same as normal post)
    creation_event = emit_post_created(reply_post, cm, log_list, pqc_cid)
    creation_event.event_type = "wall_reply_created"  # Distinguish if needed
    events.append(creation_event)

    # 2. Parent author gets engagement reward
    engagement_reward = "5000000000000000"  # 0.005 CHR

    engagement_event = EconomicEvent(
        event_id=f"post_reply_received_{reply_post.metadata.get('parent_post_id')}_{reply_post.post_id}",
        event_type="wall_post_reply_received",
        wallet_id=parent_author_wallet,
        token_type="CHR",
        amount=engagement_reward,
        timestamp=reply_post.timestamp,
        metadata={
            "parent_post_id": reply_post.metadata.get("parent_post_id"),
            "reply_post_id": reply_post.post_id,
            "pqc_cid": pqc_cid,
        },
        pqc_signature="",
    )
    log_list.append(
        {
            "operation": "event_emitted",
            "event_type": "wall_post_reply_received",
            "amount": engagement_reward,
        }
    )
    events.append(engagement_event)

    return events
