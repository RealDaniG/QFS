
import os
import uuid
import jwt
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from eth_account.messages import encode_defunct
from eth_account import Account
from v13.ATLAS.src.security.crypto_utils import verify_signature

from v13.ledger.genesis_ledger import GenesisLedger
# from v13.integrations.event_bridge import get_event_bridge # Architecture preference

logger = logging.getLogger(__name__)

# Config
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me-in-prod")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours for V1

# In-memory nonce store for V1 (Use Redis in V2)
# Format: {wallet_address: {nonce: str, expires: float}}
_nonce_store: Dict[str, Dict[str, Any]] = {}

router = APIRouter(prefix="/v1/auth", tags=["auth"])

class ChallengeRequest(BaseModel):
    wallet: str

class ChallengeResponse(BaseModel):
    nonce: str
    timestamp: str

class ConnectWalletRequest(BaseModel):
    wallet: str
    signature: str
    nonce: str
    referral_code: Optional[str] = None

class ConnectWalletResponse(BaseModel):
    token: str
    profile_exists: bool

# Helpers
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

# verify_signature imported from security.crypto_utils

# Routes
@router.post("/challenge", response_model=ChallengeResponse)
async def request_challenge(req: ChallengeRequest):
    """
    Generate a random nonce for the wallet to sign.
    Prevents replay attacks.
    """
    wallet = req.wallet.lower()
    nonce = f"Sign this message to login to ATLAS: {uuid.uuid4().hex}"
    
    # Store nonce with expiration (e.g., 5 minutes)
    _nonce_store[wallet] = {
        "nonce": nonce,
        "expires": time.time() + 300
    }
    
    return ChallengeResponse(
        nonce=nonce,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

@router.post("/connect-wallet", response_model=ConnectWalletResponse)
async def connect_wallet(req: ConnectWalletRequest):
    """
    Verify wallet signature and issue JWT.
    Logs LOGIN event to GenesisLedger if successful.
    """
    wallet = req.wallet.lower()
    
    # 1. Verify Nonce
    stored = _nonce_store.get(wallet)
    if not stored:
        raise HTTPException(status_code=400, detail="Challenge expired or not requested")
    
    if stored["nonce"] != req.nonce:
        raise HTTPException(status_code=400, detail="Invalid nonce")
        
    if time.time() > stored["expires"]:
        del _nonce_store[wallet]
        raise HTTPException(status_code=400, detail="Challenge expired")
    
    # 2. Verify Signature
    if not verify_signature(wallet, req.nonce, req.signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
        
    # 3. Cleanup Nonce (One-time use)
    del _nonce_store[wallet]
    
    # 4. Check/Create User (Stub logic for V1, would query DB/Ledger)
    # For now, we assume profile exists if we see them, or just strictly auth
    profile_exists = False # In real impl, check User DB
    
    # 5. Log to Ledger (Async preferrred, here sync for V1 safety)
    try:
        # Lazy load generic ledger for the auth service
        # In prod, inject this via dependency injection
        ledger = GenesisLedger("genesis_ledger.jsonl") 
        ledger.append_event(
            event_type="LOGIN",
            wallet=wallet,
            metadata={"source": "api_auth"},
            signature=req.signature # Log the proof
        )
        
        # 5.1 Handle Referral
        if req.referral_code and not profile_exists: # Only on first login/signup (simplified)
            # In V1, we trust the client logic or check db if we had one.
            # We'll log the REFERRAL event. The Coherence Engine will validate if self-referral, etc.
            try:
                ledger.append_event(
                    event_type="REFERRAL_USE",
                    wallet=wallet,
                    metadata={"referral_code": req.referral_code},
                    signature=req.signature
                )
            except Exception as e:
                logger.error(f"Failed to log referral: {e}")
    except Exception as e:
        logger.error(f"Failed to log login event: {e}")
        # Non-blocking for login success, but critical for audit
    
    # 6. Issue Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": wallet, "scope": "user"},
        expires_delta=access_token_expires
    )
    
    return ConnectWalletResponse(
        token=token,
        profile_exists=profile_exists
    )

