from fastapi import APIRouter, Depends, HTTPException
from typing import Dict

router = APIRouter(prefix="/api/wallet", tags=["Wallet"])


@router.get("/balance")
async def get_balance():
    """Get wallet balance (test data)."""
    return {
        "balance": {"FLX": 1000.0, "ATR": 500.0, "USDC": 2500.0},
        "total_usd": 4000.0,
    }


@router.get("/transactions")
async def get_transactions():
    """Get recent transactions."""
    return {
        "transactions": [
            {
                "id": "tx_001",
                "type": "reward",
                "amount": 10,
                "token": "FLX",
                "timestamp": 1703174400,
                "description": "Daily presence confirmation",
            }
        ]
    }
