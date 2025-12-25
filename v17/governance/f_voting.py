"""
Governance F-Layer: Voting (v17 Beta)

Deterministic functions for vote casting and validation.
Enforces deterministic rules: no double-voting, deterministic tie-breaking.
"""

from typing import Optional
from v15.evidence.bus import EvidenceBus
from v17.governance.schemas import Vote, ProposalState, GovernanceConfig


def cast_vote(
    proposal_id: str,
    voter_wallet: str,
    choice: str,
    timestamp: int,
    config: GovernanceConfig,
    weight: float = 1.0,
    signature: Optional[str] = None,
    existing_state: Optional[ProposalState] = None,
) -> Vote:
    """
    Cast a deterministic vote on a proposal.

    Args:
        proposal_id: Proposal being voted on
        voter_wallet: Wallet address of voter
        choice: Vote choice (must be in config.allowed_choices)
        timestamp: Deterministic timestamp
        config: Governance configuration
        weight: Vote weight (default 1.0)
        signature: Optional EIP-191 signature
        existing_state: Optional pre-computed proposal state (for validation)

    Returns:
        Validated Vote instance

    Raises:
        ValueError: If vote is invalid (double vote, invalid choice, etc.)
    """
    # Validate choice
    if choice not in config.allowed_choices:
        raise ValueError(
            f"Invalid choice '{choice}'. Must be one of: {config.allowed_choices}"
        )

    # Fetch state if not provided to enforce rules
    if existing_state is None:
        from v17.governance.f_proposals import get_proposal_state

        existing_state = get_proposal_state(proposal_id)

    if not existing_state:
        raise ValueError(f"Proposal {proposal_id} not found")

    # Check for double voting
    for existing_vote in existing_state.votes:
        if existing_vote.voter_wallet == voter_wallet:
            raise ValueError(
                f"Wallet {voter_wallet} has already voted on proposal {proposal_id}"
            )

    # Check if voting period has ended
    if timestamp > existing_state.proposal.voting_ends_at:
        raise ValueError(
            f"Voting period ended at {existing_state.proposal.voting_ends_at}, "
            f"cannot vote at {timestamp}"
        )

    # Create vote - convert weight to BigNum128 string format
    weight_str = f"{weight:.18f}"
    vote = Vote(
        proposal_id=proposal_id,
        voter_wallet=voter_wallet,
        choice=choice,
        weight=weight_str,
        timestamp=timestamp,
        signature=signature,
    )

    # Emit to EvidenceBus
    EvidenceBus.emit(
        "GOV_VOTE_CAST",
        {
            "vote": vote.model_dump(),
            "timestamp": timestamp,
        },
    )

    return vote


def validate_vote_eligibility(
    voter_wallet: str,
    proposal_state: ProposalState,
    timestamp: int,
) -> tuple[bool, str]:
    """
    Validate if a wallet is eligible to vote (pure function).

    Args:
        voter_wallet: Wallet to check
        proposal_state: Current proposal state
        timestamp: Current timestamp

    Returns:
        Tuple of (is_eligible, reason)
    """
    # Check if already voted
    for vote in proposal_state.votes:
        if vote.voter_wallet == voter_wallet:
            return False, "Already voted"

    # Check if voting period is active
    if timestamp < proposal_state.proposal.created_at:
        return False, "Voting has not started"

    if timestamp > proposal_state.proposal.voting_ends_at:
        return False, "Voting period has ended"

    return True, "Eligible"


def get_voter_choice(
    voter_wallet: str,
    proposal_state: ProposalState,
) -> Optional[str]:
    """
    Get the choice a wallet voted for (pure function).

    Args:
        voter_wallet: Wallet to check
        proposal_state: Current proposal state

    Returns:
        Vote choice if voted, None otherwise
    """
    for vote in proposal_state.votes:
        if vote.voter_wallet == voter_wallet:
            return vote.choice

    return None


def compute_participation_rate(proposal_state: ProposalState) -> float:
    """
    Compute participation rate (pure function).

    Args:
        proposal_state: Current proposal state

    Returns:
        Participation rate (0.0 to 1.0)

    Note:
        In a real system, this would compare against total eligible voters.
        For now, we use total_votes as a proxy.
    """
    if proposal_state.total_votes == 0:
        return 0.0

    # In production, this would be:
    # return proposal_state.total_votes / total_eligible_voters
    # For now, we return a normalized value
    return min(
        1.0, proposal_state.total_votes / 100.0
    )  # Assume 100 is "full participation"
