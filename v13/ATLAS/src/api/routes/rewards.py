from fastapi import APIRouter
from src.lib.storage import db

router = APIRouter(prefix="/api/v18/rewards", tags=["rewards"])


@router.get("/streak")
async def get_streak_v18(wallet: str):
    cycle = db.get_cycle(wallet)
    if not cycle:
        return {"active": False, "day_index": 0, "current_reward": 0}

    return {
        "active": cycle["status"] == "active",
        "day_index": cycle["day_index"],
        "current_reward": cycle["total_reward"],
        "next_window": (cycle["last_window_id"] + 1) * 86400,
    }
