"""
Transaction models for the ATLAS API.
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
from pydantic import BaseModel, Field, validator, ConfigDict


class TransactionBase(BaseModel):
    """Base transaction model with common fields."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    sender: str = Field(..., description="Sender's wallet address")
    receiver: str = Field(..., description="Recipient's wallet address")
    amount: QAmount = Field(..., gt=0, description="Amount to transfer")
    asset: str = Field("QFS", description="Asset symbol (default: QFS)")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional transaction metadata"
    )


class TransactionCreate(TransactionBase):
    """Model for creating a new transaction."""

    pass


class TransactionResponse(TransactionBase):
    """Transaction response model with additional fields."""

    tx_id: str = Field(..., description="Unique transaction ID")
    timestamp: str = Field(..., description="Transaction timestamp in ISO format")
    status: str = Field(..., description="Transaction status")
    signature: Optional[str] = Field(None, description="Digital signature (if signed)")

    @validator("timestamp")
    def validate_timestamp(cls, v):
        """Validate that the timestamp is in ISO format."""
        try:
            det_time_now()
            return v
        except ValueError:
            raise ValueError("Invalid ISO format for timestamp")


class TransactionListResponse(BaseModel):
    """Response model for listing transactions with pagination."""

    transactions: List[TransactionResponse]
    total: int
    page: int
    page_size: int


class TransactionStatus(BaseModel):
    """Transaction status response model."""

    tx_id: str = Field(..., description="Transaction ID")
    status: str = Field(..., description="Current status")
    confirmations: int = Field(0, description="Number of confirmations")
    block_hash: Optional[str] = Field(None, description="Block hash if confirmed")
    block_height: Optional[int] = Field(None, description="Block height if confirmed")
    timestamp: Optional[str] = Field(None, description="Confirmation timestamp")


class TransactionFeeEstimate(BaseModel):
    """Transaction fee estimation model."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    estimated_fee: QAmount = Field(..., description="Estimated fee in base currency")
    fee_rate: QAmount = Field(..., description="Fee rate in satoshis/byte")
    fee_asset: str = Field("QFS", description="Asset used for fees")
    estimated_confirmation_time: Optional[int] = Field(
        None, description="Estimated confirmation time in seconds"
    )


class TransactionSignRequest(BaseModel):
    """Model for signing a transaction."""

    tx_id: str = Field(..., description="Transaction ID to sign")
    private_key: str = Field(..., description="Private key for signing")
    key_id: Optional[str] = Field(None, description="Key ID (if using key management)")


class TransactionBroadcastRequest(BaseModel):
    """Model for broadcasting a signed transaction."""

    signed_tx: str = Field(..., description="Signed transaction data")
    network: str = Field("mainnet", description="Network to broadcast to")


class TransactionSearchQuery(BaseModel):
    """Model for searching transactions."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    address: Optional[str] = Field(
        None, description="Filter by address (sender or receiver)"
    )
    asset: Optional[str] = Field(None, description="Filter by asset")
    start_time: Optional[str] = Field(None, description="Start time in ISO format")
    end_time: Optional[str] = Field(None, description="End time in ISO format")
    min_amount: Optional[QAmount] = Field(None, description="Minimum amount")
    max_amount: Optional[QAmount] = Field(None, description="Maximum amount")
    status: Optional[str] = Field(None, description="Transaction status")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")

