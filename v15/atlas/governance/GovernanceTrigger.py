"""
GovernanceTrigger.py (v15) - Deterministic Parameter Activation

Manages the transition of governance parameters from "Registry" (Approved) to
"Active Snapshot" (Effective). Ensures that parameters only change at
deterministic boundaries (e.g., Epoch Ticks), preventing mid-cycle economic instability.

Invariants:
- TRIG-I1: Active parameters must remain constant within an epoch.
- TRIG-I2: Updates are applied atomically at `process_tick`.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import copy

from v13.libs.BigNum128 import BigNum128
from v15.atlas.governance.GovernanceParameterRegistry import GovernanceParameterRegistry


@dataclass
class ActiveParameterSnapshot:
    """Immutable snapshot of active parameters for the current epoch."""

    epoch_index: int
    parameters: Dict[str, BigNum128]


class GovernanceTrigger:
    """
    Orchestrates the activation of governance parameters.
    """

    def __init__(self, registry: GovernanceParameterRegistry):
        self.registry = registry
        self.current_epoch = 0

        # Initialize first snapshot from Registry defaults
        self._active_snapshot = ActiveParameterSnapshot(
            epoch_index=0, parameters=self._deep_copy_params(registry._storage)
        )

    def _deep_copy_params(self, params: Dict[str, BigNum128]) -> Dict[str, BigNum128]:
        """Creates a safe copy of parameters."""
        return copy.deepcopy(params)

    def current_snapshot(self) -> ActiveParameterSnapshot:
        """Returns the currently effective parameter set."""
        return self._active_snapshot

    def process_tick(self, block_height: int, epoch_length: int = 100) -> bool:
        """
        Called at every block (or relevant tick).
        Checks if a new epoch has started. If so, updates the snapshot.

        Args:
            block_height: Current block number / sequence.
            epoch_length: Number of blocks per epoch.

        Returns:
            bool: True if a new snapshot was generated (Epoch Boundary).
        """
        new_epoch = block_height // epoch_length

        if new_epoch > self.current_epoch:
            # EPOCH BOUNDARY: Activate current Registry state
            self.current_epoch = new_epoch

            # Pull latest values from Registry
            # In a real system, we might have a 'Queued' state, but here
            # the Registry holds the 'Approved' state, so we just sync it.
            new_params = self._deep_copy_params(self.registry._storage)

            self._active_snapshot = ActiveParameterSnapshot(
                epoch_index=new_epoch, parameters=new_params
            )
            return True

        return False

    def get_parameter(self, key: str) -> BigNum128:
        """
        Convenience method to get a parameter from the ACTIVE snapshot.
        Falls back to Registry defaults/constants if not in snapshot (Immutable).
        """
        if key in self._active_snapshot.parameters:
            return self._active_snapshot.parameters[key]

        # Fallback to Registry logic which falls back to Constants
        return self.registry.get(key)
