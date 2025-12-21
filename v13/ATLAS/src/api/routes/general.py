from fastapi import APIRouter

# These were at /api/v18/trending and /api/v18/bounties
# We can bundle them in a 'discovery' or general router.
router = APIRouter(prefix="/api/v18", tags=["general"])


@router.get("/trending")
async def get_trending_v18():
    return [
        {
            "id": "topic_1",
            "name": "QFS Transparency",
            "posts": 1247,
            "engagement": 8934,
            "growth": 45.2,
            "coherenceScore": 0.91,
        },
        {
            "id": "topic_2",
            "name": "Coherence Scoring",
            "posts": 892,
            "engagement": 6721,
            "growth": 32.8,
            "coherenceScore": 0.88,
        },
        {
            "id": "topic_3",
            "name": "Guard Systems",
            "posts": 645,
            "engagement": 5234,
            "growth": 28.5,
            "coherenceScore": 0.93,
        },
    ]


@router.get("/bounties")
async def get_bounties_v18():
    return [
        {
            "id": "bty_001",
            "title": "Optimize ASCON-128 Implementation",
            "description": "Reduce latency in session establishment for primary clusters.",
            "reward": 500.0,
            "status": "Open",
            "difficulty": "Hard",
            "type": "Engineering",
        },
        {
            "id": "bty_002",
            "title": "Draft Governance Policy for AI Agents",
            "description": "Define initial guard parameters for autonomous agent contributions.",
            "reward": 250.0,
            "status": "In Progress",
            "difficulty": "Medium",
            "type": "Policy",
        },
        {
            "id": "bty_003",
            "title": "Verify v18 Cluster Propagation",
            "description": "Run comprehensive node health check across all testnet clusters.",
            "reward": 100.0,
            "status": "Open",
            "difficulty": "Easy",
            "type": "Testing",
        },
    ]
