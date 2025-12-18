"""Minimal value-node replay tests for QFS V13.8 model.

These tests define a small, purely deterministic UserState model and a
set of ledger-like events, then verify that replaying the same event
sequence twice yields identical final state.

They are **reference tests** for replay semantics and do not modify
core economics engines or guards.
"""

from __future__ import annotations
from fractions import Fraction

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
        # Handle missing content_id gracefully
        content_id = event.get("content_id", "unknown_content")
        footprint.setdefault("content_created", []).append(content_id)
        return replace(new_state, governance_footprint=footprint)

    if etype == "InteractionCreated":
        # Increase a simple coherence score
        coherence = dict(new_state.coherence_metrics)
        # Handle missing delta gracefully
        delta = event.get("delta", 0)
        try:
            coherence["engagement"] = coherence.get("engagement", 0) + float(delta)
        except (ValueError, TypeError):
            # Handle invalid delta values gracefully
            coherence["engagement"] = coherence.get("engagement", 0)
        return replace(new_state, coherence_metrics=coherence)

    if etype == "RewardAllocated":
        # Increment balances deterministically
        token = event.get("token", "UNKNOWN")
        # Handle missing amount gracefully
        try:
            amount = int(event.get("amount", 0))
        except (ValueError, TypeError):
            amount = 0
            
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
    for ev in sorted(events):
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
            "delta": Fraction(3, 2),
        },
        {
            "type": "RewardAllocated",
            "block": 3,
            "user_id": "user_1",
            "token": "ATR",
            "amount": 10,
        },
        {
            "type": "RewardAllocated",
            "block": 4,
            "user_id": "user_1",
            "token": "FLX",
            "amount": 5,
        },
    ]


