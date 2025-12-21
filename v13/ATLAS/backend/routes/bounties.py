from fastapi import APIRouter

router = APIRouter(prefix="/api/bounties", tags=["Bounties"])


@router.get("/active")
async def get_active_bounties():
    """Get active bounties."""
    return {
        "bounties": [
            {
                "id": "bounty_001",
                "title": "Test Beta Features",
                "description": "Thoroughly test all beta features and report bugs",
                "reward": 100,
                "token": "FLX",
                "status": "open",
                "created_at": 1703174400,
            }
        ]
    }
