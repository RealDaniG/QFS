"""
ATLAS API Routes for Secure Chat

Provides REST endpoints for secure chat operations using QFSClient.
"""

from libs.deterministic_helpers import det_time_isoformat
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
import base64
from libs.PQC import PQC
from ..dependencies import get_current_user, get_qfs_client
from ...models.user import User
from ...qfs_client import QFSClient
from ...types import Transaction
from ...secure_chat.core.engine import ThreadStatus
from ...core.pqc_session import pqc_session_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/secure-chat", tags=["secure-chat"])

# --- Handshake Models ---


class HandshakeResponse(BaseModel):
    algorithm: str
    public_key_b64: str
    fingerprint: str


class EstablishRequest(BaseModel):
    wallet_id: str
    kem_ciphertext_b64: str


class EstablishResponse(BaseModel):
    session_id: str
    status: str


# --- Handshake Endpoints ---


@router.get("/handshake", response_model=HandshakeResponse)
async def get_handshake_params():
    """
    Get (static) server PQC Public Key for KEM.
    """
    pk_b64 = base64.b64encode(pqc_session_manager.public_key).decode("utf-8")
    # Simple fingerprint
    import hashlib

    fingerprint = hashlib.sha256(pqc_session_manager.public_key).hexdigest()[:16]
    return HandshakeResponse(
        algorithm=PQC.KYBER1024, public_key_b64=pk_b64, fingerprint=fingerprint
    )


@router.post("/establish", response_model=EstablishResponse)
async def establish_session(request: EstablishRequest):
    """
    Establish a logical secure session using PQC KEM.
    Client encapsulates a shared secret against server's public key.
    Server decapsulates and stores the session key.
    """
    try:
        session_id = pqc_session_manager.create_session(request.kem_ciphertext_b64)
        return EstablishResponse(session_id=session_id, status="ESTABLISHED")
    except ValueError:
        raise HTTPException(status_code=400, detail="Handshake failed")


# --- Chat Models ---


class ThreadCreateRequest(BaseModel):
    participants: List[str] = Field(..., min_items=1, max_items=100)
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ThreadResponse(BaseModel):
    thread_id: str
    creator_id: str
    participants: List[str]
    created_at: str
    status: str
    metadata: Dict[str, Any]
    transaction_id: str


class MessageCreateRequest(BaseModel):
    thread_id: str
    content_hash: str = Field(..., min_length=64, max_length=64)
    content_size: int = Field(..., gt=0, le=1048576)
    content_type: str = "text/plain"
    message_type: str = "text"
    metadata: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    message_id: str
    thread_id: str
    sender_id: str
    content_hash: str
    content_size: int
    timestamp: str
    message_type: str
    transaction_id: str


class ThreadListResponse(BaseModel):
    threads: List[ThreadResponse]
    total: int


class MessageListResponse(BaseModel):
    messages: List[MessageResponse]
    total: int
    thread_id: str


# --- Helper Functions ---


def build_secure_chat_thread_tx(
    creator_id: str, request: ThreadCreateRequest
) -> Transaction:
    """Build QFS transaction for thread creation"""
    return Transaction(
        transaction_id=None,
        operation_type="secure_chat_thread_created",
        creator_id=creator_id,
        data={
            "participants": request.participants,
            "title": request.title,
            "metadata": request.metadata or {},
            "timestamp": det_time_isoformat(),
        },
    )


def build_secure_chat_message_tx(
    creator_id: str, request: MessageCreateRequest
) -> Transaction:
    """Build QFS transaction for message creation"""
    return Transaction(
        transaction_id=None,
        operation_type="secure_chat_message_posted",
        creator_id=creator_id,
        data={
            "thread_id": request.thread_id,
            "content_hash": request.content_hash,
            "content_size": request.content_size,
            "content_type": request.content_type,
            "message_type": request.message_type,
            "metadata": request.metadata or {},
            "timestamp": det_time_isoformat(),
        },
    )


def build_thread_response(
    receipt, creator_id: str, request: ThreadCreateRequest
) -> ThreadResponse:
    """Build thread response from receipt"""
    return ThreadResponse(
        thread_id=receipt.transaction_id,
        creator_id=creator_id,
        participants=request.participants,
        created_at=receipt.timestamp,
        status="ACTIVE",
        metadata=request.metadata or {},
        transaction_id=receipt.transaction_id,
    )


