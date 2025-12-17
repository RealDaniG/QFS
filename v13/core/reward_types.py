"""
reward_types.py - Shared reward data types for QFS V13

Contains shared data structures for reward calculations to avoid circular dependencies
between TreasuryEngine and RewardAllocator.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Import required modules
try:
    # Try relative imports first (for package usage)
    from ..libs.CertifiedMath import BigNum128
except ImportError:
    # Fallback to absolute imports (for direct execution)
    try:
        from v13.libs.CertifiedMath import BigNum128
    except ImportError:
        # For Zero-Sim compliance, use direct import without sys.path modification
        from libs.CertifiedMath import BigNum128


@dataclass
class RewardBundle:
    """Container for reward calculations"""
    chr_reward: BigNum128
    flx_reward: BigNum128
    res_reward: BigNum128
    psi_sync_reward: BigNum128
    atr_reward: BigNum128
    nod_reward: BigNum128  # ← NEW: NOD reward from ATR fees
    total_reward: BigNum128