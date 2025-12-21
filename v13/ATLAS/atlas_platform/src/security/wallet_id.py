import hashlib

def wallet_to_user_id(wallet_address: str) -> str:
    """
    Generate immutable, deterministic user ID from wallet.
    
    CRITICAL: This mapping is permanent. Once assigned, it cannot change.
    Referral trees and coherence scores depend on ID stability.
    
    Args:
        wallet_address: The Ethereum-style wallet address (0x...)
        
    Returns:
        str: A deterministic user ID in format 'user_{hash}'
    """
    if not wallet_address:
        raise ValueError('Wallet address cannot be empty')
    canonical = wallet_address.lower().strip()
    if hasattr(hashlib, 'sha3_256'):
        hash_bytes = hashlib.sha3_256(canonical.encode()).digest()
    else:
        hash_bytes = hashlib.sha256(canonical.encode()).digest()
    return f'user_{hash_bytes[:16].hex()}'