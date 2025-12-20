import pytest
from unittest.mock import patch
from v17.ui.governance_projection import GovernanceProjection
from v17.ui.bounty_projection import BountyProjection
from v17.ui.social_projection import SocialProjection
from v17.bounties.schemas import BountyState, Bounty


@pytest.fixture
def mock_events_advisory():
    return [
        # Governance
        {
            "event": {
                "type": "GOV_PROPOSAL_CREATED",
                "payload": {
                    "proposal": {
                        "proposal_id": "p1",
                        "title": "Prop",
                        "created_at": 100,
                        "creator_wallet": "0xA",
                    }
                },
            }
        },
        {
            "event": {
                "type": "AGENT_ADVISORY_PROPOSAL",
                "payload": {
                    "signal": {
                        "target_id": "p1",
                        "score": 0.4,
                        "reasons": ["Risk"],
                        "model_version": "v1",
                    },
                    "timestamp": 101,
                },
            }
        },
        # Bounty
        {
            "event": {
                "type": "BOUNTY_CREATED",
                "payload": {
                    "bounty": {
                        "bounty_id": "b1",
                        "title": "Bug",
                        "created_at": 200,
                        "reward_amount": 100,
                        "currency": "QFS",
                    }
                },
            }
        },
        {
            "event": {
                "type": "AGENT_ADVISORY_BOUNTY",
                "payload": {
                    "signal": {
                        "target_id": "b1:0xA",  # Logic checks startswith(bounty_id)
                        "score": 0.9,
                        "reasons": ["Great work"],
                        "model_version": "v1",
                    },
                    "timestamp": 201,
                },
            }
        },
        # Social
        {
            "event": {
                "type": "SOCIAL_THREAD_CREATED",
                "payload": {"thread": {"thread_id": "t1", "reference_id": "p1"}},
            }
        },
        {
            "event": {
                "type": "AGENT_ADVISORY_SOCIAL",
                "payload": {
                    "signal": {"target_id": "t1", "score": 0.8},
                    "timestamp": 301,
                },
            }
        },
    ]


def test_governance_projection_advisory(mock_events_advisory):
    with patch(
        "v15.evidence.bus.EvidenceBus.get_events", return_value=mock_events_advisory
    ):
        proj = GovernanceProjection()
        props = proj.list_proposals()
        assert len(props) == 1
        p = props[0]
        assert "advisory" in p
        assert p["advisory"][0]["score"] == 0.4
        assert "Risk" in p["advisory"][0]["reasons"]


def test_bounty_projection_advisory(mock_events_advisory):
    # Mocking get_bounty_state to verify independent overlay logic
    with patch("v17.ui.bounty_projection.get_bounty_state") as mock_state:
        # returns state with bounty_id="b1"
        mock_state.return_value = BountyState(
            bounty=Bounty(
                bounty_id="b1",
                space_id="s1",
                title="Bug",
                description="Fix bug",
                created_by="0xA",
                reward_amount=100,
                currency="QFS",
                created_at=200,
            ),
            contributions=[],
            reward_decisions=[],
            advisory_signals=[],
        )

        with patch(
            "v15.evidence.bus.EvidenceBus.get_events", return_value=mock_events_advisory
        ):
            proj = BountyProjection()
            timeline = proj.get_bounty_timeline("b1")

            assert timeline is not None
            # Check for overlay item
            found_adv = False
            for item in timeline["timeline"]:
                if item.get("stage") == "Agent Suggestion":
                    assert "Score: 0.9" in item["description"]
                    found_adv = True

            assert found_adv


def test_social_projection_advisory(mock_events_advisory):
    with patch(
        "v15.evidence.bus.EvidenceBus.get_events", return_value=mock_events_advisory
    ):
        proj = SocialProjection()
        threads = proj.get_threads_for_entity("p1")
        assert len(threads) == 1
        t = threads[0]
        assert "advisory" in t
        assert t["advisory"][0]["score"] == 0.8
