"""
GovernanceParameterRegistry.py - Registry for Mutable Economic Parameters

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
    # Attempting to update any key not in this list will raise a SecurityError.
    MUTABLE_KEYS = {"VIRAL_POOL_CAP", "FLX_REWARD_FRACTION", "ATR_BASE_ACTION_COST"}

    def __init__(self):
        # Initialize storage with default values from the Constitution (economic_constants)
        # We only store mutable keys here to avoid confusion; immutable ones should be read from consts directly
        # or exposed via get() fallbacks if we want a unified interface.
        self._storage: Dict[str, BigNum128] = {}

        # Load initial defaults for mutable keys
        # Note: We map string keys to the actual constant values
        self._load_defaults()

    def _load_defaults(self):
        """Loads default values for mutable parameters from economic_constants."""
        # Mapping logic: We assume the constant name in economic_constants matches the key.
        if hasattr(consts, "CHR_DAILY_EMISSION_CAP"):
            # For VIRAL_POOL_CAP, we might default to a fraction of daily cap or a specific value.
            # In Stage 4 we used 1,000,000. Let's look for a constant or set a safe default.
            # Since VIRAL_POOL_CAP wasn't in economic_constants, we initialize it to the value used in Stage 4.
            self._storage["VIRAL_POOL_CAP"] = BigNum128.from_int(1_000_000)

        if hasattr(consts, "FLX_REWARD_FRACTION"):
            self._storage["FLX_REWARD_FRACTION"] = consts.FLX_REWARD_FRACTION

        if hasattr(consts, "ATR_BASE_ACTION_COST"):
            self._storage["ATR_BASE_ACTION_COST"] = consts.ATR_BASE_ACTION_COST

    def get(self, key: str) -> BigNum128:
        """
        Retrieve the current active value for a parameter.
        If key is mutable, returns registry value.
        If key is immutable (not in storage but in consts), returns const value.
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

        Args:
            key: The parameter name.
            new_value: The new BigNum128 value.
            proposal_id: The ID of the executing proposal (for audit/binding).

        Raises:
            ValueError: If key is not in MUTABLE_KEYS (protects Constitution).
        """
        if key not in self.MUTABLE_KEYS:
            raise ValueError(
                f"[SECURITY] Attempted to modify IMMUTABLE parameter '{key}'. "
                "Only parameters in MUTABLE_KEYS can be changed via governance."
            )

        # In a real system we would verify proposal_id exists and is PASSED.
        # For this stage, the call itself implies authorization from the ProposalEngine.

        self._storage[key] = new_value

        # In production this would write to a ledger/log
        # print(f"Governance Update: {key} -> {new_value.to_decimal_string()} (Prop: {proposal_id})")


def test_registry():
    """Self-test for GovernanceParameterRegistry."""
    reg = GovernanceParameterRegistry()

    # Test 1: Read Default
    val = reg.get("VIRAL_POOL_CAP")
    assert val == BigNum128.from_int(1_000_000)

    # Test 2: Update Mutable
    new_val = BigNum128.from_int(500_000)
    reg.update_parameter("VIRAL_POOL_CAP", new_val, "prop_123")
    assert reg.get("VIRAL_POOL_CAP") == new_val

    # Test 3: Updates are persistent
    assert reg.get("VIRAL_POOL_CAP") == new_val

    # Test 4: Immutable Protection
    try:
        reg.update_parameter("CHR_DAILY_EMISSION_CAP", new_val, "prop_bad")
        assert False, "Should have raised ValueError for immutable key"
    except ValueError as e:
        assert "IMMUTABLE" in str(e)

    print("GovernanceParameterRegistry self-test passed.")


if __name__ == "__main__":
    test_registry()
