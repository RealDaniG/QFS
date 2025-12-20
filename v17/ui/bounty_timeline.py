"""
Bounty Timeline View (v17 UI Layer)

Human-legible bounty timeline showing creation → contributions → rewards.
Explicitly distinguishes "what agents suggested" vs "what protocol decided".
"""

from typing import Dict, List, Optional
from v15.evidence.bus import EvidenceBus
from v17.bounties.f_bounties import get_bounty_state


class BountyTimelineView:
    """
    Bounty Timeline: Creation → Contributions → Advisory → Rewards

    Makes advisory vs F-layer distinction visible to users.
    """

    def __init__(self):
        self.bus = EvidenceBus

    def get_bounty_timeline(self, bounty_id: str) -> Dict:
        """
        Get complete timeline for a bounty (pure function).

        Returns:
            {
                "bounty": {...},
                "stages": [
                    {
                        "stage": "created",
                        "timestamp": 1000000,
                        "actor": "0xabc...",
                        "what_happened": "Bounty created: 'Implement feature X'",
                        "evidence_hash": "abc123..."
                    },
                    {
                        "stage": "contribution_submitted",
                        "timestamp": 1000100,
                        "actor": "0xdef...",
                        "what_happened": "Contribution submitted: PR #123",
                        "evidence_hash": "def456..."
                    },
                    {
                        "stage": "advisory_score",
                        "timestamp": 1000200,
                        "actor": "agent:mock",
                        "what_happened": "Agent suggested quality score: 0.85",
                        "is_advisory": true,
                        "evidence_hash": "ghi789..."
                    },
                    {
                        "stage": "reward_decided",
                        "timestamp": 1000300,
                        "actor": "protocol",
                        "what_happened": "Protocol decided: 650 QFS (65%)",
                        "is_final": true,
                        "evidence_hash": "jkl012..."
                    }
                ],
                "advisory_vs_final": {
                    "agents_suggested": [...],
                    "protocol_decided": [...]
                },
                "evidence_link": "/evidence/bounty/{bounty_id}"
            }
        """
        # Get bounty state from EvidenceBus
        state = get_bounty_state(bounty_id)

        if not state:
            return {"error": "Bounty not found", "bounty_id": bounty_id}

        # Build timeline stages
        stages = []

        # Stage 1: Bounty created
        stages.append(
            {
                "stage": "created",
                "timestamp": state.bounty.created_at,
                "actor": state.bounty.created_by,
                "what_happened": f"Bounty created: '{state.bounty.title}' ({state.bounty.reward_amount} {state.bounty.currency})",
                "is_advisory": False,
                "is_final": False,
                "evidence_hash": None,
            }
        )

        # Stage 2: Contributions submitted
        for contribution in state.contributions:
            stages.append(
                {
                    "stage": "contribution_submitted",
                    "timestamp": contribution.submitted_at,
                    "actor": contribution.contributor_wallet,
                    "what_happened": f"Contribution submitted: {contribution.reference}",
                    "is_advisory": False,
                    "is_final": False,
                    "evidence_hash": None,
                }
            )

        # Stage 3: Advisory signals (if any)
        for advisory in state.advisory_signals:
            if isinstance(advisory, dict):
                content_score = advisory.get("content_score", {})
                if isinstance(content_score, dict):
                    stages.append(
                        {
                            "stage": "advisory_score",
                            "timestamp": advisory.get("timestamp", 0),
                            "actor": f"agent:{advisory.get('provider', 'unknown')}",
                            "what_happened": f"Agent suggested quality score: {content_score.get('quality', 0):.2f}",
                            "is_advisory": True,
                            "is_final": False,
                            "evidence_hash": None,
                        }
                    )

        # Stage 4: Reward decisions (final)
        for decision in state.reward_decisions:
            stages.append(
                {
                    "stage": "reward_decided",
                    "timestamp": decision.decided_at,
                    "actor": "protocol",
                    "what_happened": f"Protocol decided: {decision.amount:.2f} {state.bounty.currency} ({decision.percentage:.0%}) to {decision.recipient_wallet}",
                    "is_advisory": False,
                    "is_final": True,
                    "evidence_hash": None,
                }
            )

        # Sort stages by timestamp
        stages.sort(key=lambda s: s.get("timestamp", 0))

        # Separate advisory vs final decisions
        advisory_suggestions = [s for s in stages if s.get("is_advisory")]
        final_decisions = [s for s in stages if s.get("is_final")]

        return {
            "bounty": {
                "id": state.bounty.bounty_id,
                "title": state.bounty.title,
                "reward_amount": state.bounty.reward_amount,
                "currency": state.bounty.currency,
                "created_by": state.bounty.created_by,
                "created_at": state.bounty.created_at,
            },
            "stages": stages,
            "contribution_summary": {
                "total_contributions": state.total_contributions,
                "total_rewards_allocated": state.total_rewards_allocated,
            },
            "advisory_vs_final": {
                "agents_suggested": advisory_suggestions,
                "protocol_decided": final_decisions,
            },
            "evidence_link": f"/evidence/bounty/{bounty_id}",
        }

    def get_all_bounties(self, limit: int = 50) -> List[Dict]:
        """
        Get list of all bounties with summary info.

        Returns:
            List of bounty summaries for dashboard display
        """
        all_events = self.bus.get_events(limit=limit * 10)

        bounties = {}

        for envelope in all_events:
            if not isinstance(envelope, dict):
                continue

            event = envelope.get("event", {})
            if not isinstance(event, dict):
                continue

            event_type = event.get("type")
            payload = event.get("payload", {})

            # Track bounty creation
            if event_type == "BOUNTY_CREATED":
                bounty = payload.get("bounty", {})
                if isinstance(bounty, dict):
                    bounty_id = bounty.get("bounty_id")
                    if bounty_id:
                        bounties[bounty_id] = {
                            "id": bounty_id,
                            "title": bounty.get("title"),
                            "reward_amount": bounty.get("reward_amount"),
                            "currency": bounty.get("currency", "QFS"),
                            "created_by": bounty.get("created_by"),
                            "created_at": bounty.get("created_at"),
                            "status": "open",
                            "contributions": 0,
                            "rewards_allocated": 0,
                        }

            # Track contributions
            elif event_type == "BOUNTY_CONTRIBUTION_SUBMITTED":
                contribution = payload.get("contribution", {})
                if isinstance(contribution, dict):
                    bounty_id = contribution.get("bounty_id")
                    if bounty_id in bounties:
                        bounties[bounty_id]["contributions"] += 1

            # Track reward decisions
            elif event_type == "BOUNTY_REWARD_DECIDED":
                decision = payload.get("decision", {})
                if isinstance(decision, dict):
                    bounty_id = decision.get("bounty_id")
                    if bounty_id in bounties:
                        bounties[bounty_id]["rewards_allocated"] += decision.get(
                            "amount", 0
                        )
                        bounties[bounty_id]["status"] = "completed"

        # Convert to list and sort by creation time
        bounty_list = list(bounties.values())
        bounty_list.sort(key=lambda b: b.get("created_at", 0), reverse=True)

        return bounty_list[:limit]

    def explain_reward_decision(self, bounty_id: str) -> Dict:
        """
        Generate human-readable explanation of reward allocation.

        Returns:
            {
                "summary": "Rewards allocated based on normalized quality scores",
                "rule_applied": "Proportional distribution based on contribution scores",
                "inputs_considered": {
                    "total_contributions": 3,
                    "advisory_scores": [0.85, 0.70, 0.60],
                    "final_scores": [0.85, 0.70, 0.60]
                },
                "why_this_outcome": "Contributor A received 65% because their quality score (0.85) was highest...",
                "show_record_link": "/evidence/bounty/{bounty_id}"
            }
        """
        state = get_bounty_state(bounty_id)

        if not state:
            return {"error": "Bounty not found"}

        if not state.reward_decisions:
            return {
                "summary": "No rewards allocated yet",
                "status": "pending",
            }

        # Extract scores and decisions
        advisory_scores = []
        for advisory in state.advisory_signals:
            if isinstance(advisory, dict):
                content_score = advisory.get("content_score", {})
                if isinstance(content_score, dict):
                    advisory_scores.append(content_score.get("quality", 0))

        # Build explanation
        total_allocated = sum(d.amount for d in state.reward_decisions)

        summary = f"Rewards allocated: {total_allocated:.2f} {state.bounty.currency} distributed among {len(state.reward_decisions)} contributors"

        why = "Rewards were distributed proportionally based on normalized contribution scores. "
        if advisory_scores:
            why += f"Advisory agents provided quality scores, which were used as inputs to the deterministic reward formula. "
        why += "The protocol computed final allocations using a deterministic formula that ensures fairness and transparency."

        return {
            "summary": summary,
            "rule_applied": "Proportional distribution based on normalized scores",
            "inputs_considered": {
                "total_contributions": state.total_contributions,
                "advisory_scores": advisory_scores,
                "total_reward_pool": state.bounty.reward_amount,
                "total_allocated": total_allocated,
            },
            "why_this_outcome": why,
            "reward_breakdown": [
                {
                    "recipient": d.recipient_wallet,
                    "amount": d.amount,
                    "percentage": d.percentage,
                    "reason": d.reason,
                }
                for d in state.reward_decisions
            ],
            "show_record_link": f"/evidence/bounty/{bounty_id}",
        }