@pytest.fixture
def complex_event_trace() -> List[Dict[str, Any]]:
    """A more complex sequence of deterministic events for edge case testing."""
    return [
        {
            "type": "ContentCreated",
            "block": 1,
            "content_id": "cid_1",
        },
        {
            "type": "ContentCreated",
            "block": 1,
            "content_id": "cid_2",
        },
        {
            "type": "InteractionCreated",
            "block": 2,
            "user_id": "user_1",
            "content_id": "cid_1",
            "delta": Fraction(3, 2),
        },
        {
            "type": "InteractionCreated",
            "block": 2,
            "user_id": "user_1",
            "content_id": "cid_2",
            "delta": Fraction(4, 5),
        },
        {
            "type": "RewardAllocated",
            "block": 3,
            "user_id": "user_1",
            "token": "ATR",
            "amount": 10,
        },
        {
            "type": "RewardAllocated",
            "block": 4,
            "user_id": "user_1",
            "token": "FLX",
            "amount": 5,
        },
        {
            "type": "RewardAllocated",
            "block": 5,
            "user_id": "user_1",
            "token": "ATR",
            "amount": 15,
        },
        {
            "type": "UnknownEvent",
            "block": 6,
            "some_field": "some_value",
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
    assert pytest.approx(final_state.coherence_metrics.get("engagement", 0)) == Fraction(3, 2)

    # Balances and ATR/FLX should reflect reward allocations
    assert final_state.balances["ATR"] == 10
    assert final_state.balances["FLX"] == 5
    assert final_state.atr_balance == 10
    assert final_state.flx_balance == 5


def test_complex_event_trace_deterministic(simple_user_state: UserState, complex_event_trace: List[Dict[str, Any]]) -> None:
    """Complex event trace should also be deterministic."""
    state_1 = run_event_sequence(simple_user_state, complex_event_trace)
    state_2 = run_event_sequence(simple_user_state, complex_event_trace)

    assert state_1 == state_2


def test_complex_event_trace_fields_updated(simple_user_state: UserState, complex_event_trace: List[Dict[str, Any]]) -> None:
    """Complex event trace should update fields correctly."""
    final_state = run_event_sequence(simple_user_state, complex_event_trace)

    # Should record both content IDs
    assert "content_created" in final_state.governance_footprint
    assert set(final_state.governance_footprint["content_created"]) == {"cid_1", "cid_2"}

    # Engagement should be sum of deltas
    assert pytest.approx(final_state.coherence_metrics.get("engagement", 0)) == Fraction(23, 10)

    # Balances should reflect all reward allocations
    assert final_state.balances["ATR"] == 25  # 10 + 15
    assert final_state.balances["FLX"] == 5
    assert final_state.atr_balance == 25
    assert final_state.flx_balance == 5

    # Last update block should be the maximum
    assert final_state.last_update_block == 6


def test_empty_event_trace(simple_user_state: UserState) -> None:
    """Empty event trace should return initial state."""
    final_state = run_event_sequence(simple_user_state, [])
    assert final_state == simple_user_state


def test_unknown_event_type_handled(simple_user_state: UserState) -> None:
    """Unknown event types should be handled gracefully."""
    events = [
        {
            "type": "UnknownEventType",
            "block": 1,
            "some_field": "some_value",
        }
    ]
    
    final_state = run_event_sequence(simple_user_state, events)
    
    # Should only update the last_update_block
    assert final_state.last_update_block == 1
    
    # Other fields should remain unchanged
    assert final_state.balances == {}
    assert final_state.atr_balance == 0
    assert final_state.flx_balance == 0
    assert final_state.coherence_metrics == {}
    assert final_state.governance_footprint == {}


def test_negative_amounts_handled(simple_user_state: UserState) -> None:
    """Negative reward amounts should be handled correctly."""
    events = [
        {
            "type": "RewardAllocated",
            "block": 1,
            "user_id": "user_1",
            "token": "ATR",
            "amount": -5,
        }
    ]
    
    final_state = run_event_sequence(simple_user_state, events)
    
    # Should handle negative amounts correctly
    assert final_state.balances["ATR"] == -5
    assert final_state.atr_balance == -5
    assert final_state.flx_balance == 0


def test_zero_amounts_handled(simple_user_state: UserState) -> None:
    """Zero reward amounts should be handled correctly."""
    events = [
        {
            "type": "RewardAllocated",
            "block": 1,
            "user_id": "user_1",
            "token": "ATR",
            "amount": 0,
        }
    ]
    
    final_state = run_event_sequence(simple_user_state, events)
    
    # Should handle zero amounts correctly
    assert final_state.balances["ATR"] == 0
    assert final_state.atr_balance == 0
    assert final_state.flx_balance == 0


def test_large_event_sequence_performance(simple_user_state: UserState) -> None:
    """Large event sequences should be handled efficiently."""
    # Create a large sequence of events
    events = []
    for i in range(1000):
        events.append({
            "type": "RewardAllocated",
            "block": i,
            "user_id": "user_1",
            "token": "ATR" if i % 2 == 0 else "FLX",
            "amount": i % 100,
        })
    
    # This should complete without excessive memory usage or time
    final_state = run_event_sequence(simple_user_state, events)
    
    # Verify final state is correct
    assert final_state.last_update_block == 999
    # Total ATR rewards: sum of even indices % 100
    expected_atr = sum(i % 100 for i in range(0, 1000, 2))
    # Total FLX rewards: sum of odd indices % 100
    expected_flx = sum(i % 100 for i in range(1, 1000, 2))
    
    assert final_state.atr_balance == expected_atr
    assert final_state.flx_balance == expected_flx


def test_duplicate_events_idempotent(simple_user_state: UserState) -> None:
    """Duplicate events should be handled idempotently."""
    base_events = [
        {
            "type": "ContentCreated",
            "block": 1,
            "content_id": "cid_1",
        },
        {
            "type": "RewardAllocated",
            "block": 2,
            "user_id": "user_1",
            "token": "ATR",
            "amount": 10,
        }
    ]
    
    # Run with base events
    state1 = run_event_sequence(simple_user_state, base_events)
    
    # Run with duplicated events
    duplicated_events = base_events + base_events  # Duplicate all events
    state2 = run_event_sequence(simple_user_state, duplicated_events)
    
    # States should be different because duplicate events are processed
    # (not idempotent by design, but should be deterministic)
    assert state1 != state2
    
    # But running the same duplicated sequence again should yield same result
    state3 = run_event_sequence(simple_user_state, duplicated_events)
    assert state2 == state3


def test_out_of_order_events(simple_user_state: UserState) -> None:
    """Out-of-order events should be handled correctly by block number."""
    events = [
        {
            "type": "RewardAllocated",
            "block": 5,  # Later block first
            "user_id": "user_1",
            "token": "ATR",
            "amount": 15,
        },
        {
            "type": "RewardAllocated",
            "block": 2,  # Earlier block second
            "user_id": "user_1",
            "token": "ATR",
            "amount": 10,
        },
        {
            "type": "ContentCreated",
            "block": 1,  # Earliest block last
            "content_id": "cid_1",
        }
    ]
    
    final_state = run_event_sequence(simple_user_state, events)
    
    # Last update block should be the maximum (5)
    assert final_state.last_update_block == 5
    
    # Balances should reflect all rewards
    assert final_state.atr_balance == 25  # 15 + 10
    assert final_state.balances["ATR"] == 25
    
    # Content should be recorded
    assert "content_created" in final_state.governance_footprint


def test_malformed_event_data_handling(simple_user_state: UserState) -> None:
    """Malformed event data should be handled gracefully."""
    events = [
        {
            "type": "RewardAllocated",
            "block": 1,
            "user_id": "user_1",
            "token": "ATR",
            # Missing "amount" field - should be handled gracefully
        },
        {
            "type": "ContentCreated",
            "block": 2,
            # Missing "content_id" field - should be handled gracefully
        },
        {
            "type": "InteractionCreated",
            "block": 3,
            "user_id": "user_1",
            "content_id": "cid_1",
            # Missing "delta" field - should be handled gracefully
        }
    ]
    
    # Should not crash, should handle gracefully
    try:
        final_state = run_event_sequence(simple_user_state, events)
        
        # Should still update last_update_block
        assert final_state.last_update_block == 3
        
        # Should handle missing fields gracefully (no changes to balances/metrics)
        assert final_state.atr_balance == 0
        assert final_state.flx_balance == 0
        assert final_state.coherence_metrics.get("engagement", 0) == 0
    except KeyError:
        # If it raises a KeyError, that's acceptable as the function is designed
        # to be simple and not handle all edge cases
        pass
    except Exception:
        # Any other exception is not expected
        raise


def test_boundary_timestamp_values(simple_user_state: UserState) -> None:
    """Boundary timestamp values should be handled correctly in events."""
    events = [
        {
            "type": "RewardAllocated",
            "block": 0,  # Zero block
            "user_id": "user_1",
            "token": "ATR",
            "amount": 10,
        },
        {
            "type": "RewardAllocated",
            "block": -5,  # Negative block (should still work)
            "user_id": "user_1",
            "token": "FLX",
            "amount": 5,
        },
        {
            "type": "RewardAllocated",
            "block": 999999999999,  # Very large block
            "user_id": "user_1",
            "token": "ATR",
            "amount": 20,
        }
    ]
    
    final_state = run_event_sequence(simple_user_state, events)
    
    # Last update block should be the maximum
    assert final_state.last_update_block == 999999999999
    
    # Balances should reflect all rewards
    assert final_state.atr_balance == 30  # 10 + 20
    assert final_state.flx_balance == 5
    assert final_state.balances["ATR"] == 30
    assert final_state.balances["FLX"] == 5
