"""
Wallet API endpoints for the ATLAS system.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, List, Optional
import logging

from ....core.transaction_processor import TransactionProcessor
from ...models.wallet import WalletBalance, WalletCreate, WalletResponse

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory wallet store (in a real app, this would be a database)
wallets = {}

# Shared transaction processor
transaction_processor = TransactionProcessor()

@router.post("/", response_model=WalletResponse, status_code=status.HTTP_201_CREATED)
async def create_wallet(
    wallet_data: WalletCreate,
    current_user: dict = Depends(lambda: {"username": "demo_user", "id": "user123"})
) -> WalletResponse:
    """
    Create a new wallet for the current user.
    
    Args:
        wallet_data: Wallet creation data
        current_user: Authenticated user
        
    Returns:
        WalletResponse: The created wallet
    """
    try:
        wallet_id = f"wallet_{len(wallets) + 1}"
        
        # In a real implementation, we would generate secure keys here
        wallet = {
            "id": wallet_id,
            "owner_id": current_user["id"],
            "name": wallet_data.name,
            "description": wallet_data.description,
            "created_at": "2023-01-01T00:00:00Z",  # Would be datetime.utcnow().isoformat()
            "is_active": True,
            "metadata": wallet_data.metadata or {}
        }
        
        wallets[wallet_id] = wallet
        logger.info(f"Created wallet {wallet_id} for user {current_user['id']}")
        
        return WalletResponse(**wallet, balances=[])
        
    except Exception as e:
        logger.error(f"Error creating wallet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create wallet"
        )

@router.get("/{wallet_id}", response_model=WalletResponse)
async def get_wallet(
    wallet_id: str,
    current_user: dict = Depends(lambda: {"username": "demo_user", "id": "user123"})
) -> WalletResponse:
    """
    Get wallet by ID.
    
    Args:
        wallet_id: Wallet ID
        current_user: Authenticated user
        
    Returns:
        WalletResponse: The requested wallet with balances
    """
    wallet = wallets.get(wallet_id)
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
        
    # Check if the user is authorized to view this wallet
    if wallet["owner_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this wallet"
        )
    
    # Get balances for this wallet
    # In a real implementation, this would query the ledger
    balances = [
        {"asset": "QFS", "balance": 1000.0},  # Example balance
        {"asset": "BTC", "balance": 0.5}      # Example balance
    ]
    
    return WalletResponse(
        **wallet,
        balances=balances
    )

@router.get("/{wallet_id}/balance", response_model=List[WalletBalance])
async def get_wallet_balances(
    wallet_id: str,
    asset: Optional[str] = None,
    current_user: dict = Depends(lambda: {"username": "demo_user", "id": "user123"})
) -> List[WalletBalance]:
    """
    Get balances for a specific wallet.
    
    Args:
        wallet_id: Wallet ID
        asset: Optional asset filter
        current_user: Authenticated user
        
    Returns:
        List[WalletBalance]: List of wallet balances
    """
    wallet = wallets.get(wallet_id)
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
        
    # Check if the user is authorized to view this wallet
    if wallet["owner_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this wallet"
        )
    
    # In a real implementation, this would query the ledger
    all_balances = [
        {"asset": "QFS", "balance": 1000.0},
        {"asset": "BTC", "balance": 0.5}
    ]
    
    # Filter by asset if specified
    if asset:
        return [b for b in all_balances if b["asset"] == asset]
    
    return all_balances

@router.get("/", response_model=List[WalletResponse])
async def list_wallets(
    current_user: dict = Depends(lambda: {"username": "demo_user", "id": "user123"})
) -> List[WalletResponse]:
    """
    List all wallets for the current user.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        List[WalletResponse]: List of user's wallets
    """
    # Filter wallets by owner
    user_wallets = [w for w in wallets.values() if w["owner_id"] == current_user["id"]]
    
    # Add empty balances for each wallet
    return [
        WalletResponse(
            **wallet,
            balances=[
                {"asset": "QFS", "balance": 1000.0},
                {"asset": "BTC", "balance": 0.5}
            ]
        )
        for wallet in user_wallets
    ]
