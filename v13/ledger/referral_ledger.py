"""
ReferralLedger: Handles all referral-related Genesis Ledger operations.
"""


from typing import Dict, Any, List, Optional
from v13.events.referral_events import (
    ReferralCreated, ReferralAccepted, ReferralActivated, 
    ReferralFraudBlocked, deterministic_referral_code
)
# from v13.ledger.genesis_ledger import GenesisLedger # Assuming this exists or using mock
import logging

# logger = logging.getLogger(__name__)

class ReferralLedger:
    """Referral system ledger interface."""
    
    # Constants (immutable)
    MAX_REFERRALS_PER_WALLET = 100
    # Tier structure: (min_count, max_count, reward_amount)
    REWARD_TIERS = (
        (1, 5, 10_000_000_000),    # Referrals 1-5: 100 FLX
        (6, 20, 8_000_000_000),    # Referrals 6-20: 80 FLX
        (21, 50, 5_000_000_000),   # Referrals 21-50: 50 FLX
        (51, 100, 2_000_000_000),  # Referrals 51-100: 20 FLX
    )
    
    def __init__(self, genesis_ledger):
        self.ledger = genesis_ledger
    
    def create_link(self, referrer_wallet: str, epoch: int, source: str) -> str:
        """
        Generate deterministic referral link.
        
        Raises:
            ValueError: If referrer exceeds max referrals
        """
        # Check cap
        count = self._count_referrals(referrer_wallet)
        if count >= self.MAX_REFERRALS_PER_WALLET:
            raise ValueError(f"REFERRAL_CAP_EXCEEDED: {referrer_wallet} has {count} referrals")
        
        # Generate deterministic code
        code = deterministic_referral_code(referrer_wallet, epoch)
        
        # Create event
        event = ReferralCreated(
            referrer_wallet=referrer_wallet,
            referral_code=code,
            epoch=epoch,
            source=source
        )
        
        # Append to ledger
        self.ledger.append_event(event)
        
        logging.getLogger(__name__).info(f"Created referral link for {referrer_wallet}: {code}")
        return code
    
    def accept(
        self, 
        referral_code: str, 
        referee_wallet: str, 
        epoch: int,
        device_hash: str
    ):
        """
        Accept referral (referee clicked link).
        
        Raises:
            ValueError: If fraud detected
        """
        # Resolve referrer from code
        referrer_wallet = self._resolve_code(referral_code)
        
        if not referrer_wallet:
            raise ValueError(f"INVALID_REFERRAL_CODE: {referral_code}")
        
        # Anti-fraud: Self-referral
        if referrer_wallet == referee_wallet:
            evidence = {"reason": "referrer == referee"}
            # Ensure dict is sorted if needed, but here it's simple
            self._log_fraud(
                referrer_wallet, referee_wallet, "SELF_REF", epoch, evidence
            )
            raise ValueError("SELF_REFERRAL_BLOCKED")
        
        # Anti-fraud: Duplicate device
        if self._is_duplicate_device(device_hash):
            evidence = {"device_hash": device_hash}
            self._log_fraud(
                referrer_wallet, referee_wallet, "DUP_DEVICE", epoch, evidence
            )
            raise ValueError("DUPLICATE_DEVICE_BLOCKED")
        
        # Accept
        event = ReferralAccepted(
            referrer_wallet=referrer_wallet,
            referee_wallet=referee_wallet,
            referral_code=referral_code,
            epoch=epoch,
            device_hash=device_hash
        )
        
        self.ledger.append_event(event)
        logging.getLogger(__name__).info(f"Referral accepted: {referee_wallet} via {referrer_wallet}")
    
    def activate(
        self,
        referee_wallet: str,
        activation_type: str,
        epoch: int
    ):
        """
        Activate referral (referee completed required action).
        Triggers reward calculation.
        """
        # Find pending referral
        referral = self._get_pending_referral(referee_wallet)
        
        if not referral:
            logging.getLogger(__name__).warning(f"No pending referral for {referee_wallet}")
            return
        
        # Activate
        event = ReferralActivated(
            referrer_wallet=referral['referrer'],
            referee_wallet=referee_wallet,
            referral_code=referral['code'],
            epoch=epoch,
            activation_type=activation_type
        )
        
        self.ledger.append_event(event)
        
        # Calculate and grant reward
        self._grant_reward(event)
    
    def _grant_reward(self, activation_event: ReferralActivated):
        """Calculate and grant referral reward via CoherenceEngine."""
        referrer = activation_event.referrer_wallet
        count = self._count_referrals(referrer)
        
        # Determine reward amount based on tier (using current count + 1 as this is the new one? 
        # Actually _count_referrals might include this one if created? 
        # Typically we count *prior* successful referrals. Let's assume count is prior.
        # So this is the (count + 1)th referral.
        current_referral_index = count + 1
        
        amount = 0
        # Use range(len()) for deterministic iteration over tuple
        for i in range(len(self.REWARD_TIERS)):
            min_c, max_c, reward = self.REWARD_TIERS[i]
            if min_c <= current_referral_index <= max_c:
                amount = reward
                break
        
        if amount > 0:
            from v13.events.referral_events import ReferralRewarded
            
            reward_event = ReferralRewarded(
                referrer_wallet=referrer,
                referee_wallet=activation_event.referee_wallet,
                token_type="FLX",
                amount_scaled=amount,
                epoch=activation_event.epoch,
                reason=f"REFERRAL_TIER_{current_referral_index}",
                guard_cir_code="CIR_PASS" # Placeholder for actual guard validation
            )
            
            self.ledger.append_event(reward_event)
            logging.getLogger(__name__).info(f"Granted referral reward {amount} FLX to {referrer}")
        else:
            logging.getLogger(__name__).info(f"No reward for referral {current_referral_index} (outside tiers)")

    def _count_referrals(self, wallet: str) -> int:
        """Count existing referrals for wallet from ledger."""
        # In a real impl, this would query the ledger index
        # For now, return 0 or mock
        return 0

    def _resolve_code(self, code: str) -> str:
        """Resolve referral code to referrer wallet."""
        # Query ledger index
        # Mock for now
        return "mock_referrer_wallet"

    def _is_duplicate_device(self, device_hash: str) -> bool:
        """Check if device hash has been used before."""
        return False
        
    def _log_fraud(self, referrer, referee, ftype, epoch, evidence):
        """Log fraud event."""
        event = ReferralFraudBlocked(
            referrer_wallet=referrer,
            referee_wallet=referee,
            fraud_type=ftype,
            epoch=epoch,
            evidence=evidence
        )
        self.ledger.append_event(event)
        
    def get_referral_summary(self, wallet: str) -> Dict[str, Any]:
        """
        Get referral summary for wallet.
        Return ledger-derived data (mocked for now).
        """
        count = self._count_referrals(wallet)
        # Calculate current tier
        current_tier = "NONE"
        next_tier_progress = 0
        
        # Use range(len()) for deterministic iteration
        for i in range(len(self.REWARD_TIERS)):
            min_c, max_c, reward_amt = self.REWARD_TIERS[i]
            if min_c <= count <= max_c:
                current_tier = f"TIER_{i+1}"
                break
            if count < min_c:
                # Assuming tiers are ordered
                next_tier_progress = count
                break
                
        return {
            "referral_count": count,
            "current_tier": current_tier,
            "max_referrals": self.MAX_REFERRALS_PER_WALLET
        }

    def list_referrals(self, wallet: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List successful referrals.
        """
        # In real impl, query ledger for ReferralActivated/ReferralRewarded events where referrer_wallet == wallet
        # For now return empty list
        return []

    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get global referral system metrics for dashboards.
        """
        # In real impl, aggregate from ledger events
        # returning mock structure for now
        return {
             "total_referrals": 0,
             "total_rewards_flx": 0,
             "fraud_blocked_count": 0,
             "fraud_by_type": {
                 "SELF_REF": 0,
                 "DUP_DEVICE": 0
             },
             "tier_distribution": {
                 "TIER_1": 0,
                 "TIER_2": 0,
                 "TIER_3": 0,
                 "TIER_4": 0
             }
        }

    def _get_pending_referral(self, referee_wallet: str):
        """Get pending referral data for referee."""
        # Mock
        return {"referrer": "mock_referrer", "code": "mock_code"}


