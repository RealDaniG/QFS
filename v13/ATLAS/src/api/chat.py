
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status
from typing import Dict, List
import json
import logging
from datetime import datetime, timezone
import uuid

from v13.ATLAS.src.api.auth import verify_signature # Or JWT decode logic
from v13.ATLAS.src.models.user import UserProfile
from v13.integrations.event_bridge import get_event_bridge, EventBridge
from v13.ledger.genesis_ledger import GenesisLedger # Direct ledger access for V1 replay

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/chat", tags=["chat"])

# Connection Manager
class ConnectionManager:
    def __init__(self):
        # wallet -> list of websockets (multi-device support)
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, start_websocket: WebSocket, wallet: str):
        await start_websocket.accept()
        if wallet not in self.active_connections:
            self.active_connections[wallet] = []
        self.active_connections[wallet].append(start_websocket)
        logger.info(f"Wallet {wallet} connected. Total devices: {len(self.active_connections[wallet])}")

    def disconnect(self, websocket: WebSocket, wallet: str):
        if wallet in self.active_connections:
            if websocket in self.active_connections[wallet]:
                self.active_connections[wallet].remove(websocket)
            if not self.active_connections[wallet]:
                del self.active_connections[wallet]

    async def send_personal_message(self, message: dict, wallet: str):
        if wallet in self.active_connections:
            # Broadcast to all devices of this user
            dead_sockets = []
            for connection in self.active_connections[wallet]:
                try:
                    await connection.send_json(message)
                except Exception:
                    dead_sockets.append(connection)
            
            # Cleanup dead sockets
            for ds in dead_sockets:
                self.disconnect(ds, wallet)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """
    Real-time chat WebSocket.
    Authentication via Query Param 'token' (JWT).
    """
    # 1. Verify Token (stub logic using decoding, ideally use PyJWT verify)
    try:
        # In PROD: jwt.decode(token, SECRET, algorithms=[ALGO])
        # For V1 MVP/Demo compatibility with Auth logic:
        import jwt
        from v13.ATLAS.src.api.auth import JWT_SECRET, JWT_ALGORITHM
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        wallet = payload.get("sub")
        
        if not wallet:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
            
    except Exception as e:
        logger.error(f"WS Auth failed: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 2. Accept Connection
    await manager.connect(websocket, wallet)
    
    try:
        while True:
            # 3. Receive Message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Expecting: {recipient: "0x...", ciphertext: "...", timestamp: "..."}
            recipient = message_data.get("recipient")
            ciphertext = message_data.get("ciphertext")
            
            if recipient and ciphertext:
                # 4. Construct Payload
                event_id = str(uuid.uuid4())
                timestamp = datetime.now(timezone.utc).isoformat()
                
                payload = {
                    "id": event_id,
                    "sender": wallet,
                    "recipient": recipient,
                    "ciphertext": ciphertext,
                    "timestamp": timestamp,
                    "type": "CHAT_MESSAGE"
                }
                
                # 5. Send to Recipient (if online)
                await manager.send_personal_message(payload, recipient)
                
                # 6. Echo back to Sender (for other devices / confirmation)
                await manager.send_personal_message(payload, wallet)
                
                # 7. Persist via EventBridge (Async)
                # In V2 this calls Redis. V1 calls Ledger if Bridge initialized.
                try:
                    # Generic logger usage, signature assumed handled by client wrapper or skipped for V1 Chat MVP 
                    # (Chat often doesn't sign every msg on ledger for scalability, but V1 roadmap says "Log to Genesis")
                    # We'll log a simplified event
                    bridge = get_event_bridge() # Must be initialized at app startup
                    bridge.publish_event(
                        event_type="MESSAGE",
                        wallet=wallet,
                        metadata={"recipient": recipient, "msg_id": event_id},
                        signature="client_sig_placeholder" # Client should send this
                    )
                except Exception as e:
                    logger.warning(f"Failed to persist chat event: {e}")

    except WebSocketDisconnect:
        manager.disconnect(websocket, wallet)

@router.get("/threads")
async def list_threads(token: str):
    """
    List active chat threads by replaying the Genesis Ledger.
    Returns unique list of peers communicated with.
    """
    # 1. Auth (simplification: reuse token logic or dependency)
    # Ideally use Depends(get_current_user) but we kept it raw in WS example.
    # We will assume a valid token is passed as query or header.
    # For V1 MVP, we parse it manually here to match existing style.
    try:
        import jwt
        from v13.ATLAS.src.api.auth import JWT_SECRET, JWT_ALGORITHM
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        current_wallet = payload.get("sub")
    except:
        # If token fails, return empty structure or 401
        return []

    # 2. Replay Ledger
    # In V2, query a database projection.
    # In V1 Zero-Sim, we scan the file.
    ledger = GenesisLedger("genesis_ledger.jsonl")
    # Optimize: Read backwards or index?
    # Simple scan:
    threads = {} # peer_wallet -> {last_ts, last_msg}
    
    # We need to expose a generator or list from ledger
    # Assuming ledger.replay_events() returns iterable
    # We'll read the file raw if replay_events prints to stdout, 
    # but let's assume we can access raw storage for this service.
    # Let's use the public API if possible.
    # If not exposed, we iterate the file directly here as a service extension.
    
    if os.path.exists(ledger.filepath):
        with open(ledger.filepath, 'r') as f:
            for line in f:
                try:
                    evt = json.loads(line)
                    if evt.get("type") != "MESSAGE":
                        continue
                        
                    meta = evt.get("metadata", {})
                    sender = evt.get("wallet") # The one who signed
                    recipient = meta.get("recipient")
                    
                    if sender == current_wallet:
                        peer = recipient
                    elif recipient == current_wallet:
                        peer = sender
                    else:
                        continue # Not my message
                        
                    if peer:
                        # Keep latest
                        ts = evt.get("timestamp")
                        threads[peer] = {
                            "peer": peer,
                            "last_active": ts,
                            "msg_id": meta.get("msg_id")
                        }
                except:
                    continue

    return list(threads.values())

