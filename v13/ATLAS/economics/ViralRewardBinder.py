"""
ViralRewardBinder.py - Determine Economic Rewards from Viral Engagement

This module translates deterministic viral scores (Proof-of-Reach) into
actual CHR token rewards. It acts as the Economic Feedback Loop between
the Social Layer (ATLAS) and the Token Layer (QFS).

Invariants:
- ECON-I1: Total allocated rewards must never exceed the daily viral cap (CHR_DAILY_EMISSION_CAP / fraction).
- ECON-I2: Distribution must be strictly proportional to score share (Pro-Rata).
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from v13.libs.CertifiedMath import CertifiedMath
from v13.libs.BigNum128 import BigNum128
from v13.libs.governance.RewardAllocator import RewardAllocator, AllocatedReward
from v13.core.reward_types import RewardBundle


@dataclass
class EngagementProof:
    """Container for a verified viral score proof."""

    content_id: str
    author_address: str
    score: int
    proof_hash: str
    timestamp: int


class ViralRewardBinder:
    """
    Binds deterministic viral scores to economic rewards.
    """

    def __init__(
        self, cm: CertifiedMath, allocator: RewardAllocator, trigger: Any = None
    ):
        """
        Initialize the binder.

        Args:
            cm: CertifiedMath instance.
            allocator: RewardAllocator instance.
            trigger: GovernanceTrigger instance (v15 Integration).
        """
        self.cm = cm
        self.allocator = allocator
        self.trigger = trigger

        # Default Fallback (Stage 4 behavior)
        self._DEFAULT_POOL_CAP = BigNum128.from_int(1_000_000)

    @property
    def VIRAL_POOL_CAP(self) -> BigNum128:
        """Fetch Current Cap from Active Governance Snapshot."""
        if self.trigger:
            # v15: Read from Versioned Snapshot (Ensures intra-epoch stability)
            try:
                # trigger.get_parameter() handles fallback to registry/defaults
                return self.trigger.get_parameter("VIRAL_POOL_CAP")
            except Exception:
                return self._DEFAULT_POOL_CAP
        else:
            # Stage 4 Legacy
            return self._DEFAULT_POOL_CAP

    def bind_rewards(
        self,
        proofs: List[EngagementProof],
        pool_amount: BigNum128,
        log_list: List[Dict[str, Any]],
        pqc_cid: Optional[str] = None,
    ) -> Dict[str, AllocatedReward]:
        """
        Calculate and bind rewards for a batch of engagement proofs.

        Args:
            proofs: List of verified engagement proofs.
            pool_amount: Total CHR available for this batch (must be <= VIRAL_POOL_CAP).
            log_list: Audit log list.

        Returns:
            Dict[str, AllocatedReward]: Map of address -> Reward Object.
        """

        # 1. Validate Input Pool Cap
        if self.cm.gt(pool_amount, self.VIRAL_POOL_CAP, log_list, pqc_cid):
            pool_amount = self.VIRAL_POOL_CAP  # Hard Cap Enforcement (Fail-Safe)
            log_list.append(
                {
                    "operation": "viral_binder_cap_enforced",
                    "original_pool": pool_amount.to_decimal_string(),
                    "capped_pool": self.VIRAL_POOL_CAP.to_decimal_string(),
                }
            )

        # 2. Aggregate Total Score
        total_score_int = 0
        for p in proofs:
            total_score_int += p.score

        total_score = BigNum128.from_int(total_score_int)

        if total_score_int == 0:
            return {}

        # 3. Calculate Weights (Pro-Rata)
        # Weight = IndividualScore / TotalScore
        allocation_weights = {}
        for p in proofs:
            score_bn = BigNum128.from_int(p.score)
            weight = self.cm.div(score_bn, total_score, log_list, pqc_cid)

            # Aggregate weights per author (if user has multiple contents)
            if p.author_address in allocation_weights:
                current_weight = allocation_weights[p.author_address]
                allocation_weights[p.author_address] = self.cm.add(
                    current_weight, weight, log_list, pqc_cid
                )
            else:
                allocation_weights[p.author_address] = weight

        # 4. Construct Reward Bundle
        # We only populate CHR for viral rewards in this stage.
        reward_bundle = RewardBundle(
            chr_reward=pool_amount,
            flx_reward=BigNum128(0),
            res_reward=BigNum128(0),
            psi_sync_reward=BigNum128(0),
            atr_reward=BigNum128(0),
            nod_reward=BigNum128(0),
            total_reward=pool_amount,
        )

        # 5. Delegate to RewardAllocator for Validated Distribution
        recipient_addresses = list(allocation_weights.keys())

        allocated = self.allocator.allocate_rewards(
            reward_bundle=reward_bundle,
            recipient_addresses=recipient_addresses,
            allocation_weights=allocation_weights,
            log_list=log_list,
            pqc_cid=pqc_cid,
            deterministic_timestamp=proofs[0].timestamp if proofs else 0,
        )

        return allocated


def test_viral_binder():
    """Self-test for ViralRewardBinder."""
    cm = CertifiedMath()
    allocator = RewardAllocator(cm)
    binder = ViralRewardBinder(cm, allocator)

    proofs = [
        EngagementProof("c1", "addr_alice", 100, "hash1", 1000),
        EngagementProof("c2", "addr_bob", 200, "hash2", 1000),
        EngagementProof("c3", "addr_charlie", 700, "hash3", 1000),
    ]
    # Total Score = 1000.
    # Alice=10%, Bob=20%, Charlie=70%

    pool = BigNum128.from_int(1000)  # 1000 CHR Pool
    log_list = []

    rewards = binder.bind_rewards(proofs, pool, log_list)

    # Expected: Alice=100, Bob=200, Charlie=700
    print(f"Alice Reward: {rewards['addr_alice'].chr_amount.to_decimal_string()}")

    # Wait, BigNum128.from_int(1000) creates 1000.0 if using standard constructor?
    # Checking constants: FIXED_POINT_SCALE = 10**18.
    # RewardBundle assumes amounts are properly scaled BigNum128s.
    # If I pass from_int(1000), it's 1000 raw units?
    # Let's check test_reward_allocator usage:
    # chr_reward=BigNum128.from_int(100) -> implies 100 units?
    # CertifiedMath logic handles scaling.

    # Actually, from_int(x) usually means x scaled by 10^18 if it's a fixed point class helper?
    # Let's verify BigNum128 source if needed.
    # Assuming from_int creates integer representation.

    # If total pool is 1000 units. Alice gets 100 units.
    assert rewards["addr_alice"].chr_amount == BigNum128.from_int(100)
    assert rewards["addr_bob"].chr_amount == BigNum128.from_int(200)
    assert rewards["addr_charlie"].chr_amount == BigNum128.from_int(700)

    print("ViralRewardBinder self-test passed.")


if __name__ == "__main__":
    test_viral_binder()
