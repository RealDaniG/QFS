"""Tests for the V13.8 reference value graph helper.

These tests exercise ValueGraphRef purely as a deterministic, reference-only
view over an event trace. They do **not** touch TreasuryEngine, ledger
adapters, or real economics engines.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Any, List

import pytest

# Ensure the repository's ATLAS src directory is on sys.path
_THIS_FILE = Path(__file__).resolve()
_ATLAS_ROOT = None
for parent in _THIS_FILE.parents:
    if parent.name == "ATLAS":
        _ATLAS_ROOT = parent
        break
if _ATLAS_ROOT is not None:
    _SRC_DIR = _ATLAS_ROOT / "src"
    if str(_SRC_DIR) not in sys.path:
        sys.path.insert(0, str(_SRC_DIR))

from value_graph_ref import ValueGraphRef  # type: ignore

# Import helpers from test_value_node_replay in the same directory
if str(_THIS_FILE.parent) not in sys.path:
    sys.path.insert(0, str(_THIS_FILE.parent))

from test_value_node_replay import (  # type: ignore
    simple_user_state,
    simple_event_trace,
    run_event_sequence,
)


@pytest.fixture
def graph(simple_event_trace: List[Dict[str, Any]]) -> ValueGraphRef:
    g = ValueGraphRef()
    g.build_from_events(simple_event_trace)
    return g


def test_value_graph_deterministic_construction(simple_event_trace: List[Dict[str, Any]]) -> None:
    """Building graphs from the same events yields identical structures."""
    g1 = ValueGraphRef().build_from_events(simple_event_trace)
    g2 = ValueGraphRef().build_from_events(simple_event_trace)

    assert set(g1.users.keys()) == set(g2.users.keys())
    assert set(g1.contents.keys()) == set(g2.contents.keys())

    assert g1.interactions == g2.interactions
    assert g1.rewards == g2.rewards
    assert g1.governance == g2.governance


def test_value_graph_consistent_with_userstate(
    simple_user_state,
    simple_event_trace: List[Dict[str, Any]],
) -> None:
    """Reference graph should match UserState replay aggregates.

    We expect:
    - Total ATR rewards in the graph for a user to match the ATR_delta in
      the UserState replay.
    - Number of interactions in the graph to match the engagement count in
      the UserState coherence metrics.
    """
    from test_value_node_replay import UserState  # type: ignore

    user_state: UserState = simple_user_state
    final_state = run_event_sequence(user_state, simple_event_trace)

    g = ValueGraphRef().build_from_events(simple_event_trace)

    # Our simple_event_trace uses user_1 consistently
    user_id = "user_1"

    # ATR rewards consistency
    atr_from_graph = sum(
        edge.amount_atr for edge in g.rewards if edge.user_id == user_id
    )
    assert atr_from_graph == final_state.atr_balance

    # Interaction / engagement consistency
    interactions_from_graph = sum(
        1 for edge in g.interactions if edge.user_id == user_id
    )
    engagement_from_state = final_state.coherence_metrics.get("engagement", 0.0)

    assert interactions_from_graph == int(engagement_from_state)


def test_value_graph_replay_invariance(simple_event_trace: List[Dict[str, Any]]) -> None:
    """Rebuilding the graph from the same ordered events is invariant."""
    g1 = ValueGraphRef().build_from_events(simple_event_trace)
    g2 = ValueGraphRef().build_from_events(simple_event_trace)

    assert g1.users == g2.users
    assert g1.contents == g2.contents
    assert g1.interactions == g2.interactions
    assert g1.rewards == g2.rewards
    assert g1.governance == g2.governance


def test_value_graph_multiple_users_and_contents() -> None:
    """Graph should support multiple users and multiple content nodes deterministically."""
    events: List[Dict[str, Any]] = [
        {"type": "ContentCreated", "block": 1, "user_id": "user_a", "content_id": "c1"},
        {"type": "ContentCreated", "block": 2, "user_id": "user_b", "content_id": "c2"},
        {"type": "InteractionCreated", "block": 3, "user_id": "user_b", "content_id": "c1", "interaction_type": "like"},
        {"type": "InteractionCreated", "block": 4, "user_id": "user_a", "content_id": "c2", "interaction_type": "comment"},
        {"type": "RewardAllocated", "block": 5, "user_id": "user_a", "token": "ATR", "amount": 7, "content_id": "c1"},
        {"type": "RewardAllocated", "block": 6, "user_id": "user_b", "token": "ATR", "amount": 3, "content_id": "c2"},
    ]

    g = ValueGraphRef().build_from_events(events)

    assert set(g.contents.keys()) == {"c1", "c2"}
    assert set(g.users.keys()) == {"user_a", "user_b"}

    assert len(g.interactions) == 2
    assert len(g.rewards) == 2

    assert g.users["user_a"].total_interactions == 1
    assert g.users["user_b"].total_interactions == 1

    assert g.users["user_a"].total_rewards_atr == 7
    assert g.users["user_b"].total_rewards_atr == 3


def test_value_graph_mixed_atr_flx_rewards_atr_only() -> None:
    """Only ATR rewards should be aggregated and emitted as RewardEdges in the reference graph."""
    events: List[Dict[str, Any]] = [
        {"type": "ContentCreated", "block": 1, "user_id": "user_a", "content_id": "c1"},
        {"type": "RewardAllocated", "block": 2, "user_id": "user_a", "token": "ATR", "amount": 10},
        {"type": "RewardAllocated", "block": 3, "user_id": "user_a", "token": "FLX", "amount": 999},
        {"type": "RewardAllocated", "block": 4, "user_id": "user_a", "token": "ATR", "amount": 5},
    ]

    g = ValueGraphRef().build_from_events(events)

    # Only ATR should be counted
    assert g.users["user_a"].total_rewards_atr == 15

    # Only ATR RewardEdges are emitted
    assert len(g.rewards) == 2
    assert [e.amount_atr for e in g.rewards] == [10, 5]


def test_value_graph_governance_edges_and_votes() -> None:
    """GovernanceVoteCast should create GovernanceEdges and increment per-user vote counters."""
    events: List[Dict[str, Any]] = [
        {"type": "GovernanceVoteCast", "block": 1, "user_id": "user_a", "proposal_id": "p1", "vote_type": "yes"},
        {"type": "GovernanceVoteCast", "block": 2, "user_id": "user_a", "proposal_id": "p2", "vote_type": "no"},
        {"type": "GovernanceVoteCast", "block": 3, "user_id": "user_b", "proposal_id": "p1", "vote_type": "abstain"},
        {"type": "GovernanceVoteCast", "block": 4, "user_id": "user_b", "proposal_id": "p3", "vote_type": "yes"},
        {"type": "GovernanceVoteCast", "block": 5, "user_id": "user_b", "proposal_id": "p3", "vote_type": "yes"},
    ]

    g = ValueGraphRef().build_from_events(events)

    assert len(g.governance) == 5
    assert g.users["user_a"].governance_votes == 2
    assert g.users["user_b"].governance_votes == 3

    # Structural assertions on edge content/order
    assert g.governance[0].user_id == "user_a"
    assert g.governance[0].proposal_id == "p1"
    assert g.governance[0].vote_type == "yes"

    assert g.governance[-1].user_id == "user_b"
    assert g.governance[-1].proposal_id == "p3"
    assert g.governance[-1].vote_type == "yes"


def test_value_graph_long_trace_stays_deterministic() -> None:
    """A longer mixed trace should remain fully deterministic and structurally equal across builds."""
    events: List[Dict[str, Any]] = [
        # Content nodes
        {"type": "ContentCreated", "block": 1, "user_id": "alice", "content_id": "cA"},
        {"type": "ContentCreated", "block": 2, "user_id": "bob", "content_id": "cB"},
        {"type": "ContentCreated", "block": 3, "user_id": "alice", "content_id": "cC"},

        # Interactions
        {"type": "InteractionCreated", "block": 4, "user_id": "bob", "content_id": "cA", "interaction_type": "like"},
        {"type": "InteractionCreated", "block": 5, "user_id": "alice", "content_id": "cB", "interaction_type": "comment"},
        {"type": "InteractionCreated", "block": 6, "user_id": "carol", "content_id": "cA", "interaction_type": "share"},
        {"type": "InteractionCreated", "block": 7, "user_id": "carol", "content_id": "cC", "interaction_type": "like"},

        # Rewards (mixed ATR + FLX; reference counts ATR only)
        {"type": "RewardAllocated", "block": 8, "user_id": "alice", "token": "ATR", "amount": 10, "content_id": "cA"},
        {"type": "RewardAllocated", "block": 9, "user_id": "alice", "token": "FLX", "amount": 999, "content_id": "cA"},
        {"type": "RewardAllocated", "block": 10, "user_id": "bob", "token": "ATR", "amount": 3, "content_id": "cB"},
        {"type": "RewardAllocated", "block": 11, "user_id": "carol", "token": "ATR", "amount": 1, "content_id": "cA"},
        {"type": "RewardAllocated", "block": 12, "user_id": "carol", "token": "FLX", "amount": 50, "content_id": "cC"},

        # Governance
        {"type": "GovernanceVoteCast", "block": 13, "user_id": "alice", "proposal_id": "p1", "vote_type": "yes"},
        {"type": "GovernanceVoteCast", "block": 14, "user_id": "bob", "proposal_id": "p1", "vote_type": "no"},
        {"type": "GovernanceVoteCast", "block": 15, "user_id": "carol", "proposal_id": "p2", "vote_type": "yes"},
    ]

    g1 = ValueGraphRef().build_from_events(events)
    g2 = ValueGraphRef().build_from_events(events)

    assert g1.users == g2.users
    assert g1.contents == g2.contents
    assert g1.interactions == g2.interactions
    assert g1.rewards == g2.rewards
    assert g1.governance == g2.governance

    # Optional manual cross-checks
    assert g1.users["alice"].total_rewards_atr == 10
    assert g1.users["bob"].total_rewards_atr == 3
    assert g1.users["carol"].total_rewards_atr == 1

    assert g1.users["alice"].total_interactions == 1
    assert g1.users["bob"].total_interactions == 1
    assert g1.users["carol"].total_interactions == 2

