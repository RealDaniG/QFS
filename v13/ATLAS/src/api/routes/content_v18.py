"""
V18 Content API Routes
Integrated with ClusterAdapter for chat/content publishing.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import hashlib
import time
from ..dependencies import get_current_wallet
from v18.cluster import V18ClusterAdapter, ChatCommand, TxResult

router = APIRouter(prefix="/api/v18/content", tags=["content-v18"])

# Initialize ClusterAdapter
cluster_adapter = V18ClusterAdapter(
    node_endpoints=[
        "http://localhost:8001",
        "http://localhost:8002",
        "http://localhost:8003",
    ],
    timeout_seconds=10,
)


# ============================================================================
# Request/Response Models
# ============================================================================


class PublishMessageRequest(BaseModel):
    channel_id: str
    content: str
    reply_to: Optional[str] = None
    visibility: str = "public"  # public, private, followers


class PublishMessageResponse(BaseModel):
    message_id: str
    content_hash: str
    committed: bool
    evidence_event_ids: List[str]
    timestamp: float


class MessageSummary(BaseModel):
    id: str
    channel_id: str
    sender: str
    content: str
    content_hash: str
    timestamp: float
    reply_to: Optional[str] = None


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/publish", response_model=PublishMessageResponse)
async def publish_message(
    request: PublishMessageRequest, wallet: str = Depends(get_current_wallet)
):
    """
    Publish a message/post to a channel.

    Flow:
    1. Hash the content (Class B - mutable)
    2. Submit hash to EvidenceBus via ClusterAdapter (Class A - immutable)
    3. Store full content in projection DB
    """
    try:
        # Generate content hash (deterministic)
        content_hash = hashlib.sha256(request.content.encode()).hexdigest()

        # Create chat command
        cmd = ChatCommand(
            action_type="post",
            sender_wallet=wallet,
            channel_id=request.channel_id,
            message_content=request.content,  # Full content for now
            message_hash=content_hash,
        )

        # Submit to cluster (this anchors the hash in EvidenceBus)
        result: TxResult = cluster_adapter.submit_chat_message(cmd)

        if not result.committed:
            raise HTTPException(
                status_code=500,
                detail=f"Message publishing failed: {result.error_message}",
            )

        # Extract message ID from event
        message_id = (
            result.evidence_event_ids[0]
            if result.evidence_event_ids
            else f"msg_{int(time.time())}"
        )

        return PublishMessageResponse(
            message_id=message_id,
            content_hash=content_hash,
            committed=result.committed,
            evidence_event_ids=result.evidence_event_ids,
            timestamp=result.timestamp,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feed", response_model=List[MessageSummary])
async def get_feed(channel_id: Optional[str] = None, limit: int = 20, offset: int = 0):
    """
    Get content feed.
    Queries from projection database.
    """
    # TODO: Query from projection database
    # For now, return mock data
    return [
        MessageSummary(
            id="msg_001",
            channel_id=channel_id or "general",
            sender="0xABC123",
            content="Hello from ATLAS v18!",
            content_hash="abc123...",
            timestamp=time.time(),
            reply_to=None,
        )
    ]


@router.get("/messages/{message_id}", response_model=MessageSummary)
async def get_message(message_id: str):
    """
    Get a specific message by ID.
    """
    # TODO: Query from projection database
    return MessageSummary(
        id=message_id,
        channel_id="general",
        sender="0xABC123",
        content="Sample message content",
        content_hash="hash123...",
        timestamp=time.time(),
        reply_to=None,
    )


@router.post("/messages/{message_id}/react")
async def add_reaction(
    message_id: str, emoji: str, wallet: str = Depends(get_current_wallet)
):
    """
    Add a reaction to a message.
    """
    try:
        cmd = ChatCommand(
            action_type="react",
            sender_wallet=wallet,
            channel_id="",  # Not needed for reactions
            message_hash=message_id,
        )

        result: TxResult = cluster_adapter.submit_chat_message(cmd)

        if not result.committed:
            raise HTTPException(status_code=500, detail=result.error_message)

        return {
            "status": "success",
            "reaction_id": result.evidence_event_ids[0]
            if result.evidence_event_ids
            else "unknown",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

