"""
Referral events for GenesisLedger.
All events are deterministic and zero-simulation compliant.
"""

from dataclasses import dataclass, field
from typing import Dict, Any
import hashlib

def deterministic_referral_code(wallet: str, epoch: int) -> str:
    """
    Generate deterministic referral code.
    Same wallet + epoch always produces same code.
    """
    input_str = f"{wallet}:{epoch}:QFS_REF_V1"
    hash_bytes = hashlib.sha3_256(input_str.encode()).digest()
    
    # Base58-like encoding (using restricted charset for URLs)
    charset = "0123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    code = ""
    num = int.from_bytes(hash_bytes[:16], 'big')
    
    while num > 0 and len(code) < 22:
        num, remainder = divmod(num, len(charset))
        code = charset[remainder] + code
    
    return code.rjust(22, '0')

@dataclass(frozen=True)  # Immutable
class ReferralCreated:
    """Emitted when user generates referral link."""
    referrer_wallet: str
    referral_code: str
    epoch: int
    source: str  # "profile", "chat", "quest"
    event_type: str = field(default="REFERRAL_CREATED", init=False)
    campaign_id: str = "genesis_v1"
    
    def __post_init__(self):
        # Validate referral code is deterministic
        expected = deterministic_referral_code(self.referrer_wallet, self.epoch)
        if self.referral_code != expected:
            raise ValueError(f"Non-deterministic referral code: {self.referral_code} != {expected}")

@dataclass(frozen=True)
class ReferralAccepted:
    """Emitted when referee clicks link and connects wallet."""
    referrer_wallet: str
    referee_wallet: str
    referral_code: str
    epoch: int
    device_hash: str  # SHA3-256 of user-agent + IP /24 subnet
    event_type: str = field(default="REFERRAL_ACCEPTED", init=False)

@dataclass(frozen=True)
class ReferralActivated:
    """Emitted when referee completes activation criteria."""
    referrer_wallet: str
    referee_wallet: str
    referral_code: str
    epoch: int
    activation_type: str  # "FIRST_MESSAGE", "PROFILE_COMPLETE", "FIRST_QUEST"
    event_type: str = field(default="REFERRAL_ACTIVATED", init=False)

@dataclass(frozen=True)
class ReferralRewarded:
    """Emitted when CoherenceEngine grants reward."""
    referrer_wallet: str
    referee_wallet: str
    token_type: str  # "FLX", "CHR", "ATR"
    amount_scaled: int  # BigNum128 (1e8 scale factor)
    epoch: int
    reason: str
    guard_cir_code: str  # From EconomicsGuard validation
    event_type: str = field(default="REFERRAL_REWARDED", init=False)

@dataclass(frozen=True)
class ReferralFraudBlocked:
    """Emitted when anti-fraud rules trigger."""
    referrer_wallet: str
    referee_wallet: str
    fraud_type: str  # "SELF_REF", "DUP_DEVICE", "CIRCULAR"
    epoch: int
    evidence: Dict[str, str]  # Sorted dict for determinism
    event_type: str = field(default="REFERRAL_FRAUD_BLOCKED", init=False)
