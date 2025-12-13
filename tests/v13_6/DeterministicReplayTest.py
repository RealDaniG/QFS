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
from src.libs.governance.InfrastructureGovernance import InfrastructureGovernance


class DeterministicReplayTest:
    """
    V13.6 Deterministic Replay Test Suite.
    
    Validates NOD-I4: Given identical ledger state and telemetry inputs,
    NOD allocation must be bit-for-bit reproducible.
    """
    
    def __init__(self):
        self.cm = CertifiedMath
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
                "schema_version": "1.0",
                "block_height": 1000,
                "nodes": {
                    "node_001": {
                        "uptime_blocks": 1000,
                        "bandwidth_gb": 500,
                        "storage_tb": 10,
                        "health_score": 95
                    },
                    "node_002": {
                        "uptime_blocks": 950,
                        "bandwidth_gb": 450,
                        "storage_tb": 8,
                        "health_score": 90
                    },
                    "node_003": {
                        "uptime_blocks": 980,
                        "bandwidth_gb": 480,
                        "storage_tb": 9,
                        "health_score": 92
                    }
                }
            }
        elif scenario == "high_load":
            telemetry = {
                "schema_version": "1.0",
                "block_height": 2000,
                "nodes": {
                    "node_001": {"uptime_blocks": 2000, "bandwidth_gb": 1000, "storage_tb": 20, "health_score": 98},
                    "node_002": {"uptime_blocks": 1950, "bandwidth_gb": 950, "storage_tb": 18, "health_score": 96},
                    "node_003": {"uptime_blocks": 1980, "bandwidth_gb": 980, "storage_tb": 19, "health_score": 97},
                    "node_004": {"uptime_blocks": 1900, "bandwidth_gb": 900, "storage_tb": 17, "health_score": 94}
                }
            }
        else:  # degraded
            telemetry = {
                "schema_version": "1.0",
                "block_height": 500,
                "nodes": {
                    "node_001": {"uptime_blocks": 400, "bandwidth_gb": 200, "storage_tb": 5, "health_score": 75},
                    "node_002": {"uptime_blocks": 350, "bandwidth_gb": 150, "storage_tb": 4, "health_score": 70}
                }
            }
        
        # Generate deterministic hash
        telemetry_json = json.dumps(telemetry, sort_keys=True, separators=(',', ':'))
        snapshot_hash = hashlib.sha256(telemetry_json.encode('utf-8')).hexdigest()
        
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
                "public_key": f"pk_{node_id}",
                "registered_at": 0,
                "status": "active"
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
                print(f"  ❌ FAIL: Run {i} log hash mismatch")
            if result['nod_allocated'] != reference['nod_allocated']:
                all_identical = False
                print(f"  ❌ FAIL: Run {i} NOD allocation mismatch")
        
        if all_identical:
            print(f"  ✅ PASS: All {runs} runs produced identical results")
        
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
                proposer_node_id="node_001",
                proposal_type="storage_replication_factor",
                parameters={"new_value": 3},
                total_nod_supply=BigNum128.from_string("1000000.0"),
                registry_snapshot=registry_snapshot["registry"],
                telemetry_snapshot=aegis_snapshot["telemetry"],
                log_list=log_list,
                deterministic_timestamp=1000
            )
            
            # Cast votes
            governance.cast_vote(
                proposal_id=proposal_id,
                voter_node_id="node_001",
                vote=True,
                voting_power=BigNum128.from_string("400000.0"),
                log_list=log_list,
                deterministic_timestamp=1001
            )
            
            governance.cast_vote(
                proposal_id=proposal_id,
                voter_node_id="node_002",
                vote=True,
                voting_power=BigNum128.from_string("350000.0"),
                log_list=log_list,
                deterministic_timestamp=1002
            )
            
            # Tally votes
            tally_result = governance.tally_votes(
                proposal_id=proposal_id,
                total_nod_supply=BigNum128.from_string("1000000.0"),
                log_list=log_list,
                deterministic_timestamp=2000
            )
            
            # Generate log hash
            log_json = json.dumps(log_list, sort_keys=True, separators=(',', ':'))
            log_hash = hashlib.sha256(log_json.encode('utf-8')).hexdigest()
            
            results.append({
                "run": run + 1,
                "proposal_status": tally_result["status"],
                "votes_for": tally_result["votes_for"],
                "votes_against": tally_result["votes_against"],
                "log_hash": log_hash
            })
            
            print(f"  Run {run + 1}: Status = {tally_result['status']}, log_hash = {log_hash[:16]}...")
        
        # Verify bit-for-bit equality
        reference = results[0]
        all_identical = True
        
        for i, result in enumerate(results[1:], start=2):
            if result["log_hash"] != reference["log_hash"]:
                all_identical = False
                print(f"  ❌ FAIL: Run {i} log hash mismatch")
            if result["proposal_status"] != reference["proposal_status"]:
                all_identical = False
                print(f"  ❌ FAIL: Run {i} proposal status mismatch")
        
        if all_identical:
            print(f"  ✅ PASS: All {runs} runs produced identical results")
        
        return {
            "test": "governance_replay",
            "passed": all_identical,
            "runs": runs,
            "reference_log_hash": reference["log_hash"],
            "reference_status": reference["proposal_status"],
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
            "timestamp": "2025-12-13T12:45:00Z",
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "test_results": self.test_results,
            "nod_i4_compliance": passed_tests == total_tests
        }
        
        # Save evidence
        os.makedirs("evidence/v13.6", exist_ok=True)
        with open("evidence/v13.6/nod_replay_determinism.json", "w") as f:
            json.dump(evidence, f, indent=2, sort_keys=True)
        
        print(f"\n✅ Evidence saved: evidence/v13.6/nod_replay_determinism.json")
        
        return evidence


if __name__ == "__main__":
    test_suite = DeterministicReplayTest()
    results = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results["nod_i4_compliance"] else 1)
