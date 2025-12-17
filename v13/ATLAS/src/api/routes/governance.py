"""
Governance API endpoints for the ATLAS system.

Provides access to immutable audit logs and governance state.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any, List, Optional

router = APIRouter(prefix="/governance", tags=["governance"])


@router.get("/audit-log")
async def get_audit_log(
    limit: int = 50, type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve system audit logs.
    """
    logs = [
        {
            "id": "evt_1",
            "timestamp": "2025-01-01T12:00:00Z",
            "type": "CONTRACT",
            "severity": "INFO",
            "actor_did": "did:key:zAdmin",
            "action": "Upgraded Contract to V1.3",
            "integrity_hash": "sha256-abc...",
            "verified": True,
        },
        {
            "id": "evt_2",
            "timestamp": "2025-01-01T11:55:00Z",
            "type": "SIGNAL",
            "severity": "INFO",
            "actor_did": "did:key:zAES",
            "action": "Registered ArtisticSignalAddon",
            "integrity_hash": "sha256-def...",
            "verified": True,
        },
        {
            "id": "evt_3",
            "timestamp": "2025-01-01T11:50:00Z",
            "type": "REWARD",
            "severity": "WARNING",
            "actor_did": "did:key:zSystem",
            "action": "Cap Applied to Wallet 0x123",
            "integrity_hash": "sha256-ghi...",
            "verified": True,
        },
        {
            "id": "evt_4",
            "timestamp": "2025-01-01T11:45:00Z",
            "type": "STORAGE",
            "severity": "INFO",
            "actor_did": "did:key:zNode1",
            "action": "Storage Proof Verified",
            "integrity_hash": "sha256-jkl...",
            "verified": True,
        },
    ]
    if type:
        logs = [l for l in logs if l["type"] == type]
    return logs[:limit]
