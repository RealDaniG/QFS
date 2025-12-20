"""
Bounty F-Layer (v17 Beta)

Deterministic functions for bounty lifecycle and reward computation.
All operations consume EvidenceBus history; F remains final authority.
"""

import hashlib
from typing import Dict, List, Optional, Any
from v15.evidence.bus import EvidenceBus
from v17.bounties.schemas import (
    Bounty,
    Contribution,
    RewardDecision,
    BountyState,
    BountyConfig,
)


def create_bounty(
    space_id: str,
    title: str,
    description: str,
    reward_amount: float,
    created_by: str,
    timestamp: int,
    currency: str = "QFS",
    deadline: Optional[int] = None,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict] = None,
) -> Bounty:
    """
    Create a deterministic bounty.

    Args:
        space_id: Space where bounty is created
        title: Bounty title
        description: Bounty description
        reward_amount: Total reward amount
        created_by: Creator wallet address
        timestamp: Deterministic timestamp
        currency: Reward currency (default "QFS")
        deadline: Optional deadline timestamp
        tags: Optional tags/categories
        metadata: Optional additional data

    Returns:
        Validated Bounty instance
    """
    # Generate deterministic bounty ID
    bounty_id = _generate_bounty_id(space_id, title, created_by, timestamp)

    # Create bounty
    bounty = Bounty(
        bounty_id=bounty_id,
        space_id=space_id,
        title=title,
        description=description,
        reward_amount=reward_amount,
        currency=currency,
        created_by=created_by,
        created_at=timestamp,
        deadline=deadline,
        tags=tags or [],
        metadata=metadata or {},
    )

    # Emit to EvidenceBus
    EvidenceBus.emit(
        "BOUNTY_CREATED",
        {
            "bounty": bounty.model_dump(),
            "timestamp": timestamp,
        },
    )

    return bounty


def submit_contribution(
    bounty_id: str,
    contributor_wallet: str,
    reference: str,
    timestamp: int,
    proof: Optional[Dict] = None,
) -> Contribution:
    """
    Submit a deterministic contribution to a bounty.

    Args:
        bounty_id: Bounty being contributed to
        contributor_wallet: Contributor wallet address
        reference: Reference (PR URL, commit hash, etc.)
        timestamp: Deterministic timestamp
        proof: Optional proof of contribution

    Returns:
        Validated Contribution instance
    """
    # Generate deterministic contribution ID
    contribution_id = _generate_contribution_id(
        bounty_id, contributor_wallet, timestamp
    )

    # Create contribution
    contribution = Contribution(
        contribution_id=contribution_id,
        bounty_id=bounty_id,
        contributor_wallet=contributor_wallet,
        reference=reference,
        submitted_at=timestamp,
        proof=proof,
    )

    # Emit to EvidenceBus
    EvidenceBus.emit(
        "BOUNTY_CONTRIBUTION_SUBMITTED",
        {
            "contribution": contribution.model_dump(),
            "timestamp": timestamp,
        },
    )

    return contribution


