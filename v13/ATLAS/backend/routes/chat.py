from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List
from lib.dependencies import get_current_user

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# Simple in-memory message store
messages = []
active_connections: List[WebSocket] = []


@router.get("/messages")
async def get_messages(
    room_id: str = "general", wallet_address: str = Depends(get_current_user)
):
    """Get chat messages for room."""
    return {
        "messages": [
            {
                "id": "msg_001",
                "room_id": room_id,
                "author": "0x742d35Cc...",
                "content": "Welcome to ATLAS v18 Beta!",
                "timestamp": 1703174400,
            }
        ]
    }


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time chat."""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast to all connections
            for connection in active_connections:
                await connection.send_text(data)
    except WebSocketDisconnect:
        active_connections.remove(websocket)
