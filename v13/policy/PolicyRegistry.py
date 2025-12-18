"""
PolicyRegistry.py - Registry for managing and retrieving historical policy configurations.

Allows 'time-travel' retrieval of policy rules based on epoch, ensuring that
explanations are always generated using the policy version active at the time of the event.
"""
from typing import Dict, Any, Optional
import copy

class PolicyRegistry:
    """
    Central registry for QFS Policies (Economics, Content, Storage).
    Supports versioning and epoch-based retrieval.
    """
    _instance = None

    def __init__(self):
        self.history: Dict[str, Dict[int, Any]] = {}
        self.active_policies: Dict[str, Any] = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = PolicyRegistry()
        return cls._instance

    def register_policy(self, policy_type: str, policy_config: Any, start_epoch: int):
        """
        Register a policy configuration starting at a specific epoch.
        """
        if policy_type not in self.history:
            self.history[policy_type] = {}
        self.history[policy_type][start_epoch] = policy_config
        latest_epoch = max(self.history[policy_type].keys())
        if start_epoch == latest_epoch:
            self.active_policies[policy_type] = policy_config

    def get_policy_for_epoch(self, policy_type: str, epoch: int) -> Optional[Any]:
        """
        Retrieve the policy configuration active at `epoch`.
        Walks backwards from `epoch` to find the nearest start_epoch <= epoch.
        """
        if policy_type not in self.history:
            return None
        timeline = sorted(self.history[policy_type].keys())
        effective_epoch = None
        for start_epoch in sorted(timeline):
            if start_epoch <= epoch:
                effective_epoch = start_epoch
            else:
                break
        if effective_epoch is None:
            return None
        return copy.deepcopy(self.history[policy_type][effective_epoch])

    def get_active_policy(self, policy_type: str) -> Optional[Any]:
        """Get the currently active policy."""
        return copy.deepcopy(self.active_policies.get(policy_type))
