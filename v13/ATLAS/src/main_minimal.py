import logging
import sys
import uvicorn
from pythonjsonlogger import jsonlogger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings

# Import routers
from src.api.routes import (
    auth,
    rewards,
    wallet,
    spaces,
    chat,
    governance,
    content,
    ledger,
    general,
    v1_auth,
    wallets,
    transactions,
    evidence,
    p2p,
    bounties,
)

# Setup structured logging
logger = logging.getLogger()
logHandler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Initialize App
app = FastAPI(
    title="ATLAS Quantum Financial System (v18.5 Modular)",
    description="Refactored backend for v18 testing",
    version="18.9.5",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS Configuration
if settings.ALLOWED_ORIGINS == "*":
    origins = ["*"]
else:
    origins = [
        origin.strip()
        for origin in settings.ALLOWED_ORIGINS.split(",")
        if origin.strip()
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(v1_auth.router)  # V1 compatibility layer
app.include_router(rewards.router)
app.include_router(wallet.router)
app.include_router(spaces.router)
app.include_router(chat.router)
app.include_router(governance.router)
app.include_router(content.router)
app.include_router(ledger.router)
app.include_router(general.router)
app.include_router(evidence.router)
app.include_router(content.discovery_router, prefix="/api/v18")
app.include_router(p2p.router, prefix="/api/p2p", tags=["p2p"])
app.include_router(bounties.router)

# Explicitly register V1 legacy routers with prefixes for tool compatibility
# Explicitly register V1 legacy routers with prefixes for tool compatibility
app.include_router(wallets.router, tags=["wallets-v1"])
app.include_router(transactions.router, tags=["transactions-v1"])


# Health Check
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "version": "18.9.5",
        "services": {"v18_clusters": "ready", "architecture": "modular"},
    }


if __name__ == "__main__":
    port = int(settings.PORT)
    logger.info(f"Starting ATLAS v18 Backend on port {port}...")
    uvicorn.run(app, host=settings.HOST, port=port)
