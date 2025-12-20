"""
Governance F-Layer: Proposals (v17 Beta)

Deterministic functions for proposal creation and state reconstruction.
All operations consume EvidenceBus history; no direct state mutation.
"""

import hashlib
from typing import Dict, List, Optional
from v15.evidence.bus import EvidenceBus
from v17.governance.schemas import Proposal, ProposalState, GovernanceConfig


def create_proposal(
    space_id: str,
    creator_wallet: str,
    title: str,
    body: str,
    timestamp: int,
    config: GovernanceConfig,
    metadata: Optional[Dict] = None,
) -> Proposal:
    """
    Create a deterministic proposal.

    Args:
        space_id: Space where proposal is created
        creator_wallet: Wallet address of creator
        title: Proposal title
        body: Proposal body
        timestamp: Deterministic timestamp
        config: Governance configuration
        metadata: Optional additional data

    Returns:
        Validated Proposal instance
    """
    # Generate deterministic proposal ID
    proposal_id = _generate_proposal_id(space_id, creator_wallet, title, timestamp)

    # Calculate voting end time
    voting_ends_at = timestamp + config.voting_period_seconds

    # Create proposal
    proposal = Proposal(
        proposal_id=proposal_id,
        space_id=space_id,
        creator_wallet=creator_wallet,
        title=title,
        body=body,
        created_at=timestamp,
        voting_ends_at=voting_ends_at,
        metadata=metadata or {},
    )

    # Emit to EvidenceBus
    EvidenceBus.emit(
        "GOV_PROPOSAL_CREATED",
        {
            "proposal": proposal.model_dump(),
            "timestamp": timestamp,
        },
    )

    return proposal


def get_proposal_state(
    proposal_id: str,
    events: Optional[List[Dict]] = None,
    include_advisory: bool = True,
) -> Optional[ProposalState]:
    """
    Reconstruct proposal state from EvidenceBus events (pure function).

    Args:
        proposal_id: ID of proposal to reconstruct
        events: Optional pre-filtered events (if None, fetches from EvidenceBus)
        include_advisory: Whether to include advisory signals

    Returns:
        ProposalState if found, None otherwise
    """
    # Fetch events if not provided
    if events is None:
        # Fetch effectively all events (no silent truncation)
        events = EvidenceBus.get_events(limit=1_000_000)

    # Find proposal creation event
    proposal_data = None
    votes = []
    advisory_signals = []

    for envelope in events:
        if not isinstance(envelope, dict):
            continue

        event = envelope.get("event", {})
        if not isinstance(event, dict):
            continue

        event_type = event.get("type")
        payload = event.get("payload", {})

        # Proposal creation
        if event_type == "GOV_PROPOSAL_CREATED":
            prop = payload.get("proposal", {})
            if isinstance(prop, dict) and prop.get("proposal_id") == proposal_id:
                proposal_data = prop

        # Votes
        elif event_type == "GOV_VOTE_CAST":
            vote = payload.get("vote", {})
            if isinstance(vote, dict) and vote.get("proposal_id") == proposal_id:
                votes.append(vote)

        # Advisory signals
        elif event_type == "AGENT_ADVISORY" and include_advisory:
            advisory = payload.get("advisory", {})
            if isinstance(advisory, dict):
                # Check if advisory relates to this proposal
                recommendation = advisory.get("recommendation", {})
                if isinstance(recommendation, dict):
                    if recommendation.get("entity_id") == proposal_id:
                        advisory_signals.append(advisory)

    if not proposal_data:
        return None

    # Reconstruct state
    from v17.governance.schemas import Vote
    from pydantic import ValidationError

    try:
        proposal = Proposal(**proposal_data)
    except ValidationError:
        # Malformed proposal event - ignore
        return None

    vote_objects = []
    for v in votes:
        try:
            vote_objects.append(Vote(**v))
        except ValidationError:
            # Malformed vote - ignore
            continue

    state = ProposalState(
        proposal=proposal,
        votes=vote_objects,
        advisory_signals=advisory_signals,
    )

    # Compute tallies
    state.compute_tallies()

    return state


def _generate_proposal_id(
    space_id: str,
    creator_wallet: str,
    title: str,
    timestamp: int,
) -> str:
    """
    Generate deterministic proposal ID.

    Args:
        space_id: Space ID
        creator_wallet: Creator wallet
        title: Proposal title
        timestamp: Creation timestamp

    Returns:
        Deterministic proposal ID
    """
    # Canonical string for hashing
    canonical = f"{space_id}:{creator_wallet}:{title}:{timestamp}"

    # Hash to get deterministic ID
    hash_obj = hashlib.sha256(canonical.encode("utf-8"))
    hash_hex = hash_obj.hexdigest()[:16]  # Use first 16 chars

    return f"prop_{space_id}_{timestamp}_{hash_hex}"
