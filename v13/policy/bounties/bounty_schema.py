"""
Bounty Schema for Developer Rewards

Defines deterministic bounty structures for QFS × ATLAS contributor rewards.
All bounties are:
- Deterministic (fixed rewards, clear criteria)
- Explainable (bounty ID + commit hash)
- Zero-Sim compliant (replayable)
- Constitutionally sound (bounded, non-speculative)
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from enum import Enum
import json


class BountyStatus(Enum):
    """Bounty lifecycle states"""

    OPEN = "open"
    CLAIMED = "claimed"
    SUBMITTED = "submitted"
    VERIFIED = "verified"
    PAID = "paid"
    REJECTED = "rejected"
    EXPIRED = "expired"


class SubmissionStatus(Enum):
    """Submission review states"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISIONS_REQUESTED = "revisions_requested"


class ImpactTier(Enum):
    """Contribution impact classification for ATR boosts"""

    MINOR = "minor"  # Docs, small fixes: +10 ATR
    FEATURE = "feature"  # Modules, services: +50 ATR
    CORE = "core"  # Math, Zero-Sim, governance: +100 ATR


@dataclass
class Bounty:
    """
    Deterministic bounty specification.

    All fields are immutable after creation except status.
    Rewards are fixed at creation time for determinism.
    """

    bounty_id: str  # e.g., "BOUNTY-2025-001"
    title: str
    scope: str  # Detailed description
    acceptance_criteria: List[str]  # Deterministic, testable criteria
    reward_flx: int  # Fixed FLX reward
    reward_chr: int  # Fixed CHR reward
    res_stake_required: int  # Anti-spam RES stake
    created_at: int  # Unix timestamp (deterministic)
    created_by: str  # Wallet address
    status: BountyStatus = BountyStatus.OPEN
    expires_at: Optional[int] = None  # Unix timestamp, None = no expiration
    impact_tier: ImpactTier = ImpactTier.FEATURE  # For ATR boost
    tags: List[str] = field(default_factory=list)  # e.g., ["ci", "testing"]

    def to_dict(self) -> Dict:
        """Serialize to dictionary for storage"""
        data = asdict(self)
        data["status"] = self.status.value
        data["impact_tier"] = self.impact_tier.value
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "Bounty":
        """Deserialize from dictionary"""
        data["status"] = BountyStatus(data["status"])
        data["impact_tier"] = ImpactTier(data["impact_tier"])
        return cls(**data)

    def is_expired(self, current_timestamp: int) -> bool:
        """Check if bounty has expired"""
        if self.expires_at is None:
            return False
        return current_timestamp > self.expires_at

    def can_claim(self) -> bool:
        """Check if bounty can be claimed"""
        return self.status == BountyStatus.OPEN

    def validate_criteria(self) -> bool:
        """Validate acceptance criteria are deterministic and testable"""
        if not self.acceptance_criteria:
            return False

        # Check for vague language
        vague_terms = ["good", "better", "improve", "enhance", "optimize"]
        for criterion in self.acceptance_criteria:
            if any(term in criterion.lower() for term in vague_terms):
                return False

        return True


@dataclass
class BountySubmission:
    """
    Contributor submission for bounty completion.

    Links bounty to PR and tracks verification status.
    """

    submission_id: str  # e.g., "SUB-2025-001"
    bounty_id: str
    contributor_wallet: str
    pr_number: int
    commit_hash: str  # For deterministic replay
    res_staked: int  # Actual RES staked
    submitted_at: int  # Unix timestamp
    status: SubmissionStatus = SubmissionStatus.PENDING
    verification_notes: str = ""
    verified_by: Optional[str] = None  # Verifier wallet
    verified_at: Optional[int] = None  # Verification timestamp

    def to_dict(self) -> Dict:
        """Serialize to dictionary for storage"""
        data = asdict(self)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "BountySubmission":
        """Deserialize from dictionary"""
        data["status"] = SubmissionStatus(data["status"])
        return cls(**data)

    def can_verify(self) -> bool:
        """Check if submission can be verified"""
        return self.status == SubmissionStatus.PENDING

    def can_pay(self) -> bool:
        """Check if submission can be paid"""
        return self.status == SubmissionStatus.APPROVED


@dataclass
class ContributorProfile:
    """
    Contributor reputation and history tracking.

    Non-transferable reputation (ATR) and contribution history.
    """

    wallet_address: str
    total_atr: int = 0
    bounties_completed: int = 0
    total_flx_earned: int = 0
    total_chr_earned: int = 0
    first_contribution_at: Optional[int] = None
    last_contribution_at: Optional[int] = None
    contribution_history: List[Dict] = field(default_factory=list)

    def add_contribution(
        self,
        bounty_id: str,
        pr_number: int,
        atr_delta: int,
        flx_earned: int,
        chr_earned: int,
        timestamp: int,
    ):
        """Record a new contribution"""
        self.total_atr += atr_delta
        self.bounties_completed += 1
        self.total_flx_earned += flx_earned
        self.total_chr_earned += chr_earned

        if self.first_contribution_at is None:
            self.first_contribution_at = timestamp
        self.last_contribution_at = timestamp

        self.contribution_history.append(
            {
                "bounty_id": bounty_id,
                "pr_number": pr_number,
                "atr_delta": atr_delta,
                "flx_earned": flx_earned,
                "chr_earned": chr_earned,
                "timestamp": timestamp,
            }
        )

    def to_dict(self) -> Dict:
        """Serialize to dictionary for storage"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "ContributorProfile":
        """Deserialize from dictionary"""
        return cls(**data)


# ATR boost amounts by impact tier
ATR_BOOST_AMOUNTS = {ImpactTier.MINOR: 10, ImpactTier.FEATURE: 50, ImpactTier.CORE: 100}


def calculate_atr_boost(impact_tier: ImpactTier) -> int:
    """Calculate ATR boost for given impact tier"""
    return ATR_BOOST_AMOUNTS[impact_tier]


def classify_impact_tier(files_changed: List[str], pr_labels: List[str]) -> ImpactTier:
    """
    Classify contribution impact tier based on files and labels.

    Rules:
    - Core: Changes to v13/libs/, v13/core/, Zero-Sim, governance
    - Feature: Changes to v13/atlas/, v13/policy/, new modules
    - Minor: Changes to docs/, tests/, scripts/, small fixes
    """
    # Check for core changes
    core_paths = [
        "v13/libs/",
        "v13/core/",
        "v13/scripts/zero_sim",
        "v13/policy/governance/",
    ]

    if any(any(path in f for path in core_paths) for f in files_changed):
        return ImpactTier.CORE

    # Check for feature changes
    feature_paths = ["v13/atlas/", "v13/policy/"]

    if any(any(path in f for path in feature_paths) for f in files_changed):
        return ImpactTier.FEATURE

    # Check labels
    if "core" in pr_labels or "critical" in pr_labels:
        return ImpactTier.CORE

    if "feature" in pr_labels or "enhancement" in pr_labels:
        return ImpactTier.FEATURE

    # Default to minor
    return ImpactTier.MINOR
