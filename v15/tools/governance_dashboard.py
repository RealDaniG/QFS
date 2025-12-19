"""
governance_dashboard.py (v15) - Deterministic Governance Visibility CLI

Provides a read-only view of the current governance state.
Usage: python v15/tools/governance_dashboard.py
"""

import sys
import os
import json
from typing import Any

# Path Setup
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
)

from v15.atlas.governance.GovernanceTrigger import GovernanceTrigger
from v15.atlas.governance.GovernanceParameterRegistry import GovernanceParameterRegistry
from v15.atlas.governance.ProposalEngine import ProposalEngine


from v15.atlas.aegis.GovernanceCoherenceCheck import GovernanceCoherenceCheck


class GovernanceDashboard:
    def __init__(self):
        # In a real app, these would load from persistent storage/ledger
        self.registry = GovernanceParameterRegistry()
        self.trigger = GovernanceTrigger(self.registry)
        self.engine = ProposalEngine()
        self.aegis = GovernanceCoherenceCheck(self.registry, self.trigger)

    def render(self):
        print("\n" + "=" * 80)
        print("          QFS AUTONOMOUS GOVERNANCE DASHBOARD (v15) - OPERATOR VIEW")
        print("=" * 80 + "\n")

        # 0. System Health (AEGIS)
        print("--- [ SYSTEM HEALTH (AEGIS) ] ---")
        is_coherent = self.aegis.verify_coherence()
        status_icon = "✅ PASS" if is_coherent else "❌ FAIL"
        print(f"  Registry-Trigger Coherence: {status_icon}")
        if not is_coherent:
            print("  ⚠️  WARNING: Active Parameters do not match Registry! Check logs.")

        # 1. Active Snapshot (Effective Parameters)
        print("\n--- [ ACTIVE PARAMETERS (Epoch Based) ] ---")
        snapshot = self.trigger.current_snapshot()
        print(f"  Epoch Index: {snapshot.epoch_index}")
        for k, v in snapshot.parameters.items():
            print(
                f"  {k:<25}: {v.to_decimal_string() if hasattr(v, 'to_decimal_string') else v}"
            )

        # 2. Registry State (Approved / Next Epoch)
        print("\n--- [ APPROVED REGISTRY STATE (Pending Activation) ] ---")
        print("  (Parameters awaiting next epoch tick)")
        for k, v in self.registry._storage.items():
            print(
                f"  {k:<25}: {v.to_decimal_string() if hasattr(v, 'to_decimal_string') else v}"
            )

        # 3. Active Proposals
        print("\n--- [ ACTIVE PROPOSALS ] ---")
        if not self.engine.proposals:
            print("  (No active proposals)")
        else:
            for pid, prop in self.engine.proposals.items():
                print(
                    f"  ID: {pid[:12]}... | Kind: {prop.kind.value} | Status: {prop.status.value}"
                )
                print(f"  Votes: Yes={prop.tally.yes}, No={prop.tally.no}")

        # 4. PoE Artifacts (Recent)
        print("\n--- [ RECENT PROOF-OF-EXECUTION ARTIFACTS ] ---")
        # In a real system, we'd query a PoE Store. Here we mock check based on proposals.
        executed_count = sum(
            1 for p in self.engine.proposals.values() if p.status.value == "EXECUTED"
        )
        if executed_count == 0:
            print("  (No recent executions)")
        else:
            for pid, prop in self.engine.proposals.items():
                if prop.status.value == "EXECUTED":
                    # Mock retrieving the artifact hash
                    print(
                        f"  Proposal {pid[:8]}... -> Artifact: [HASH_CHAINED_PROOF_LOCATED_ON_LEDGER]"
                    )

        print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    dash = GovernanceDashboard()
    dash.render()
