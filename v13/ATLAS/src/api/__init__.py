"""
ATLAS API Package

This package contains the API endpoints and middleware for the ATLAS system.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# API version
API_VERSION = "1.0.0"

# Create FastAPI app
app = FastAPI(
    title="ATLAS Quantum Financial System",
    description="Advanced Transaction Ledger and Security System with Quantum Resistance",
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# API dependencies
def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dependency to get the current user from the token."""
    # In a real implementation, validate the token and return user info
    # This is a simplified version for demonstration
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"username": "demo_user", "id": "user123"}

# Import and include routers
from .routes import transactions, wallets, quantum, secure_chat, metrics, proofs

# Include API routers
app.include_router(
    transactions.router,
    prefix="/api/v1/transactions",
    tags=["transactions"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    wallets.router,
    prefix="/api/v1/wallets",
    tags=["wallets"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    quantum.router,
    prefix="/api/v1/quantum",
    tags=["quantum"]
)

app.include_router(
    secure_chat.router,
    prefix="/api/v1",
    tags=["secure-chat"],
)

app.include_router(
    metrics.router,
    prefix="/api/v1",
    tags=["metrics"],
)

app.include_router(
    proofs.router,
    prefix="/api/v1",
    tags=["proofs"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": API_VERSION,
        "service": "ATLAS Quantum Financial System"
    }
