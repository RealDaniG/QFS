"""
test_onboarding_tours.py - Unit tests for Onboarding Tours
"""
import pytest
from v13.services.onboarding.tours import TourRegistry
from v13.services.onboarding.progress import ProgressTracker

def test_tour_registry():
    registry = TourRegistry()
    tours = registry.list_tours()
    assert len(tours) > 0
    welcome = registry.get_tour('welcome_v1')
    assert welcome is not None
    assert welcome['tour_id'] == 'welcome_v1'
    assert len(welcome['steps']) == 3

def test_progress_tracking():
    tracker = ProgressTracker()
    user = '0xUser1'
    tour = 'welcome_v1'
    tracker.start_tour(user, tour)
    progress = tracker.get_progress(user, tour, total_steps=3)
    assert progress['completion_percentage'] == 0
    assert len(progress['completed_steps']) == 0
    tracker.complete_step(user, tour, 'step_1')
    progress = tracker.get_progress(user, tour, total_steps=3)
    assert progress['completion_percentage'] == 33
    assert 'step_1' in progress['completed_steps']
    assert progress['current_step'] == 'step_2'
    tracker.complete_step(user, tour, 'step_2')
    progress = tracker.get_progress(user, tour, total_steps=3)
    assert progress['completion_percentage'] == 66
    tracker.complete_step(user, tour, 'step_3')
    progress = tracker.get_progress(user, tour, total_steps=3)
    assert progress['completion_percentage'] == 100
    assert progress['current_step'] is None

def test_multiple_users():
    tracker = ProgressTracker()
    tracker.complete_step('0xUser1', 'welcome_v1', 'step_1')
    tracker.complete_step('0xUser2', 'welcome_v1', 'step_1')
    tracker.complete_step('0xUser2', 'welcome_v1', 'step_2')
    p1 = tracker.get_progress('0xUser1', 'welcome_v1', total_steps=3)
    p2 = tracker.get_progress('0xUser2', 'welcome_v1', total_steps=3)
    assert len(p1['completed_steps']) == 1
    assert len(p2['completed_steps']) == 2

def test_tour_step_rewards():
    registry = TourRegistry()
    tour = registry.get_tour('welcome_v1')
    total_rewards = sum((step['reward'] for step in tour['steps']))
    assert total_rewards == 30