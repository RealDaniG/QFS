"""
Explain-This API endpoints for the ATLAS system.

Provides read-only, deterministic explanations for rewards and rankings
derived from QFS ledger replay.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from typing import Dict, Any, Optional
import logging

from v13.core.observability.logger import TraceContext

# Import the value-node explainability helper
from v13.policy.value_node_explainability import ValueNodeExplainabilityHelper
from v13.policy.humor_policy import HumorSignalPolicy, HumorPolicy
from v13.core.QFSReplaySource import QFSReplaySource
from v13.core.QFSReplaySource import QFSReplaySource
from ..dependencies import get_replay_source, get_current_user
import os

logger = logging.getLogger(__name__)

# Enforce Live Sources in Production
EXPLAIN_THIS_SOURCE = os.getenv("EXPLAIN_THIS_SOURCE", "qfs_ledger")
if EXPLAIN_THIS_SOURCE != "qfs_ledger":
    # Fail closed if attempting to use insecure/mock sources in production
    raise RuntimeError(
        f"Audit Integrity Violation: EXPLAIN_THIS_SOURCE must be 'qfs_ledger', got '{EXPLAIN_THIS_SOURCE}'."
    )

router = APIRouter(prefix="/explain", tags=["explain"])

from v13.policy.artistic_policy import ArtisticSignalPolicy, ArtisticPolicy

# Initialize the explainability helper with a humor policy (as example)
humor_policy = HumorSignalPolicy(
    policy=HumorPolicy(
        enabled=True,
        mode="rewarding",
        dimension_weights={
            "chronos": 0.15,
            "lexicon": 0.10,
            "surreal": 0.10,
            "empathy": 0.20,
            "critique": 0.15,
            "slapstick": 0.10,
            "meta": 0.20,
        },
        max_bonus_ratio=0.25,
        per_user_daily_cap_atr=1.0,
    )
)

artistic_policy = ArtisticSignalPolicy(
    policy=ArtisticPolicy(
        enabled=True,
        mode="rewarding",
        dimension_weights={
            "composition": 0.20,
            "originality": 0.25,
            "emotional_resonance": 0.25,
            "technical_execution": 0.15,
            "cultural_context": 0.15,
        },
        max_bonus_ratio=0.30,
        per_user_daily_cap_atr=2.0,
    )
)

explain_helper = ValueNodeExplainabilityHelper(humor_policy, artistic_policy)


@router.get("/reward/{wallet_id}")
async def explain_reward(
    wallet_id: str,
    request: Request,
    epoch: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    replay_source: QFSReplaySource = Depends(get_replay_source),
) -> Dict[str, Any]:
    """
    Explain reward calculation for a wallet in a given epoch.

    This endpoint returns a deterministic, replay-derived breakdown of
    how a reward was calculated, including base, bonuses, caps, and
    guard results. It does not mutate any state.

    Args:
        wallet_id: Target wallet identifier
        epoch: Optional epoch number; defaults to current epoch
        replay_source: Injected QFSReplaySource for zero-sim history

    Returns:
        Dict with reward explanation components
    """
    # Authorization check
    if wallet_id != current_user["wallet_id"]:
        # Check if user has audit permissions via AEGIS
        if "audit_all_explanations" not in current_user.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other users' reward explanations without audit permission",
            )

    try:
        # Extract Trace Context
        ctx = TraceContext.from_headers(request.headers)

        # Initialize Replay Engine with the helper
        from v13.policy.value_node_replay import ValueNodeReplayEngine

        replay_engine = ValueNodeReplayEngine(explain_helper)

        # LIVE LEDGER SOURCE: Fetch from QFS Ledger via ReplaySource
        events = replay_source.get_reward_events(wallet_id, epoch or 1)

        if not events:
            raise HTTPException(
                status_code=404,
                detail=f"No reward events found for wallet {wallet_id} in epoch {epoch or 1}",
            )

        # 1. Replay the events to build state (UserNode, etc.)
        replay_engine.replay_events(events)

        # 2. Ask the engine to explain the specific reward event
        # Find the ID of the RewardAllocated event we just fetched
        reward_event_id = next(
            (e["id"] for e in events if e["type"] == "RewardAllocated"), None
        )

        if not reward_event_id:
            raise HTTPException(
                status_code=404,
                detail="RewardAllocated event missing from history context",
            )

        explanation = replay_engine.explain_specific_reward(
            reward_event_id, events, trace_id=ctx.trace_id
        )

        if not explanation:
            raise HTTPException(
                status_code=404, detail="Failed to generate explanation from event"
            )

        # 3. Generate simplified explanation for the API response
        simplified = explain_helper.get_simplified_explanation(explanation)

        # 4. Return the structured response that matches the ExplainThisPanel schema
        return {
            "wallet_id": wallet_id,
            "epoch": epoch or 1,
            "base": simplified["breakdown"]["base_reward"]["ATR"],
            "bonuses": simplified["breakdown"]["bonuses"],
            "caps": simplified["breakdown"]["caps"],
            "guards": simplified["breakdown"]["guards"],
            "total": simplified["breakdown"]["total_reward"]["ATR"],
            "metadata": {
                "replay_hash": explanation.explanation_hash,
                "computed_at": events[-1][
                    "timestamp"
                ],  # Use timestamp of last event for determinism
                "source": "qfs_replay_verified",
            },
        }

        # Add artistic bonus if policy enabled (Optional Integration)
        if artistic_policy.policy.enabled:
            # Note: In a real scenario, we would need the dimensions from the event/replay.
            # This is a placeholder demonstration as requested by the prompt for integration structure.
            pass
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating reward explanation for {wallet_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate reward explanation: {str(e)}",
        )


def test_invalid_wallet_id():
    """Test reward explanation with invalid wallet ID."""
    from fastapi.testclient import TestClient
    from v13.ATLAS.src.api import app

    client = TestClient(app)

    # Test with empty wallet ID
    response = client.get("/explain/reward/")
    assert response.status_code == 404  # Not found due to missing path parameter

    # Test with special characters in wallet ID
    response = client.get("/explain/reward/wallet_123!@#$")
    # Should still work (we're not validating wallet ID format in this stub)


def test_edge_case_epoch_values():
    """Test reward explanation with edge case epoch values."""
    from fastapi.testclient import TestClient
    from v13.ATLAS.src.api import app

    client = TestClient(app)

    # Test with zero epoch
    response = client.get("/explain/reward/wallet_123?epoch=0")
    assert response.status_code == 200

    # Test with negative epoch
    response = client.get("/explain/reward/wallet_123?epoch=-1")
    assert response.status_code == 200

    # Test with very large epoch
    response = client.get("/explain/reward/wallet_123?epoch=999999999")
    assert response.status_code == 200


def test_ranking_explanation_edge_cases():
    """Test ranking explanation with edge cases."""
    from fastapi.testclient import TestClient
    from v13.ATLAS.src.api import app

    client = TestClient(app)

    # Test with empty content ID
    response = client.get("/explain/ranking/")
    assert response.status_code == 404  # Not found due to missing path parameter

    # Test with special characters in content ID
    response = client.get("/explain/ranking/content_123!@#$")
    assert response.status_code == 200  # Should still work

    # Test with edge case epoch values
    response = client.get("/explain/ranking/content_123?epoch=0")
    assert response.status_code == 200

    response = client.get("/explain/ranking/content_123?epoch=-5")
    assert response.status_code == 200


@router.get("/ranking/{content_id}")
async def explain_ranking(
    content_id: str,
    epoch: Optional[int] = None,
    replay_source: QFSReplaySource = Depends(get_replay_source),
) -> Dict[str, Any]:
    """
    Explain ranking calculation for a piece of content.

    Returns a deterministic breakdown of how a content item was ranked,
    including signal weights, scores, and neighbor comparisons.

    Args:
        content_id: Target content identifier
        epoch: Optional epoch number
        replay_source: Injected QFSReplaySource

    Returns:
        Dict with ranking explanation components
    """
    try:
        from v13.policy.value_node_replay import ValueNodeReplayEngine

        replay_engine = ValueNodeReplayEngine(explain_helper)

        # LIVE LEDGER SOURCE: Fetch from QFS Ledger
        events = replay_source.get_ranking_events(content_id)

        if not events:
            raise HTTPException(
                status_code=404,
                detail=f"No ranking events found for content {content_id}",
            )

        # Replay
        replay_engine.replay_events(events)

        explanation = replay_engine.explain_content_ranking(content_id, events)

        if not explanation:
            raise HTTPException(status_code=404, detail="Content ranking not found")

        return {
            "content_id": explanation.content_id,
            "epoch": explanation.epoch,
            "signals": explanation.signals,
            "neighbors": explanation.neighbors,
            "final_rank": explanation.final_rank,
            "metadata": {
                "replay_hash": explanation.explanation_hash,
                "computed_at": events[-1]["timestamp"] if events else 0,
                "source": "qfs_replay_verified",
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating ranking explanation for {content_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate ranking explanation: {str(e)}",
        )


@router.get("/storage/{content_id}")
async def explain_storage(
    content_id: str, replay_source: QFSReplaySource = Depends(get_replay_source)
) -> Dict[str, Any]:
    """
    Explain why specific nodes were selected for content storage.

    Returns deterministic proof of replica assignment logic and
    verification status of storage proofs.
    """
    try:
        from v13.policy.storage_explainability import explain_storage_placement

        # Fetch storage events
        events = replay_source.get_storage_events(content_id)
        if not events:
            raise HTTPException(
                status_code=404, detail=f"No storage history found for {content_id}"
            )

        # Generate explanation
        explanation = explain_storage_placement(content_id, events)

        return {
            "content_id": explanation.content_id,
            "replica_count": explanation.replica_count,
            "assigned_nodes": explanation.storage_nodes,
            "shards": explanation.shard_ids,
            "proof_outcomes": explanation.proof_outcomes,
            "metadata": {
                "epoch": explanation.epoch_assigned,
                "integrity_hash": explanation.integrity_hash,
                "explanation_hash": explanation.explanation_hash,
                "policy_version": explanation.policy_version,
                "source": "qfs_replay_verified",
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error explaining storage for {content_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate storage explanation: {str(e)}",
        )
