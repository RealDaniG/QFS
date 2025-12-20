import pytest
from unittest.mock import patch, MagicMock
from v17.ui.social_projection import SocialProjection


class TestSocialProjection:
    @pytest.fixture
    def mock_events(self):
        return [
            {
                "event": {
                    "type": "GOV_PROPOSAL_CREATED",
                    "payload": {
                        "timestamp": 1000,
                        "proposal": {
                            "proposal_id": "prop_1",
                            "creator_wallet": "wallet_A",
                            "title": "Proposal A",
                        },
                    },
                }
            },
            {
                "event": {
                    "type": "GOV_VOTE_CAST",
                    "payload": {
                        "timestamp": 1001,
                        "vote": {
                            "proposal_id": "prop_1",
                            "voter_wallet": "wallet_B",
                            "choice": "approve",
                            "weight": 10.0,
                        },
                    },
                }
            },
            {
                "event": {
                    "type": "SOCIAL_THREAD_CREATED",
                    "payload": {
                        "timestamp": 1002,
                        "thread": {
                            "thread_id": "thread_1",
                            "space_id": "space_1",
                            "created_by": "wallet_B",
                            "title": "Discussion on Prop A",
                            "reference_id": "prop_1",
                            "reference_type": "proposal",
                        },
                    },
                }
            },
            {
                "event": {
                    "type": "SOCIAL_COMMENT_POSTED",
                    "payload": {
                        "timestamp": 1003,
                        "comment": {
                            "comment_id": "comm_1",
                            "thread_id": "thread_1",
                            "author_wallet": "wallet_A",
                            "content": "Thanks for support",
                        },
                    },
                }
            },
            {
                "event": {
                    "type": "SOCIAL_DISPUTE_OPENED",
                    "payload": {
                        "timestamp": 1004,
                        "dispute": {
                            "dispute_id": "disp_1",
                            "target_id": "prop_1",
                            "target_type": "proposal",
                            "raised_by": "wallet_B",
                            "reason": "Invalid quorum",
                            "status": "OPEN",
                        },
                    },
                }
            },
        ]

    def test_social_binding_structure(self, mock_events):
        with patch("v15.evidence.bus.EvidenceBus.get_events", return_value=mock_events):
            proj = SocialProjection()
            # Check binding for prop_1
            threads = proj.get_threads_for_entity("prop_1")

            assert len(threads) == 1
            assert threads[0]["thread_id"] == "thread_1"
            assert threads[0]["title"] == "Discussion on Prop A"

    def test_user_history_aggregation_wallet_A(self, mock_events):
        """Wallet A created proposal and commented."""
        with patch("v15.evidence.bus.EvidenceBus.get_events", return_value=mock_events):
            proj = SocialProjection()
            profile = proj.get_user_history("wallet_A")

            assert profile["wallet"] == "wallet_A"
            stats = profile["stats"]
            assert stats["proposals"] == 1
            assert stats["comments"] == 1
            assert stats["votes"] == 0

            timeline = profile["timeline"]
            assert len(timeline) == 2
            # Sort desc: comment (1003) then proposal (1000)
            assert timeline[0]["type"] == "comment"
            assert timeline[1]["type"] == "proposal_created"

    def test_user_history_aggregation_wallet_B(self, mock_events):
        """Wallet B voted, created thread, and raised dispute."""
        with patch("v15.evidence.bus.EvidenceBus.get_events", return_value=mock_events):
            proj = SocialProjection()
            profile = proj.get_user_history("wallet_B")

            stats = profile["stats"]
            assert stats["votes"] == 1
            assert stats["threads"] == 1
            assert stats["disputes_raised"] == 1

            timeline = profile["timeline"]
            assert len(timeline) == 3
            # Sort desc: dispute (1004), thread (1002), vote (1001)
            assert timeline[0]["type"] == "dispute"
            assert timeline[0]["status"] == "OPEN"
