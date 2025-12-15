"""
ATLAS API Package

This package contains the API endpoints and middleware for the ATLAS system.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
import logging

from .routes import wallets, transactions, metrics, proofs, quantum, secure_chat, explain
from . import auth, users, chat # New Chat module
from .dependencies import get_current_user

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

# API router aggregation
api_routes = [
    wallets.router,
    transactions.router,
    metrics.router,
    proofs.router,
    quantum.router,
    secure_chat.router,
    explain.router,  # New Explain-This endpoints
    auth.router,     # V1 Auth
    users.router,    # V1 User Profiles
    chat.router,     # V1 WebSocket Chat
]

# Register all route modules
for router in api_routes:
    if router == transactions.router or router == wallets.router:
        app.include_router(router, dependencies=[Depends(get_current_user)])
    else:
        app.include_router(router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": API_VERSION,
        "service": "ATLAS Quantum Financial System"
    }