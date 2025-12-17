"""
progress.py - User Tour Progress Tracking
"""
from typing import Dict, List, Any
from ...libs.CertifiedMath import CertifiedMath

class ProgressTracker:
    """
    Tracks user progress through onboarding tours.
    """

    def __init__(self):
        self._progress: Dict[str, Dict[str, List[str]]] = {}

    def start_tour(self, user_id: str, tour_id: str):
        """Initialize progress for a user-tour combination."""
        if user_id not in self._progress:
            self._progress[user_id] = {}
        if tour_id not in self._progress[user_id]:
            self._progress[user_id][tour_id] = []

    def complete_step(self, user_id: str, tour_id: str, step_id: str):
        """Mark a step as completed."""
        if user_id not in self._progress:
            self.start_tour(user_id, tour_id)
        if step_id not in self._progress[user_id][tour_id]:
            self._progress[user_id][tour_id].append(step_id)

    def get_progress(self, user_id: str, tour_id: str, total_steps: int) -> Dict[str, Any]:
        """Get progress summary."""
        if user_id not in self._progress or tour_id not in self._progress[user_id]:
            return {'tour_id': tour_id, 'completed_steps': [], 'current_step': None, 'total_steps': total_steps, 'completion_percentage': 0}
        completed = self._progress[user_id][tour_id]
        completion_pct = CertifiedMath.idiv(len(completed) * 100, total_steps) if total_steps > 0 else 0
        return {'tour_id': tour_id, 'completed_steps': completed, 'current_step': f'step_{len(completed) + 1}' if len(completed) < total_steps else None, 'total_steps': total_steps, 'completion_percentage': completion_pct}