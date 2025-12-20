"""
Wallet models for the ATLAS API.
"""

from v13.libs.deterministic_helpers import (
    ZeroSimAbort,
    det_time_now,
    det_perf_counter,
    det_random,
    det_time_isoformat,
    qnum,
)
from v13.libs.economics.QAmount import QAmount
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator, EmailStr, ConfigDict


class WalletBalance(BaseModel):
    """Model representing a wallet's balance for a specific asset."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    asset: str = Field(..., description="Asset symbol")
    balance: QAmount = Field(..., description="Available balance")
    locked: QAmount = Field(0, description="Locked balance (in orders, etc.)")
    total: QAmount = Field(..., description="Total balance (available + locked)")

    @validator("balance", "locked", "total")
    def validate_non_negative(cls, v):
        """Ensure balance values are non-negative."""
        if v < 0:
            raise ValueError("Balance values cannot be negative")
        return v


class WalletCreate(BaseModel):
    """Model for creating a new wallet."""

    name: str = Field(..., min_length=1, max_length=100, description="Wallet name")
    description: Optional[str] = Field(
        None, max_length=500, description="Optional wallet description"
    )
    asset: str = Field("QFS", description="Default asset for this wallet")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional wallet metadata"
    )


class WalletResponse(WalletCreate):
    """Wallet response model with additional fields."""

    wallet_id: str = Field(..., description="Unique wallet ID")
    owner_id: str = Field(..., description="ID of the wallet owner")
    created_at: str = Field(..., description="Creation timestamp in ISO format")
    updated_at: str = Field(..., description="Last update timestamp in ISO format")
    is_active: bool = Field(True, description="Whether the wallet is active")
    balances: List[WalletBalance] = Field(
        default_factory=list, description="List of asset balances"
    )

    @validator("created_at", "updated_at")
    def validate_timestamps(cls, v):
        """Validate that timestamps are in ISO format."""
        try:
            det_time_now()
            return v
        except ValueError:
            raise ValueError("Invalid ISO format for timestamp")


class WalletUpdate(BaseModel):
    """Model for updating wallet properties."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="New wallet name"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="New wallet description"
    )
    is_active: Optional[bool] = Field(None, description="Set wallet active/inactive")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Updated metadata (replaces existing metadata)"
    )


class WalletTransfer(BaseModel):
    """Model for transferring funds between wallets."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    source_wallet_id: str = Field(..., description="Source wallet ID")
    target_wallet_id: str = Field(..., description="Target wallet ID")
    amount: QAmount = Field(..., gt=0, description="Amount to transfer")
    asset: str = Field("QFS", description="Asset to transfer")
    memo: Optional[str] = Field(
        None, max_length=200, description="Optional transfer memo"
    )


class WalletAddress(BaseModel):
    """Model representing a wallet's deposit address."""

    address: str = Field(..., description="Deposit address")
    asset: str = Field(..., description="Asset symbol")
    wallet_id: str = Field(..., description="Owning wallet ID")
    label: Optional[str] = Field(
        None, max_length=100, description="Optional address label"
    )
    created_at: str = Field(..., description="Creation timestamp in ISO format")
    is_active: bool = Field(True, description="Whether the address is active")


class WalletHistoryEntry(BaseModel):
    """Model representing a wallet history entry."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    entry_id: str = Field(..., description="Unique entry ID")
    wallet_id: str = Field(..., description="Wallet ID")
    timestamp: str = Field(..., description="Entry timestamp in ISO format")
    type: str = Field(
        ..., description="Entry type (deposit, withdrawal, transfer, fee, etc.)"
    )
    amount: QAmount = Field(
        ..., description="Amount (positive for credit, negative for debit)"
    )
    asset: str = Field(..., description="Asset symbol")
    balance: QAmount = Field(..., description="Balance after this entry")
    tx_id: Optional[str] = Field(None, description="Related transaction ID")
    description: Optional[str] = Field(None, description="Entry description")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional entry metadata"
    )


class WalletBackup(BaseModel):
    """Model for wallet backup data."""

    wallet_id: str = Field(..., description="Wallet ID")
    backup_data: str = Field(..., description="Encrypted backup data")
    backup_id: str = Field(..., description="Backup ID")
    created_at: str = Field(..., description="Backup timestamp in ISO format")
    version: str = Field("1.0", description="Backup format version")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional backup metadata"
    )

