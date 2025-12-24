from fastapi import APIRouter

router = APIRouter(prefix="/api/v18/ledger", tags=["ledger"])


@router.get("")
async def get_ledger_v18():
    return [
        {
            "id": "event_1024",
            "type": "AUTH_SESSION_CREATED",
            "status": "ASCON_SEALED",
            "timestamp": "2024-01-01T00:00:00Z",
            "payload_hash": "sha256:e3b0c442...",
        },
        {
            "id": "event_1025",
            "type": "TREASURY_SYNC_COMPLETE",
            "status": "VERIFIED",
            "timestamp": "2024-01-01T00:03:00Z",
            "payload_hash": "sha256:e3b0c442...",
        },
        {
            "id": "event_1026",
            "type": "CONTENT_PUBLISHED",
            "status": "COMMITTED",
            "timestamp": "2024-01-01T00:04:15Z",
        },
    ]
