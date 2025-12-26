"""
models.py - Canonical Social Layer Models for ATLAS

Defines the deterministic data structures for the ATLAS Social Layer,
including Posts, Comments, and Social Epochs used for Coherence Scoring
and Reward Distribution.

Strictly follows Phase 0 requirements for defining canonical objects.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from v13.libs.BigNum128 import BigNum128
from v13.core.reward_types import RewardBundle


@dataclass
class SocialContentBase:
    """Base class for social content (Post, Comment)"""

    id: str
    author_id: str
    timestamp: int
    content_hash: str  # IPFS or other deterministic hash
    text_content: str

    # Coherence & Reward State
    # coh_score is a BigNum128 in range [0, 1] (scaled by precision)
    coherence_score: Optional[BigNum128] = None
    reward_bundle: Optional[RewardBundle] = None


@dataclass
class Post(SocialContentBase):
    """Canonical Post object"""

    thread_id: str = ""
    title: str = ""
    tags: List[str] = field(default_factory=list)

    # Metrics stored as BigNum128 for precision in scoring
    engagement_metrics: Dict[str, BigNum128] = field(default_factory=dict)

    # For Phase 2: Computed engagement weight
    engagement_weight: Optional[BigNum128] = None


@dataclass
class Comment(SocialContentBase):
    """Canonical Comment object"""

    post_id: str = ""
    parent_comment_id: Optional[str] = None

    # Quality metrics
    quality_score: Optional[BigNum128] = None
    helper_flag: bool = False  # If it answers a question


@dataclass
class SocialEpoch:
    """Represents a discrete time window for social rewards"""

    epoch_id: int
    start_time: int
    end_time: int
    emission_pool: BigNum128  # Total FLX available for this epoch

    # State tracking
    is_closed: bool = False
    is_finalized: bool = False
    merkle_root: Optional[str] = None

    # Aggregates for Growth Dynamics (Phase 5)
    total_coherence: Optional[BigNum128] = None


@dataclass
class SocialEpochSnapshot:
    """
    Deterministic snapshot of an epoch for governance/replay.
    Used to generate the Merkle root.
    """

    epoch_id: int
    post_ids: List[str]
    # We store string representations of BigNum128 to ensure JSON serialization consistency
    coherence_scores_map: Dict[str, str]
    reward_allocations_map: Dict[str, str]
    merkle_root: str


@dataclass
class SocialRewardReceipt:
    """
    Detailed receipt for a social reward distribution.
    Enables EvidenceBus logging and full provenance.
    """

    epoch_id: int
    post_id: str
    author_id: str

    # Outcomes
    bundle: RewardBundle

    # Factors (All BigNum128)
    coherence_score: BigNum128
    engagement_weight: BigNum128
    sybil_multiplier: BigNum128
    eligibility_factor: BigNum128

    # Metadata
    merkle_leaf_hash: str = ""
