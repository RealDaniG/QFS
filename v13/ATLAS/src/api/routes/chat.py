from fastapi import APIRouter, Body
from src.lib.storage import db
import uuid

router = APIRouter(prefix="/api/v18/chat", tags=["chat"])


@router.get("/conversations")
async def get_conversations_v18():
    messages = db.get_messages()
    last_msg_text = "Awaiting secure link..." if not messages else messages[-1]["text"]

    return [
        {
            "id": "conv_1",
            "name": "System / Secure Channel",
            "avatar": "/avatars/group.jpg",
            "lastMessage": last_msg_text,
            "timestamp": "Just now",
            "unread": 0,
            "isGroup": True,
            "members": 2,
            "isEncrypted": True,
        },
        {
            "id": "conv_2",
            "name": "QFS Governance",
            "avatar": "/avatars/gov.jpg",
            "lastMessage": "Proposal #1024 is open for voting.",
            "timestamp": "2h ago",
            "unread": 3,
            "isGroup": True,
            "members": 142,
            "isEncrypted": False,
        },
    ]


@router.get("/history")
async def get_chat_history_v18():
    return db.get_messages()


@router.post("/send")
async def send_chat_message_v18(payload: dict = Body(...)):
    # In future, use Pydantic model SendMessagePayload
    text = payload.get("text", "")
    new_msg = {
        "id": f"msg_{uuid.uuid4()}",
        "sender": "You",
        "text": text,
        "timestamp": "2024-01-01T00:00:00Z",  # Zero-Sim
    }
    db.add_message(new_msg)
    return {"status": "sent", "message": new_msg}
