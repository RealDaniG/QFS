import logging
from eth_account.messages import encode_defunct
from eth_account import Account
logger = logging.getLogger(__name__)

def verify_signature(wallet: str, nonce: str, signature: str) -> bool:
    try:
        message = encode_defunct(text=nonce)
        recovered_address = Account.recover_message(message, signature=signature)
        return recovered_address.lower() == wallet.lower()
    except Exception as e:
        logger.error(f'Signature verification failed: {e}')
        return False