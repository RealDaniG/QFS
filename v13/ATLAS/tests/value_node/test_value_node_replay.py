"""Minimal value-node replay tests for QFS V13.8 model.

These tests define a small, purely deterministic UserState model and a
set of ledger-like events, then verify that replaying the same event
sequence twice yields identical final state.

They are **reference tests** for replay semantics and do not modify
core economics engines or guards.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Dict, Any, List

import pytest


@dataclass(frozen=True)
class UserState:
    """Simplified value-node state for replay tests.

    This mirrors the structure described in QFS_V13_8_VALUE_NODE_MODEL.md
    but intentionally omits any core engine logic.
    """

    user_id: str
    balances: Dict[str, int]
    atr_balance: int
    flx_balance: int
    coherence_metrics: Dict[str, float]
    governance_footprint: Dict[str, Any]
    last_update_block: int


def apply_event(state: UserState, event: Dict[str, Any]) -> UserState:
    """Apply a minimal, deterministic event to UserState.

    This function is deliberately simple and side-effect-free. It uses
    only integer additions and dictionary updates to emulate how a
    real state transition function might behave.

    Event schema (minimal for tests):
      - type: "ContentCreated" | "InteractionCreated" | "RewardAllocated"
      - block: int
      - fields specific to each type.
    """

    etype = event["type"]
    block = event["block"]

    # Always advance last_update_block monotonically
    new_state = replace(state, last_update_block=max(state.last_update_block, block))

    if etype == "ContentCreated":
        # Record a simple footprint marker
        footprint = dict(new_state.governance_footprint)
        content_id = event["content_id"]
        footprint.setdefault("content_created", []).append(content_id)
        return replace(new_state, governance_footprint=footprint)

    if etype == "InteractionCreated":
        # Increase a simple coherence score
        coherence = dict(new_state.coherence_metrics)
        coherence["engagement"] = coherence.get("engagement", 0.0) + float(event.get("delta", 0.0))
        return replace(new_state, coherence_metrics=coherence)

    if etype == "RewardAllocated":
        # Increment balances deterministically
        token = event["token"]
        amount = int(event["amount"])
        balances = dict(new_state.balances)
        balances[token] = balances.get(token, 0) + amount

        atr = new_state.atr_balance
        flx = new_state.flx_balance
        if token == "ATR":
            atr += amount
        if token == "FLX":
            flx += amount

        return replace(new_state, balances=balances, atr_balance=atr, flx_balance=flx)

    # Unknown event type: no-op but deterministic
    return new_state


def run_event_sequence(initial: UserState, events: List[Dict[str, Any]]) -> UserState:
    """Apply a sequence of events in order, returning the final state."""
    state = initial
    for ev in events:
        state = apply_event(state, ev)
    return state


@pytest.fixture
def simple_user_state() -> UserState:
    """Provide a minimal initial UserState for replay tests."""
    return UserState(
        user_id="user_1",
        balances={},
        atr_balance=0,
        flx_balance=0,
        coherence_metrics={},
        governance_footprint={},
        last_update_block=0,
    )


@pytest.fixture
def simple_event_trace() -> List[Dict[str, Any]]:
    """A small, fixed sequence of deterministic events."""
    return [
        {
            "type": "ContentCreated",
            "block": 1,
            "content_id": "cid_1",
        },
        {
            "type": "InteractionCreated",
            "block": 2,
            "user_id": "user_1",
            "content_id": "cid_1",
            "delta": 1.5,
        },
        {
            "type": "RewardAllocated",
            "block": 3,
            "user_id": "user_1",
            "user_id": "user_1",
            "token": "ATR",
            "amount": 10,
        },
        {
            "type": "RewardAllocated",
            "block": 4,
            "user_id": "user_1",
            "user_id": "user_1",
            "token": "FLX",
            "amount": 5,
        },
    ]


def test_value_node_replay_is_deterministic(simple_user_state: UserState, simple_event_trace: List[Dict[str, Any]]) -> None:
    """Replaying the same event sequence twice yields identical final state."""
    state_1 = run_event_sequence(simple_user_state, simple_event_trace)
    state_2 = run_event_sequence(simple_user_state, simple_event_trace)

    assert state_1 == state_2


def test_value_node_state_fields_updated_as_expected(simple_user_state: UserState, simple_event_trace: List[Dict[str, Any]]) -> None:
    """Basic sanity on which fields are updated by the example trace."""
    final_state = run_event_sequence(simple_user_state, simple_event_trace)

    # Governance footprint should record created content
    assert "content_created" in final_state.governance_footprint
    assert final_state.governance_footprint["content_created"] == ["cid_1"]

    # Coherence engagement metric should be updated
    assert pytest.approx(final_state.coherence_metrics.get("engagement", 0.0)) == 1.5

    # Balances and ATR/FLX should reflect reward allocations
    assert final_state.balances["ATR"] == 10
    assert final_state.balances["FLX"] == 5
    assert final_state.atr_balance == 10
    assert final_state.flx_balance == 5
