import pytest
from src.lib.cycles import (
    get_window_id,
    update_cycle,
    calculate_daily_reward,
    calculate_cycle_bonus,
)


def test_window_id_deterministic():
    """Test that window IDs are deterministic."""
    ts = 1703116800  # 2023-12-21 00:00:00 UTC
    assert get_window_id(ts) == 19712
    assert get_window_id(ts) == get_window_id(ts)

    # Next day
    next_day = ts + 86400
    assert get_window_id(next_day) == 19713
    assert get_window_id(next_day) == get_window_id(ts) + 1


def test_daily_reward_progression():
    """Test that rewards increase each day."""
    assert calculate_daily_reward(1) < calculate_daily_reward(2)
    assert calculate_daily_reward(14) < calculate_daily_reward(15)


def test_cycle_start():
    """Test cycle creation."""
    cycle = update_cycle(None, 100, "0xABC")

    assert cycle["day_index"] == 1
    assert cycle["status"] == "active"
    assert cycle["wallet"] == "0xABC"
    assert cycle["start_window"] == 100


def test_cycle_consecutive_days():
    """Test cycle progression over consecutive days."""
    cycle = update_cycle(None, 100, "0xABC")

    # Simulate days 2 to 15
    for day in range(2, 16):
        cycle = update_cycle(cycle, 100 + day - 1, "0xABC")

    assert cycle["day_index"] == 15
    assert cycle["status"] == "completed"
    assert cycle["total_reward"] > 450  # Includes completion bonus


def test_cycle_reset_on_missed_day():
    """Test that cycle resets when a day is missed."""
    cycle = update_cycle(None, 100, "0xABC")
    cycle = update_cycle(cycle, 101, "0xABC")

    # Skip day 102, go to 103
    cycle = update_cycle(cycle, 103, "0xABC")

    assert cycle["day_index"] == 1
    assert cycle["start_window"] == 103


def test_cycle_same_day_no_change():
    """Test that signing twice on same day doesn't change cycle."""
    cycle = update_cycle(None, 100, "0xABC")
    original_reward = cycle["total_reward"]

    # Try to update again on same window
    cycle = update_cycle(cycle, 100, "0xABC")

    assert cycle["day_index"] == 1
    assert cycle["total_reward"] == original_reward
