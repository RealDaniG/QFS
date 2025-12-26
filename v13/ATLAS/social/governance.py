"""
governance.py - Social Layer Governance & Replay Logic

Handles the creation of deterministic epoch snapshots (Merkle Roots)
and provides verification utilities for governance audits.
"""

import hashlib
import json
from typing import List, Dict, Any, Tuple
from v13.atlas.social.models import SocialEpochSnapshot, SocialEpoch
from v13.core.reward_types import RewardBundle


class SocialGovernance:
    """
    Governance engine for snapshotting and verifying social epochs.
    """

    @staticmethod
    def _hash_leaf(data: str) -> str:
        """SHA-256 hash of a leaf string."""
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    @staticmethod
    def _compute_merkle_root(current_level: List[str]) -> str:
        """
        Recursively computes the Merkle Root of a list of hashes.
        Strictly deterministic ordering is assumed to be handled by caller.
        """
        if not current_level:
            return SocialGovernance._hash_leaf("")

        if len(current_level) == 1:
            return current_level[0]

        next_level = []
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            if i + 1 < len(current_level):
                right = current_level[i + 1]
            else:
                right = left  # Duplicate last if odd number

            combined = f"{left}{right}"
            next_level.append(SocialGovernance._hash_leaf(combined))

        return SocialGovernance._compute_merkle_root(next_level)

    def create_epoch_snapshot(
        self,
        epoch: SocialEpoch,
        post_ids: List[str],
        post_coherence: Dict[str, Any],  # Any that has __str__ or is BigNum128
        reward_results: Dict[str, RewardBundle],
    ) -> SocialEpochSnapshot:
        """
        Freezes the results of an epoch into a merkle-proofed snapshot.
        """

        # 1. Deterministic Leaf Preparation
        # We process posts in ID order
        sorted_ids = sorted(post_ids)

        leaf_hashes = []
        coherence_map = {}
        alloc_map = {}

        for pid in sorted_ids:
            # Serialize Coherence
            coh_val = post_coherence.get(pid, "0")
            coh_str = str(coh_val)
            coherence_map[pid] = coh_str

            # Serialize Rewards (FLX, CHR, RES)
            bundle = reward_results.get(pid)
            if bundle:
                # Format: "FLX:100|CHR:5|RES:10"
                reward_str = (
                    f"FLX:{bundle.flx_reward}|"
                    f"CHR:{bundle.chr_reward}|"
                    f"RES:{bundle.res_reward}"
                )
            else:
                reward_str = "FLX:0|CHR:0|RES:0"

            alloc_map[pid] = reward_str

            # Leaf content: "PostID:Coh:Reward"
            leaf_content = f"{pid}:{coh_str}:{reward_str}"
            leaf_hashes.append(self._hash_leaf(leaf_content))

        # 2. Compute Root
        merkle_root = self._compute_merkle_root(leaf_hashes)

        return SocialEpochSnapshot(
            epoch_id=epoch.epoch_id,
            post_ids=sorted_ids,
            coherence_scores_map=coherence_map,
            reward_allocations_map=alloc_map,
            merkle_root=merkle_root,
        )

    def validate_snapshot(
        self,
        original_snapshot: SocialEpochSnapshot,
        replayed_snapshot: SocialEpochSnapshot,
    ) -> Tuple[bool, str]:
        """
        Compares a historical snapshot with a recomputed one.
        Returns (IsValid, Reason).
        """
        if original_snapshot.merkle_root != replayed_snapshot.merkle_root:
            return (
                False,
                f"Merkle Root Mismatch: {original_snapshot.merkle_root} != {replayed_snapshot.merkle_root}",
            )

        if original_snapshot.epoch_id != replayed_snapshot.epoch_id:
            return False, "Epoch ID Mismatch"

        return True, "Valid"
