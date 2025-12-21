from fastapi import APIRouter, Depends, HTTPException
from typing import Dict
from lib.dependencies import get_current_user

router = APIRouter(prefix="/api/wallet", tags=["Wallet"])


@router.get("/balance")
async def get_balance(wallet_address: str = Depends(get_current_user)):
    """Get wallet balance (test data)."""
    return {
        "wallet_address": wallet_address,
        "balance": {"FLX": 1000.0, "ATR": 500.0, "USDC": 2500.0},
        "total_usd": 4000.0,
    }


@router.get("/transactions")
async def get_transactions(wallet_address: str = Depends(get_current_user)):
    """Get recent transactions."""
    return {
        "wallet_address": wallet_address,
        "transactions": [
            {
                "id": "tx_001",
                "type": "reward",
                "amount": 10,
                "token": "FLX",
                "timestamp": 1703174400,
                "description": "Daily presence confirmation",
            }
        ],
    }
