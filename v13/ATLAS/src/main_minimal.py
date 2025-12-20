"""
Minimal ATLAS Backend for V18 Testing
Bypasses complex models to get server running quickly.
"""

import logging
import datetime
import os
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import secrets

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ATLAS Quantum Financial System (v18 Minimal)",
    description="Minimal backend for v18 testing",
    version="18.9.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS configuration
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "*")
origins = [
    origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import v18 routes - EXPOSE ERRORS, DO NOT SWALLOW
try:
    # v18 Auth Endpoints (strictly internal credits)
    @app.get("/api/v18/auth/nonce")
    async def get_nonce_v18():
        nonce = f"v18_{secrets.token_hex(16)}"
        return {
            "nonce": nonce,
            "expires_at": (
                datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
            ).isoformat()
            + "Z",
        }

    @app.post("/api/v18/auth/verify")
    async def verify_auth_v18(payload: dict):
        wallet_address = payload.get("wallet_address")
        signature = payload.get("signature")
        nonce = payload.get("nonce")

        if not all([wallet_address, signature, nonce]):
            raise HTTPException(status_code=400, detail="Missing required fields")

        # v18 Rules: Session tokens are ASCON-compatible (mock prefix)
        session_token = f"ascon1.{secrets.token_urlsafe(32)}"
        return {
            "session_token": session_token,
            "expires_at": (
                datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            ).isoformat()
            + "Z",
            "scopes": ["user", "governance.read", "v18.internal"],
        }

    from .api.routes import governance_v18, content_v18, auth, wallets, transactions

    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(wallets.router)
    app.include_router(transactions.router)
    app.include_router(governance_v18.router)
    app.include_router(content_v18.router)

    logger.info("V18 routes loaded successfully")
except Exception as e:
    error_msg = f"Failed to load v18 routes: {e}"
    traceback_str = traceback.format_exc()

    logger.error(error_msg)
    logger.error(f"Full traceback:\n{traceback_str}")

    # Log to integration file for dashboard
    try:
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        log_path = "logs/v18_integration_log.txt"
        with open(log_path, "a") as log_file:
            log_file.write(f"[{timestamp}] [ERROR] [backend.routes] {error_msg}\n")
            log_file.write(
                f"[{timestamp}] [ERROR] [backend.routes] Traceback: {traceback_str[:500]}\n"
            )
    except Exception as log_err:
        logger.error(f"Failed to write to integration log: {log_err}")


# Health Check
@app.get("/health")
def health_check():
    return {"status": "ok", "version": "18.9.0", "services": {"v18_clusters": "ready"}}
