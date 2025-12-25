from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from v13.policy.bounties.bounty_schema import Bounty, BountyStatus, BountySubmission
from v13.policy.bounties.bounty_events import (
    EconomicEvent,
    emit_bounty_claimed_event,
    emit_bounty_paid_event,
    emit_res_stake_returned_event,
    emit_bounty_rejected_event,
    emit_atr_boost_event,
)
from v13.policy.treasury.dev_rewards_treasury import DevRewardsTreasury
from v13.libs.BigNum128 import BigNum128


class BountyStateMachine:
    """
    Manages the lifecycle of a Bounty from OPEN to PAID/REJECTED.
    Enforces deterministic transitions and emits precise events.
    """

    def __init__(self, treasury: DevRewardsTreasury):
        self.treasury = treasury
        self.transition_log: List[Any] = []

    def claim_bounty(
        self, bounty: Bounty, actor_address: str, res_amount: BigNum128
    ) -> List[EconomicEvent]:
        """
        Transition: OPEN -> CLAIMED
        Requirement: RES stake >= bounty.res_stake_required
        """
        if bounty.status != BountyStatus.OPEN:
            raise ValueError(
                f"Bounty {bounty.bounty_id} is not OPEN (status: {bounty.status})"
            )

        # Accept both int and BigNum128 for backward compatibility
        if isinstance(res_amount, int):
            res_amount = BigNum128.from_int(res_amount)

        required_stake = BigNum128.from_int(bounty.res_stake_required)
        if res_amount.value < required_stake.value:
            raise ValueError(
                f"Insufficient RES stake. Required: {required_stake.to_decimal_string()}, Provided: {res_amount.to_decimal_string()}"
            )

        bounty.status = BountyStatus.CLAIMED
        bounty.current_claimant = actor_address

        event = emit_bounty_claimed_event(
            bounty_id=bounty.bounty_id,
            contributor_wallet=actor_address,
            res_staked=res_amount.value,  # Events expect int for now
        )
        self.transition_log.append(event)
        return [event]

    def submit_bounty(
        self, bounty: Bounty, submission: BountySubmission
    ) -> List[EconomicEvent]:
        """
        Transition: CLAIMED -> SUBMITTED
        Requirement: Submission comes from claimant
        """
        if bounty.status != BountyStatus.CLAIMED:
            raise ValueError(f"Bounty {bounty.bounty_id} is not CLAIMED")

        if bounty.current_claimant != submission.contributor_wallet:
            raise ValueError("Submission must come from current claimant")

        bounty.status = BountyStatus.SUBMITTED
        bounty.submission = submission
        return []

    def verify_bounty(
        self, bounty: Bounty, verifier: str, valid: bool, reason: str = ""
    ) -> List[EconomicEvent]:
        """
        Transition: SUBMITTED -> VERIFIED (if valid) or REJECTED (if invalid)
        """
        if bounty.status != BountyStatus.SUBMITTED:
            raise ValueError(f"Bounty {bounty.bounty_id} is not SUBMITTED")

        events = []

        if valid:
            bounty.status = BountyStatus.VERIFIED
        else:
            bounty.status = BountyStatus.REJECTED

            # Simple logic: Return stake unless reason is SPAM
            if reason != "SPAM" and bounty.res_stake_required > 0:
                refund_event = emit_res_stake_returned_event(
                    bounty_id=bounty.bounty_id,
                    contributor_wallet=bounty.current_claimant,
                    res_amount=bounty.res_stake_required,
                    reason=f"REJECTED: {reason}",
                )
                events.append(refund_event)
            elif reason == "SPAM" and bounty.res_stake_required > 0:
                pass

            reject_event = emit_bounty_rejected_event(
                bounty_id=bounty.bounty_id,
                contributor_wallet=bounty.current_claimant,
                verifier=verifier,
                reason=reason,
                res_slashed=bounty.res_stake_required if reason == "SPAM" else 0,
            )
            events.append(reject_event)

        return events

    def process_payment(self, bounty: Bounty, verifier: str) -> List[EconomicEvent]:
        """
        Transition: VERIFIED -> PAID
        Effect: Distributes rewards from Treasury, applies ATR boost, returns Stake.
        """
        if bounty.status != BountyStatus.VERIFIED:
            raise ValueError(f"Bounty {bounty.bounty_id} is not VERIFIED")

        events = []

        # 1. Payout from Treasury (convert to BigNum128)
        flx_reward = BigNum128.from_int(bounty.reward_flx)
        chr_reward = BigNum128.from_int(bounty.reward_chr)

        payout_event = self.treasury.pay_bounty(
            bounty_id=bounty.bounty_id,
            contributor=bounty.current_claimant,
            flx=flx_reward,
            chr=chr_reward,
            pr_number=bounty.submission.pr_number if bounty.submission else 0,
            commit_hash=bounty.submission.commit_hash if bounty.submission else "N/A",
            verifier=verifier,
        )
        events.append(payout_event)

        # 2. Return Stake
        if bounty.res_stake_required > 0:
            return_event = emit_res_stake_returned_event(
                bounty_id=bounty.bounty_id,
                contributor_wallet=bounty.current_claimant,
                res_amount=bounty.res_stake_required,
                reason="PAID",
            )
            events.append(return_event)

        # 3. Apply ATR Boost
        # Ensure we pass the enum value or object correctly to helper
        atr_amount = self._calculate_atr(bounty.impact_tier)
        atr_event = emit_atr_boost_event(
            contributor_wallet=bounty.current_claimant,
            pr_number=bounty.submission.pr_number if bounty.submission else 0,
            commit_hash=bounty.submission.commit_hash if bounty.submission else "N/A",
            impact_tier=bounty.impact_tier.value
            if hasattr(bounty.impact_tier, "value")
            else bounty.impact_tier,
            atr_delta=atr_amount,
            bounty_id=bounty.bounty_id,
        )
        events.append(atr_event)

        bounty.status = BountyStatus.PAID

        return events

    def _calculate_atr(self, tier: Any) -> int:
        from v13.policy.bounties.bounty_schema import ImpactTier

        # Handle both Enum and string cases
        tier_value = tier.value if hasattr(tier, "value") else tier

        if tier_value == ImpactTier.MINOR.value or tier == ImpactTier.MINOR:
            return 10
        if tier_value == ImpactTier.FEATURE.value or tier == ImpactTier.FEATURE:
            return 50
        if tier_value == ImpactTier.CORE.value or tier == ImpactTier.CORE:
            return 100
        return 0
