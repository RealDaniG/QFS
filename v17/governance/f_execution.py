"""
Governance F-Layer: Execution (v17 Beta)

Deterministic functions for outcome computation and proposal finalization.
All logic is pure: same state + config → same outcome.
"""

from typing import Dict, Optional
from v15.evidence.bus import EvidenceBus
from v17.governance.schemas import (
    ProposalState,
    ExecutionRecord,
    GovernanceConfig,
)


def compute_outcome(
    proposal_state: ProposalState,
    config: GovernanceConfig,
    current_timestamp: int,
) -> ExecutionRecord:
    """
    Compute deterministic proposal outcome (pure function).

    Args:
        proposal_state: Current proposal state with votes
        config: Governance configuration
        current_timestamp: Current deterministic timestamp

    Returns:
        ExecutionRecord with final outcome and reasoning
    """
    # Check if voting period has ended
    if current_timestamp < proposal_state.proposal.voting_ends_at:
        raise ValueError(
            f"Cannot compute outcome before voting ends at "
            f"{proposal_state.proposal.voting_ends_at}"
        )

    # Parse thresholds from BigNum128 string format to float
    quorum_threshold = float(config.quorum_threshold)
    approval_threshold = float(config.approval_threshold)

    # Compute participation rate
    # In production, this would use total eligible voters
    # For now, we use a simple threshold
    participation_rate = (
        proposal_state.total_votes / 100.0
    )  # Assume 100 is full participation

    # Check quorum
    if participation_rate < quorum_threshold:
        return ExecutionRecord(
            proposal_id=proposal_state.proposal.proposal_id,
            final_outcome="no_quorum",
            executed_at=current_timestamp,
            total_votes=proposal_state.total_votes,
            total_weight=proposal_state.total_weight,
            approve_weight=proposal_state.approve_weight,
            reject_weight=proposal_state.reject_weight,
            effects=None,
            reason=f"Quorum not met: {participation_rate:.2%} < {quorum_threshold:.2%}",
        )

    # Compute approval rate (excluding abstentions) - parse string weights
    approve_weight = float(proposal_state.approve_weight)
    reject_weight = float(proposal_state.reject_weight)
    voting_weight = approve_weight + reject_weight

    if voting_weight == 0:
        # All abstentions - use tie-break rule
        outcome = _apply_tie_break_rule(config.tie_break_rule)
        return ExecutionRecord(
            proposal_id=proposal_state.proposal.proposal_id,
            final_outcome=outcome,
            executed_at=current_timestamp,
            total_votes=proposal_state.total_votes,
            total_weight=proposal_state.total_weight,
            approve_weight=proposal_state.approve_weight,
            reject_weight=proposal_state.reject_weight,
            effects=None,
            reason=f"All votes abstained, tie-break rule applied: {config.tie_break_rule}",
        )

    approval_rate = approve_weight / voting_weight

    # Check for exact tie
    if approve_weight == reject_weight:
        outcome = _apply_tie_break_rule(config.tie_break_rule)
        return ExecutionRecord(
            proposal_id=proposal_state.proposal.proposal_id,
            final_outcome=outcome,
            executed_at=current_timestamp,
            total_votes=proposal_state.total_votes,
            total_weight=proposal_state.total_weight,
            approve_weight=proposal_state.approve_weight,
            reject_weight=proposal_state.reject_weight,
            effects=None,
            reason=f"Exact tie (50/50), tie-break rule applied: {config.tie_break_rule}",
        )

    # Determine outcome based on approval threshold
    if approval_rate >= approval_threshold:
        outcome = "approved"
        reason = (
            f"Quorum met ({participation_rate:.2%} >= {quorum_threshold:.2%}), "
            f"approval threshold met ({approval_rate:.2%} >= {approval_threshold:.2%})"
        )
    else:
        outcome = "rejected"
        reason = (
            f"Quorum met ({participation_rate:.2%} >= {quorum_threshold:.2%}), "
            f"approval threshold not met ({approval_rate:.2%} < {approval_threshold:.2%})"
        )

    return ExecutionRecord(
        proposal_id=proposal_state.proposal.proposal_id,
        final_outcome=outcome,
        executed_at=current_timestamp,
        total_votes=proposal_state.total_votes,
        total_weight=proposal_state.total_weight,
        approve_weight=proposal_state.approve_weight,
        reject_weight=proposal_state.reject_weight,
        effects=None,  # Effects would be determined by proposal type
        reason=reason,
    )


def finalize_proposal(
    proposal_id: str,
    execution_record: ExecutionRecord,
    timestamp: int,
) -> ExecutionRecord:
    """
    Finalize a proposal by emitting execution events.

    Args:
        proposal_id: Proposal being finalized
        execution_record: Computed execution record
        timestamp: Deterministic timestamp

    Returns:
        The execution record (for chaining)
    """
    # Emit finalization event
    EvidenceBus.emit(
        "GOV_PROPOSAL_FINALIZED",
        {
            "proposal_id": proposal_id,
            "execution_record": execution_record.model_dump(),
            "timestamp": timestamp,
        },
    )

    # If approved, emit execution event
    if execution_record.final_outcome == "approved":
        EvidenceBus.emit(
            "GOV_PROPOSAL_EXECUTED",
            {
                "proposal_id": proposal_id,
                "effects": execution_record.effects or {},
                "timestamp": timestamp,
            },
        )

    return execution_record


def _apply_tie_break_rule(rule: str) -> str:
    """
    Apply deterministic tie-break rule (pure function).

    Args:
        rule: Tie-break rule ("reject", "approve", "extend")

    Returns:
        Outcome: "approved", "rejected", or "tie"
    """
    if rule == "reject":
        return "rejected"
    elif rule == "approve":
        return "approved"
    elif rule == "extend":
        return "tie"  # Would trigger extension in a real system
    else:
        # Default to reject for safety
        return "rejected"
