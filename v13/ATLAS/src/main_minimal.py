"""
Minimal ATLAS Backend for V18 Testing
Bypasses complex models to get server running quickly.
"""

import logging
import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import v18 routes - EXPOSE ERRORS, DO NOT SWALLOW
try:
    from .api.routes import governance_v18, content_v18, auth, wallets, transactions

    app.include_router(auth.router)
    app.include_router(wallets.router)
    app.include_router(transactions.router)
    app.include_router(governance_v18.router)
    app.include_router(content_v18.router)

    logger.info("V18 routes loaded successfully")
except Exception as e:
    import traceback
    import datetime

    error_msg = f"Failed to load v18 routes: {e}"
    traceback_str = traceback.format_exc()

    logger.error(error_msg)
    logger.error(f"Full traceback:\n{traceback_str}")

    # Log to integration file for dashboard
    try:
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        with open("../../logs/v18_integration_log.txt", "a") as log_file:
            log_file.write(f"[{timestamp}] [ERROR] [backend.routes] {error_msg}\n")
            log_file.write(
                f"[{timestamp}] [ERROR] [backend.routes] Traceback: {traceback_str[:500]}\n"
            )
    except:
        pass

    # RE-RAISE to expose the real problem
    raise


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "18.9.0-minimal",
        "service": "ATLAS v18 Backend",
        "routes_loaded": ["auth", "governance_v18", "content_v18"],
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "ATLAS Quantum Financial System",
        "version": "18.9.0-minimal",
        "description": "V18 Backend with ClusterAdapter support",
        "documentation": "/api/docs",
        "status": "operational",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main_minimal:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
    )
