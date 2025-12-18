from typing import Dict, Any, List, Optional
import logging
from v13.ledger.referral_ledger import ReferralLedger

class ReferralHandler:
    """
    Handler for Referral System API endpoints.
    Delegates to ReferralLedger for authoritative state.
    """

    def __init__(self, referral_ledger: ReferralLedger):
        self.ledger = referral_ledger

    async def create_referral_link(self, wallet: str, epoch: int, source: str) -> Dict[str, Any]:
        """
        Create a new referral link.
        POST /referral/create
        """
        try:
            code = self.ledger.create_link(wallet, epoch, source)
            return {'success': True, 'referral_code': code, 'wallet': wallet, 'epoch': epoch}
        except ValueError as e:
            logging.getLogger(__name__).warning(f'Create link failed: {str(e)}')
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logging.getLogger(__name__).error(f'Internal error creating link: {str(e)}')
            return {'success': False, 'error': 'Internal Server Error'}

    async def get_referral_status(self, wallet: str) -> Dict[str, Any]:
        """
        Get referral status for a wallet.
        GET /referral/status
        """
        try:
            summary = self.ledger.get_referral_summary(wallet)
            return {'success': True, 'data': summary}
        except Exception as e:
            logging.getLogger(__name__).error(f'Error fetching referral status: {str(e)}')
            return {'success': False, 'error': str(e)}

    async def list_referrals(self, wallet: str, limit: int=20, offset: int=0) -> Dict[str, Any]:
        """
        List successful referrals for a wallet.
        GET /referral/list
        """
        try:
            referrals = self.ledger.list_referrals(wallet, limit, offset)
            return {'success': True, 'data': referrals}
        except Exception as e:
            logging.getLogger(__name__).error(f'Error listing referrals: {str(e)}')
            return {'success': False, 'error': str(e)}
