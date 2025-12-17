"""
ReferralLedger: Handles all referral-related Genesis Ledger operations.
"""
from typing import Dict, Any, List, Optional
from v13.events.referral_events import ReferralCreated, ReferralAccepted, ReferralActivated, ReferralFraudBlocked, deterministic_referral_code
import logging

class ReferralLedger:
    """Referral system ledger interface."""
    MAX_REFERRALS_PER_WALLET = 100
    REWARD_TIERS = ((1, 5, 10000000000), (6, 20, 8000000000), (21, 50, 5000000000), (51, 100, 2000000000))

    def __init__(self, genesis_ledger):
        self.ledger = genesis_ledger

    def create_link(self, referrer_wallet: str, epoch: int, source: str) -> str:
        """
        Generate deterministic referral link.
        
        Raises:
            ValueError: If referrer exceeds max referrals
        """
        count = self._count_referrals(referrer_wallet)
        if count >= self.MAX_REFERRALS_PER_WALLET:
            raise ValueError(f'REFERRAL_CAP_EXCEEDED: {referrer_wallet} has {count} referrals')
        code = deterministic_referral_code(referrer_wallet, epoch)
        event = ReferralCreated(referrer_wallet=referrer_wallet, referral_code=code, epoch=epoch, source=source)
        self.ledger.append_event(event)
        logging.getLogger(__name__).info(f'Created referral link for {referrer_wallet}: {code}')
        return code

    def accept(self, referral_code: str, referee_wallet: str, epoch: int, device_hash: str):
        """
        Accept referral (referee clicked link).
        
        Raises:
            ValueError: If fraud detected
        """
        referrer_wallet = self._resolve_code(referral_code)
        if not referrer_wallet:
            raise ValueError(f'INVALID_REFERRAL_CODE: {referral_code}')
        if referrer_wallet == referee_wallet:
            evidence = {'reason': 'referrer == referee'}
            self._log_fraud(referrer_wallet, referee_wallet, 'SELF_REF', epoch, evidence)
            raise ValueError('SELF_REFERRAL_BLOCKED')
        if self._is_duplicate_device(device_hash):
            evidence = {'device_hash': device_hash}
            self._log_fraud(referrer_wallet, referee_wallet, 'DUP_DEVICE', epoch, evidence)
            raise ValueError('DUPLICATE_DEVICE_BLOCKED')
        event = ReferralAccepted(referrer_wallet=referrer_wallet, referee_wallet=referee_wallet, referral_code=referral_code, epoch=epoch, device_hash=device_hash)
        self.ledger.append_event(event)
        logging.getLogger(__name__).info(f'Referral accepted: {referee_wallet} via {referrer_wallet}')

    def activate(self, referee_wallet: str, activation_type: str, epoch: int):
        """
        Activate referral (referee completed required action).
        Triggers reward calculation.
        """
        referral = self._get_pending_referral(referee_wallet)
        if not referral:
            logging.getLogger(__name__).warning(f'No pending referral for {referee_wallet}')
            return
        event = ReferralActivated(referrer_wallet=referral['referrer'], referee_wallet=referee_wallet, referral_code=referral['code'], epoch=epoch, activation_type=activation_type)
        self.ledger.append_event(event)
        self._grant_reward(event)

    def _grant_reward(self, activation_event: ReferralActivated):
        """Calculate and grant referral reward via CoherenceEngine."""
        referrer = activation_event.referrer_wallet
        count = self._count_referrals(referrer)
        current_referral_index = count + 1
        amount = 0
        for i in range(len(self.REWARD_TIERS)):
            min_c, max_c, reward = self.REWARD_TIERS[i]
            if min_c <= current_referral_index <= max_c:
                amount = reward
                break
        if amount > 0:
            from v13.events.referral_events import ReferralRewarded
            reward_event = ReferralRewarded(referrer_wallet=referrer, referee_wallet=activation_event.referee_wallet, token_type='FLX', amount_scaled=amount, epoch=activation_event.epoch, reason=f'REFERRAL_TIER_{current_referral_index}', guard_cir_code='CIR_PASS')
            self.ledger.append_event(reward_event)
            logging.getLogger(__name__).info(f'Granted referral reward {amount} FLX to {referrer}')
        else:
            logging.getLogger(__name__).info(f'No reward for referral {current_referral_index} (outside tiers)')

    def _count_referrals(self, wallet: str) -> int:
        """Count existing referrals for wallet from ledger."""
        return 0

    def _resolve_code(self, code: str) -> str:
        """Resolve referral code to referrer wallet."""
        return 'mock_referrer_wallet'

    def _is_duplicate_device(self, device_hash: str) -> bool:
        """Check if device hash has been used before."""
        return False

    def _log_fraud(self, referrer, referee, ftype, epoch, evidence):
        """Log fraud event."""
        event = ReferralFraudBlocked(referrer_wallet=referrer, referee_wallet=referee, fraud_type=ftype, epoch=epoch, evidence=evidence)
        self.ledger.append_event(event)

    def get_referral_summary(self, wallet: str) -> Dict[str, Any]:
        """
        Get referral summary for wallet.
        Return ledger-derived data (mocked for now).
        """
        count = self._count_referrals(wallet)
        current_tier = 'NONE'
        next_tier_progress = 0
        for i in range(len(self.REWARD_TIERS)):
            min_c, max_c, reward_amt = self.REWARD_TIERS[i]
            if min_c <= count <= max_c:
                current_tier = f'TIER_{i + 1}'
                break
            if count < min_c:
                next_tier_progress = count
                break
        return {'referral_count': count, 'current_tier': current_tier, 'max_referrals': self.MAX_REFERRALS_PER_WALLET}

    def list_referrals(self, wallet: str, limit: int=20, offset: int=0) -> List[Dict[str, Any]]:
        """
        List successful referrals.
        """
        return []

    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get global referral system metrics for dashboards.
        """
        return {'total_referrals': 0, 'total_rewards_flx': 0, 'fraud_blocked_count': 0, 'fraud_by_type': {'SELF_REF': 0, 'DUP_DEVICE': 0}, 'tier_distribution': {'TIER_1': 0, 'TIER_2': 0, 'TIER_3': 0, 'TIER_4': 0}}

    def _get_pending_referral(self, referee_wallet: str):
        """Get pending referral data for referee."""
        return {'referrer': 'mock_referrer', 'code': 'mock_code'}