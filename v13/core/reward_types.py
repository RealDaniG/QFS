"""
reward_types.py - Shared reward data types for QFS V13

Contains shared data structures for reward calculations to avoid circular dependencies
between TreasuryEngine and RewardAllocator.
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
try:
    from ..libs.CertifiedMath import BigNum128
except ImportError:
    try:
        from v13.libs.CertifiedMath import BigNum128
    except ImportError:
        from libs.CertifiedMath import BigNum128

@dataclass
class RewardBundle:
    """Container for reward calculations"""
    chr_reward: BigNum128
    flx_reward: BigNum128
    res_reward: BigNum128
    psi_sync_reward: BigNum128
    atr_reward: BigNum128
    nod_reward: BigNum128
    total_reward: BigNum128