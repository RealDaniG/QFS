"""
ATLAS API Package

This package contains the API endpoints and middleware for the ATLAS system.
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
import logging
from .routes import wallets, transactions, metrics, proofs, quantum, secure_chat, explain
from .dependencies import get_current_user
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
API_VERSION = '1.0.0'
app = FastAPI(title='ATLAS Quantum Financial System', description='Advanced Transaction Ledger and Security System with Quantum Resistance', version=API_VERSION, docs_url='/docs', redoc_url='/redoc')
api_routes = [wallets.router, transactions.router, metrics.router, proofs.router, quantum.router, secure_chat.router, explain.router]
for router in sorted(api_routes):
    if router == transactions.router or router == wallets.router:
        app.include_router(router, dependencies=[Depends(get_current_user)])
    else:
        app.include_router(router)

@app.get('/health')
async def health_check():
    """Health check endpoint for monitoring."""
    return {'status': 'healthy', 'version': API_VERSION, 'service': 'ATLAS Quantum Financial System'}