def build_message_response(
    receipt, request: MessageCreateRequest, sender_id: str
) -> MessageResponse:
    """Build message response from receipt"""
    return MessageResponse(
        message_id=receipt.transaction_id,
        thread_id=request.thread_id,
        sender_id=sender_id,
        content_hash=request.content_hash,
        content_size=request.content_size,
        timestamp=receipt.timestamp,
        message_type=request.message_type,
        transaction_id=receipt.transaction_id,
    )


# --- Chat Endpoints ---


@router.post(
    "/threads", response_model=ThreadResponse, status_code=status.HTTP_201_CREATED
)
async def create_thread(
    request: ThreadCreateRequest,
    current_user: User = Depends(get_current_user),
    qfs: QFSClient = Depends(get_qfs_client),
):
    """
    Create a new secure chat thread.

    Only metadata is stored on-chain; actual content is stored off-chain
    via IPFS and referenced by content_hash.
    """
    try:
        if current_user.id not in request.participants:
            request.participants.append(current_user.id)
        tx = build_secure_chat_thread_tx(current_user.id, request)
        receipt = await qfs.submit_transaction(tx)
        return build_thread_response(receipt, current_user.id, request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create thread: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create thread",
        )


@router.post(
    "/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED
)
async def send_message(
    request: MessageCreateRequest,
    current_user: User = Depends(get_current_user),
    qfs: QFSClient = Depends(get_qfs_client),
):
    """
    Send a message to a secure chat thread.

    Client must have already stored ciphertext via StorageEngine/IPFS
    and provided content_hash + size. No plaintext is transmitted.
    """
    try:
        tx = build_secure_chat_message_tx(current_user.id, request)
        receipt = await qfs.submit_transaction(tx)
        return build_message_response(receipt, request, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message",
        )


@router.get("/threads", response_model=ThreadListResponse)
async def list_threads(
    current_user: User = Depends(get_current_user),
    qfs: QFSClient = Depends(get_qfs_client),
    limit: int = 100,
    offset: int = 0,
):
    """
    List all threads for the current user.
    """
    try:
        user_state = await qfs.get_state(current_user.id)
        threads = user_state.get("threads", [])
        paginated_threads = threads[offset : offset + limit]
        return ThreadListResponse(threads=paginated_threads, total=len(threads))
    except Exception as e:
        logger.error(f"Failed to list threads: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list threads",
        )


@router.get("/threads/{thread_id}", response_model=ThreadResponse)
async def get_thread(
    thread_id: str,
    current_user: User = Depends(get_current_user),
    qfs: QFSClient = Depends(get_qfs_client),
):
    """
    Get thread metadata by ID.
    """
    try:
        thread_state = await qfs.get_state(thread_id)
        if current_user.id not in thread_state.get("participants", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
        return ThreadResponse(
            thread_id=thread_id,
            creator_id=thread_state.get("creator_id"),
            participants=thread_state.get("participants", []),
            created_at=thread_state.get("created_at"),
            status=thread_state.get("status", "ACTIVE"),
            metadata=thread_state.get("metadata", {}),
            transaction_id=thread_state.get("transaction_id", thread_id),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get thread {thread_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get thread",
        )


@router.get("/threads/{thread_id}/messages", response_model=MessageListResponse)
async def list_messages(
    thread_id: str,
    current_user: User = Depends(get_current_user),
    qfs: QFSClient = Depends(get_qfs_client),
    limit: int = 100,
    before: Optional[str] = None,
):
    """
    List messages in a thread.
    """
    try:
        thread_state = await qfs.get_state(thread_id)
        if current_user.id not in thread_state.get("participants", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
        messages = thread_state.get("messages", [])
        if before:
            messages = [m for m in messages if m.get("timestamp") < before]
        paginated_messages = messages[-limit:]
        return MessageListResponse(
            messages=paginated_messages, total=len(messages), thread_id=thread_id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list messages for thread {thread_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list messages",
        )


@router.put("/threads/{thread_id}/status")
async def update_thread_status(
    thread_id: str,
    status: str,
    current_user: User = Depends(get_current_user),
    qfs: QFSClient = Depends(get_qfs_client),
):
    """
    Update thread status (archive, delete, etc.).
    """
    try:
        if status not in [s.value for s in ThreadStatus]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status"
            )
        thread_state = await qfs.get_state(thread_id)
        if thread_state.get("creator_id") != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only thread creator can update status",
            )
        tx = Transaction(
            transaction_id=None,
            operation_type="secure_chat_thread_updated",
            creator_id=current_user.id,
            data={
                "thread_id": thread_id,
                "status": status,
                "timestamp": det_time_isoformat(),
            },
        )
        receipt = await qfs.submit_transaction(tx)
        return {"status": "updated", "transaction_id": receipt.transaction_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update thread status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update thread status",
        )