def get_bounty_state(
    bounty_id: str,
    events: Optional[List[Dict]] = None,
    include_advisory: bool = True,
) -> Optional[BountyState]:
    """
    Reconstruct bounty state from EvidenceBus events (pure function).

    Args:
        bounty_id: ID of bounty to reconstruct
        events: Optional pre-filtered events (if None, fetches from EvidenceBus)
        include_advisory: Whether to include advisory signals

    Returns:
        BountyState if found, None otherwise
    """
    # Fetch events if not provided
    if events is None:
        events = EvidenceBus.get_events(limit=1_000_000)

    # Find bounty creation event
    bounty_data = None
    contributions = []
    reward_decisions = []
    advisory_signals = []

    for envelope in events:
        if not isinstance(envelope, dict):
            continue

        event = envelope.get("event", {})
        if not isinstance(event, dict):
            continue

        event_type = event.get("type")
        payload = event.get("payload", {})

        # Bounty creation
        if event_type == "BOUNTY_CREATED":
            b = payload.get("bounty", {})
            if isinstance(b, dict) and b.get("bounty_id") == bounty_id:
                bounty_data = b

        # Contributions
        elif event_type == "BOUNTY_CONTRIBUTION_SUBMITTED":
            contrib = payload.get("contribution", {})
            if isinstance(contrib, dict) and contrib.get("bounty_id") == bounty_id:
                contributions.append(contrib)

        # Reward decisions
        elif event_type == "BOUNTY_REWARD_DECIDED":
            decision = payload.get("decision", {})
            if isinstance(decision, dict) and decision.get("bounty_id") == bounty_id:
                reward_decisions.append(decision)

        # Advisory signals
        elif event_type == "AGENT_ADVISORY" and include_advisory:
            advisory = payload.get("advisory", {})
            if isinstance(advisory, dict):
                # Check if advisory relates to this bounty
                content_score = advisory.get("content_score", {})
                if isinstance(content_score, dict):
                    if content_score.get("content_id") == bounty_id:
                        advisory_signals.append(advisory)

    if not bounty_data:
        return None

    # Reconstruct state
    from pydantic import ValidationError

    try:
        bounty = Bounty(**bounty_data)
    except ValidationError:
        return None

    contribution_objects = []
    for c in contributions:
        try:
            contribution_objects.append(Contribution(**c))
        except ValidationError:
            continue

    decision_objects = []
    for d in reward_decisions:
        try:
            decision_objects.append(RewardDecision(**d))
        except ValidationError:
            continue

    state = BountyState(
        bounty=bounty,
        contributions=contribution_objects,
        reward_decisions=decision_objects,
        advisory_signals=advisory_signals,
    )

    # Compute totals
    state.compute_totals()

    return state


def compute_rewards(
    bounty_state: BountyState,
    timestamp: int,
    use_advisory: bool = True,
    config: Optional[BountyConfig] = None,
) -> List[RewardDecision]:
    """
    Compute deterministic reward allocation (pure function).

    Args:
        bounty_state: Current bounty state with contributions
        timestamp: Deterministic timestamp
        use_advisory: Whether to use advisory signals in scoring
        config: Optional configuration for caps/limits

    Returns:
        List of RewardDecision objects
    """
    if not bounty_state.contributions:
        return []

    # 1. Compute raw scores
    scores = []
    for contribution in bounty_state.contributions:
        score = _compute_contribution_score(
            contribution,
            bounty_state.advisory_signals if use_advisory else [],
        )
        scores.append((contribution, score))

    total_score = sum(s[1] for s in scores)

    # Handle zero sums
    if total_score <= 0:
        # Fallback: Equal distribution if all scores zero?
        # Or no rewards? Safe default is NO REWARDS if quality is 0.
        # But for backward compat with previous logic (fallback equal), let's see.
        # Previous: "Equal distribution if all scores are zero".
        # Safe V17: If quality is 0, payout is 0.
        # But to avoid "stuck" funds on low-quality, maybe fallback is needed?
        # Let's keep strict: 0 score = 0 reward.
        return []

    # 2. Calculate raw allocations
    total_reward_pool = bounty_state.bounty.reward_amount
    allocations = []

    # Cap ratio (default 1.0 = 100%)
    max_ratio = config.max_reward_per_contributor_ratio if config else 1.0

    current_allocated_sum = 0.0

    for contribution, score in scores:
        # Raw share
        share_ratio = score / total_score

        # Apply cap to the RATIO (or amount)
        # If one person gets 90% but cap is 80%, they get 80%.
        # The remainder 10% stays unallocated (safe).

        effective_ratio = min(share_ratio, max_ratio)
        amount = total_reward_pool * effective_ratio

        # floor to 2 decimals for currency safety (or keep float precision and floor at end?)
        # For determinism, let's keep high precision float but maybe simple round?
        # Actually standard python float is deterministic enough for this scale usually.

        allocations.append(
            {
                "contribution": contribution,
                "amount": amount,
                "percentage": effective_ratio,
                "raw_score": score,
            }
        )
        current_allocated_sum += amount

    # 3. Final safety check: ensure we don't exceed total pool
    # (Math says we won't if sum(ratios) <= 1.0, and capping only reduces it).
    # But floating point errors can happen.
    if current_allocated_sum > total_reward_pool:
        # Scale down linearly to fit perfect pool
        scale_factor = total_reward_pool / current_allocated_sum
        for alloc in allocations:
            alloc["amount"] *= scale_factor
            alloc["percentage"] *= scale_factor

    # 4. Generate Decisions
    decisions = []
    for alloc in allocations:
        decision = RewardDecision(
            bounty_id=bounty_state.bounty.bounty_id,
            recipient_wallet=alloc["contribution"].contributor_wallet,
            amount=alloc["amount"],
            percentage=alloc["percentage"],
            reason=f"Score: {alloc['raw_score']:.2f}, Share: {alloc['percentage']:.2%}",
            decided_at=timestamp,
            quality_score=alloc["raw_score"],
        )
        decisions.append(decision)

    return decisions


