"""
HSMF-Enabled Wall Service - Economic Scoring for Social Actions

Wraps WallService with HSMF integration to compute action costs and
rewards for all social actions (posts, quotes, reactions).

Flow: post request → metrics extraction → HSMF evaluation → HSMFProof → post creation

Zero-Sim compliant: no floats, no randomness, deterministic throughout.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional

try:
    from v13.libs.BigNum128 import BigNum128
    from v13.libs.CertifiedMath import CertifiedMath
    from v13.core.HSMF import HSMF, HSMFProof
    from v13.services.hsmf_integration import HSMFIntegrationService, HSMFActionResult
    from v13.atlas.wall.wall_service import WallService
    from v13.atlas.wall.wall_models import Post, PostType, Visibility
except ImportError:
    from libs.BigNum128 import BigNum128
    from libs.CertifiedMath import CertifiedMath
    from core.HSMF import HSMF, HSMFProof
    from services.hsmf_integration import HSMFIntegrationService, HSMFActionResult
    from atlas.wall.wall_service import WallService
    from atlas.wall.wall_models import Post, PostType, Visibility


@dataclass
class ScoredPost:
    """
    Post with HSMF scoring attached.
    """

    post: Post
    hsmf_result: HSMFActionResult
    action_cost_met: bool  # True if user "paid" the action cost


class HSMFWallService:
    """
    Wall service with HSMF integration for economic scoring.

    Every social action (create_post, quote, reaction) is evaluated via HSMF:
    1. Extract metrics from user's token state
    2. Compute action cost and c_holo
    3. Emit HSMFProof for auditing
    4. Return scored result with post

    This service does NOT:
    - Mint or burn tokens directly
    - Modify TreasuryEngine state
    - Perform any non-deterministic operations
    """

    def __init__(
        self,
        cm: CertifiedMath,
        spaces_manager=None,
        hsmf_service: Optional[HSMFIntegrationService] = None,
    ):
        """
        Initialize HSMF-enabled wall service.

        Args:
            cm: CertifiedMath instance
            spaces_manager: Optional spaces manager for space validation
            hsmf_service: Optional HSMFIntegrationService (created if not provided)
        """
        self.cm = cm
        self.wall_service = WallService(cm, spaces_manager)
        self.hsmf_service = hsmf_service or HSMFIntegrationService(cm)

        # Default metrics for new users (can be overridden per-call)
        self.DEFAULT_S_CHR = BigNum128.from_int(1000)  # Starting coherence
        self.DEFAULT_LAMBDA1 = BigNum128.from_int(1)
        self.DEFAULT_LAMBDA2 = BigNum128.from_int(1)

    def create_scored_post(
        self,
        author_wallet: str,
        content: str,
        timestamp: int,
        user_metrics: Optional[Dict[str, Any]] = None,
        space_id: Optional[str] = None,
        post_type: PostType = PostType.STANDARD,
        visibility: Visibility = Visibility.PUBLIC,
        metadata: Optional[Dict[str, Any]] = None,
        log_list: Optional[List[Dict[str, Any]]] = None,
        pqc_cid: Optional[str] = None,
    ) -> ScoredPost:
        """
        Create a post with HSMF scoring.

        Args:
            author_wallet: User's wallet address
            content: Post content
            timestamp: Deterministic timestamp
            user_metrics: Optional dict with s_res, s_flx, s_psi_sync, f_atr, s_chr
            space_id: Optional space ID
            post_type: Type of post
            visibility: Visibility setting
            metadata: Optional metadata
            log_list: Audit log
            pqc_cid: PQC correlation ID

        Returns:
            ScoredPost with post and HSMF evaluation
        """
        if log_list is None:
            log_list = []

        # Generate action ID from wallet and timestamp
        action_id = f"post_{author_wallet[:8]}_{timestamp}"

        # Extract or default user metrics
        metrics = user_metrics or {}
        s_res = BigNum128.from_int(metrics.get("s_res", 0))
        s_flx = BigNum128.from_int(metrics.get("s_flx", 0))
        s_psi_sync = BigNum128.from_int(metrics.get("s_psi_sync", 0))
        f_atr = BigNum128.from_int(metrics.get("f_atr", 10))  # Default small ATR
        s_chr = BigNum128.from_int(metrics.get("s_chr", 1000))
        lambda1 = BigNum128.from_int(metrics.get("lambda1", 1))
        lambda2 = BigNum128.from_int(metrics.get("lambda2", 1))

        # Evaluate via HSMF
        hsmf_result = self.hsmf_service.process_action(
            action_id=action_id,
            user_id=author_wallet,
            s_res=s_res,
            s_flx=s_flx,
            s_psi_sync=s_psi_sync,
            f_atr=f_atr,
            s_chr=s_chr,
            lambda1=lambda1,
            lambda2=lambda2,
            log_list=log_list,
            pqc_cid=pqc_cid,
        )

        # Log HSMF evaluation for post
        log_list.append(
            {
                "operation": "hsmf_post_evaluation",
                "action_id": action_id,
                "action_cost": hsmf_result.action_cost.to_decimal_string(),
                "c_holo": hsmf_result.c_holo.to_decimal_string(),
                "is_valid": hsmf_result.is_valid,
            }
        )

        # Create the post (always, even if HSMF validation fails)
        # The scoring is advisory; rejection is policy-level
        post = self.wall_service.create_post(
            author_wallet=author_wallet,
            content=content,
            timestamp=timestamp,
            space_id=space_id,
            post_type=post_type,
            visibility=visibility,
            metadata=metadata,
            log_list=log_list,
        )

        return ScoredPost(
            post=post,
            hsmf_result=hsmf_result,
            action_cost_met=hsmf_result.is_valid,
        )

    def create_scored_quote(
        self,
        author_wallet: str,
        parent_post_id: str,
        content: str,
        timestamp: int,
        user_metrics: Optional[Dict[str, Any]] = None,
        log_list: Optional[List[Dict[str, Any]]] = None,
        pqc_cid: Optional[str] = None,
    ) -> ScoredPost:
        """
        Quote a post with HSMF scoring.

        Quotes have slightly higher f_atr by default (more engagement).
        """
        if log_list is None:
            log_list = []

        action_id = f"quote_{author_wallet[:8]}_{timestamp}"

        metrics = user_metrics or {}
        s_res = BigNum128.from_int(metrics.get("s_res", 0))
        s_flx = BigNum128.from_int(metrics.get("s_flx", 0))
        s_psi_sync = BigNum128.from_int(metrics.get("s_psi_sync", 0))
        f_atr = BigNum128.from_int(metrics.get("f_atr", 15))  # Higher for quotes
        s_chr = BigNum128.from_int(metrics.get("s_chr", 1000))
        lambda1 = BigNum128.from_int(metrics.get("lambda1", 1))
        lambda2 = BigNum128.from_int(metrics.get("lambda2", 1))

        hsmf_result = self.hsmf_service.process_action(
            action_id=action_id,
            user_id=author_wallet,
            s_res=s_res,
            s_flx=s_flx,
            s_psi_sync=s_psi_sync,
            f_atr=f_atr,
            s_chr=s_chr,
            lambda1=lambda1,
            lambda2=lambda2,
            log_list=log_list,
            pqc_cid=pqc_cid,
        )

        log_list.append(
            {
                "operation": "hsmf_quote_evaluation",
                "action_id": action_id,
                "parent_post_id": parent_post_id,
                "action_cost": hsmf_result.action_cost.to_decimal_string(),
            }
        )

        post = self.wall_service.quote_post(
            author_wallet=author_wallet,
            parent_post_id=parent_post_id,
            content=content,
            timestamp=timestamp,
            log_list=log_list,
        )

        return ScoredPost(
            post=post,
            hsmf_result=hsmf_result,
            action_cost_met=hsmf_result.is_valid,
        )

    def score_reaction(
        self,
        post_id: str,
        reactor_wallet: str,
        emoji: str,
        timestamp: int,
        user_metrics: Optional[Dict[str, Any]] = None,
        log_list: Optional[List[Dict[str, Any]]] = None,
        pqc_cid: Optional[str] = None,
    ) -> HSMFActionResult:
        """
        Score a reaction via HSMF (low-cost action).

        Reactions have minimal dissonance impact and low f_atr.
        """
        if log_list is None:
            log_list = []

        action_id = f"react_{reactor_wallet[:8]}_{timestamp}"

        metrics = user_metrics or {}
        s_res = BigNum128.from_int(metrics.get("s_res", 0))
        s_flx = BigNum128.from_int(metrics.get("s_flx", 0))
        s_psi_sync = BigNum128.from_int(metrics.get("s_psi_sync", 0))
        f_atr = BigNum128.from_int(metrics.get("f_atr", 1))  # Minimal for reactions
        s_chr = BigNum128.from_int(metrics.get("s_chr", 1000))
        lambda1 = BigNum128.from_int(metrics.get("lambda1", 1))
        lambda2 = BigNum128.from_int(metrics.get("lambda2", 1))

        hsmf_result = self.hsmf_service.process_action(
            action_id=action_id,
            user_id=reactor_wallet,
            s_res=s_res,
            s_flx=s_flx,
            s_psi_sync=s_psi_sync,
            f_atr=f_atr,
            s_chr=s_chr,
            lambda1=lambda1,
            lambda2=lambda2,
            log_list=log_list,
            pqc_cid=pqc_cid,
        )

        # Apply the reaction
        self.wall_service.add_reaction(
            post_id=post_id,
            reactor_wallet=reactor_wallet,
            emoji=emoji,
            log_list=log_list,
        )

        log_list.append(
            {
                "operation": "hsmf_reaction_evaluation",
                "action_id": action_id,
                "post_id": post_id,
                "emoji": emoji,
                "total_reward": hsmf_result.total_reward.to_decimal_string(),
            }
        )

        return hsmf_result


def test_hsmf_wall_integration():
    """Test the HSMF-enabled wall service."""
    cm = CertifiedMath()
    wall = HSMFWallService(cm)
    log_list: List[Dict[str, Any]] = []

    # Create a scored post
    result = wall.create_scored_post(
        author_wallet="0xalice123",
        content="Hello, QFS World!",
        timestamp=1000,
        user_metrics={"s_res": 10, "s_flx": 5, "s_chr": 900},
        log_list=log_list,
    )

    print(f"Post ID: {result.post.post_id}")
    print(f"Action Cost: {result.hsmf_result.action_cost.to_decimal_string()}")
    print(f"C_holo: {result.hsmf_result.c_holo.to_decimal_string()}")
    print(f"Total Reward: {result.hsmf_result.total_reward.to_decimal_string()}")
    print(f"Valid: {result.action_cost_met}")
    print(f"Log entries: {len(log_list)}")

    # Verify HSMFProof was emitted
    proof_entries = [e for e in log_list if e.get("op_name") == "hsmf_proof"]
    print(f"HSMFProof entries: {len(proof_entries)}")

    assert result.post is not None, "Post should be created"
    assert result.hsmf_result.is_valid, "HSMF result should be valid"
    assert len(proof_entries) == 1, "One HSMFProof should be emitted"

    print("\nHSMF Wall Integration Test PASSED")


if __name__ == "__main__":
    test_hsmf_wall_integration()
