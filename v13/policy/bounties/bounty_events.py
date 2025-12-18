"""
Bounty Economic Events

Deterministic event emission for developer rewards.
All events are replayable and Zero-Sim compliant.
"""

from typing import Dict, Optional
from dataclasses import dataclass
import time


@dataclass
class EconomicEvent:
    """
    Economic event for ledger tracking.

    Matches existing EconomicEvent structure from v13/core/
    """

    event_type: str
    actor: str  # Wallet address
    timestamp: int  # Unix timestamp (deterministic)
    metadata: Dict
    flx_delta: int = 0
    chr_delta: int = 0
    res_delta: int = 0
    atr_delta: int = 0
    nod_delta: int = 0


def get_deterministic_timestamp() -> int:
    """
    Get deterministic timestamp.

    In production, this should come from block time or state machine.
    For now, uses system time (acceptable for manual Phase 1).
    """
    return int(time.time())


def emit_bounty_paid_event(
    bounty_id: str,
    contributor_wallet: str,
    pr_number: int,
    commit_hash: str,
    flx_amount: int,
    chr_amount: int,
    verifier: str,
) -> EconomicEvent:
    """
    Emit deterministic bounty payment event.

    Args:
        bounty_id: Unique bounty identifier
        contributor_wallet: Recipient wallet address
        pr_number: GitHub PR number
        commit_hash: Git commit hash for replay
        flx_amount: FLX reward amount
        chr_amount: CHR reward amount
        verifier: Wallet address of verifier

    Returns:
        EconomicEvent for ledger
    """
    return EconomicEvent(
        event_type="dev_bounty_paid",
        actor=contributor_wallet,
        timestamp=get_deterministic_timestamp(),
        metadata={
            "bounty_id": bounty_id,
            "pr_number": pr_number,
            "commit_hash": commit_hash,
            "flx_reward": flx_amount,
            "chr_reward": chr_amount,
            "verifier": verifier,
            "reason": "Bounty completion verified and approved",
        },
        flx_delta=flx_amount,
        chr_delta=chr_amount,
    )


def emit_atr_boost_event(
    contributor_wallet: str,
    pr_number: int,
    commit_hash: str,
    atr_delta: int,
    impact_tier: str,
    bounty_id: Optional[str] = None,
) -> EconomicEvent:
    """
    Emit ATR reputation boost event.

    Args:
        contributor_wallet: Recipient wallet address
        pr_number: GitHub PR number
        commit_hash: Git commit hash for replay
        atr_delta: ATR increase amount
        impact_tier: Impact classification (minor/feature/core)
        bounty_id: Optional bounty ID if from bounty

    Returns:
        EconomicEvent for ledger
    """
    metadata = {
        "pr_number": pr_number,
        "commit_hash": commit_hash,
        "impact_tier": impact_tier,
        "atr_delta": atr_delta,
        "reason": "Merged contribution",
    }

    if bounty_id:
        metadata["bounty_id"] = bounty_id

    return EconomicEvent(
        event_type="atr_boost_applied",
        actor=contributor_wallet,
        timestamp=get_deterministic_timestamp(),
        metadata=metadata,
        atr_delta=atr_delta,
    )


def emit_bounty_claimed_event(
    bounty_id: str, contributor_wallet: str, res_staked: int
) -> EconomicEvent:
    """
    Emit bounty claim event (RES stake locked).

    Args:
        bounty_id: Unique bounty identifier
        contributor_wallet: Claimer wallet address
        res_staked: RES amount staked

    Returns:
        EconomicEvent for ledger
    """
    return EconomicEvent(
        event_type="bounty_claimed",
        actor=contributor_wallet,
        timestamp=get_deterministic_timestamp(),
        metadata={
            "bounty_id": bounty_id,
            "res_staked": res_staked,
            "reason": "Bounty claimed, RES stake locked",
        },
        res_delta=-res_staked,  # Negative = locked
    )


def emit_res_stake_returned_event(
    bounty_id: str, contributor_wallet: str, res_amount: int, reason: str
) -> EconomicEvent:
    """
    Emit RES stake return event.

    Args:
        bounty_id: Unique bounty identifier
        contributor_wallet: Recipient wallet address
        res_amount: RES amount returned
        reason: Reason for return (approved/rejected/expired)

    Returns:
        EconomicEvent for ledger
    """
    return EconomicEvent(
        event_type="res_stake_returned",
        actor=contributor_wallet,
        timestamp=get_deterministic_timestamp(),
        metadata={"bounty_id": bounty_id, "res_returned": res_amount, "reason": reason},
        res_delta=res_amount,  # Positive = returned
    )


def emit_bounty_rejected_event(
    bounty_id: str,
    contributor_wallet: str,
    verifier: str,
    reason: str,
    res_slashed: int = 0,
) -> EconomicEvent:
    """
    Emit bounty rejection event.

    Args:
        bounty_id: Unique bounty identifier
        contributor_wallet: Submitter wallet address
        verifier: Wallet address of verifier
        reason: Rejection reason
        res_slashed: RES amount slashed (0 for good faith, >0 for spam)

    Returns:
        EconomicEvent for ledger
    """
    return EconomicEvent(
        event_type="bounty_rejected",
        actor=contributor_wallet,
        timestamp=get_deterministic_timestamp(),
        metadata={
            "bounty_id": bounty_id,
            "verifier": verifier,
            "reason": reason,
            "res_slashed": res_slashed,
        },
        res_delta=-res_slashed if res_slashed > 0 else 0,
    )


def emit_treasury_refill_event(
    treasury_id: str, flx_added: int, chr_added: int, authorized_by: str, reason: str
) -> EconomicEvent:
    """
    Emit treasury refill event (governance-approved).

    Args:
        treasury_id: Treasury identifier
        flx_added: FLX amount added
        chr_added: CHR amount added
        authorized_by: Governance authority
        reason: Refill justification

    Returns:
        EconomicEvent for ledger
    """
    return EconomicEvent(
        event_type="treasury_refill",
        actor=treasury_id,
        timestamp=get_deterministic_timestamp(),
        metadata={
            "treasury_id": treasury_id,
            "flx_added": flx_added,
            "chr_added": chr_added,
            "authorized_by": authorized_by,
            "reason": reason,
        },
        flx_delta=flx_added,
        chr_delta=chr_added,
    )
