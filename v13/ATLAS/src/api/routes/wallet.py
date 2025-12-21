from fastapi import APIRouter, Depends
from src.api.dependencies import require_auth

router = APIRouter(prefix="/api/v18/wallet", tags=["wallet"])


@router.get("/balance")
async def get_wallet_balance_v18(session: dict = Depends(require_auth)):
    return {
        "balance": 1420.00,
        "staked": 450.00,
        "rewards": 142.00,
        "currency": "FLX",
        "reputation": 142.0,
        "reputation_breakdown": {
            "content_quality": 0.85,
            "engagement": 0.72,
            "governance": 0.65,
        },
        "compliance": "Verified",
        "adr_signal": "Positive",
    }


@router.get("/history")
async def get_wallet_history_v18():
    return [
        {
            "id": "tx_001",
            "type": "Reward",
            "amount": 50.00,
            "reason": "Content Coherence Bonus",
            "status": "Confirmed",
            "timestamp": "2025-12-19T10:30:00Z",
        },
        {
            "id": "tx_002",
            "type": "Reward",
            "amount": 25.00,
            "reason": "Network Validation Reward",
            "status": "Confirmed",
            "timestamp": "2025-12-18T15:45:00Z",
        },
        {
            "id": "tx_003",
            "type": "Stake",
            "amount": -450.00,
            "reason": "Node Staking (V18 Proof)",
            "status": "Confirmed",
            "timestamp": "2025-12-17T09:00:00Z",
        },
    ]
