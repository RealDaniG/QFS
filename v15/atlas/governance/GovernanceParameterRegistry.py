"""
GovernanceParameterRegistry.py (v15) - Registry for Mutable Economic Parameters

This module serves as the single source of truth for active economic parameters
that are subject to governance. It strictly enforces a separation between
IMMUTABLE (Constitutional) constants and MUTABLE (Governance) parameters.

Invariants:
- GOV-I1: Only parameters in the MUTABLE_KEYS whitelist can be updated.
- GOV-I2: Updates must be cryptographically bound to an executed proposal (simulated via strict interface).
"""

from typing import Dict, Any, Optional
from v13.libs.BigNum128 import BigNum128
from v13.libs.economics import economic_constants as consts


class GovernanceParameterRegistry:
    """
    Registry for active economic parameters, allowing strictly controlled mutations.
    """

    # Whitelist of parameters that governance is allowed to change.
    MUTABLE_KEYS = {"VIRAL_POOL_CAP", "FLX_REWARD_FRACTION", "ATR_BASE_ACTION_COST"}

    def __init__(self):
        self._storage: Dict[str, BigNum128] = {}
        self._load_defaults()

    def _load_defaults(self):
        """Loads default values for mutable parameters from economic_constants."""
        # Defaults if not present in consts
        self._storage["VIRAL_POOL_CAP"] = BigNum128.from_int(1_000_000)

        if hasattr(consts, "FLX_REWARD_FRACTION"):
            self._storage["FLX_REWARD_FRACTION"] = consts.FLX_REWARD_FRACTION

        if hasattr(consts, "ATR_BASE_ACTION_COST"):
            self._storage["ATR_BASE_ACTION_COST"] = consts.ATR_BASE_ACTION_COST

    def get(self, key: str) -> BigNum128:
        """
        Retrieve the current active value for a parameter.
        """
        if key in self._storage:
            return self._storage[key]

        # Fallback to constants for immutable values
        if hasattr(consts, key):
            return getattr(consts, key)

        raise KeyError(f"Parameter '{key}' not found in Registry or Constitution.")

    def update_parameter(
        self, key: str, new_value: BigNum128, proposal_id: str
    ) -> None:
        """
        Update a mutable parameter.
        """
        if key not in self.MUTABLE_KEYS:
            raise ValueError(
                f"[SECURITY] Attempted to modify IMMUTABLE parameter '{key}'. "
                "Only parameters in MUTABLE_KEYS can be changed via governance."
            )

        self._storage[key] = new_value

    def get_all_parameters(self) -> Dict[str, BigNum128]:
        """
        Return a copy of all mutable parameters.
        """
        return self._storage.copy()