def finalize_bounty(
    bounty_id: str,
    reward_decisions: List[RewardDecision],
    timestamp: int,
) -> List[RewardDecision]:
    """
    Finalize a bounty by emitting reward decision events.

    Args:
        bounty_id: Bounty being finalized
        reward_decisions: Computed reward decisions
        timestamp: Deterministic timestamp

    Returns:
        The reward decisions (for chaining)
    """
    for decision in reward_decisions:
        EvidenceBus.emit(
            "BOUNTY_REWARD_DECIDED",
            {
                "decision": decision.model_dump(),
                "timestamp": timestamp,
            },
        )

    return reward_decisions


def _generate_bounty_id(
    space_id: str,
    title: str,
    created_by: str,
    timestamp: int,
) -> str:
    """Generate deterministic bounty ID."""
    canonical = f"{space_id}:{title}:{created_by}:{timestamp}"
    hash_obj = hashlib.sha256(canonical.encode("utf-8"))
    hash_hex = hash_obj.hexdigest()[:16]
    return f"bounty_{space_id}_{timestamp}_{hash_hex}"


def _generate_contribution_id(
    bounty_id: str,
    contributor_wallet: str,
    timestamp: int,
) -> str:
    """Generate deterministic contribution ID."""
    canonical = f"{bounty_id}:{contributor_wallet}:{timestamp}"
    hash_obj = hashlib.sha256(canonical.encode("utf-8"))
    hash_hex = hash_obj.hexdigest()[:16]
    return f"contrib_{bounty_id}_{timestamp}_{hash_hex}"


def _compute_contribution_score(
    contribution: Contribution,
    advisory_signals: List[Dict],
) -> float:
    """
    Compute deterministic contribution score (pure function).

    Args:
        contribution: Contribution to score
        advisory_signals: Advisory signals from agent layer

    Returns:
        Score (0.0 to 1.0)
    """
    # Base score (deterministic hash-based)
    hash_obj = hashlib.sha256(contribution.contribution_id.encode("utf-8"))
    base_score = int(hash_obj.hexdigest()[:8], 16) / 0xFFFFFFFF  # Normalize to 0-1

    # Adjust with advisory signals if available
    advisory_score = 0.0
    advisory_count = 0

    for signal in advisory_signals:
        content_score = signal.get("content_score", {})
        if isinstance(content_score, dict):
            if content_score.get("content_id") == contribution.contribution_id:
                quality = content_score.get("quality", 0.0)
                if isinstance(quality, (int, float)):
                    advisory_score += quality
                    advisory_count += 1

    if advisory_count > 0:
        advisory_score /= advisory_count
        # Weighted average: 50% base, 50% advisory
        return (base_score * 0.5) + (advisory_score * 0.5)

    return base_score
