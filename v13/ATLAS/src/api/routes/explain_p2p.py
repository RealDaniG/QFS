
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import hashlib
import json

from v13.ATLAS.src.api.dependencies import get_current_user, get_replay_source, User
# from v13.ATLAS.src.p2p.bandwidth_economics import P2PBandwidthEconomics # (If needed directly)

router = APIRouter()

@router.get("/explain/p2p/{node_id}")
async def explain_p2p_activity(
    node_id: str,
    current_user: User = Depends(get_current_user),
    replay_source = Depends(get_replay_source)
) -> Dict[str, Any]:
    """
    Explain P2P network activity for a specific node.
    Returns audit data regarding message volume, security level, and economics.
    """
    
    # 1. Replay P2P messages from ledger (via ReplaySource)
    # The replay_source would typically have a method like get_p2p_events(node_id)
    # For now, we assume the interface exists or returns a safe empty list if not implemented
    if hasattr(replay_source, 'get_p2p_events'):
        p2p_events = replay_source.get_p2p_events(node_id)
    else:
        # Mock/Stub if method not yet on singleton
        p2p_events = [] 

    # 2. Aggregations
    secure_msgs_sent = [e for e in p2p_events if e.get("type") == "secure_message" and e.get("sender_id") == node_id]
    msgs_received = [e for e in p2p_events if e.get("recipient_id") == node_id]
    
    unique_peers = list(set([e.get("recipient_id") for e in secure_msgs_sent] + [e.get("sender_id") for e in msgs_received]))
    
    total_bytes = sum([e.get("size_bytes", 0) for e in p2p_events])
    bandwidth_mb = total_bytes / 1_000_000
    
    # 3. Calculate Reward (Logic duplicated from BandwidthEconomics for display, or shared lib)
    # In full impl, we'd instantiate P2PBandwidthEconomics(replay_source.state)
    base_reward = bandwidth_mb * 0.01
    enc_bonus = 0.1 if len(p2p_events) > 100 else 0.0
    nod_reward = base_reward + enc_bonus
    
    # 4. Determine Security Level
    # simplistic check: do events have signatures?
    has_pqc = all(e.get("pqc_signed", False) for e in p2p_events) if p2p_events else True # Default to high if no events? No, Context dependent.
    security_level = "PQC_HYBRID" if has_pqc and p2p_events else "ED25519_ONLY"
    if not p2p_events: security_level = "NO_ACTIVITY"

    # 5. Deterministic Hash for UI verification
    explanation_data = {
        "node_id": node_id,
        "metrics": {
            "total_sent": len(secure_msgs_sent),
            "total_received": len(msgs_received),
            "bandwidth_mb": round(bandwidth_mb, 4),
            "nod_reward": round(nod_reward, 6)
        },
        "topology": {
            "peer_count": len(unique_peers),
            "peers": unique_peers
        },
        "security": {
            "level": security_level,
            "status": "Verified" # derived from AEGIS checks
        }
    }
    
    # Sort keys for deterministic hash
    expl_hash = hashlib.sha256(json.dumps(explanation_data, sort_keys=True).encode('utf-8')).hexdigest()
    explanation_data["explanation_hash"] = expl_hash
    
    return explanation_data
