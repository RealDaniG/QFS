"""
AEGIS Main API Router

Aggregates all AEGIS service endpoints.
Mount this under /aegis in the main application.
"""

from fastapi import APIRouter
from .services import evidence_api
from .services import explanation_api
from .services import governance_map
from .governance import api as governance_api
from .sandbox import api as sandbox_api  # Added Track 5

api_router = APIRouter()

# Track 1: Evidence API
api_router.include_router(evidence_api.router, tags=["AEGIS Evidence"])

# Track 2: Governance API (Meta-Governance)
api_router.include_router(
    governance_api.router, prefix="/governance", tags=["AEGIS Meta-Governance"]
)

# Track 3: Explanation Controls
api_router.include_router(explanation_api.router, tags=["AEGIS Explanations"])

# Track 4: Governance Consequence Map
api_router.include_router(governance_map.router, tags=["AEGIS Analysis"])

# Track 5: Sandbox
api_router.include_router(sandbox_api.router, tags=["AEGIS Sandbox"])
