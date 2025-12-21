from fastapi import APIRouter

router = APIRouter(prefix="/api/v18/spaces", tags=["spaces"])


@router.get("")
async def get_spaces_v18():
    return [
        {
            "id": "space_001",
            "name": "QFS Core",
            "description": "Primary protocol development and governance",
            "members": 142,
            "coherence_rank": 0.98,
            "rewardPool": 15420.50,
            "growthRate": 12.5,
            "isPublic": True,
            "isVerified": True,
            "tags": ["Development", "QFS", "Core"],
        },
        {
            "id": "space_002",
            "name": "Distributed AI",
            "description": "Integration of ATLAS with Open-A.G.I framework",
            "members": 89,
            "coherence_rank": 0.92,
            "rewardPool": 8750.25,
            "growthRate": 8.3,
            "isPublic": True,
            "isVerified": True,
            "tags": ["AI", "Agents", "Compute"],
        },
    ]


@router.post("/{space_id}/join")
async def join_space_v18(space_id: str):
    # In a real impl, this would update the user's graph
    return {"status": "joined", "space_id": space_id, "role": "member"}
