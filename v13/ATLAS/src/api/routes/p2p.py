from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Optional
import hashlib


from ..dependencies import get_current_user, get_evidence_bus, EvidenceBus


router = APIRouter()


@router.get("/session")
async def get_p2p_session(
    space_id: str = Query(..., description="Target Space ID"),
    current_user: Dict = Depends(get_current_user),
    bus: EvidenceBus = Depends(get_evidence_bus),
):
    """
    Get session parameters for P2P connection.
    Returns nonce and head hash to allow client to derive session key.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    wallet_address = current_user.get("wallet_address")

    # 1. Get Evidence Head
    head_hash = await bus.get_head_hash()

    # 2. Generate Deterministic Nonce (Stateless for v14)
    # In full v20, this might be a random value stored in Redis.
    # For now, we use a deterministic hash of (wallet + space) to ensure
    # the backend can re-derive it without state.
    # Deterministic nonce (SHA3-256, 16 bytes) - v19 Standard
    nonce_input = f"{wallet_address}:{space_id}".encode()
    session_nonce = hashlib.sha3_256(nonce_input).digest()[:16]
    session_nonce_hex = session_nonce.hex()

    return {
        "space_id": space_id,
        "session_nonce": session_nonce_hex,
        "evidence_head": head_hash,
        "wallet_address": wallet_address,
    }


# --- P2P WebSocket Gateway ---
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
from backend.lib.message_envelope import EnvelopeFactory, MessageEnvelope
import json


class ConnectionManager:
    def __init__(self):
        # Map space_id -> List[WebSocket]
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, space_id: str):
        await websocket.accept()
        if space_id not in self.active_connections:
            self.active_connections[space_id] = []
        self.active_connections[space_id].append(websocket)

    def disconnect(self, websocket: WebSocket, space_id: str):
        if space_id in self.active_connections:
            if websocket in self.active_connections[space_id]:
                self.active_connections[space_id].remove(websocket)

    async def broadcast(self, message: str, space_id: str, sender: WebSocket):
        if space_id in self.active_connections:
            for connection in self.active_connections[space_id]:
                if connection != sender:
                    await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/{space_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    space_id: str,
    bus: EvidenceBus = Depends(get_evidence_bus),
):
    await manager.connect(websocket, space_id)
    try:
        while True:
            data = await websocket.receive_text()

            # 1. Parse Envelope
            try:
                envelope_dict = json.loads(data)
                envelope = MessageEnvelope(**envelope_dict)
            except Exception as e:
                print(f"Invalid envelope: {e}")
                continue

            # 2. Verify Signature (MOCKQPC)
            try:
                sender_pub_bytes = bytes.fromhex(envelope.sender_pubkey)
                is_valid = EnvelopeFactory.verify_envelope(envelope, sender_pub_bytes)

                if not is_valid:
                    print(
                        f"Signature verification failed for {envelope.sender_pubkey[:8]}..."
                    )
                    continue

                # 3. Commit to EvidenceBus
                event = {
                    "type": "p2p.message_received",
                    "space_id": space_id,
                    "sender": envelope.sender_pubkey,
                    "payload_hash": envelope.payload_hash,
                    "signature": envelope.signature,
                }
                await bus.commit_event(event)

            except Exception as e:
                print(f"Verification error: {e}")
                continue

            # 4. Broadcast
            await manager.broadcast(data, space_id, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket, space_id)
