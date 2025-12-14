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
