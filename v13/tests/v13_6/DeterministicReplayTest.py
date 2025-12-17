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
from fractions import Fraction
from libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
import json
import hashlib
from typing import Dict, Any, List
from v13.libs.BigNum128 import BigNum128
from v13.libs.CertifiedMath import CertifiedMath
from v13.libs.governance.NODAllocator import NODAllocator
from v13.libs.governance.InfrastructureGovernance import InfrastructureGovernance, GovernanceProposalType

class DeterministicReplayTest:
    """
    V13.6 Deterministic Replay Test Suite.
    
    Validates NOD-I4: Given identical ledger state and telemetry inputs,
    NOD allocation must be bit-for-bit reproducible.
    """

    def __init__(self):
        self.cm = CertifiedMath()
        self.test_results = []

    def create_deterministic_aegis_snapshot(self, scenario: str='baseline') -> Dict[str, Any]:
        """
        Create deterministic AEGIS telemetry snapshot for testing.
        
        Args:
            scenario: Test scenario ("baseline", "high_load", "degraded")
            
        Returns:
            Dict with telemetry snapshot + SHA-256 hash
        """
        if scenario == 'baseline':
            telemetry = {'schema_version': 'v1.0', 'block_height': 1000, 'nodes': {'node_001': {'uptime_ratio': Fraction(19, 20), 'health_score': Fraction(19, 20)}, 'node_002': {'uptime_ratio': Fraction(93, 100), 'health_score': Fraction(9, 10)}, 'node_003': {'uptime_ratio': Fraction(47, 50), 'health_score': Fraction(23, 25)}}}
        elif scenario == 'high_load':
            telemetry = {'schema_version': 'v1.0', 'block_height': 2000, 'nodes': {'node_001': {'uptime_ratio': Fraction(49, 50), 'health_score': Fraction(49, 50)}, 'node_002': {'uptime_ratio': Fraction(24, 25), 'health_score': Fraction(24, 25)}, 'node_003': {'uptime_ratio': Fraction(97, 100), 'health_score': Fraction(97, 100)}, 'node_004': {'uptime_ratio': Fraction(47, 50), 'health_score': Fraction(47, 50)}}}
        else:
            telemetry = {'schema_version': 'v1.0', 'block_height': 500, 'nodes': {'node_001': {'uptime_ratio': Fraction(91, 100), 'health_score': Fraction(81, 100)}, 'node_002': {'uptime_ratio': Fraction(9, 10), 'health_score': Fraction(4, 5)}}}
        telemetry_json = json.dumps(telemetry, sort_keys=True, separators=(',', ':'))
        snapshot_hash = hashlib.sha256(telemetry_json.encode('utf-8')).hexdigest()
        telemetry['telemetry_hash'] = snapshot_hash
        return {'telemetry': telemetry, 'snapshot_hash': snapshot_hash}

    def create_registry_snapshot(self, node_ids: List[str]) -> Dict[str, Any]:
        """
        Create deterministic AEGIS registry snapshot.
        
        Args:
            node_ids: List of node IDs to include
            
        Returns:
            Dict with registry snapshot + SHA-256 hash
        """
        registry = {'schema_version': '1.0', 'nodes': {}}
        for node_id in sorted(node_ids):
            registry['nodes'][node_id] = {'pqc_public_key': f'pk_{node_id}', 'pqc_scheme': 'Dilithium5', 'registered_at': 0, 'status': 'active', 'revoked': False}
        registry_json = json.dumps(registry, sort_keys=True, separators=(',', ':'))
        snapshot_hash = hashlib.sha256(registry_json.encode('utf-8')).hexdigest()
        return {'registry': registry, 'snapshot_hash': snapshot_hash}

    def test_nod_allocation_replay(self, runs: int=3) -> Dict[str, Any]:
        """
        Test NOD allocation deterministic replay.
        
        Runs NOD allocation multiple times with identical inputs and asserts
        bit-for-bit equality.
        
        Args:
            runs: Number of replay runs (default: 3)
            
        Returns:
            Test result dict with pass/fail and evidence
        """
        print(f'\n[TEST] NOD Allocation Replay ({runs} runs)')
        aegis_snapshot = self.create_deterministic_aegis_snapshot('baseline')
        registry_snapshot = self.create_registry_snapshot(['node_001', 'node_002', 'node_003'])
        atr_fees = BigNum128.from_string('1000000.0')
        results = []
        for run in range(runs):
            log_list = []
            allocator = NODAllocator(self.cm)
            allocation_result = allocator.allocate_from_atr_fees(atr_total_fees=atr_fees, node_contributions={'node_001': BigNum128.from_string('500'), 'node_002': BigNum128.from_string('300'), 'node_003': BigNum128.from_string('200')}, registry_snapshot=registry_snapshot['registry'], telemetry_snapshot=aegis_snapshot['telemetry'], log_list=log_list, deterministic_timestamp=1000)
            total_nod = BigNum128(0)
            for alloc in sorted(allocation_result):
                total_nod = self.cm.add(total_nod, alloc.nod_amount, log_list)
            log_json = json.dumps(log_list, sort_keys=True, separators=(',', ':'))
            log_hash = hashlib.sha256(log_json.encode('utf-8')).hexdigest()
            results.append({'run': run + 1, 'nod_allocated': total_nod.to_decimal_string(), 'node_allocations': [{'node_id': a.node_id, 'amount': a.nod_amount.to_decimal_string()} for a in allocation_result], 'log_hash': log_hash, 'telemetry_snapshot_hash': aegis_snapshot['snapshot_hash'], 'registry_snapshot_hash': registry_snapshot['snapshot_hash']})
            print(f'  Run {run + 1}: NOD allocated = {total_nod.to_decimal_string()}, log_hash = {log_hash[:16]}...')
        reference = results[0]
        all_identical = True
        for i, result in enumerate(results[1:], start=2):
            if result['log_hash'] != reference['log_hash']:
                all_identical = False
                print(f'  [FAIL] Run {i} log hash mismatch')
            if result['nod_allocated'] != reference['nod_allocated']:
                all_identical = False
                print(f'  [FAIL] Run {i} NOD allocation mismatch')
        if all_identical:
            print(f'  [PASS] All {runs} runs produced identical results')
        return {'test': 'nod_allocation_replay', 'passed': all_identical, 'runs': runs, 'reference_log_hash': reference['log_hash'], 'reference_nod_allocated': reference['nod_allocated'], 'results': results}

    def test_governance_replay(self, runs: int=3) -> Dict[str, Any]:
        """
        Test infrastructure governance deterministic replay.
        
        Runs governance voting multiple times with identical inputs and asserts
        bit-for-bit equality.
        
        Args:
            runs: Number of replay runs (default: 3)
            
        Returns:
            Test result dict with pass/fail and evidence
        """
        print(f'\n[TEST] Governance Replay ({runs} runs)')
        aegis_snapshot = self.create_deterministic_aegis_snapshot('baseline')
        registry_snapshot = self.create_registry_snapshot(['node_001', 'node_002', 'node_003'])
        results = []
        for run in range(runs):
            log_list = []
            governance = InfrastructureGovernance(self.cm)
            proposal_id = governance.create_proposal(title='Storage Replication Factor Update', description='Propose updating storage replication factor', proposal_type=GovernanceProposalType.STORAGE_REPLICATION_FACTOR, proposer_node_id='node_001', parameters={'proposed_factor': 3}, total_nod_supply=BigNum128.from_string('1000000.0'), creation_timestamp=1000, voting_duration_blocks=100, registry_snapshot=registry_snapshot['registry'], telemetry_snapshot=aegis_snapshot['telemetry'], log_list=log_list)
            governance.cast_vote(proposal_id=proposal_id, voter_node_id='node_001', voter_nod_balance=BigNum128.from_string('400000.0'), vote_yes=True, timestamp=1001000000000000000000, log_list=log_list)
            governance.cast_vote(proposal_id=proposal_id, voter_node_id='node_002', voter_nod_balance=BigNum128.from_string('350000.0'), vote_yes=True, timestamp=1002000000000000000000, log_list=log_list)
            tally_passed = governance.tally_votes(proposal_id=proposal_id, timestamp=2700000000000000000001, log_list=log_list)
            log_json = json.dumps(log_list, sort_keys=True, separators=(',', ':'))
            log_hash = hashlib.sha256(log_json.encode('utf-8')).hexdigest()
            proposal = governance.proposals[proposal_id]
            results.append({'run': run + 1, 'proposal_passed': tally_passed, 'proposal_status': proposal.status.value, 'votes_for': proposal.yes_votes.to_decimal_string(), 'votes_against': proposal.no_votes.to_decimal_string(), 'log_hash': log_hash})
            print(f'  Run {run + 1}: Status = {proposal.status.value}, passed = {tally_passed}, log_hash = {log_hash[:16]}...')
        reference = results[0]
        all_identical = True
        for i, result in enumerate(results[1:], start=2):
            if result['log_hash'] != reference['log_hash']:
                all_identical = False
                print(f'  [FAIL] Run {i} log hash mismatch')
            if result['proposal_status'] != reference['proposal_status']:
                all_identical = False
                print(f'  [FAIL] Run {i} proposal status mismatch')
            if result['proposal_passed'] != reference['proposal_passed']:
                all_identical = False
                print(f'  [FAIL] Run {i} proposal passed mismatch')
        if all_identical:
            print(f'  [PASS] All {runs} runs produced identical results')
        return {'test': 'governance_replay', 'passed': all_identical, 'runs': runs, 'reference_log_hash': reference['log_hash'], 'reference_status': reference['proposal_status'], 'reference_passed': reference['proposal_passed'], 'results': results}

    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all deterministic replay tests.
        
        Returns:
            Complete test results
        """
        print('=' * 80)
        print('QFS V13.6 - Deterministic Replay Test Suite (NOD-I4)')
        print('=' * 80)
        nod_replay_result = self.test_nod_allocation_replay(runs=3)
        self.test_results.append(nod_replay_result)
        governance_replay_result = self.test_governance_replay(runs=3)
        self.test_results.append(governance_replay_result)
        passed_tests = sum((1 for r in self.test_results if r['passed']))
        total_tests = len(self.test_results)
        print('\n' + '=' * 80)
        print(f'SUMMARY: {passed_tests}/{total_tests} tests passed')
        print('=' * 80)
        evidence = {'test_suite': 'DeterministicReplayTest', 'version': 'V13.6', 'timestamp': '2025-12-13T15:00:00Z', 'total_tests': total_tests, 'passed_tests': passed_tests, 'test_results': self.test_results, 'nod_i4_compliance': passed_tests == total_tests}
        os.makedirs('evidence/v13_6', exist_ok=True)
        with open('evidence/v13_6/nod_replay_determinism.json', 'w') as f:
            json.dump(evidence, f, indent=2, sort_keys=True)
        print(f'\n[PASS] Evidence saved: evidence/v13.6/nod_replay_determinism.json')
        return evidence
if __name__ == '__main__':
    test_suite = DeterministicReplayTest()
    results = test_suite.run_all_tests()
    raise ZeroSimAbort(0 if results['nod_i4_compliance'] else 1)