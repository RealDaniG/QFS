"""
ATLAS Quantum Financial System - Main Application

This is the main entry point for the ATLAS Quantum Financial System API.
"""

import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from .api import app as api_app
from .core.quantum_engine import QuantumEngine
from .core.transaction_processor import TransactionProcessor

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AppState:
    def __init__(self):
        self.quantum_engine = None
        self.transaction_processor = None


app_state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    logger.info("Initializing ATLAS Quantum Financial System...")
    app_state.quantum_engine = QuantumEngine(qubits=256)
    logger.info("Quantum Engine initialized")
    app_state.transaction_processor = TransactionProcessor(app_state.quantum_engine)
    logger.info("Transaction Processor initialized")
    yield
    logger.info("Shutting down ATLAS Quantum Financial System...")


app = FastAPI(
    title="ATLAS Quantum Financial System",
    description="\n    ATLAS (Advanced Transaction Ledger and Security) is a quantum-resistant\n    financial system designed for secure and scalable digital asset management.\n    \n    ## Features\n    - Quantum-resistant cryptography\n    - Secure transaction processing\n    - Multi-asset wallet management\n    - Quantum key generation and management\n    - Entangled quantum states for secure communication\n    ",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(
        f"Request completed: {request.method} {request.url} - {response.status_code}"
    )
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation Error", "errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )


app.include_router(api_app.router)


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "ATLAS Quantum Financial System",
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "ATLAS Quantum Financial System",
        "version": "1.0.0",
        "description": "Advanced Transaction Ledger and Security System with Quantum Resistance",
        "documentation": "/api/docs",
        "status": "operational",
    }


if __name__ == "__main__":
    import uvicorn
    from .config import PORT

    uvicorn.run(
        "v13.ATLAS.src.main:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,
        log_level="info",
    )
