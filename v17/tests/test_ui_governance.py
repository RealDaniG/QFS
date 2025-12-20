"""
Tests for Governance UI Projection (v17) - Wiring & Parsing Only
"""

import os
import tempfile
from v15.evidence.bus import EvidenceBus
from v17.governance.schemas import GovernanceConfig
from v17.governance.f_proposals import create_proposal
from v17.ui.governance_projection import GovernanceProjection


def test_governance_projection_structure():
    original_log = EvidenceBus._log_file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
        EvidenceBus._log_file = f.name
    try:
        EvidenceBus._chain_tip = "0" * 64
        config = GovernanceConfig(
            quorum_threshold=0.3, approval_threshold=0.5, voting_period_seconds=1000
        )

        # Create
        prop = create_proposal(
            "space_Y", "0xOwner", "Structure Test", "Content", 1000, config
        )

        projection = GovernanceProjection(bus=EvidenceBus)

        # Verify List
        proposals = projection.list_proposals()
        assert len(proposals) == 1
        assert proposals[0]["id"] == prop.proposal_id

        # Verify Detail
        timeline = projection.get_proposal_timeline(prop.proposal_id, config)
        assert timeline["info"]["title"] == "Structure Test"
        assert len(timeline["timeline"]) == 1  # Created
        assert timeline["evidence_link"].startswith("/evidence")

    finally:
        EvidenceBus._log_file = original_log
        if os.path.exists(f.name):
            os.unlink(f.name)


if __name__ == "__main__":
    test_governance_projection_structure()
