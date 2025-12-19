"""
test_protocol_health_check.py - Unit Tests for Protocol Health Monitoring

Covers:
- HEALTH-I1: All metrics derived from deterministic, on-ledger data
- HEALTH-I2: Critical failures (AEGIS) return non-zero exit code
- HEALTH-I3: No external dependencies or network calls
"""

import unittest
import json
import sys
import os
from unittest.mock import Mock, patch

# Robust Path Setup
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from v15.ops.ProtocolHealthCheck import ProtocolHealthCheck, HealthStatus
from v15.atlas.governance.GovernanceParameterRegistry import GovernanceParameterRegistry
from v15.atlas.governance.GovernanceTrigger import GovernanceTrigger
from v15.atlas.governance.ProposalEngine import ProposalEngine
from v15.atlas.aegis.GovernanceCoherenceCheck import GovernanceCoherenceCheck
from v13.libs.BigNum128 import BigNum128


class TestProtocolHealthCheck(unittest.TestCase):
    """Test suite for ProtocolHealthCheck operational tool."""

    def test_health_check_deterministic_metrics(self):
        """HEALTH-I1: Verify all metrics are derived from deterministic sources."""
        checker = ProtocolHealthCheck()
        result = checker.run_check()

        # All metrics should be present
        self.assertIn("aegis_coherence", result.metrics)
        self.assertIn("governance_total_proposals", result.metrics)
        self.assertIn("governance_executed", result.metrics)
        self.assertIn("governance_active", result.metrics)
        self.assertIn("emission_viral_cap", result.metrics)

        # Metrics should be deterministic (same values on repeated calls)
        result2 = checker.run_check()
        self.assertEqual(result.metrics, result2.metrics)

    def test_health_check_aegis_pass(self):
        """HEALTH-I2: Verify AEGIS coherence pass results in HEALTHY status."""
        checker = ProtocolHealthCheck()
        result = checker.run_check()

        # With default state, AEGIS should be coherent
        self.assertTrue(result.metrics["aegis_coherence"])
        self.assertEqual(result.status, "HEALTHY")
        self.assertEqual(len(result.issues), 0)

    def test_health_check_aegis_fail_detection(self):
        """HEALTH-I2: Verify AEGIS coherence failure is detected and flagged."""
        # Create a scenario where AEGIS coherence would fail
        # by manually corrupting the trigger snapshot
        checker = ProtocolHealthCheck()

        # Manually corrupt the trigger's snapshot to simulate coherence failure
        # (In real scenario, this would be detected by AEGIS)
        with patch.object(checker.aegis, "verify_coherence", return_value=False):
            result = checker.run_check()

            self.assertFalse(result.metrics["aegis_coherence"])
            self.assertEqual(result.status, "CRITICAL")
            self.assertTrue(any("CRITICAL" in issue for issue in result.issues))

    def test_health_check_emission_safety_warning(self):
        """HEALTH-I2: Verify emission cap safety warnings are triggered."""
        checker = ProtocolHealthCheck()

        # Set an extremely high viral cap to trigger warning
        extreme_cap = BigNum128.from_int(15_000_000)
        checker.registry.update_parameter(
            "VIRAL_POOL_CAP", extreme_cap, "test_proposal"
        )
        checker.trigger.process_tick(100)  # Activate the change

        result = checker.run_check()

        # Should have warning but not be CRITICAL
        self.assertEqual(result.status, "DEGRADED")
        self.assertTrue(any("WARNING" in issue for issue in result.issues))

    def test_health_check_no_external_dependencies(self):
        """HEALTH-I3: Verify health check has no external dependencies."""
        checker = ProtocolHealthCheck()

        # Mock network calls to ensure none are made
        with (
            patch("urllib.request.urlopen") as mock_urlopen,
            patch("requests.get") as mock_requests,
        ):
            result = checker.run_check()

            # Verify no network calls were made
            mock_urlopen.assert_not_called()
            mock_requests.assert_not_called()

            # Health check should still succeed
            self.assertIsInstance(result, HealthStatus)

    def test_health_check_json_serializable(self):
        """Verify health check results are JSON serializable."""
        checker = ProtocolHealthCheck()
        result = checker.run_check()

        # Should be able to serialize to JSON
        try:
            json_str = json.dumps(
                {
                    "status": result.status,
                    "metrics": result.metrics,
                    "issues": result.issues,
                }
            )
            self.assertIsInstance(json_str, str)
        except (TypeError, ValueError) as e:
            self.fail(f"Health check result not JSON serializable: {e}")

    def test_health_check_idempotent(self):
        """Verify health check is idempotent (no side effects)."""
        checker = ProtocolHealthCheck()

        # Capture initial state
        initial_registry_state = dict(checker.registry._storage)
        initial_proposal_count = len(checker.engine.proposals)

        # Run health check multiple times
        for _ in range(3):
            checker.run_check()

        # Verify state unchanged
        self.assertEqual(dict(checker.registry._storage), initial_registry_state)
        self.assertEqual(len(checker.engine.proposals), initial_proposal_count)


if __name__ == "__main__":
    unittest.main()
