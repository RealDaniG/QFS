"""Bounty system package"""

from .bounty_schema import (
    Bounty,
    BountySubmission,
    ContributorProfile,
    BountyStatus,
    SubmissionStatus,
    ImpactTier,
    calculate_atr_boost,
    classify_impact_tier,
    ATR_BOOST_AMOUNTS,
)

from .bounty_events import (
    EconomicEvent,
    emit_bounty_paid_event,
    emit_atr_boost_event,
    emit_bounty_claimed_event,
    emit_res_stake_returned_event,
    emit_bounty_rejected_event,
    emit_treasury_refill_event,
    get_deterministic_timestamp,
)

__all__ = [
    # Schema
    "Bounty",
    "BountySubmission",
    "ContributorProfile",
    "BountyStatus",
    "SubmissionStatus",
    "ImpactTier",
    "calculate_atr_boost",
    "classify_impact_tier",
    "ATR_BOOST_AMOUNTS",
    # Events
    "EconomicEvent",
    "emit_bounty_paid_event",
    "emit_atr_boost_event",
    "emit_bounty_claimed_event",
    "emit_res_stake_returned_event",
    "emit_bounty_rejected_event",
    "emit_treasury_refill_event",
    "get_deterministic_timestamp",
]
