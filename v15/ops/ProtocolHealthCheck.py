"""
ProtocolHealthCheck.py (v15 OPS) - Automated System Health Monitoring

Purpose:
Run periodic checks on the QFS v15 Governance & Economic stack to ensure
invariants are held and system is healthy.

KPIs:
1. AEGIS Coherence: MUST be PASS.
2. Proposal Activity: Count of Active/Executed.
3. Emission Safety: Check if current Binder Cap is within constitutional limits.
"""

import sys
import os
import json
from dataclasses import dataclass

# Path Setup
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
)

from v15.atlas.governance.GovernanceTrigger import GovernanceTrigger
from v15.atlas.governance.GovernanceParameterRegistry import GovernanceParameterRegistry
from v15.atlas.governance.ProposalEngine import ProposalEngine, ProposalStatus
from v15.atlas.aegis.GovernanceCoherenceCheck import GovernanceCoherenceCheck
from v13.libs.BigNum128 import BigNum128


@dataclass
class HealthStatus:
    status: str  # "HEALTHY", "DEGRADED", "CRITICAL"
    metrics: dict
    issues: list


class ProtocolHealthCheck:
    def __init__(self):
        self.registry = GovernanceParameterRegistry()
        self.trigger = GovernanceTrigger(self.registry)
        self.engine = ProposalEngine()
        self.aegis = GovernanceCoherenceCheck(self.registry, self.trigger)

    def run_check(self) -> HealthStatus:
        issues = []
        metrics = {}

        # 1. AEGIS Coherence Check (CRITICAL)
        is_coherent = self.aegis.verify_coherence()
        metrics["aegis_coherence"] = is_coherent
        if not is_coherent:
            issues.append(
                "CRITICAL: Active Parameters do not match Registry (AEGIS Fail)."
            )

        # 2. Governance Activity
        total_props = len(self.engine.proposals)
        executed_props = sum(
            1
            for p in self.engine.proposals.values()
            if p.status == ProposalStatus.EXECUTED
        )
        active_props = sum(
            1
            for p in self.engine.proposals.values()
            if p.status == ProposalStatus.ACTIVE
        )

        metrics["governance_total_proposals"] = total_props
        metrics["governance_executed"] = executed_props
        metrics["governance_active"] = active_props

        # 3. Emission Safety Check
        # Ensure VIRAL_POOL_CAP is not insane (e.g. > 10M)
        # This is a heuristic check for "Fat Finger" parameters
        current_cap = self.trigger.get_parameter("VIRAL_POOL_CAP")
        metrics["emission_viral_cap"] = current_cap.to_decimal_string()

        limit = BigNum128.from_int(10_000_000)
        if current_cap > limit:
            issues.append(
                f"WARNING: Viral Pool Cap {current_cap.to_decimal_string()} exceeds safety warning limit (10M)."
            )

        # Determine Overall Status
        status = "HEALTHY"
        if any("CRITICAL" in i for i in issues):
            status = "CRITICAL"
        elif issues:
            status = "DEGRADED"

        return HealthStatus(status, metrics, issues)


if __name__ == "__main__":
    checker = ProtocolHealthCheck()
    result = checker.run_check()

    print(
        json.dumps(
            {
                "status": result.status,
                "metrics": result.metrics,
                "issues": result.issues,
            },
            indent=2,
        )
    )

    if result.status == "CRITICAL":
        sys.exit(1)
    sys.exit(0)
