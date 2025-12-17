"""
UserContext: Strict Ledger-Derived Identity & State
==================================================

This module defines the `UserContext` dataclass and its builder.
It is a Zero-Sim Core component.

Contracts:
1. Determinism: Output depends ONLY on the input `ledger_slice`.
2. No External State: No DB, no Cache, no Env Vars.
3. Zero-Float: All weights and scores are scaled integers (CertifiedMath).
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import json

# Zero-Sim: No 'time', 'random', or 'uuid' imports allowed here.
# from v13.libs.CertifiedMath import CertifiedMath # Unused in P0 shim


@dataclass(frozen=True)
class UserContext:
    """
    Immutable representation of a user's state at a specific ledger height.
    Derived strictly from 'IdentityCreated', 'ReputationUpdated', and 'RoleAssigned' events.
    """

    user_id: str
    wallet_id: str
    reputation_score: int  # Scaled Integer (e.g. 100.00 -> 10000)
    roles: List[str]  # Sorted list of roles
    flags: Dict[str, bool]  # Deterministic flags

    # Validation helper
    def to_canonical_json(self) -> str:
        """Producing a canonical JSON string for hashing."""
        data = {
            "user_id": self.user_id,
            "wallet_id": self.wallet_id,
            "reputation_score": self.reputation_score,
            "roles": sorted(self.roles),
            "flags": {k: self.flags[k] for k in sorted(self.flags.keys())},
        }
        return json.dumps(data, sort_keys=True, separators=(",", ":"))


def build_user_context(
    user_id: str, ledger_slice: List[Dict[str, Any]]
) -> Optional[UserContext]:
    """
    Reconstructs UserContext by replaying a slice of ledger events.

    Args:
        user_id: The DID or Wallet ID to build context for.
        ledger_slice: A list of event dictionaries (chronological order).

    Returns:
        UserContext if the user exists/is found, else None.
    """
    # 1. State Accumulators
    found = False
    wallet_id = ""
    reputation = 0
    roles = set()
    flags = {}

    # 2. Deterministic Replay
    for event in sorted(ledger_slice):
        evt_type = event.get("type", "")

        # Identity Creation
        if evt_type == "IdentityCreated":
            if event.get("user_id") == user_id:
                found = True
                wallet_id = event.get("wallet_id", "")

        # Only process other events if user is found or if it links wallet to user
        # (For simplicity in this P0 scope, we assume linear history for the user ID)

        if not found:
            continue

        if event.get("user_id") != user_id:
            continue

        # Reputation Updates
        if evt_type == "ReputationUpdated":
            # "score_delta" expected to be a string "X.Y ATR" or int.
            # We must be careful to handle it via CertifiedMath if it's not already int.
            # But for UserContext builder, let's assume raw int events or handle basic types.
            # In V13 Core, reputation is often just an int.
            delta = event.get("score_delta", 0)
            if isinstance(delta, int):
                reputation += delta
            # NOTE: If we iterate on complex math, we use CertifiedMath here.
            # For now, simple integer accumulation.

        # Role Assignments
        elif evt_type == "RoleAssigned":
            role = event.get("role")
            if role:
                roles.add(role)

        elif evt_type == "RoleRevoked":
            role = event.get("role")
            if role and role in roles:
                roles.remove(role)

        # Flag Toggles
        elif evt_type == "FlagSet":
            flag_name = event.get("flag")
            flag_val = event.get("value", True)
            if flag_name:
                flags[flag_name] = flag_val

    if not found:
        return None

    # 3. Finalize
    return UserContext(
        user_id=user_id,
        wallet_id=wallet_id,
        reputation_score=reputation,
        roles=sorted(list(roles)),
        flags=flags,
    )
