"""
Integration Test for Admin Dashboard (v17 UI Layer)

Verifies that AdminDashboard correctly delegates to v17 projections.
"""

import os
import tempfile
from v15.evidence.bus import EvidenceBus
from v15.ui.admin_dashboard import AdminDashboard
from v17.governance.f_proposals import create_proposal
from v17.governance.schemas import GovernanceConfig


def test_admin_dashboard_integration():
    # 1. Setup
    original_log = EvidenceBus._log_file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
        EvidenceBus._log_file = f.name

    try:
        EvidenceBus._chain_tip = "0" * 64
        dashboard = AdminDashboard()

        # 2. Add Data
        config = GovernanceConfig(
            quorum_threshold=0.3, approval_threshold=0.5, voting_period_seconds=1000
        )
        create_proposal("space_X", "0xAdmin", "Integration Test", "Body", 1000, config)

        # 3. Test Governance Dashboard
        gov_view = dashboard.get_governance_dashboard()
        assert gov_view["count"] == 1
        assert gov_view["proposals"][0]["title"] == "Integration Test"

        # 4. Test Bounty Dashboard (empty)
        bounty_view = dashboard.get_bounty_dashboard()
        assert bounty_view["count"] == 0

        print("✅ AdminDashboard Integration Verified")

    finally:
        EvidenceBus._log_file = original_log
        if os.path.exists(f.name):
            os.unlink(f.name)


if __name__ == "__main__":
    test_admin_dashboard_integration()
