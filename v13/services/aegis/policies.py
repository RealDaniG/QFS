"""
AEGIS Policy Registry
=====================

Pure functional capability gating.
Zero-Sim Enforced: No Side Effects, No IO, No Random, No Time.

Contracts:
- Input: UserContext, EvidenceHash (str), PolicyVersion (int)
- Output: Decision (bool) or Reason (str)
"""

from typing import Dict, Callable
from v13.services.governance.context import UserContext

# Type alias for Policy Function
# (ctx, evidence_hash, *args) -> bool
PolicyFunc = Callable[..., bool]


def policy_can_appeal(ctx: UserContext, evidence_hash: str) -> bool:
    """
    Policy: Can a user initiate an appeal?
    Rules:
    1. Must have reputation > 10.0 ATR (1000 units).
    2. Must NOT have 'is_banned' flag.
    """
    if ctx.flags.get("is_banned", False):
        return False

    if ctx.reputation_score < 1000:
        return False

    return True


def policy_can_vote(ctx: UserContext, appeal_id: str) -> bool:
    """
    Policy: Can a user vote on an appeal?
    Rules:
    1. Must have 'VALIDATOR' or 'JURY' role.
    2. Must be active.
    """
    if not ctx.flags.get("is_active", True):
        return False

    allowed_roles = {"VALIDATOR", "JURY"}
    # set intersection
    user_roles = set(ctx.roles)
    if not user_roles.intersection(allowed_roles):
        return False

    return True


# Registry mapping policy names to functions
POLICY_REGISTRY: Dict[str, PolicyFunc] = {
    "can_appeal": policy_can_appeal,
    "can_vote": policy_can_vote,
}


def evaluate_policy(policy_name: str, ctx: UserContext, **kwargs) -> bool:
    """
    Deterministic evaluation of a named policy.
    """
    func = POLICY_REGISTRY.get(policy_name)
    if not func:
        # Default deny (Fail Secure)
        return False

    return func(ctx, **kwargs)
