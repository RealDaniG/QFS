from fastapi import APIRouter
import datetime

router = APIRouter(prefix="/api/v18/ledger", tags=["ledger"])


@router.get("")
async def get_ledger_v18():
    return [
        {
            "id": "event_1024",
            "type": "AUTH_SESSION_CREATED",
            "status": "ASCON_SEALED",
            "timestamp": (
                datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
            ).isoformat()
            + "Z",
            "payload_hash": "sha256:e3b0c442...",
        },
        {
            "id": "event_1025",
            "type": "TREASURY_SYNC_COMPLETE",
            "status": "VERIFIED",
            "timestamp": (
                datetime.datetime.utcnow() - datetime.timedelta(minutes=2)
            ).isoformat()
            + "Z",
            "payload_hash": "sha256:e3b0c442...",
        },
        {
            "id": "event_1026",
            "type": "CONTENT_PUBLISHED",
            "status": "COMMITTED",
            "timestamp": (
                datetime.datetime.utcnow() - datetime.timedelta(seconds=45)
            ).isoformat()
            + "Z",
        },
    ]
