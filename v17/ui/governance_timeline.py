"""
Governance Timeline View (v17 UI Layer)

Human-legible governance timeline with decision explanations and evidence links.
Part of the "compression and reveal" strategy.
"""

from typing import Dict, List, Optional
from v15.evidence.bus import EvidenceBus
from v17.governance.f_proposals import get_proposal_state
from v17.governance.schemas import GovernanceConfig


class GovernanceTimelineView:
    """
    Governance Timeline: Proposal → Votes → Outcome → Execution

    Surfaces existing deterministic guarantees through human-legible UI.
    """

    def __init__(self):
        self.bus = EvidenceBus

    def get_proposal_timeline(self, proposal_id: str) -> Dict:
        """
        Get complete timeline for a proposal (pure function).

        Returns:
            {
                "proposal": {...},
                "stages": [
                    {
                        "stage": "created",
                        "timestamp": 1000000,
                        "actor": "0xabc...",
                        "what_happened": "Proposal created: 'Increase emission cap'",
                        "evidence_hash": "abc123..."
                    },
                    {
                        "stage": "vote_cast",
                        "timestamp": 1000100,
                        "actor": "0xdef...",
                        "what_happened": "Vote cast: approve",
                        "evidence_hash": "def456..."
                    },
                    ...
                ],
                "outcome": {...},
                "evidence_link": "/evidence/proposal/{proposal_id}"
            }
        """
        # Get proposal state from EvidenceBus
        state = get_proposal_state(proposal_id)

        if not state:
            return {"error": "Proposal not found", "proposal_id": proposal_id}

        # Build timeline stages
        stages = []

        # Stage 1: Proposal created
        stages.append(
            {
                "stage": "created",
                "timestamp": state.proposal.created_at,
                "actor": state.proposal.creator_wallet,
                "what_happened": f"Proposal created: '{state.proposal.title}'",
                "rule_applied": None,
                "evidence_hash": None,  # Would be populated from events
            }
        )

        # Stage 2: Votes cast
        for vote in state.votes:
            stages.append(
                {
                    "stage": "vote_cast",
                    "timestamp": vote.timestamp,
                    "actor": vote.voter_wallet,
                    "what_happened": f"Vote cast: {vote.choice} (weight: {vote.weight})",
                    "rule_applied": None,
                    "evidence_hash": None,
                }
            )

        # Stage 3: Voting ended (if applicable)
        # This would be determined by checking if current time > voting_ends_at

        # Stage 4: Outcome computed (if finalized)
        # This would check for GOV_PROPOSAL_FINALIZED events

        return {
            "proposal": {
                "id": state.proposal.proposal_id,
                "title": state.proposal.title,
                "creator": state.proposal.creator_wallet,
                "created_at": state.proposal.created_at,
                "voting_ends_at": state.proposal.voting_ends_at,
            },
            "stages": stages,
            "vote_summary": {
                "total_votes": state.total_votes,
                "approve": state.approve_weight,
                "reject": state.reject_weight,
                "abstain": state.abstain_weight,
            },
            "advisory_signals": len(state.advisory_signals),
            "evidence_link": f"/evidence/proposal/{proposal_id}",
        }

    def get_all_proposals(self, limit: int = 50) -> List[Dict]:
        """
        Get list of all proposals with summary info.

        Returns:
            List of proposal summaries for dashboard display
        """
        all_events = self.bus.get_events(limit=limit * 10)

        proposals = {}

        for envelope in all_events:
            if not isinstance(envelope, dict):
                continue

            event = envelope.get("event", {})
            if not isinstance(event, dict):
                continue

            event_type = event.get("type")
            payload = event.get("payload", {})

            # Track proposal creation
            if event_type == "GOV_PROPOSAL_CREATED":
                proposal = payload.get("proposal", {})
                if isinstance(proposal, dict):
                    proposal_id = proposal.get("proposal_id")
                    if proposal_id:
                        proposals[proposal_id] = {
                            "id": proposal_id,
                            "title": proposal.get("title"),
                            "creator": proposal.get("creator_wallet"),
                            "created_at": proposal.get("created_at"),
                            "status": "open",
                            "votes": 0,
                        }

            # Track votes
            elif event_type == "GOV_VOTE_CAST":
                vote = payload.get("vote", {})
                if isinstance(vote, dict):
                    proposal_id = vote.get("proposal_id")
                    if proposal_id in proposals:
                        proposals[proposal_id]["votes"] += 1

            # Track finalization
            elif event_type == "GOV_PROPOSAL_FINALIZED":
                proposal_id = payload.get("proposal_id")
                execution_record = payload.get("execution_record", {})
                if proposal_id in proposals and isinstance(execution_record, dict):
                    proposals[proposal_id]["status"] = execution_record.get(
                        "final_outcome", "finalized"
                    )

        # Convert to list and sort by creation time
        proposal_list = list(proposals.values())
        proposal_list.sort(key=lambda p: p.get("created_at", 0), reverse=True)

        return proposal_list[:limit]

    def explain_outcome(self, proposal_id: str, config: GovernanceConfig) -> Dict:
        """
        Generate human-readable explanation of proposal outcome.

        Returns:
            {
                "summary": "Proposal approved: quorum met (65%), approval threshold met (70% > 60%)",
                "rule_applied": "Quorum: 50%, Approval: 60%",
                "inputs_considered": {
                    "total_votes": 100,
                    "approve": 70,
                    "reject": 30,
                    "advisory_signals": 3
                },
                "why_this_outcome": "The proposal received 70% approval, exceeding the 60% threshold...",
                "show_record_link": "/evidence/proposal/{proposal_id}"
            }
        """
        state = get_proposal_state(proposal_id)

        if not state:
            return {"error": "Proposal not found"}

        # Calculate participation and approval rates
        participation_rate = state.total_votes / 100.0  # Simplified
        voting_weight = state.approve_weight + state.reject_weight
        approval_rate = state.approve_weight / voting_weight if voting_weight > 0 else 0

        # Determine outcome
        if participation_rate < config.quorum_threshold:
            summary = f"Proposal failed: quorum not met ({participation_rate:.0%} < {config.quorum_threshold:.0%})"
            why = f"Only {state.total_votes} votes were cast, which is below the required quorum threshold of {config.quorum_threshold:.0%}."
        elif approval_rate >= config.approval_threshold:
            summary = f"Proposal approved: quorum met ({participation_rate:.0%}), approval threshold met ({approval_rate:.0%} ≥ {config.approval_threshold:.0%})"
            why = f"The proposal received {state.approve_weight:.0f} approve votes out of {voting_weight:.0f} total votes ({approval_rate:.0%}), exceeding the {config.approval_threshold:.0%} approval threshold."
        else:
            summary = f"Proposal rejected: quorum met ({participation_rate:.0%}), approval threshold not met ({approval_rate:.0%} < {config.approval_threshold:.0%})"
            why = f"The proposal received {state.approve_weight:.0f} approve votes out of {voting_weight:.0f} total votes ({approval_rate:.0%}), which is below the {config.approval_threshold:.0%} approval threshold."

        return {
            "summary": summary,
            "rule_applied": f"Quorum: {config.quorum_threshold:.0%}, Approval: {config.approval_threshold:.0%}",
            "inputs_considered": {
                "total_votes": state.total_votes,
                "approve": state.approve_weight,
                "reject": state.reject_weight,
                "abstain": state.abstain_weight,
                "advisory_signals": len(state.advisory_signals),
            },
            "why_this_outcome": why,
            "show_record_link": f"/evidence/proposal/{proposal_id}",
        }
