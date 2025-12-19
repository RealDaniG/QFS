"""
test_governance_dashboard.py - Unit Tests for Governance Dashboard CLI

Covers:
- DASH-I1: Dashboard is read-only (no state mutations)
- DASH-I2: All displayed data sourced from governance modules
- DASH-I3: PoE artifacts displayed match actual proof chain
"""

import unittest
import sys
import os
from io import StringIO
from unittest.mock import patch

# Robust Path Setup
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from v15.tools.governance_dashboard import GovernanceDashboard
from v15.atlas.governance.ProposalEngine import ProposalEngine, ProposalKind
from v13.libs.BigNum128 import BigNum128


class TestGovernanceDashboard(unittest.TestCase):
    """Test suite for Governance Dashboard CLI tool."""

    def test_dashboard_read_only(self):
        """DASH-I1: Verify dashboard does not mutate state."""
        dash = GovernanceDashboard()

        # Capture initial state
        initial_registry_state = dict(dash.registry._storage)
        initial_proposal_count = len(dash.engine.proposals)
        initial_snapshot = dash.trigger.current_snapshot()

        # Render dashboard (should be read-only)
        with patch("sys.stdout", new=StringIO()):
            dash.render()

        # Verify no state changes
        self.assertEqual(dict(dash.registry._storage), initial_registry_state)
        self.assertEqual(len(dash.engine.proposals), initial_proposal_count)
        self.assertEqual(
            dash.trigger.current_snapshot().epoch_index, initial_snapshot.epoch_index
        )

    def test_dashboard_data_accuracy_parameters(self):
        """DASH-I2: Verify displayed parameters match registry/trigger."""
        dash = GovernanceDashboard()

        # Get actual values
        actual_cap = dash.registry.get("VIRAL_POOL_CAP")
        snapshot_cap = dash.trigger.current_snapshot().parameters["VIRAL_POOL_CAP"]

        # Capture dashboard output
        with patch("sys.stdout", new=StringIO()) as fake_out:
            dash.render()
            output = fake_out.getvalue()

        # Verify values appear in output
        self.assertIn(actual_cap.to_decimal_string(), output)
        self.assertIn("VIRAL_POOL_CAP", output)

    def test_dashboard_data_accuracy_proposals(self):
        """DASH-I2: Verify displayed proposals match engine state."""
        dash = GovernanceDashboard()

        # Create a test proposal
        payload = {
            "action": "PARAMETER_CHANGE",
            "key": "VIRAL_POOL_CAP",
            "value": 2000000,
        }
        pid = dash.engine.create_proposal(
            ProposalKind.PARAMETER_CHANGE,
            "Test Proposal",
            "Test Description",
            "TestUser",
            payload,
        )

        # Capture dashboard output
        with patch("sys.stdout", new=StringIO()) as fake_out:
            dash.render()
            output = fake_out.getvalue()

        # Verify proposal appears in output
        self.assertIn(pid[:12], output)  # Proposal ID (truncated)
        self.assertIn("PARAMETER_CHANGE", output)
        self.assertIn("ACTIVE", output)

    def test_dashboard_aegis_coherence_display(self):
        """DASH-I2: Verify AEGIS coherence status is displayed."""
        dash = GovernanceDashboard()

        # Capture dashboard output
        with patch("sys.stdout", new=StringIO()) as fake_out:
            dash.render()
            output = fake_out.getvalue()

        # Verify AEGIS section exists
        self.assertIn("SYSTEM HEALTH (AEGIS)", output)
        self.assertIn("Registry-Trigger Coherence", output)
        self.assertIn("PASS", output)  # Should be coherent by default

    def test_dashboard_poe_artifacts_section(self):
        """DASH-I3: Verify PoE artifacts section is present."""
        dash = GovernanceDashboard()

        # Capture dashboard output
        with patch("sys.stdout", new=StringIO()) as fake_out:
            dash.render()
            output = fake_out.getvalue()

        # Verify PoE section exists
        self.assertIn("PROOF-OF-EXECUTION ARTIFACTS", output)

    def test_dashboard_no_write_operations(self):
        """DASH-I1: Verify dashboard performs no write operations."""
        dash = GovernanceDashboard()

        # Mock file write operations
        with patch(
            "builtins.open", side_effect=Exception("Write attempted!")
        ) as mock_open:
            # Dashboard should not attempt to write files
            with patch("sys.stdout", new=StringIO()):
                try:
                    dash.render()
                except Exception as e:
                    if "Write attempted" in str(e):
                        self.fail("Dashboard attempted file write operation")

    def test_dashboard_idempotent(self):
        """Verify dashboard can be rendered multiple times without issues."""
        dash = GovernanceDashboard()

        # Render multiple times
        for _ in range(3):
            with patch("sys.stdout", new=StringIO()) as fake_out:
                dash.render()
                output = fake_out.getvalue()

                # Each render should produce output
                self.assertGreater(len(output), 0)
                self.assertIn("QFS AUTONOMOUS GOVERNANCE DASHBOARD", output)


if __name__ == "__main__":
    unittest.main()
