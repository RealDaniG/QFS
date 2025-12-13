"""
DeterministicReplayTest.py - V13.6 NOD-I4 Deterministic Replay Verification

Tests that NOD allocation and infrastructure governance produce identical
results when run multiple times with the same inputs (AEGIS snapshots, ATR fees).

Success Criteria:
- Bit-for-bit identical NOD distributions across runs
- Identical log hashes across runs
- Identical governance outcomes across runs
- AEGIS snapshot hashes match across runs

Evidence Artifact: evidence/v13.6/nod_replay_determinism.json
"""

import json
import hashlib
from typing import Dict, Any, List
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.libs.BigNum128 import BigNum128
from src.libs.CertifiedMath import CertifiedMath
from src.libs.governance.NODAllocator import NODAllocator
from src.libs.governance.InfrastructureGovernance import InfrastructureGovernance, GovernanceProposalType


class DeterministicReplayTest:
    """
    V13.6 Deterministic Replay Test Suite.
    
    Validates NOD-I4: Given identical ledger state and telemetry inputs,
    NOD allocation must be bit-for-bit reproducible.
    """
    
    def __init__(self):
        self.cm = CertifiedMath()
        self.test_results = []
        
    def create_deterministic_aegis_snapshot(self, scenario: str = "baseline") -> Dict[str, Any]:
        """
        Create deterministic AEGIS telemetry snapshot for testing.
        
        Args:
            scenario: Test scenario ("baseline", "high_load", "degraded")
            
        Returns:
            Dict with telemetry snapshot + SHA-256 hash
        """
        if scenario == "baseline":
            telemetry = {
                "schema_version": "v1.0",
                "block_height": 1000,
                "nodes": {
                    "node_001": {
                        "uptime_ratio": 0.95,
                        "health_score": 0.95
                    },
                    "node_002": {
                        "uptime_ratio": 0.93,
                        "health_score": 0.90
                    },
                    "node_003": {
                        "uptime_ratio": 0.94,
                        "health_score": 0.92
                    }
                }
            }
        elif scenario == "high_load":
            telemetry = {
                "schema_version": "v1.0",
                "block_height": 2000,
                "nodes": {
                    "node_001": {"uptime_ratio": 0.98, "health_score": 0.98},
                    "node_002": {"uptime_ratio": 0.96, "health_score": 0.96},
                    "node_003": {"uptime_ratio": 0.97, "health_score": 0.97},
                    "node_004": {"uptime_ratio": 0.94, "health_score": 0.94}
                }
            }
        else:  # degraded
            telemetry = {
                "schema_version": "v1.0",
                "block_height": 500,
                "nodes": {
                    "node_001": {"uptime_ratio": 0.91, "health_score": 0.81},
                    "node_002": {"uptime_ratio": 0.90, "health_score": 0.80}
                }
            }
        
        # Generate deterministic hash
        telemetry_json = json.dumps(telemetry, sort_keys=True, separators=(',', ':'))
        snapshot_hash = hashlib.sha256(telemetry_json.encode('utf-8')).hexdigest()
        
        # Add telemetry_hash field required by AEGIS_Node_Verification
        telemetry["telemetry_hash"] = snapshot_hash
        
        return {
            "telemetry": telemetry,
            "snapshot_hash": snapshot_hash
        }
    
    def create_registry_snapshot(self, node_ids: List[str]) -> Dict[str, Any]:
        """
        Create deterministic AEGIS registry snapshot.
        
        Args:
            node_ids: List of node IDs to include
            
        Returns:
            Dict with registry snapshot + SHA-256 hash
        """
        registry = {
            "schema_version": "1.0",
            "nodes": {}
        }
        
        for node_id in node_ids:
            registry["nodes"][node_id] = {
                "pqc_public_key": f"pk_{node_id}",
                "pqc_scheme": "Dilithium5",
                "registered_at": 0,
                "status": "active",
                "revoked": False
            }
        
        # Generate deterministic hash
        registry_json = json.dumps(registry, sort_keys=True, separators=(',', ':'))
        snapshot_hash = hashlib.sha256(registry_json.encode('utf-8')).hexdigest()
        
        return {
            "registry": registry,
            "snapshot_hash": snapshot_hash
        }
    
    def test_nod_allocation_replay(self, runs: int = 3) -> Dict[str, Any]:
        """
        Test NOD allocation deterministic replay.
        
        Runs NOD allocation multiple times with identical inputs and asserts
        bit-for-bit equality.
        
        Args:
            runs: Number of replay runs (default: 3)
            
        Returns:
            Test result dict with pass/fail and evidence
        """
        print(f"\n[TEST] NOD Allocation Replay ({runs} runs)")
        
        # Create deterministic inputs
        aegis_snapshot = self.create_deterministic_aegis_snapshot("baseline")
        registry_snapshot = self.create_registry_snapshot(["node_001", "node_002", "node_003"])
        atr_fees = BigNum128.from_string("1000000.0")  # 1M ATR fees
        
        # Run allocation multiple times
        results = []
        for run in range(runs):
            log_list = []
            
            # Initialize NODAllocator
            allocator = NODAllocator(self.cm)
            
            # Run allocation
            allocation_result = allocator.allocate_from_atr_fees(
                atr_total_fees=atr_fees,
                node_contributions={"node_001": BigNum128.from_string("500"), "node_002": BigNum128.from_string("300"), "node_003": BigNum128.from_string("200")},
                registry_snapshot=registry_snapshot["registry"],
                telemetry_snapshot=aegis_snapshot["telemetry"],
                log_list=log_list,
                deterministic_timestamp=1000
            )
            
            # Calculate total NOD allocated
            total_nod = BigNum128(0)
            for alloc in allocation_result:
                total_nod = self.cm.add(total_nod, alloc.nod_amount, log_list)
            
            # Generate log hash
            log_json = json.dumps(log_list, sort_keys=True, separators=(',', ':'))
            log_hash = hashlib.sha256(log_json.encode('utf-8')).hexdigest()
            
            results.append({
                "run": run + 1,
                "nod_allocated": total_nod.to_decimal_string(),
                "node_allocations": [{'node_id': a.node_id, 'amount': a.nod_amount.to_decimal_string()} for a in allocation_result],
                "log_hash": log_hash,
                "telemetry_snapshot_hash": aegis_snapshot["snapshot_hash"],
                "registry_snapshot_hash": registry_snapshot["snapshot_hash"]
            })
            
            print(f"  Run {run + 1}: NOD allocated = {total_nod.to_decimal_string()}, log_hash = {log_hash[:16]}...")
        
        # Verify bit-for-bit equality
        reference = results[0]
        all_identical = True
        
        for i, result in enumerate(results[1:], start=2):
            if result["log_hash"] != reference["log_hash"]:
                all_identical = False
                print(f"  [FAIL] Run {i} log hash mismatch")
            if result['nod_allocated'] != reference['nod_allocated']:
                all_identical = False
                print(f"  [FAIL] Run {i} NOD allocation mismatch")
        
        if all_identical:
            print(f"  [PASS] All {runs} runs produced identical results")
        
        return {
            "test": "nod_allocation_replay",
            "passed": all_identical,
            "runs": runs,
            "reference_log_hash": reference["log_hash"],
            "reference_nod_allocated": reference['nod_allocated'],
            "results": results
        }
    
    def test_governance_replay(self, runs: int = 3) -> Dict[str, Any]:
        """
        Test infrastructure governance deterministic replay.
        
        Runs governance voting multiple times with identical inputs and asserts
        bit-for-bit equality.
        
        Args:
            runs: Number of replay runs (default: 3)
            
        Returns:
            Test result dict with pass/fail and evidence
        """
        print(f"\n[TEST] Governance Replay ({runs} runs)")
        
        # Create deterministic inputs
        aegis_snapshot = self.create_deterministic_aegis_snapshot("baseline")
        registry_snapshot = self.create_registry_snapshot(["node_001", "node_002", "node_003"])
        
        # Run governance multiple times
        results = []
        for run in range(runs):
            log_list = []
            
            # Initialize InfrastructureGovernance
            governance = InfrastructureGovernance(self.cm)
            
            # Create proposal
            proposal_id = governance.create_proposal(
                title="Storage Replication Factor Update",
                description="Propose updating storage replication factor",
                proposal_type=GovernanceProposalType.STORAGE_REPLICATION_FACTOR,
                proposer_node_id="node_001",
                parameters={"proposed_factor": 3},
                total_nod_supply=BigNum128.from_string("1000000.0"),
                creation_timestamp=1000,
                voting_duration_blocks=100,  # Short voting window for test
                registry_snapshot=registry_snapshot["registry"],
                telemetry_snapshot=aegis_snapshot["telemetry"],
                log_list=log_list
            )
            
            # Cast votes
            governance.cast_vote(
                proposal_id=proposal_id,
                voter_node_id="node_001",
                voter_nod_balance=BigNum128.from_string("400000.0"),
                vote_yes=True,
                timestamp=1001000000000000000000,  # 1001 + offset for BigNum128 scale
                log_list=log_list
            )
            
            governance.cast_vote(
                proposal_id=proposal_id,
                voter_node_id="node_002",
                voter_nod_balance=BigNum128.from_string("350000.0"),
                vote_yes=True,
                timestamp=1002000000000000000000,  # 1002 + offset for BigNum128 scale
                log_list=log_list
            )
            
            # Tally votes (after voting window ends)
            # voting_end_timestamp = 1000000000000000000000 + (100 * 17000000000000000000) = 2700000000000000000000
            tally_passed = governance.tally_votes(
                proposal_id=proposal_id,
                timestamp=2700000000000000000001,  # After voting window ends
                log_list=log_list
            )
            
            # Generate log hash
            log_json = json.dumps(log_list, sort_keys=True, separators=(',', ':'))
            log_hash = hashlib.sha256(log_json.encode('utf-8')).hexdigest()
            
            # Get proposal object to extract vote counts
            proposal = governance.proposals[proposal_id]
            results.append({
                "run": run + 1,
                "proposal_passed": tally_passed,
                "proposal_status": proposal.status.value,
                "votes_for": proposal.yes_votes.to_decimal_string(),
                "votes_against": proposal.no_votes.to_decimal_string(),
                "log_hash": log_hash
            })
            
            print(f"  Run {run + 1}: Status = {proposal.status.value}, passed = {tally_passed}, log_hash = {log_hash[:16]}...")
        
        # Verify bit-for-bit equality
        reference = results[0]
        all_identical = True
        
        for i, result in enumerate(results[1:], start=2):
            if result["log_hash"] != reference["log_hash"]:
                all_identical = False
                print(f"  [FAIL] Run {i} log hash mismatch")
            if result["proposal_status"] != reference["proposal_status"]:
                all_identical = False
                print(f"  [FAIL] Run {i} proposal status mismatch")
            if result["proposal_passed"] != reference["proposal_passed"]:
                all_identical = False
                print(f"  [FAIL] Run {i} proposal passed mismatch")
        
        if all_identical:
            print(f"  [PASS] All {runs} runs produced identical results")
        
        return {
            "test": "governance_replay",
            "passed": all_identical,
            "runs": runs,
            "reference_log_hash": reference["log_hash"],
            "reference_status": reference["proposal_status"],
            "reference_passed": reference["proposal_passed"],
            "results": results
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all deterministic replay tests.
        
        Returns:
            Complete test results
        """
        print("=" * 80)
        print("QFS V13.6 - Deterministic Replay Test Suite (NOD-I4)")
        print("=" * 80)
        
        # Test 1: NOD Allocation Replay
        nod_replay_result = self.test_nod_allocation_replay(runs=3)
        self.test_results.append(nod_replay_result)
        
        # Test 2: Governance Replay
        governance_replay_result = self.test_governance_replay(runs=3)
        self.test_results.append(governance_replay_result)
        
        # Summary
        passed_tests = sum(1 for r in self.test_results if r["passed"])
        total_tests = len(self.test_results)
        
        print("\n" + "=" * 80)
        print(f"SUMMARY: {passed_tests}/{total_tests} tests passed")
        print("=" * 80)
        
        # Generate evidence artifact
        evidence = {
            "test_suite": "DeterministicReplayTest",
            "version": "V13.6",
            "timestamp": "2025-12-13T15:00:00Z",  # Updated timestamp
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "test_results": self.test_results,
            "nod_i4_compliance": passed_tests == total_tests
        }
        
        # Save evidence
        os.makedirs("evidence/v13_6", exist_ok=True)
        with open("evidence/v13_6/nod_replay_determinism.json", "w") as f:
            json.dump(evidence, f, indent=2, sort_keys=True)
        
        print(f"\n[PASS] Evidence saved: evidence/v13.6/nod_replay_determinism.json")
        
        return evidence


if __name__ == "__main__":
    test_suite = DeterministicReplayTest()
    results = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results["nod_i4_compliance"] else 1)
