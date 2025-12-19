"""
Developer Rewards Treasury

Bounded treasury for developer bounty rewards.
Constitutional compliance: no unbounded minting, explainable payments.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict
import json
import logging

from v13.policy.bounties.bounty_events import (
    emit_bounty_paid_event,
    emit_treasury_refill_event,
    EconomicEvent,
)
from v13.libs.BigNum128 import BigNum128

# Setup logger
logger = logging.getLogger(__name__)


class InsufficientTreasuryError(Exception):
    """Raised when treasury cannot fulfill payment"""

    pass


class TreasuryDepletionWarning(Warning):
    """Warning when treasury is running low"""

    pass


@dataclass
class TreasuryPayment:
    """Record of a treasury payment"""

    bounty_id: str
    contributor: str
    flx_amount: BigNum128
    chr_amount: BigNum128
    timestamp: int
    pr_number: int
    commit_hash: str


@dataclass
class DevRewardsTreasury:
    """
    Bounded treasury for developer rewards.

    Constitutional guarantees:
    - Bounded reserves (no unbounded minting)
    - Explainable payments (bounty ID + commit hash)
    - Deterministic (fixed rewards)
    - Auditable (full payment history)
    """

    treasury_id: str = "dev_rewards_v1"
    flx_reserve: BigNum128 = field(default_factory=lambda: BigNum128.from_int(0))
    chr_reserve: BigNum128 = field(default_factory=lambda: BigNum128.from_int(0))
    total_paid_flx: BigNum128 = field(default_factory=lambda: BigNum128.from_int(0))
    total_paid_chr: BigNum128 = field(default_factory=lambda: BigNum128.from_int(0))
    payment_history: List[TreasuryPayment] = field(default_factory=list)
    refill_history: List[Dict] = field(default_factory=list)

    # Alert thresholds
    LOW_RESERVE_THRESHOLD: float = 0.2  # 20% remaining
    CRITICAL_RESERVE_THRESHOLD: float = 0.1  # 10% remaining

    def __post_init__(self):
        """Initialize with default allocation if not set"""
        if self.flx_reserve.value == 0 and self.chr_reserve.value == 0:
            # Default allocation (can be overridden)
            self.flx_reserve = BigNum128.from_int(10000)
            self.chr_reserve = BigNum128.from_int(5000)

    def can_pay(self, flx: BigNum128, chr: BigNum128) -> bool:
        """Check if treasury has sufficient reserves"""
        return (
            self.flx_reserve.value >= flx.value and self.chr_reserve.value >= chr.value
        )

    def get_reserve_percentage(self) -> Dict[str, float]:
        """Get current reserve levels as percentages"""
        initial_flx = self.flx_reserve.value + self.total_paid_flx.value
        initial_chr = self.chr_reserve.value + self.total_paid_chr.value

        return {
            "flx_pct": (self.flx_reserve.value / initial_flx)
            if initial_flx > 0
            else 0.0,
            "chr_pct": (self.chr_reserve.value / initial_chr)
            if initial_chr > 0
            else 0.0,
        }

    def check_depletion_status(self) -> Optional[str]:
        """
        Check if treasury is running low.

        Returns:
            "critical" if below 10%
            "low" if below 20%
            None if healthy
        """
        reserves = self.get_reserve_percentage()
        min_reserve = min(reserves["flx_pct"], reserves["chr_pct"])

        if min_reserve < self.CRITICAL_RESERVE_THRESHOLD:
            return "critical"
        elif min_reserve < self.LOW_RESERVE_THRESHOLD:
            return "low"
        return None

    def pay_bounty(
        self,
        bounty_id: str,
        contributor: str,
        flx: BigNum128,
        chr: BigNum128,
        pr_number: int,
        commit_hash: str,
        verifier: str,
    ) -> EconomicEvent:
        """
        Pay bounty from treasury (deterministic).

        Args:
            bounty_id: Unique bounty identifier
            contributor: Recipient wallet address
            flx: FLX amount to pay
            chr: CHR amount to pay
            pr_number: GitHub PR number
            commit_hash: Git commit hash
            verifier: Wallet address of verifier

        Returns:
            EconomicEvent for ledger

        Raises:
            InsufficientTreasuryError: If treasury cannot pay
        """
        if not self.can_pay(flx, chr):
            raise InsufficientTreasuryError(
                f"Treasury cannot pay {flx} FLX + {chr} CHR. "
                f"Available: {self.flx_reserve} FLX + {self.chr_reserve} CHR"
            )

        # Deduct from reserves
        self.flx_reserve = BigNum128(self.flx_reserve.value - flx.value)
        self.chr_reserve = BigNum128(self.chr_reserve.value - chr.value)
        self.total_paid_flx = BigNum128(self.total_paid_flx.value + flx.value)
        self.total_paid_chr = BigNum128(self.total_paid_chr.value + chr.value)

        # Record payment
        from .bounty_events import get_deterministic_timestamp

        payment = TreasuryPayment(
            bounty_id=bounty_id,
            contributor=contributor,
            flx_amount=flx,
            chr_amount=chr,
            timestamp=get_deterministic_timestamp(),
            pr_number=pr_number,
            commit_hash=commit_hash,
        )
        self.payment_history.append(payment)

        # Check depletion status
        status = self.check_depletion_status()
        if status == "critical":
            logger.warning(f"CRITICAL: Treasury reserves below 10%!")
        elif status == "low":
            logger.warning(f"WARNING: Treasury reserves below 20%")

        # Emit economic event
        return emit_bounty_paid_event(
            bounty_id=bounty_id,
            contributor_wallet=contributor,
            pr_number=pr_number,
            commit_hash=commit_hash,
            flx_amount=flx,
            chr_amount=chr,
            verifier=verifier,
        )

    def refill(
        self,
        flx_amount: BigNum128,
        chr_amount: BigNum128,
        authorized_by: str,
        reason: str,
    ) -> EconomicEvent:
        """
        Refill treasury (requires governance approval).

        Args:
            flx_amount: FLX to add
            chr_amount: CHR to add
            authorized_by: Governance authority
            reason: Refill justification

        Returns:
            EconomicEvent for ledger
        """
        self.flx_reserve = BigNum128(self.flx_reserve.value + flx_amount.value)
        self.chr_reserve = BigNum128(self.chr_reserve.value + chr_amount.value)

        # Record refill
        from .bounty_events import get_deterministic_timestamp

        self.refill_history.append(
            {
                "flx_added": flx_amount.to_decimal_string(),
                "chr_added": chr_amount.to_decimal_string(),
                "authorized_by": authorized_by,
                "reason": reason,
                "timestamp": get_deterministic_timestamp(),
            }
        )

        return emit_treasury_refill_event(
            treasury_id=self.treasury_id,
            flx_added=flx_amount,
            chr_added=chr_amount,
            authorized_by=authorized_by,
            reason=reason,
        )

    def get_stats(self) -> Dict:
        """Get treasury statistics"""
        reserves = self.get_reserve_percentage()

        return {
            "treasury_id": self.treasury_id,
            "reserves": {
                "flx": self.flx_reserve.to_decimal_string(),
                "chr": self.chr_reserve.to_decimal_string(),
                "flx_pct": reserves["flx_pct"],
                "chr_pct": reserves["chr_pct"],
            },
            "total_paid": {
                "flx": self.total_paid_flx.to_decimal_string(),
                "chr": self.total_paid_chr.to_decimal_string(),
            },
            "payments_count": len(self.payment_history),
            "refills_count": len(self.refill_history),
            "status": self.check_depletion_status() or "healthy",
        }

    def to_dict(self) -> Dict:
        """Serialize to dictionary for storage"""
        return {
            "treasury_id": self.treasury_id,
            "flx_reserve": self.flx_reserve.to_decimal_string(),
            "chr_reserve": self.chr_reserve.to_decimal_string(),
            "total_paid_flx": self.total_paid_flx.to_decimal_string(),
            "total_paid_chr": self.total_paid_chr.to_decimal_string(),
            "payment_history": [
                {
                    **asdict(p),
                    "flx_amount": p.flx_amount.to_decimal_string(),
                    "chr_amount": p.chr_amount.to_decimal_string(),
                }
                for p in self.payment_history
            ],
            "refill_history": self.refill_history,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "DevRewardsTreasury":
        """Deserialize from dictionary"""
        payment_history = []
        for p in data.get("payment_history", []):
            p["flx_amount"] = BigNum128.from_string(str(p["flx_amount"]))
            p["chr_amount"] = BigNum128.from_string(str(p["chr_amount"]))
            payment_history.append(TreasuryPayment(**p))

        return cls(
            treasury_id=data.get("treasury_id", "dev_rewards_v1"),
            flx_reserve=BigNum128.from_string(str(data["flx_reserve"])),
            chr_reserve=BigNum128.from_string(str(data["chr_reserve"])),
            total_paid_flx=BigNum128.from_string(str(data.get("total_paid_flx", "0"))),
            total_paid_chr=BigNum128.from_string(str(data.get("total_paid_chr", "0"))),
            payment_history=payment_history,
            refill_history=data.get("refill_history", []),
        )

    def save_to_file(self, filepath: str):
        """Save treasury state to JSON file"""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, filepath: str) -> "DevRewardsTreasury":
        """Load treasury state from JSON file"""
        with open(filepath, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)
