from fractions import Fraction
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import hashlib
import json
from v13.ATLAS.src.api.dependencies import get_current_user, get_replay_source, User
router = APIRouter()

@router.get('/explain/p2p/{node_id}')
async def explain_p2p_activity(node_id: str, current_user: User=Depends(get_current_user), replay_source=Depends(get_replay_source)) -> Dict[str, Any]:
    """
    Explain P2P network activity for a specific node.
    Returns audit data regarding message volume, security level, and economics.
    """
    if hasattr(replay_source, 'get_p2p_events'):
        p2p_events = replay_source.get_p2p_events(node_id)
    else:
        p2p_events = []
    secure_msgs_sent = [e for e in p2p_events if e.get('type') == 'secure_message' and e.get('sender_id') == node_id]
    msgs_received = [e for e in p2p_events if e.get('recipient_id') == node_id]
    unique_peers = list(set([e.get('recipient_id') for e in secure_msgs_sent] + [e.get('sender_id') for e in msgs_received]))
    total_bytes = sum([e.get('size_bytes', 0) for e in p2p_events])
    bandwidth_mb = total_bytes / 1000000
    base_reward = bandwidth_mb * Fraction(1, 100)
    enc_bonus = Fraction(1, 10) if len(p2p_events) > 100 else 0
    nod_reward = base_reward + enc_bonus
    has_pqc = all((e.get('pqc_signed', False) for e in p2p_events)) if p2p_events else True
    security_level = 'PQC_HYBRID' if has_pqc and p2p_events else 'ED25519_ONLY'
    if not p2p_events:
        security_level = 'NO_ACTIVITY'
    explanation_data = {'node_id': node_id, 'metrics': {'total_sent': len(secure_msgs_sent), 'total_received': len(msgs_received), 'bandwidth_mb': round(bandwidth_mb, 4), 'nod_reward': round(nod_reward, 6)}, 'topology': {'peer_count': len(unique_peers), 'peers': unique_peers}, 'security': {'level': security_level, 'status': 'Verified'}}
    expl_hash = hashlib.sha256(json.dumps(explanation_data, sort_keys=True).encode('utf-8')).hexdigest()
    explanation_data['explanation_hash'] = expl_hash
    return explanation_data