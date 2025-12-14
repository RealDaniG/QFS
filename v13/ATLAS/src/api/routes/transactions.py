"""
Transaction API endpoints for the ATLAS system.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime, timezone
import logging

from ....core.transaction_processor import Transaction, TransactionProcessor
from ...models.transaction import TransactionCreate, TransactionResponse

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory transaction processor (in a real app, this would be a database or service)
transaction_processor = TransactionProcessor()

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: dict = Depends(lambda: {"username": "demo_user", "id": "user123"})
) -> TransactionResponse:
    """
    Create a new transaction.
    
    Args:
        transaction_data: Transaction details
        current_user: Authenticated user (from dependency)
        
    Returns:
        TransactionResponse: The created transaction
    """
    try:
        # In a real implementation, we would validate the user has sufficient balance
        # and proper authorization to perform the transaction
        
        tx = transaction_processor.create_transaction(
            sender=current_user["id"],
            receiver=transaction_data.receiver,
            amount=transaction_data.amount,
            asset=transaction_data.asset or "QFS",
            metadata=transaction_data.metadata
        )
        
        # Add to pending transactions
        if not transaction_processor.add_transaction(tx):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add transaction to pending pool"
            )
            
        # Process pending transactions
        transaction_processor.process_pending_transactions()
        
        return TransactionResponse(
            **tx.to_dict(),
            status="pending"
        )
        
    except Exception as e:
        logger.error(f"Error creating transaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create transaction"
        )

@router.get("/{tx_id}", response_model=TransactionResponse)
async def get_transaction(
    tx_id: str,
    current_user: dict = Depends(lambda: {"username": "demo_user", "id": "user123"})
) -> TransactionResponse:
    """
    Get transaction by ID.
    
    Args:
        tx_id: Transaction ID
        current_user: Authenticated user
        
    Returns:
        TransactionResponse: The requested transaction
    """
    tx = transaction_processor.get_transaction(tx_id)
    
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
        
    # In a real implementation, check if the user is authorized to view this transaction
    if tx.sender != current_user["id"] and tx.receiver != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this transaction"
        )
        
    return TransactionResponse(
        **tx.to_dict(),
        status=tx.status
    )

@router.get("/", response_model=List[TransactionResponse])
async def list_transactions(
    skip: int = 0,
    limit: int = 20,
    current_user: dict = Depends(lambda: {"username": "demo_user", "id": "user123"})
) -> List[TransactionResponse]:
    """
    List transactions for the current user.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Authenticated user
        
    Returns:
        List[TransactionResponse]: List of transactions
    """
    # In a real implementation, this would query a database with proper filtering
    # and pagination
    user_txs = []
    
    # Check both pending and confirmed transactions
    for tx in list(transaction_processor.pending_transactions.values()) + transaction_processor.ledger:
        if tx.sender == current_user["id"] or tx.receiver == current_user["id"]:
            user_txs.append(TransactionResponse(
                **tx.to_dict(),
                status=tx.status
            ))
    
    # Apply pagination
    return user_txs[skip:skip + limit]
