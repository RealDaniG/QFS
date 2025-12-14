"""Reference-only value graph helper for V13.8.

This module provides a *pure*, deterministic, side-effect-free value graph
representation for tests and observability experiments. It does **not**
interact with TreasuryEngine, ledger adapters, or any core economics/guard
modules.

It is intended to mirror the conceptual model described in
specs/QFS_V13_8_VALUE_NODE_MODEL.md and
QFS_ATLAS_COHERENT_INTEGRATION_PLAN_V13_7_TO_V13_8.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class UserNode:
    """Reference representation of a user as a value node.

    This does **not** contain real balances; it is a projection for tests
    and analytics. All monetary truth remains in QFS core economics.
    """

    user_id: str
    total_rewards_atr: int = 0
    total_interactions: int = 0
    # Optional lightweight counters for future extensions
    governance_votes: int = 0


@dataclass
class ContentNode:
    """Reference representation of a content-NFT node."""

    content_id: str
    creator_id: str


@dataclass(frozen=True)
class InteractionEdge:
    """Deterministic edge from user → content representing an interaction."""

    user_id: str
    content_id: str
    interaction_type: str
    weight: float = 1.0


@dataclass(frozen=True)
class RewardEdge:
    """Deterministic edge from system → user representing ATR rewards.

    This uses simple integers for ATR amounts for reference purposes only.
    """

    user_id: str
    amount_atr: int
    content_id: Optional[str] = None


@dataclass(frozen=True)
class GovernanceEdge:
    """Deterministic edge from user → proposal representing a vote."""

    user_id: str
    proposal_id: str
    vote_type: str


class ValueGraphRef:
    """Reference value graph for V13.8 value-node and content-NFT semantics.

    This graph is built purely from an ordered list of event dictionaries.
    It is deterministic and side-effect-free, suitable for tests and
    replay-based analytics.
    """

    def __init__(self) -> None:
        self.users: Dict[str, UserNode] = {}
        self.contents: Dict[str, ContentNode] = {}
        self.interactions: List[InteractionEdge] = []
        self.rewards: List[RewardEdge] = []
        self.governance: List[GovernanceEdge] = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_user(self, user_id: str) -> UserNode:
        node = self.users.get(user_id)
        if node is None:
            node = UserNode(user_id=user_id)
            self.users[user_id] = node
        return node

    def _ensure_content(self, content_id: str, creator_id: str) -> ContentNode:
        node = self.contents.get(content_id)
        if node is None:
            node = ContentNode(content_id=content_id, creator_id=creator_id)
            self.contents[content_id] = node
        return node

    # ------------------------------------------------------------------
    # Event application
    # ------------------------------------------------------------------

    def apply_event(self, event: Dict[str, Any]) -> None:
        """Apply a single event to the reference graph.

        Supported minimal event schema (keys):
        - type: "ContentCreated" | "InteractionCreated" |
                 "RewardAllocated" | "GovernanceVoteCast"
        - For ContentCreated:
            - content_id (and optionally user_id/creator_id)
        - For InteractionCreated:
            - user_id, content_id, interaction_type, weight (optional)
        - For RewardAllocated:
            - Either (user_id, amount_atr, content_id optional) or
              (user_id, token, amount, content_id optional). Only ATR
              amounts are tracked in this reference helper.
        - For GovernanceVoteCast:
            - user_id, proposal_id, vote_type
        """

        etype = event.get("type")

        if etype == "ContentCreated":
            # Some traces may omit the explicit user_id. We treat creator_id
            # as optional metadata and only ensure the content node exists.
            content_id = event["content_id"]
            creator_id = event.get("user_id") or event.get("creator_id") or ""
            self._ensure_content(content_id, creator_id=creator_id)
            return

        if etype == "InteractionCreated":
            user_id = event["user_id"]
            content_id = event["content_id"]
            interaction_type = event.get("interaction_type", "generic")
            weight = float(event.get("weight", 1.0))

            user_node = self._ensure_user(user_id)
            self._ensure_content(content_id, creator_id=event.get("creator_id", ""))

            # Update user interaction counter
            user_node.total_interactions += 1

            self.interactions.append(
                InteractionEdge(
                    user_id=user_id,
                    content_id=content_id,
                    interaction_type=interaction_type,
                    weight=weight,
                )
            )
            return

        if etype == "RewardAllocated":
            user_id = event["user_id"]
            content_id = event.get("content_id")

            # Prefer explicit amount_atr if present; otherwise derive it
            # from token/amount when token == "ATR". Other tokens are
            # ignored for this ATR-focused reference.
            if "amount_atr" in event:
                amount_atr = int(event["amount_atr"])
            else:
                token = event.get("token")
                if token == "ATR":
                    amount_atr = int(event.get("amount", 0))
                else:
                    amount_atr = 0

            user_node = self._ensure_user(user_id)
            user_node.total_rewards_atr += amount_atr

            if amount_atr != 0:
                self.rewards.append(
                    RewardEdge(
                        user_id=user_id,
                        amount_atr=amount_atr,
                        content_id=content_id,
                    )
                )
            return

        if etype == "GovernanceVoteCast":
            user_id = event["user_id"]
            proposal_id = event["proposal_id"]
            vote_type = event.get("vote_type", "abstain")

            user_node = self._ensure_user(user_id)
            user_node.governance_votes += 1

            self.governance.append(
                GovernanceEdge(
                    user_id=user_id,
                    proposal_id=proposal_id,
                    vote_type=vote_type,
                )
            )
            return

        # Unknown event type: ignore deterministically

    def build_from_events(self, events: List[Dict[str, Any]]) -> "ValueGraphRef":
        """Build the graph from an ordered list of events.

        The same ordered event list will always produce the same internal
        structure (modulo Python dict ordering, which is stable by key
        insertion order).
        """

        for ev in events:
            self.apply_event(ev)
        return self
