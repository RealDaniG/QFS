"""
HSMF Wall Integration Tests

Tests for HSMF-enabled wall service ensuring:
1. Posts are created with HSMF scoring
2. HSMFProof is emitted for every post
3. Quotes and reactions are scored correctly
4. Determinism is maintained

References:
    - atlas/wall/hsmf_wall_service.py
    - services/hsmf_integration.py
    - docs/HSMF_MathContracts.md
"""

import pytest
from typing import Dict, List, Any

from v13.libs.CertifiedMath import CertifiedMath
from v13.atlas.wall.hsmf_wall_service import HSMFWallService, ScoredPost


class TestHSMFWallIntegration:
    """Test HSMF integration with wall posts."""

    @pytest.fixture
    def wall_service(self):
        cm = CertifiedMath()
        return HSMFWallService(cm)

    def test_scored_post_includes_hsmf_result(self, wall_service):
        """Creating a post should include HSMF evaluation."""
        log_list: List[Dict[str, Any]] = []

        result = wall_service.create_scored_post(
            author_wallet="0xtest123",
            content="Test post content",
            timestamp=1000,
            log_list=log_list,
        )

        assert isinstance(result, ScoredPost)
        assert result.post is not None
        assert result.hsmf_result is not None
        assert result.hsmf_result.action_cost.value > 0

    def test_scored_post_emits_hsmf_proof(self, wall_service):
        """Creating a post should emit HSMFProof to log."""
        log_list: List[Dict[str, Any]] = []

        wall_service.create_scored_post(
            author_wallet="0xtest456",
            content="Another test post",
            timestamp=2000,
            log_list=log_list,
        )

        proof_entries = [e for e in log_list if e.get("op_name") == "hsmf_proof"]
        assert len(proof_entries) == 1, "One HSMFProof should be emitted"
        assert "proof" in proof_entries[0]
        assert proof_entries[0]["proof"]["user_id"] == "0xtest456"

    def test_scored_post_deterministic(self, wall_service):
        """Same inputs should produce identical HSMF scores."""
        log_list_1: List[Dict[str, Any]] = []
        log_list_2: List[Dict[str, Any]] = []

        result_1 = wall_service.create_scored_post(
            author_wallet="0xdeterministic",
            content="Determinism test",
            timestamp=3000,
            user_metrics={"s_res": 100, "s_flx": 50, "s_chr": 800},
            log_list=log_list_1,
        )

        result_2 = wall_service.create_scored_post(
            author_wallet="0xdeterministic",
            content="Determinism test",
            timestamp=3000,
            user_metrics={"s_res": 100, "s_flx": 50, "s_chr": 800},
            log_list=log_list_2,
        )

        assert (
            result_1.hsmf_result.action_cost.value
            == result_2.hsmf_result.action_cost.value
        )
        assert result_1.hsmf_result.c_holo.value == result_2.hsmf_result.c_holo.value
        assert (
            result_1.hsmf_result.total_reward.value
            == result_2.hsmf_result.total_reward.value
        )

    def test_quote_has_higher_f_atr_default(self, wall_service):
        """Quotes should have higher default f_atr than posts."""
        log_list: List[Dict[str, Any]] = []

        # Create parent post
        post_result = wall_service.create_scored_post(
            author_wallet="0xauthor",
            content="Original post",
            timestamp=4000,
            log_list=log_list,
        )

        # Quote the post (with same user metrics but different action)
        quote_result = wall_service.create_scored_quote(
            author_wallet="0xquoter",
            parent_post_id=post_result.post.post_id,
            content="Quote of the post",
            timestamp=4001,
            log_list=log_list,
        )

        # Quote should have higher action cost due to higher f_atr
        assert (
            quote_result.hsmf_result.action_cost.value
            > post_result.hsmf_result.action_cost.value
        )

    def test_reaction_has_minimal_cost(self, wall_service):
        """Reactions should have minimal action cost."""
        log_list: List[Dict[str, Any]] = []

        # Create a post to react to
        post_result = wall_service.create_scored_post(
            author_wallet="0xposter",
            content="Post to react to",
            timestamp=5000,
            log_list=log_list,
        )

        # React to the post
        reaction_result = wall_service.score_reaction(
            post_id=post_result.post.post_id,
            reactor_wallet="0xreactor",
            emoji="👍",
            timestamp=5001,
            log_list=log_list,
        )

        # Reaction cost should be much lower than post cost
        assert (
            reaction_result.action_cost.value
            < post_result.hsmf_result.action_cost.value
        )

    def test_user_metrics_affect_scoring(self, wall_service):
        """Different user metrics should produce different scores."""
        log_list: List[Dict[str, Any]] = []

        # High coherence user (low dissonance)
        result_high = wall_service.create_scored_post(
            author_wallet="0xhigh",
            content="High coherence post",
            timestamp=6000,
            user_metrics={"s_res": 0, "s_flx": 0, "s_chr": 1000},
            log_list=log_list,
        )

        # Low coherence user (high dissonance)
        result_low = wall_service.create_scored_post(
            author_wallet="0xlow",
            content="Low coherence post",
            timestamp=6001,
            user_metrics={"s_res": 500, "s_flx": 300, "s_chr": 400},
            log_list=log_list,
        )

        # High coherence user should have higher c_holo
        assert (
            result_high.hsmf_result.c_holo.value > result_low.hsmf_result.c_holo.value
        )
        # High coherence user should have lower action cost
        assert (
            result_high.hsmf_result.action_cost.value
            < result_low.hsmf_result.action_cost.value
        )


class TestHSMFWallEdgeCases:
    """Edge case tests for HSMF wall integration."""

    @pytest.fixture
    def wall_service(self):
        cm = CertifiedMath()
        return HSMFWallService(cm)

    def test_zero_dissonance_user(self, wall_service):
        """User with zero dissonance should get c_holo = 1."""
        log_list: List[Dict[str, Any]] = []

        result = wall_service.create_scored_post(
            author_wallet="0xperfect",
            content="Perfect coherence post",
            timestamp=7000,
            user_metrics={"s_res": 0, "s_flx": 0, "s_psi_sync": 0, "s_chr": 1000},
            log_list=log_list,
        )

        from v13.libs.BigNum128 import BigNum128

        one = BigNum128.from_int(1)
        assert result.hsmf_result.c_holo.value == one.value

    def test_empty_metrics_uses_defaults(self, wall_service):
        """Empty metrics should use default values."""
        log_list: List[Dict[str, Any]] = []

        result = wall_service.create_scored_post(
            author_wallet="0xdefault",
            content="Default metrics post",
            timestamp=8000,
            user_metrics={},  # Empty
            log_list=log_list,
        )

        assert result.hsmf_result is not None
        assert result.hsmf_result.is_valid


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
