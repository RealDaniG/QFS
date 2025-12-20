"""
v17 Package (Beta)

QFS × ATLAS v17: Governance & Bounty F-Layer

Deterministic governance and bounty management built on v16 Evergreen Baseline.
All state transitions are pure functions consuming EvidenceBus history.
"""

# Governance
from v17.governance import (
    GovernanceConfig,
    Proposal,
    Vote,
    ProposalState,
    ExecutionRecord,
    create_proposal,
    get_proposal_state,
    cast_vote,
    validate_vote_eligibility,
    get_voter_choice,
    compute_participation_rate,
    compute_outcome,
    finalize_proposal,
)

# Bounties
from v17.bounties import (
    Bounty,
    Contribution,
    RewardDecision,
    BountyState,
    create_bounty,
    submit_contribution,
    get_bounty_state,
    compute_rewards,
    finalize_bounty,
)

__version__ = "17.0.0-beta"

__all__ = [
    # Governance
    "GovernanceConfig",
    "Proposal",
    "Vote",
    "ProposalState",
    "ExecutionRecord",
    "create_proposal",
    "get_proposal_state",
    "cast_vote",
    "validate_vote_eligibility",
    "get_voter_choice",
    "compute_participation_rate",
    "compute_outcome",
    "finalize_proposal",
    # Bounties
    "Bounty",
    "Contribution",
    "RewardDecision",
    "BountyState",
    "create_bounty",
    "submit_contribution",
    "get_bounty_state",
    "compute_rewards",
    "finalize_bounty",
]
