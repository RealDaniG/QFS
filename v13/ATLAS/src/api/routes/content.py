from fastapi import APIRouter
from src.lib.storage import db

# Router for /api/v18/content/...
router = APIRouter(prefix="/api/v18/content", tags=["content"])

# Router for /api/v18/... (discovery items like trending, activity)
discovery_router = APIRouter(tags=["discovery"])


@discovery_router.get("/recommendations")
async def get_recommendations_v18():
    return [
        {
            "type": "space",
            "name": "QFS Core",
            "reason": "Primary protocol development hub",
            "match": 98,
        },
        {
            "type": "topic",
            "name": "Transparent Governance",
            "reason": "Trending in your network",
            "match": 87,
        },
        {
            "type": "space",
            "name": "Economic Modeling",
            "reason": "Similar members have joined",
            "match": 82,
        },
    ]


@discovery_router.get("/trending")
async def get_trending_v18():
    return [
        {
            "id": "t1",
            "name": "QFS Implementation",
            "posts": 1250,
            "engagement": 5400,
            "growth": 23,
            "coherenceScore": 0.95,
        },
        {
            "id": "t2",
            "name": "Zero-Sim Compliance",
            "posts": 890,
            "engagement": 3200,
            "growth": 15,
            "coherenceScore": 0.92,
        },
        {
            "id": "t3",
            "name": "Algorithmic Guards",
            "posts": 650,
            "engagement": 2100,
            "growth": 8,
            "coherenceScore": 0.88,
        },
    ]


@discovery_router.get("/activity")
async def get_activity_v18():
    return [
        {
            "action": "New post in QFS Developers",
            "user": "Alice Chen",
            "time": "2 minutes ago",
            "type": "content",
        },
        {
            "action": 'Space "Transparency Advocates" reached 1K members',
            "user": "System",
            "time": "15 minutes ago",
            "type": "milestone",
        },
        {
            "action": 'Trending topic: "Guard Systems"',
            "user": "Network",
            "time": "1 hour ago",
            "type": "trending",
        },
        {
            "action": "New governance proposal submitted",
            "user": "Bob Martinez",
            "time": "2 hours ago",
            "type": "governance",
        },
    ]


@router.get("/feed")
async def get_content_feed_v18(limit: int = 20):
    # Return a list of recent messages as feed items
    messages = db.get_messages()
    return [
        {
            "id": m["id"],
            "content_hash": f"QmHash{m['id']}",
            "sender": m["sender"],
            "content": m["text"],
            "timestamp": m["timestamp"],
        }
        for m in messages[-limit:]
    ]


# Also adding the trending/bounties routes here or separate?
# The original file had /api/v18/trending and /api/v18/bounties at root level or similar.
# Let's put them here or in a 'discovery.py' or 'misc.py'.
# The user plan didn't specify 'discovery.py'.
# I will put trending and bounties in this file but mapped to /api/v18/trending etc if possible,
# OR I'll make a new discovery.py.
# Actually, the user plan had `content.py`.
# I'll just put them here as root-level v18 endpoints if I can, or grouped.
# To match original exact paths `/api/v18/trending`, I should probably use a separate router or just add them here with absolute paths if FastAPI allows, or just `discovery.py` mapped to `/api/v18`.

# Let's create a separate router for 'discovery' items (trending, bounties) in this file
# or just map them under generic `router` with full path override if needed,
# OR just generally assume they fall under "content" conceptually.
# Original: /api/v18/trending -> I'll stick to that.
