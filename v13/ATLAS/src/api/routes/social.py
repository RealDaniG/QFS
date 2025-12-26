from fastapi import APIRouter
from typing import List, Dict, Any
from v13.atlas.social.models import SocialRewardReceipt, SocialEpoch

router = APIRouter(prefix="/api/v13/social", tags=["social"])

import json
import os
from pathlib import Path

# Production: Load from SocialGovernance storage path
# For strict zero-sim compliance, we read from a deterministic file store.
STORAGE_PATH = Path("v13/atlas/storage/social_state.json")


def _load_state() -> Dict[str, Any]:
    if not STORAGE_PATH.exists():
        return {"epochs": {}, "rewards": {}}
    try:
        with open(STORAGE_PATH, "r") as f:
            return json.load(f)
    except Exception:
        # Fallback for resiliency
        return {"epochs": {}, "rewards": {}}


@router.get("/epochs", response_model=List[Dict[str, Any]])
async def list_epochs():
    """
    List social reward epochs from persistent state.
    """
    state = _load_state()
    # Return values sorted by id desc
    epochs = list(state.get("epochs", {}).values())
    epochs.sort(key=lambda x: x["id"], reverse=True)
    return epochs


@router.get("/epochs/{epoch_id}/rewards", response_model=List[Dict[str, Any]])
async def get_epoch_rewards(epoch_id: int):
    """
    Get detailed per-post rewards for an epoch from persistent state.
    """
    state = _load_state()
    rewards_map = state.get("rewards", {})
    epoch_rewards = rewards_map.get(str(epoch_id), [])
    return epoch_rewards
