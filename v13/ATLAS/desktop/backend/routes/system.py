from fastapi import APIRouter

router = APIRouter(prefix="/api/system", tags=["System"])


@router.get("/stats")
async def get_system_stats():
    """Get system statistics."""
    return {
        "treasury": {
            "total_value_usd": 1000000,
            "flx_supply": 500000,
            "atr_supply": 250000,
        },
        "cycles": {"current_cycle": 1, "cycle_progress": 0.35},
    }
