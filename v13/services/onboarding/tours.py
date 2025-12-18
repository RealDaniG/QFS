"""
tours.py - Tour Definitions and Registry
"""
from typing import Dict, List, Any

class TourRegistry:
    """
    Manages available onboarding tours.
    """

    def __init__(self):
        self._tours: Dict[str, Dict[str, Any]] = {}
        self._load_default_tours()

    def _load_default_tours(self):
        """Load built-in tours."""
        welcome_tour = {'tour_id': 'welcome_v1', 'name': 'Welcome to QFS × ATLAS', 'description': 'Learn the basics of the QFS platform', 'steps': [{'id': 'step_1', 'title': 'Your First Action', 'description': 'Post your first piece of content', 'task_type': 'POST_CONTENT', 'reward': 10}, {'id': 'step_2', 'title': 'Check Your Coherence', 'description': 'View your coherence score', 'task_type': 'VIEW_COHERENCE', 'reward': 5}, {'id': 'step_3', 'title': 'Explore Explain-This', 'description': 'Request an explanation for a decision', 'task_type': 'USE_EXPLAIN_THIS', 'reward': 15}]}
        self._tours['welcome_v1'] = welcome_tour

    def get_tour(self, tour_id: str) -> Dict[str, Any]:
        return self._tours.get(tour_id)

    def list_tours(self) -> List[Dict[str, Any]]:
        return [{'id': t['tour_id'], 'name': t['name'], 'steps': len(t['steps'])} for t in self._tours.values()]
