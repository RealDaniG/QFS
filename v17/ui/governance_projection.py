"""
Governance Projection Service (v17 UI Layer)

Projects pure EvidenceBus events into human-legible timeline DTOs for the Admin Dashboard.
Read-only, deterministic projection over the event sourcing log.
"""

from typing import Dict, List, Optional
from v15.evidence.bus import EvidenceBus
from v15.evidence.bus import EvidenceBus
from v17.governance.f_proposals import get_proposal_state
from v17.governance.schemas import GovernanceConfig, ProposalState


class GovernanceProjection:
    """
    Project governance events into view models for the dashboard.
    """

    def __init__(self, bus=EvidenceBus):
        self.bus = bus

    def list_proposals(self, limit: int = 50) -> List[Dict]:
        """
        Get a summary list of recent proposals.

        DTO Schema:
        {
            "id": str,
            "title": str,
            "creator": str,
            "status": "open" | "rejected" | "approved",
            "created_at": int,
            "vote_count": int,
            "outcome": str | None
        }
        """
        # In a real event-sourced system, we might maintain a read-model database.
        # For this implementation, we scan recent history or use an indexing optimization.
        # Here we re-scan recent events to build the list dynamically (deterministic).

        all_events = self.bus.get_events(limit=limit * 10)  # Scan enough history
        proposals = {}

        for envelope in all_events:
            event = envelope.get("event", {})
            event_type = event.get("type")
            payload = event.get("payload", {})

            if event_type == "GOVERNANCE_PROPOSAL":  # Legacy v16 / v17 mapping
                pass  # Handle if needed

            if event_type == "GOV_PROPOSAL_CREATED":
                prop = payload.get("proposal", {})
                pid = prop.get("proposal_id")
                if pid:
                    proposals[pid] = {
                        "id": pid,
                        "title": prop.get("title"),
                        "creator": prop.get("creator_wallet"),
                        "status": "open",
                        "created_at": prop.get("created_at"),
                        "vote_count": 0,
                        "outcome": None,
                        "voting_ends_at": prop.get("voting_ends_at"),
                    }

            elif event_type == "GOV_VOTE_CAST":
                vote = payload.get("vote", {})
                pid = vote.get("proposal_id")
                if pid in proposals:
                    proposals[pid]["vote_count"] += 1

            elif event_type == "GOV_PROPOSAL_FINALIZED":
                pid = payload.get("proposal_id")
                record = payload.get("execution_record", {})
                if pid in proposals:
                    proposals[pid]["status"] = "closed"
                    proposals[pid]["outcome"] = record.get("final_outcome")

            elif event_type == "AGENT_ADVISORY_PROPOSAL":
                signal = payload.get("signal", {})
                pid = signal.get("target_id")
                if pid in proposals:
                    if "advisory" not in proposals[pid]:
                        proposals[pid]["advisory"] = []
                    proposals[pid]["advisory"].append(
                        {
                            "score": signal.get("score"),
                            "reasons": signal.get("reasons"),
                            "model": signal.get("model_version"),
                        }
                    )

        # Sort by creation time desc
        result = list(proposals.values())
        result.sort(key=lambda x: x["created_at"], reverse=True)
        return result[:limit]

    def get_proposal_timeline(
        self, proposal_id: str, config: GovernanceConfig
    ) -> Optional[Dict]:
        """
        Get detailed timeline and explanation for a single proposal.

        DTO Schema:
        {
            "info": ProposalDTO,
            "timeline": [
                { "stage": str, "timestamp": int, "actor": str, "description": str, "evidence_hash": str }
            ],
            "explanation": { "summary": str, "detail": str, "rule": str },
            "evidence_link": str
        }
        """
        state = get_proposal_state(proposal_id)
        if not state:
            return None

        # Build timeline from state interactions
        timeline = []

        # 1. Creation
        timeline.append(
            {
                "stage": "Created",
                "timestamp": state.proposal.created_at,
                "actor": state.proposal.creator_wallet,
                "description": f"Proposal created: '{state.proposal.title}'",
                "evidence_hash": None,  # In a full impl, we'd look up the exact event hash
            }
        )

        # 2. Votes
        sorted_votes = sorted(state.votes, key=lambda v: v.timestamp)
        for vote in sorted_votes:
            timeline.append(
                {
                    "stage": "Vote Cast",
                    "timestamp": vote.timestamp,
                    "actor": vote.voter_wallet,
                    "description": f"Voted {vote.choice.upper()} (weight: {vote.weight})",
                    "evidence_hash": None,
                }
            )

        # 3. Finalization / Outcome logic (simulated if no explicit finalization event yet)
        # Check if finalized events exist in state reconstruction, if not, compute hypothetical
        # The `get_proposal_state` gives us the current aggregate.

        explanation = self._generate_explanation(state, config)

        return {
            "info": {
                "id": state.proposal.proposal_id,
                "title": state.proposal.title,
                "creator": state.proposal.creator_wallet,
                "created_at": state.proposal.created_at,
                "voting_ends_at": state.proposal.voting_ends_at,
                "total_votes": state.total_votes,
            },
            "timeline": timeline,
            "explanation": explanation,
            "evidence_link": f"/evidence?filter=proposal_id:{proposal_id}",
        }

    def _generate_explanation(
        self, state: ProposalState, config: GovernanceConfig
    ) -> Dict:
        """Generate human-readable explanation of the current state/outcome."""
        participation = (
            state.total_votes / 100.0
        )  # Placeholder logic matching f_execution

        # Parse string weights to float for calculations
        approve_weight = float(state.approve_weight)
        reject_weight = float(state.reject_weight)
        voting_weight = approve_weight + reject_weight
        approval_rate = (approve_weight / voting_weight) if voting_weight > 0 else 0.0

        # Parse string thresholds to float for comparisons
        quorum_threshold = float(config.quorum_threshold)
        approval_threshold = float(config.approval_threshold)

        quorum_met = participation >= quorum_threshold
        approval_met = approval_rate >= approval_threshold

        status = "Passing" if (quorum_met and approval_met) else "Failing"

        summary = f"Proposal is currently {status}."
        detail = (
            f"Quorum: {participation:.1%} (Target: {quorum_threshold:.0%}). "
            f"Approval: {approval_rate:.1%} (Target: {approval_threshold:.0%}). "
            f"Total votes: {state.total_votes}."
        )
        rule = f"Requires >{quorum_threshold:.0%} participation and >{approval_threshold:.0%} approval."

        return {"summary": summary, "detail": detail, "rule": rule}
