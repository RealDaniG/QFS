"""
ATLAS Quantum Financial System - Main Application

This is the main entry point for the ATLAS Quantum Financial System API.
"""

import os
import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

from .api import app as api_app
from .core.quantum_engine import QuantumEngine
from .core.transaction_processor import TransactionProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global application state
class AppState:
    def __init__(self):
        self.quantum_engine = None
        self.transaction_processor = None

app_state = AppState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info("Initializing ATLAS Quantum Financial System...")
    
    # Initialize quantum engine
    app_state.quantum_engine = QuantumEngine(qubits=256)
    logger.info("Quantum Engine initialized")
    
    # Initialize transaction processor with quantum engine
    app_state.transaction_processor = TransactionProcessor(app_state.quantum_engine)
    logger.info("Transaction Processor initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ATLAS Quantum Financial System...")

# Create FastAPI application
app = FastAPI(
    title="ATLAS Quantum Financial System",
    description="""
    ATLAS (Advanced Transaction Ledger and Security) is a quantum-resistant
    financial system designed for secure and scalable digital asset management.
    
    ## Features
    - Quantum-resistant cryptography
    - Secure transaction processing
    - Multi-asset wallet management
    - Quantum key generation and management
    - Entangled quantum states for secure communication
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Request completed: {request.method} {request.url} - {response.status_code}")
    return response

# Add exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation Error",
            "errors": exc.errors(),
        },
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )

# Include API routers
# The API app already mounts its routers under /api/v1/... so we do not add
# an extra /api prefix here (would lead to /api/api/v1/...).
app.include_router(api_app.router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "ATLAS Quantum Financial System"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "ATLAS Quantum Financial System",
        "version": "1.0.0",
        "description": "Advanced Transaction Ledger and Security System with Quantum Resistance",
        "documentation": "/api/docs",
        "status": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 8000))
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
