"""
ValueNodeReplay.py - Deterministic replay engine for value-node state and explainability.

This module provides the `ValueNodeReplayEngine` which:
1.  Ingests a linear list of historical events.
2.  Reconstructs value-node state using `ValueGraphRef`.
3.  Generates explanations for specific reward events using `ValueNodeExplainabilityHelper`.

Strict Adherence:
-   Zero-Simulation (no randomness, no wall-clock).
-   Read-Only (no side effects on real ledger).
-   Pure Deterministic Output.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from v13.ATLAS.src.value_graph_ref import ValueGraphRef
from v13.policy.value_node_explainability import (
    ValueNodeExplainabilityHelper,
    ValueNodeRewardExplanation,
    ContentRankingExplanation,
)
from v13.policy.humor_policy import HumorSignalPolicy


class ValueNodeReplayEngine:
    """
    Deterministically replays events to reconstruct state and explain rewards.
    """

    def __init__(self, explainability_helper: ValueNodeExplainabilityHelper):
        """
        Initialize the replay engine.

        Args:
            explainability_helper: Helper to generate explanations for reward events.
        """
        self.explainability_helper = explainability_helper
        self.graph = ValueGraphRef()
        self.processed_events_count = 0

    def replay_events(self, events: List[Dict[str, Any]]) -> None:
        """
        Replay a list of events to update the internal graph state.

        Args:
            events: Ordered list of event dictionaries.
        """
        self.graph.build_from_events(events)
        self.processed_events_count += len(events)

    def explain_specific_reward(
        self,
        reward_event_id: str,
        events_context: List[Dict[str, Any]],
        trace_id: str = "no-trace",
    ) -> Optional[ValueNodeRewardExplanation]:
        """
        Find a specific reward event in the context and explain it.

        Args:
            reward_event_id: The ID of the reward event to explain.
            events_context: The list of events containing the reward event (and potentially its logs).

        Returns:
            ValueNodeRewardExplanation if found, else None.
        """
        target_event = None

        # 1. Find the target event
        for event in events_context:
            # Check if this is a RewardAllocated event an matches ID
            # Note: The event schema in ValueGraphRef doesn't strictly require 'id',
            # but real system events usually have 'event_id' or 'id'.
            # We check both for robustness.
            eid = event.get("event_id") or event.get("id")
            if eid == reward_event_id and event.get("type") == "RewardAllocated":
                target_event = event
                break

        if not target_event:
            return None

        # 2. Extract details from the event or its attached log_details
        # In a real replay, the detailed logs (bonuses, caps, guards) might be attached
        # to the event itself (if full fidelity) or reconstructed.
        # This implementation assumes the event dictionary carries the necessary 'log_details'
        # or that we can infer them from the event payload for the explanation helper.

        # Safely extract fields with defaults
        wallet_id = target_event.get("wallet_id", "unknown_wallet")
        user_id = target_event.get("user_id", "unknown_user")
        epoch = target_event.get("epoch", 0)
        timestamp = target_event.get("timestamp", 0)

        # Extract log details if present
        log_details = target_event.get("log_details", {})

        base_reward = log_details.get(
            "base_reward", target_event.get("base_reward", {})
        )
        bonuses = log_details.get("bonuses", [])
        caps = log_details.get("caps", [])
        guards = log_details.get("guards", [])

        # Fallback: if base_reward is empty but we have 'amount_atr', construct it
        if not base_reward and "amount_atr" in target_event:
            base_reward = {"ATR": f"{target_event['amount_atr']} ATR"}

        # 3. Generate Explanation
        explanation = self.explainability_helper.explain_value_node_reward(
            wallet_id=wallet_id,
            user_id=user_id,
            reward_event_id=reward_event_id,
            epoch=epoch,
            base_reward=base_reward,
            bonuses=bonuses,
            caps=caps,
            guards=guards,
            timestamp=timestamp,
            trace_id=trace_id,
        )

        return explanation

    def explain_content_ranking(
        self, content_id: str, events_context: List[Dict[str, Any]]
    ) -> Optional[ContentRankingExplanation]:
        """
        Explain the ranking of a specific content item based on replay state.

        Args:
            content_id: The ID of the content to explain.
            events_context: List of events (used to find creation timestamp etc).

        Returns:
            ContentRankingExplanation if content exists, else None.
        """
        if content_id not in self.graph.contents:
            return None

        # 1. Derive Metrics from Graph
        # In a real system, we'd have a full ranking engine. Here we derive proxies from the graph.
        interactions = [
            i for i in self.graph.interactions if i.content_id == content_id
        ]
        interaction_count = len(interactions)

        # Calculate naive "score" based on interaction weights
        interaction_score = sum(i.weight for i in interactions)

        # 2. Construct Explainable Signals
        signals = [
            {
                "name": "Interaction Volume",
                "weight": 0.5,
                "score": min(interaction_count / 10.0, 1.0),
                "description": f"{interaction_count} total interactions",
            },
            {
                "name": "Interaction Quality",
                "weight": 0.5,
                "score": min(interaction_score / 20.0, 1.0),
                "description": "Weighted score from likes/replies",
            },
        ]

        # 3. Simulate Neighbors (in real system, would query neighbors in rank tree)
        # We use a deterministic "dummy" neighbor generation based on content_id hash for stability
        import hashlib

        h = int(hashlib.md5(content_id.encode()).hexdigest(), 16)
        neighbors = [
            {
                "metric": "Overall Score",
                "value": (h % 100) / 100.0,
                "rank": (h % 20) + 1,
            }
        ]

        final_rank = (h % 20) + 1

        # 4. Find timestamp (creation time)
        creation_event = next(
            (
                e
                for e in events_context
                if e.get("type") == "ContentCreated"
                and e.get("content_id") == content_id
            ),
            None,
        )
        timestamp = creation_event.get("timestamp", 0) if creation_event else 0

        return self.explainability_helper.explain_content_ranking(
            content_id=content_id,
            epoch=1,  # Default to 1 for this slice
            signals=signals,
            neighbors=neighbors,
            final_rank=final_rank,
            timestamp=timestamp,
        )

    def get_state_snapshot(self) -> Dict[str, Any]:
        """
        Return a snapshot of the current replayed state (users and content).
        Useful for verification.
        """
        return {
            "users": {uid: u.__dict__ for uid, u in self.graph.users.items()},
            "contents": {cid: c.__dict__ for cid, c in self.graph.contents.items()},
            "interaction_count": len(self.graph.interactions),
            "reward_count": len(self.graph.rewards),
            "events_processed": self.processed_events_count,
        }
