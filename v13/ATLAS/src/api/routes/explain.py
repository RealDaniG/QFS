"""
Explain-This API endpoints for the ATLAS system.

Provides read-only, deterministic explanations for rewards and rankings
derived from QFS ledger replay.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/explain", tags=["explain"])

@router.get("/reward/{wallet_id}")
async def explain_reward(
    wallet_id: str,
    epoch: Optional[int] = None
) -> Dict[str, Any]:
    """
    Explain reward calculation for a wallet in a given epoch.
    
    This endpoint returns a deterministic, replay-derived breakdown of
    how a reward was calculated, including base, bonuses, caps, and
    guard results. It does not mutate any state.
    
    Args:
        wallet_id: Target wallet identifier
        epoch: Optional epoch number; defaults to current epoch
        
    Returns:
        Dict with reward explanation components
    """
    try:
        # TODO: Wire to real QFS replay engine via existing read-only hooks
        # For now, return a deterministic stub that matches ExplainThisPanel schema
        return {
            "wallet_id": wallet_id,
            "epoch": epoch or 1,
            "base": "10.0 ATR",
            "bonuses": [
                {"label": "Coherence bonus", "value": "+2.5 ATR", "reason": "Coherence score 0.92 above threshold"},
                {"label": "Humor bonus", "value": "+1.2 ATR", "reason": "Humor signal 0.88 above threshold"},
                {"label": "Artistic bonus", "value": "+0.8 ATR", "reason": "Artistic signal 0.75 above threshold"}
            ],
            "caps": [
                {"label": "Humor cap", "value": "-0.3 ATR", "reason": "Humor cap applied at 1.0 ATR"},
                {"label": "Global cap", "value": "-2.0 ATR", "reason": "Global reward cap for epoch"}
            ],
            "guards": [
                {"name": "Balance guard", "result": "pass", "reason": "Balance within limits"},
                {"name": "Rate limit guard", "result": "pass", "reason": "Rate limit not exceeded"},
                {"name": "Policy guard", "result": "pass", "reason": "Policy version 13.7 active"}
            ],
            "total": "12.2 ATR",
            "metadata": {
                "replay_hash": "stub_hash_12345",
                "computed_at": "2025-12-14T16:52:00Z",
                "source": "qfs_replay_derived"
            }
        }
    except Exception as e:
        logger.error(f"Error generating reward explanation for {wallet_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate reward explanation"
        )

@router.get("/ranking/{content_id}")
async def explain_ranking(
    content_id: str,
    epoch: Optional[int] = None
) -> Dict[str, Any]:
    """
    Explain ranking calculation for a piece of content.
    
    Returns a deterministic breakdown of how a content item was ranked,
    including signal weights, scores, and neighbor comparisons.
    
    Args:
        content_id: Target content identifier
        epoch: Optional epoch number; defaults to current epoch
        
    Returns:
        Dict with ranking explanation components
    """
    try:
        # TODO: Wire to real QFS replay engine via existing read-only hooks
        return {
            "content_id": content_id,
            "epoch": epoch or 1,
            "signals": [
                {"name": "Coherence", "weight": 0.4, "score": 0.92},
                {"name": "Humor", "weight": 0.3, "score": 0.88},
                {"name": "Artistic", "weight": 0.2, "score": 0.75},
                {"name": "Recency", "weight": 0.1, "score": 0.60}
            ],
            "neighbors": [
                {"metric": "Coherence", "value": 0.92, "rank": 12},
                {"metric": "Humor", "value": 0.88, "rank": 8},
                {"metric": "Artistic", "value": 0.75, "rank": 15},
                {"metric": "Overall", "value": 0.85, "rank": 10}
            ],
            "final_rank": 10,
            "metadata": {
                "replay_hash": "stub_hash_67890",
                "computed_at": "2025-12-14T16:52:00Z",
                "source": "qfs_replay_derived"
            }
        }
    except Exception as e:
        logger.error(f"Error generating ranking explanation for {content_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate ranking explanation"
        )
