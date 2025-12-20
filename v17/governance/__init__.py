"""
Governance Package (v17 Beta)

Deterministic governance F-layer for QFS × ATLAS.
All functions are pure: same inputs → same outputs.
"""

from v17.governance.schemas import (
    GovernanceConfig,
    Proposal,
    Vote,
    ProposalState,
    ExecutionRecord,
)

from v17.governance.f_proposals import (
    create_proposal,
    get_proposal_state,
)

from v17.governance.f_voting import (
    cast_vote,
    validate_vote_eligibility,
    get_voter_choice,
    compute_participation_rate,
)

from v17.governance.f_execution import (
    compute_outcome,
    finalize_proposal,
)

__all__ = [
    # Schemas
    "GovernanceConfig",
    "Proposal",
    "Vote",
    "ProposalState",
    "ExecutionRecord",
    # Proposal functions
    "create_proposal",
    "get_proposal_state",
    # Voting functions
    "cast_vote",
    "validate_vote_eligibility",
    "get_voter_choice",
    "compute_participation_rate",
    # Execution functions
    "compute_outcome",
    "finalize_proposal",
]
