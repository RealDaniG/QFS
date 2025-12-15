
import time
import base64
from typing import Dict, Any

# We expect CryptoEngine to be passed in, or we could import the type for hinting if available
# from v13.core.dependencies import CryptoEngine 

def sign_discovery_announcement(node_id: str, crypto) -> Dict[str, Any]:
    """
    Sign node discovery with Ed25519 (or configured scheme).
    
    Args:
        node_id: The identifier of the node announcing itself.
        crypto: The authorized CryptoEngine instance.
        
    Returns:
        Dict containing signed announcement payload.
    """
    payload = node_id.encode('utf-8')
    signature = crypto.sign_data(payload)
    
    # Export public key to include in announcement for verification
    # Assuming crypto.identity follows the Open-A.G.I interface
    public_key = crypto.identity.export_public_identity()['signing_key']
    
    return {
        'node_id': node_id,
        'public_key': base64.b64encode(public_key).decode('utf-8'),
        'signature': base64.b64encode(signature).decode('utf-8'),
        'timestamp': int(time.time())
    }
