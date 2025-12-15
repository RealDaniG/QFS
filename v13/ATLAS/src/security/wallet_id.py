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
        raise ValueError("Wallet address cannot be empty")
        
    # Normalize to lowercase and strip whitespace for canonical input
    canonical = wallet_address.lower().strip()
    
    # Use SHA3-256 for collision resistance and quantum readiness
    # (or standard SHA256 if SHA3 not available in standard lib, but python 3.6+ has hashlib.sha3_256)
    if hasattr(hashlib, 'sha3_256'):
        hash_bytes = hashlib.sha3_256(canonical.encode()).digest()
    else:
        # Fallback for environments without SHA3 (rare in Python 3.10+)
        hash_bytes = hashlib.sha256(canonical.encode()).digest()
        
    return f"user_{hash_bytes[:16].hex()}"
