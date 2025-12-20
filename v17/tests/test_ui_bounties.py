"""
Tests for Bounty UI Projection (v17) - Wiring & Parsing Only
"""

import os
import tempfile
from v15.evidence.bus import EvidenceBus
from v17.bounties.f_bounties import create_bounty
from v17.ui.bounty_projection import BountyProjection


def test_bounty_projection_structure():
    original_log = EvidenceBus._log_file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
        EvidenceBus._log_file = f.name
    try:
        EvidenceBus._chain_tip = "0" * 64

        # Create
        bounty = create_bounty("space_Z", "Struct Test", "Desc", 500, "0xOwner", 1000)

        projection = BountyProjection(bus=EvidenceBus)

        # Verify List
        bounties = projection.list_bounties()
        assert len(bounties) == 1
        assert bounties[0]["id"] == bounty.bounty_id

        # Verify Detail
        timeline = projection.get_bounty_timeline(bounty.bounty_id)
        assert timeline["info"]["title"] == "Struct Test"
        assert len(timeline["timeline"]) == 1  # Created

    finally:
        EvidenceBus._log_file = original_log
        if os.path.exists(f.name):
            os.unlink(f.name)


if __name__ == "__main__":
    test_bounty_projection_structure()
