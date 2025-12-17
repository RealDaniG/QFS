# Zero-Sim Manual Review Queue

Total items requiring manual review: 1529

## GLOBAL_MUTATION (150)
- **v13/AEGIS\__init__.py:15**
  - Code: `__version__ = "0.1.0"`
  - Reasoning: Global assignment to '__version__' forbidden

- **v13/AEGIS\__init__.py:16**
  - Code: `__contract_version__ = "AEGIS_ADVISORY_CONTRACT_v1.0"`
  - Reasoning: Global assignment to '__contract_version__' forbidden

- **v13/AEGIS\__init__.py:25**
  - Code: `__all__ = ["models", "governance", "services", "sandbox", "ui_contracts"]`
  - Reasoning: Global assignment to '__all__' forbidden

- **v13/AEGIS\governance\proposals.py:40**
  - Code: `json_schema_extra = {`
  - Reasoning: Global assignment to 'json_schema_extra' forbidden

- **v13/AEGIS\governance\__init__.py:8**
  - Code: `__all__ = ["model_registry", "proposals"]`
  - Reasoning: Global assignment to '__all__' forbidden

- **v13/AEGIS\models\__init__.py:7**
  - Code: `__all__ = []`
  - Reasoning: Global assignment to '__all__' forbidden

- **v13/AEGIS\sandbox\__init__.py:8**
  - Code: `__all__ = ["engine", "assistant"]`
  - Reasoning: Global assignment to '__all__' forbidden

- **v13/AEGIS\services\evidence_models.py:50**
  - Code: `json_schema_extra = {`
  - Reasoning: Global assignment to 'json_schema_extra' forbidden

- **v13/AEGIS\services\governance_map.py:27**
  - Code: `router = APIRouter()`
  - Reasoning: Global assignment to 'router' forbidden

- **v13/AEGIS\services\__init__.py:8**
  - Code: `__all__ = ["evidence_service", "explanation_service", "governance_map"]`
  - Reasoning: Global assignment to '__all__' forbidden

- **v13/AEGIS\ui_contracts\schemas.py:38**
  - Code: `json_schema_extra = {`
  - Reasoning: Global assignment to 'json_schema_extra' forbidden

- **v13/AEGIS\ui_contracts\schemas.py:72**
  - Code: `json_schema_extra = {`
  - Reasoning: Global assignment to 'json_schema_extra' forbidden

- **v13/AEGIS\ui_contracts\schemas.py:98**
  - Code: `json_schema_extra = {`
  - Reasoning: Global assignment to 'json_schema_extra' forbidden

- **v13/AEGIS\ui_contracts\schemas.py:124**
  - Code: `json_schema_extra = {`
  - Reasoning: Global assignment to 'json_schema_extra' forbidden

- **v13/AEGIS\ui_contracts\schemas.py:149**
  - Code: `json_schema_extra = {`
  - Reasoning: Global assignment to 'json_schema_extra' forbidden

- **v13/AEGIS\ui_contracts\schemas.py:200**
  - Code: `json_schema_extra = {`
  - Reasoning: Global assignment to 'json_schema_extra' forbidden

- **v13/AEGIS\ui_contracts\schemas.py:229**
  - Code: `json_schema_extra = {`
  - Reasoning: Global assignment to 'json_schema_extra' forbidden

- **v13/AEGIS\ui_contracts\schemas.py:265**
  - Code: `json_schema_extra = {`
  - Reasoning: Global assignment to 'json_schema_extra' forbidden

- **v13/AEGIS\ui_contracts\schemas.py:278**
  - Code: `__all__ = [`
  - Reasoning: Global assignment to '__all__' forbidden

- **v13/AEGIS\ui_contracts\__init__.py:8**
  - Code: `__all__ = ["schemas"]`
  - Reasoning: Global assignment to '__all__' forbidden

  - ... and 130 more

## GLOBAL_KEYWORD (10)
- **v13/AEGIS\governance\model_registry.py:49**
  - Code: `global _REGISTRY_CACHE`
  - Reasoning: 'global' keyword forbidden: _REGISTRY_CACHE

- **v13/libs\deterministic_helpers.py:40**
  - Code: `global _prng_state`
  - Reasoning: 'global' keyword forbidden: _prng_state

- **v13/libs\deterministic\random.py:25**
  - Code: `global _prng_state`
  - Reasoning: 'global' keyword forbidden: _prng_state

- **v13/libs\deterministic\random.py:108**
  - Code: `global _prng_state`
  - Reasoning: 'global' keyword forbidden: _prng_state

- **v13/libs\deterministic\random.py:118**
  - Code: `global _prng_state`
  - Reasoning: 'global' keyword forbidden: _prng_state

- **v13/libs\deterministic\random.py:128**
  - Code: `global _prng_state`
  - Reasoning: 'global' keyword forbidden: _prng_state

- **v13/libs\deterministic\time.py:25**
  - Code: `global _det_time_state`
  - Reasoning: 'global' keyword forbidden: _det_time_state

- **v13/libs\deterministic\time.py:38**
  - Code: `global _det_perf_counter_state`
  - Reasoning: 'global' keyword forbidden: _det_perf_counter_state

- **v13/tests\conftest.py:34**
  - Code: `global test_logger`
  - Reasoning: 'global' keyword forbidden: test_logger

- **v13/tests\conftest.py:42**
  - Code: `global test_logger`
  - Reasoning: 'global' keyword forbidden: test_logger

## FORBIDDEN_COMP (27)
- **v13/AEGIS\governance\model_registry.py:64**
  - Code: `configs = {`
  - Reasoning: Dict comprehensions forbidden

- **v13/libs\economics\EconomicAdversarySuite.py:132**
  - Code: `return {k: self._deep_copy_state(v) for k, v in state.items()}`
  - Reasoning: Dict comprehensions forbidden

- **v13/libs\economics\GenesisHarmonicState.py:44**
  - Code: `graph = {shard: set() for shard in shard_ids}`
  - Reasoning: Dict comprehensions forbidden

- **v13/libs\economics\HarmonicEconomics.py:63**
  - Code: `self.violation_counters = {violation: 0 for violation in EconomicViolation}`
  - Reasoning: Dict comprehensions forbidden

- **v13/libs\economics\HarmonicEconomics.py:306**
  - Code: `state_dict = {'shards': {k: {'CHR': v['CHR'], 'FLX': v['FLX'], 'ATR': v['ATR'], 'RES': v['RES'], 'ΨSync': v['ΨSync'], 'DISSONANCE': v.get('DISSONANCE', 0)} for k, v in shards.items()}, 'system_constants': {'MAX_CHR_SUPPLY': state.parameters['MAX_CHR_SUPPLY'].value, 'δ_max': state.parameters['δ_max'].value, 'ε_sync': state.parameters['ε_sync'].value}}`
  - Reasoning: Dict comprehensions forbidden

- **v13/libs\economics\HarmonicEconomics.py:325**
  - Code: `return {'violation_summary': {v.value: count for v, count in self.violation_counters.items()}, 'state_history_size': len(self.economic_state_history), 'economic_constants': {'flux_proportionality': self.FLUX_PROPORTIONALITY_CONSTANT, 'max_resonance_envelope': self.MAX_RESONANCE_ENVELOPE, 'min_attractor_increment': self.MIN_ATTRACTOR_INCREMENT}}`
  - Reasoning: Dict comprehensions forbidden

- **v13/libs\economics\PsiFieldEngine.py:69**
  - Code: `self.graph = {shard: set() for shard in self.shard_ids}`
  - Reasoning: Dict comprehensions forbidden

- **v13/libs\economics\TreasuryDistributionEngine.py:85**
  - Code: `return {'distribution_map': {k: v.to_decimal_string() for k, v in distribution_map.items()}, 'total_payout': total_payout.to_decimal_string(), 'remaining_balance': remaining_balance.to_decimal_string(), 'timestamp': deterministic_timestamp, 'timestamp_source': f'drv_packet:{pkt_seq}', 'commit_hash': commit_result['commit_hash'], 'pqc_signature': commit_result['pqc_signature'], 'pqc_cid': pqc_cid}`
  - Reasoning: Dict comprehensions forbidden

- **v13/libs\economics\TreasuryDistributionEngine.py:102**
  - Code: `commit = {'event': 'TREASURY_DISTRIBUTION', 'amount': amount.to_decimal_string(), 'distribution': {k: v.to_decimal_string() for k, v in distribution_map.items()}, 'timestamp': timestamp, 'timestamp_source': f'drv_packet:{source_seq}', 'packet_hash': packet_hash, 'pqc_cid': pqc_cid, 'epoch': self.current_epoch}`
  - Reasoning: Dict comprehensions forbidden

- **v13/libs\governance\RewardAllocator.py:124**
  - Code: `return {address: equal_weight for address in recipient_addresses}`
  - Reasoning: Dict comprehensions forbidden

- **v13/libs\governance\RewardAllocator.py:145**
  - Code: `return {address: BigNum128.from_int(1) for address in allocation_weights.keys()}`
  - Reasoning: Dict comprehensions forbidden

- **v13/libs\governance\RewardAllocator.py:167**
  - Code: `weights_log = {address: weight.to_decimal_string() for address, weight in allocation_weights.items()}`
  - Reasoning: Dict comprehensions forbidden

- **v13/libs\governance\RewardAllocator.py:168**
  - Code: `allocations_log = {address: {'CHR': alloc.chr_amount.to_decimal_string(), 'FLX': alloc.flx_amount.to_decimal_string(), 'RES': alloc.res_amount.to_decimal_string(), 'PsiSync': alloc.psi_sync_amount.to_decimal_string(), 'ATR': alloc.atr_amount.to_decimal_string(), 'Total': alloc.total_amount.to_decimal_string()} for address, alloc in allocated_rewards.items()}`
  - Reasoning: Dict comprehensions forbidden

- **v13/libs\integration\StateTransitionEngine.py:220**
  - Code: `rewards_log = {address: {'CHR': alloc.chr_amount.to_decimal_string(), 'FLX': alloc.flx_amount.to_decimal_string(), 'RES': alloc.res_amount.to_decimal_string(), 'PsiSync': alloc.psi_sync_amount.to_decimal_string(), 'ATR': alloc.atr_amount.to_decimal_string(), 'Total': alloc.total_amount.to_decimal_string()} for address, alloc in allocated_rewards.items()}`
  - Reasoning: Dict comprehensions forbidden

- **v13/libs\integration\StateTransitionEngine.py:237**
  - Code: `rewards_log = {address: {'CHR': alloc.chr_amount.to_decimal_string(), 'FLX': alloc.flx_amount.to_decimal_string(), 'RES': alloc.res_amount.to_decimal_string(), 'PsiSync': alloc.psi_sync_amount.to_decimal_string(), 'ATR': alloc.atr_amount.to_decimal_string(), 'Total': alloc.total_amount.to_decimal_string()} for address, alloc in allocated_rewards.items()}`
  - Reasoning: Dict comprehensions forbidden

- **v13/libs\logging\qfs_logger.py:63**
  - Code: `hashable = {k: v for k, v in entry.items() if k != 'hash'}`
  - Reasoning: Dict comprehensions forbidden

- **v13/libs\logging\qfs_logger.py:118**
  - Code: `json.dump({'session_id': self.session_id, 'component': self.component, 'logs': self.log_buffer, 'metadata': {'total_entries': len(self.log_buffer), 'levels': {level.name: sum((1 for log in self.log_buffer if log['level'] == level.name)) for level in LogLevel}}}, f, indent=2, default=str)`
  - Reasoning: Dict comprehensions forbidden

- **v13/policy\artistic_observatory.py:60**
  - Code: `dim_avgs = {d: dim_sums[d] / dim_counts[d] for d in dim_sums}`
  - Reasoning: Dict comprehensions forbidden

- **v13/policy\artistic_observatory.py:80**
  - Code: `return {b: c / total for b, c in buckets.items()}`
  - Reasoning: Dict comprehensions forbidden

- **v13/policy\artistic_policy.py:36**
  - Code: `policy_data = {'enabled': self.enabled, 'mode': self.mode, 'dimension_weights': {k: v for k, v in sorted(self.dimension_weights.items())}, 'max_bonus_ratio': self.max_bonus_ratio, 'per_user_daily_cap_atr': self.per_user_daily_cap_atr, 'version': self.version}`
  - Reasoning: Dict comprehensions forbidden

  - ... and 7 more

## FORBIDDEN_CALL (838)
- **v13/AEGIS\governance\model_registry.py:71**
  - Code: `print(f"Error loading AEGIS model registry: {e}")`
  - Reasoning: Forbidden function: print

- **v13/libs\BigNum128.py:156**
  - Code: `return hash(self.value)`
  - Reasoning: Forbidden function: hash

- **v13/libs\BigNum128_fixed.py:155**
  - Code: `return hash(self.value)`
  - Reasoning: Forbidden function: hash

- **v13/libs\PQC.py:19**
  - Code: `print("[PQC] Using liboqs-python (High Assurance)")`
  - Reasoning: Forbidden function: print

- **v13/libs\PQC.py:21**
  - Code: `print("\n" + "=" * 80)`
  - Reasoning: Forbidden function: print

- **v13/libs\PQC.py:22**
  - Code: `print("[WARNING]: Using MockPQC (Simulation) - NOT CRYPTOGRAPHICALLY SECURE")`
  - Reasoning: Forbidden function: print

- **v13/libs\PQC.py:23**
  - Code: `print("=" * 80)`
  - Reasoning: Forbidden function: print

- **v13/libs\PQC.py:204**
  - Code: `with open(path, "w") as f:`
  - Reasoning: Forbidden function: open

- **v13/libs\core\SafetyGuard.py:139**
  - Code: `print('Testing SafetyGuard...')`
  - Reasoning: Forbidden function: print

- **v13/libs\core\SafetyGuard.py:155**
  - Code: `print(f'Safe content validation: {result1.passed}')`
  - Reasoning: Forbidden function: print

- **v13/libs\core\SafetyGuard.py:156**
  - Code: `print(f'Risk score: {result1.risk_score.to_decimal_string()}')`
  - Reasoning: Forbidden function: print

- **v13/libs\core\SafetyGuard.py:157**
  - Code: `print(f'Explanation: {result1.explanation}')`
  - Reasoning: Forbidden function: print

- **v13/libs\core\SafetyGuard.py:161**
  - Code: `print(f'Unsafe content validation: {result2.passed}')`
  - Reasoning: Forbidden function: print

- **v13/libs\core\SafetyGuard.py:162**
  - Code: `print(f'Risk score: {result2.risk_score.to_decimal_string()}')`
  - Reasoning: Forbidden function: print

- **v13/libs\core\SafetyGuard.py:163**
  - Code: `print(f'Explanation: {result2.explanation}')`
  - Reasoning: Forbidden function: print

- **v13/libs\core\SafetyGuard.py:166**
  - Code: `print(f'Media validation: {result3.passed}')`
  - Reasoning: Forbidden function: print

- **v13/libs\core\SafetyGuard.py:167**
  - Code: `print(f'Risk score: {result3.risk_score.to_decimal_string()}')`
  - Reasoning: Forbidden function: print

- **v13/libs\core\SafetyGuard.py:168**
  - Code: `print(f'Explanation: {result3.explanation}')`
  - Reasoning: Forbidden function: print

- **v13/libs\core\SafetyGuard.py:169**
  - Code: `print(f'Log entries: {len(log_list)}')`
  - Reasoning: Forbidden function: print

- **v13/libs\core\SafetyGuard.py:170**
  - Code: `print('✓ SafetyGuard test passed!')`
  - Reasoning: Forbidden function: print

  - ... and 818 more

## NONDETERMINISTIC_COMP (39)
- **v13/AEGIS\services\explanation_control.py:46**
  - Code: `dag_str = "".join([n.node_id for n in dag_nodes])`
  - Reasoning: Dict iteration in comprehension must use sorted()

- **v13/AEGIS\services\explanation_control.py:50**
  - Code: `proofs_str = "".join([pv.id for pv in proof_vectors])`
  - Reasoning: Dict iteration in comprehension must use sorted()

- **v13/AEGIS\services\explanation_service.py:42**
  - Code: `affected_nodes = [n for n in dag if n.node_type == "guard"]`
  - Reasoning: Dict iteration in comprehension must use sorted()

- **v13/AEGIS\services\explanation_service.py:43**
  - Code: `affected_modules = [n for n in dag if n.node_type == "module"]`
  - Reasoning: Dict iteration in comprehension must use sorted()

- **v13/AEGIS\services\explanation_service.py:49**
  - Code: `guards_str = ", ".join([n.label for n in affected_nodes])`
  - Reasoning: Dict iteration in comprehension must use sorted()

- **v13/AEGIS\services\governance_map.py:102**
  - Code: `dag_descriptor = {"nodes": [n.node_id for n in nodes]}`
  - Reasoning: Dict iteration in comprehension must use sorted()

- **v13/libs\PQC.py:221**
  - Code: `canonical_list = [PQC._canonicalize_for_sign(item) for item in data]`
  - Reasoning: Dict iteration in comprehension must use sorted()

- **v13/libs\economics\EconomicAdversarySuite.py:134**
  - Code: `copied_list = [self._deep_copy_state(item) for item in state]`
  - Reasoning: Dict iteration in comprehension must use sorted()

- **v13/libs\economics\PsiSyncProtocol.py:117**
  - Code: `tight_agreement_count = len([d for d in deviations if d <= epsilon_sync // 2])`
  - Reasoning: Dict iteration in comprehension must use sorted()

- **v13/libs\economics\PsiSyncProtocol.py:118**
  - Code: `tight_agreement_count = len([d for d in deviations if d <= epsilon_sync // 2])`
  - Reasoning: Dict iteration in comprehension must use sorted()

- **v13/libs\economics\PsiSyncProtocol.py:128**
  - Code: `bn_values = [BigNum128(v) for v in values]`
  - Reasoning: Dict iteration in comprehension must use sorted()

- **v13/libs\encoding\canonical.py:99**
  - Code: `return [CanonicalEncoder._normalize(item) for item in obj]`
  - Reasoning: Dict iteration in comprehension must use sorted()

- **v13/libs\governance\NODInvariantChecker.py:196**
  - Code: `return InvariantCheckResult(passed=False, invariant_id='NOD-I4', error_code=NODInvariantViolationType.INVARIANT_NOD_I4_NON_DETERMINISTIC_ORDER.value, error_message=f'NOD-I4 violation: Allocations not in deterministic sorted order', details={'expected_order': [a.node_id for a in sorted_allocations], 'actual_order': [a.node_id for a in allocations]})`
  - Reasoning: Dict iteration in comprehension must use sorted()

- **v13/libs\governance\NODInvariantChecker.py:196**
  - Code: `return InvariantCheckResult(passed=False, invariant_id='NOD-I4', error_code=NODInvariantViolationType.INVARIANT_NOD_I4_NON_DETERMINISTIC_ORDER.value, error_message=f'NOD-I4 violation: Allocations not in deterministic sorted order', details={'expected_order': [a.node_id for a in sorted_allocations], 'actual_order': [a.node_id for a in allocations]})`
  - Reasoning: Dict iteration in comprehension must use sorted()

- **v13/libs\governance\NODInvariantChecker.py:243**
  - Code: `allocation_data = {'allocations': [{'node_id': a.node_id, 'nod_amount': a.nod_amount.to_decimal_string(), 'contribution_score': a.contribution_score.to_decimal_string(), 'timestamp': a.timestamp} for a in sorted_allocations]}`
  - Reasoning: Dict iteration in comprehension must use sorted()

- **v13/libs\pqc\CanonicalSerializer.py:45**
  - Code: `return json.dumps([CanonicalSerializer.canonicalize_for_sign(v) for v in data], separators=(',', ':'), ensure_ascii=False)`
  - Reasoning: Dict iteration in comprehension must use sorted()

- **v13/policy\artistic_features\color.py:23**
  - Code: `hues = sorted([color.get('hue', 0) for color in palette])`
  - Reasoning: Dict iteration in comprehension must use sorted()

- **v13/policy\artistic_features\narrative.py:23**
  - Code: `durations = [seg.get('duration', 0) for seg in segments]`
  - Reasoning: Dict iteration in comprehension must use sorted()

- **v13/sdk\QFSV13SDK.py:250**
  - Code: `failed_invariants = [r for r in invariant_results if not r.passed]`
  - Reasoning: Dict iteration in comprehension must use sorted()

- **v13/sdk\QFSV13SDK.py:256**
  - Code: `return SDKResponse(success=True, data={'invariants_checked': len(invariant_results), 'all_passed': True, 'invariant_results': [{'invariant_id': r.invariant_id, 'passed': r.passed} for r in invariant_results], 'guard_status': 'ALL_INVARIANTS_PASSED'}, error=None, bundle_hash=None, pqc_signature=None)`
  - Reasoning: Dict iteration in comprehension must use sorted()

  - ... and 19 more

## FORBIDDEN_IMPORT (21)
- **v13/core\observability\logger.py:15**
  - Code: `import sys`
  - Reasoning: Import of sys forbidden

- **v13/core\observability\logger.py:17**
  - Code: `import uuid`
  - Reasoning: Import of uuid forbidden

- **v13/core\observability\logger.py:18**
  - Code: `import datetime`
  - Reasoning: Import of datetime forbidden

- **v13/libs\pqc_provider.py:14**
  - Code: `import os`
  - Reasoning: Import of os forbidden

- **v13/libs\encoding\canonical.py:13**
  - Code: `from decimal import Decimal`
  - Reasoning: Import from decimal forbidden

- **v13/libs\pqc\oqs_adapter.py:7**
  - Code: `import os`
  - Reasoning: Import of os forbidden

- **v13/tests\conftest.py:4**
  - Code: `import os`
  - Reasoning: Import of os forbidden

- **v13/tests\conftest.py:5**
  - Code: `import sys`
  - Reasoning: Import of sys forbidden

- **v13/tests\deterministic_verification_suite.py:8**
  - Code: `import sys`
  - Reasoning: Import of sys forbidden

- **v13/tests\deterministic_verification_suite.py:9**
  - Code: `import os`
  - Reasoning: Import of os forbidden

- **v13/tests\performance_test_suite.py:10**
  - Code: `from time import perf_counter as det_perf_counter`
  - Reasoning: Import from time forbidden

- **v13/tests\pqc\TestPQCStandardization.py:9**
  - Code: `import sys`
  - Reasoning: Import of sys forbidden

- **v13/tests\pqc\TestPQCStandardization.py:10**
  - Code: `import os`
  - Reasoning: Import of os forbidden

- **v13/tests\pqc\TestPQCStandardization.py:13**
  - Code: `from datetime import datetime, timezone`
  - Reasoning: Import from datetime forbidden

- **v13/tests\v13_6\PerformanceBenchmark.py:18**
  - Code: `import statistics`
  - Reasoning: Import of statistics forbidden

- **v13/tools\fix_drv_packet.py:1**
  - Code: `import os`
  - Reasoning: Import of os forbidden

- **v13/tools\generate_violation_taxonomy.py:3**
  - Code: `import os`
  - Reasoning: Import of os forbidden

- **v13/tools\generate_violation_taxonomy.py:4**
  - Code: `import sys`
  - Reasoning: Import of sys forbidden

- **v13/tools\generate_violation_taxonomy.py:5**
  - Code: `from datetime import datetime, timezone`
  - Reasoning: Import from datetime forbidden

- **v13/tools\ci\check_commit_status.py:3**
  - Code: `from datetime import datetime`
  - Reasoning: Import from datetime forbidden

  - ... and 1 more

## FORBIDDEN_MODULE_CALL (49)
- **v13/core\observability\logger.py:34**
  - Code: `return TraceContext(trace_id=uuid.uuid4().hex, span_id=uuid.uuid4().hex)`
  - Reasoning: uuid.uuid4 forbidden

- **v13/core\observability\logger.py:34**
  - Code: `return TraceContext(trace_id=uuid.uuid4().hex, span_id=uuid.uuid4().hex)`
  - Reasoning: uuid.uuid4 forbidden

- **v13/core\observability\logger.py:40**
  - Code: `tid = headers.get("x-trace-id") or uuid.uuid4().hex`
  - Reasoning: uuid.uuid4 forbidden

- **v13/core\observability\logger.py:41**
  - Code: `sid = headers.get("x-span-id") or uuid.uuid4().hex`
  - Reasoning: uuid.uuid4 forbidden

- **v13/libs\pqc\oqs_adapter.py:154**
  - Code: `seed = os.urandom(32)`
  - Reasoning: os.urandom forbidden

- **v13/libs\pqc\oqs_adapter.py:191**
  - Code: `seed = os.urandom(32)`
  - Reasoning: os.urandom forbidden

- **v13/libs\pqc\oqs_adapter.py:210**
  - Code: `msg_nonce = os.urandom(16)`
  - Reasoning: os.urandom forbidden

- **v13/tests\old\run_tests.py:12**
  - Code: `os.chdir(v13_dir)`
  - Reasoning: os.chdir forbidden

- **v13/tests\pqc\TestPQCAdapters.py:151**
  - Code: `os.makedirs(evidence_dir, exist_ok=True)`
  - Reasoning: os.makedirs forbidden

- **v13/tests\pqc\TestPQCStandardization.py:215**
  - Code: `"timestamp": int(datetime.now(timezone.utc).timestamp()),`
  - Reasoning: datetime.now forbidden

- **v13/tests\pqc\TestPQCStandardization.py:410**
  - Code: `os.makedirs(evidence_dir, exist_ok=True)`
  - Reasoning: os.makedirs forbidden

- **v13/tests\pqc\TestPQCStandardization.py:547**
  - Code: `os.makedirs(evidence_dir, exist_ok=True)`
  - Reasoning: os.makedirs forbidden

- **v13/tests\pqc\TestPQCStandardization.py:557**
  - Code: `"timestamp": datetime.now(timezone.utc).isoformat() + "Z",`
  - Reasoning: datetime.now forbidden

- **v13/tests\v13_6\BoundaryConditionTests.py:125**
  - Code: `os.makedirs('evidence/v13.6', exist_ok=True)`
  - Reasoning: os.makedirs forbidden

- **v13/tests\v13_6\DeterministicReplayTest.py:181**
  - Code: `os.makedirs('evidence/v13_6', exist_ok=True)`
  - Reasoning: os.makedirs forbidden

- **v13/tests\v13_6\FailureModeTests.py:311**
  - Code: `os.makedirs(evidence_dir, exist_ok=True)`
  - Reasoning: os.makedirs forbidden

- **v13/tests\v13_6\FailureModeTests.py:313**
  - Code: `evidence = {'artifact_type': 'failure_mode_verification', 'version': 'V13.6', 'test_suite': 'FailureModeTests.py', 'timestamp': datetime.utcnow().isoformat() + 'Z', 'summary': {'total_tests': self.pass_count + self.fail_count + len([r for r in self.test_results if r.get('status') == 'SKIPPED']), 'passed': self.pass_count, 'failed': self.fail_count, 'skipped': len([r for r in self.test_results if r.get('status') == 'SKIPPED']), 'pass_rate_percent': self.pass_count / (self.pass_count + self.fail_count) * 100 if self.pass_count + self.fail_count > 0 else 0}, 'test_results': self.test_results, 'constitutional_guards_status': {'EconomicsGuard': '✅ Active and enforcing bounds', 'NODInvariantChecker': '✅ Active and enforcing invariants', 'StateTransitionEngine_Firewall': '✅ Active and blocking user NOD transfers', 'AEGIS_Offline_Policy': 'PARTIALLY VERIFIED - AEGIS adapter pending'}, 'compliance_notes': ['All failure modes preserve zero-simulation integrity', 'No approximations or human overrides during failures', 'Structured error codes emitted for CIR-302 integration', 'AEGIS offline policy partially verified - AEGIS adapter pending', 'User rewards orthogonal to infrastructure status']}`
  - Reasoning: datetime.utcnow forbidden

- **v13/tests\v13_6\PerformanceBenchmark.py:72**
  - Code: `self.benchmark_results[benchmark_name] = {'iterations': iterations, 'duration_seconds': duration, 'tps': tps, 'latency_ms': {'p50': statistics.median(latencies), 'p95': statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else 0, 'p99': statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else 0, 'mean': statistics.mean(latencies), 'min': min(latencies), 'max': max(latencies)}}`
  - Reasoning: statistics.median forbidden

- **v13/tests\v13_6\PerformanceBenchmark.py:72**
  - Code: `self.benchmark_results[benchmark_name] = {'iterations': iterations, 'duration_seconds': duration, 'tps': tps, 'latency_ms': {'p50': statistics.median(latencies), 'p95': statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else 0, 'p99': statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else 0, 'mean': statistics.mean(latencies), 'min': min(latencies), 'max': max(latencies)}}`
  - Reasoning: statistics.quantiles forbidden

- **v13/tests\v13_6\PerformanceBenchmark.py:72**
  - Code: `self.benchmark_results[benchmark_name] = {'iterations': iterations, 'duration_seconds': duration, 'tps': tps, 'latency_ms': {'p50': statistics.median(latencies), 'p95': statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else 0, 'p99': statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else 0, 'mean': statistics.mean(latencies), 'min': min(latencies), 'max': max(latencies)}}`
  - Reasoning: statistics.quantiles forbidden

  - ... and 29 more

## FORBIDDEN_HASH (3)
- **v13/libs\BigNum128.py:156**
  - Code: `return hash(self.value)`
  - Reasoning: hash() is randomized ÔÇö forbidden

- **v13/libs\BigNum128_fixed.py:155**
  - Code: `return hash(self.value)`
  - Reasoning: hash() is randomized ÔÇö forbidden

- **v13/libs\economics\QAmount.py:197**
  - Code: `return hash(self._value)`
  - Reasoning: hash() is randomized ÔÇö forbidden

## FORBIDDEN_OPERATION (188)
- **v13/libs\DeterministicTime.py:61**
  - Code: `hash_mod = prev_hash_int % 2 ** 64`
  - Reasoning: Use CertifiedMath.pow(), not **

- **v13/libs\DeterministicTime.py:62**
  - Code: `return (packet.sequence + hash_mod) % 2 ** 64`
  - Reasoning: Use CertifiedMath.pow(), not **

- **v13/libs\deterministic_helpers.py:42**
  - Code: `return _prng_state / 2147483648.0`
  - Reasoning: Use CertifiedMath.idiv(), not / (produces float)

- **v13/libs\core\SafetyGuard.py:116**
  - Code: `size_mb = media_metadata['size'] / (1024 * 1024)`
  - Reasoning: Use CertifiedMath.idiv(), not / (produces float)

- **v13/libs\deterministic\random.py:27**
  - Code: `return _prng_state / 2147483648.0`
  - Reasoning: Use CertifiedMath.idiv(), not / (produces float)

- **v13/libs\economics\EconomicsGuard.py:197**
  - Code: `min_nodes = int(NOD_MIN_ACTIVE_NODES.value // NOD_MIN_ACTIVE_NODES.SCALE)`
  - Reasoning: Use CertifiedMath.idiv(), not // (can produce float)

- **v13/libs\economics\economic_constants.py:20**
  - Code: `FIXED_POINT_SCALE = BigNum128.from_int(10 ** 18)`
  - Reasoning: Use CertifiedMath.pow(), not **

- **v13/libs\economics\GenesisHarmonicState.py:33**
  - Code: `expected_flx = chr_amount * 618033989 // 1000000000`
  - Reasoning: Use CertifiedMath.idiv(), not // (can produce float)

- **v13/libs\economics\GenesisHarmonicState.py:88**
  - Code: `proofs['governance_security'] = {'active_nodes': len(active_nodes), 'recovery_threshold': CONST.EMERGENCY_RECOVERY_THRESHOLD, 'byzantine_tolerance': len(active_nodes) // 3}`
  - Reasoning: Use CertifiedMath.idiv(), not // (can produce float)

- **v13/libs\economics\GenesisHarmonicState.py:114**
  - Code: `return {'genesis_hash': get_genesis_hash(), 'validation_result': validation, 'token_metrics': {'total_chr': sum((shard['CHR'] for shard in GENESIS_STATE['token_allocations']['shards'].values())), 'total_flx': sum((shard['FLX'] for shard in GENESIS_STATE['token_allocations']['shards'].values())), 'shard_count': len(GENESIS_STATE['token_allocations']['shards']), 'avg_chr_per_shard': sum((shard['CHR'] for shard in GENESIS_STATE['token_allocations']['shards'].values())) // len(GENESIS_STATE['token_allocations']['shards'])}, 'governance_metrics': {'founding_nodes': len(FOUNDING_NODE_REGISTRY), 'active_nodes': len([n for n in FOUNDING_NODE_REGISTRY.values() if n['active']]), 'recovery_threshold': CONST.EMERGENCY_RECOVERY_THRESHOLD, 'byzantine_tolerance': len(FOUNDING_NODE_REGISTRY) // 3}, 'harmonic_constants': {'A_MAX': CONST.A_MAX, 'δ_max': CONST.δ_max, 'ε_sync': CONST.ε_sync, 'δ_curl': CONST.δ_curl}, 'timestamp': CONST.GENESIS_TIMESTAMP}`
  - Reasoning: Use CertifiedMath.idiv(), not // (can produce float)

- **v13/libs\economics\GenesisHarmonicState.py:114**
  - Code: `return {'genesis_hash': get_genesis_hash(), 'validation_result': validation, 'token_metrics': {'total_chr': sum((shard['CHR'] for shard in GENESIS_STATE['token_allocations']['shards'].values())), 'total_flx': sum((shard['FLX'] for shard in GENESIS_STATE['token_allocations']['shards'].values())), 'shard_count': len(GENESIS_STATE['token_allocations']['shards']), 'avg_chr_per_shard': sum((shard['CHR'] for shard in GENESIS_STATE['token_allocations']['shards'].values())) // len(GENESIS_STATE['token_allocations']['shards'])}, 'governance_metrics': {'founding_nodes': len(FOUNDING_NODE_REGISTRY), 'active_nodes': len([n for n in FOUNDING_NODE_REGISTRY.values() if n['active']]), 'recovery_threshold': CONST.EMERGENCY_RECOVERY_THRESHOLD, 'byzantine_tolerance': len(FOUNDING_NODE_REGISTRY) // 3}, 'harmonic_constants': {'A_MAX': CONST.A_MAX, 'δ_max': CONST.δ_max, 'ε_sync': CONST.ε_sync, 'δ_curl': CONST.δ_curl}, 'timestamp': CONST.GENESIS_TIMESTAMP}`
  - Reasoning: Use CertifiedMath.idiv(), not // (can produce float)

- **v13/libs\economics\HarmonicEconomics.py:65**
  - Code: `self.MAX_RESONANCE_ENVELOPE = 10 ** 9`
  - Reasoning: Use CertifiedMath.pow(), not **

- **v13/libs\economics\HarmonicEconomics.py:132**
  - Code: `flow_magnitude = self.math.mul(self.math.abs(gradient), self.FLUX_PROPORTIONALITY_CONSTANT) // self.SCALE_FACTOR`
  - Reasoning: Use CertifiedMath.idiv(), not // (can produce float)

- **v13/libs\economics\HarmonicEconomics.py:157**
  - Code: `return self.math.sub(old_psisync, min(max_decrease, abs(coherence_change // 1000)))`
  - Reasoning: Use CertifiedMath.idiv(), not // (can produce float)

- **v13/libs\economics\HarmonicEconomics.py:201**
  - Code: `return self.math.min(total_dissonance, 10 ** 6)`
  - Reasoning: Use CertifiedMath.pow(), not **

- **v13/libs\economics\HarmonicEconomics.py:245**
  - Code: `avg_chr = sum((s['CHR'] for s in shards.values())) // len(shards)`
  - Reasoning: Use CertifiedMath.idiv(), not // (can produce float)

- **v13/libs\economics\HarmonicEconomics.py:252**
  - Code: `flx_stability = self.math.sub(new_shard['FLX'], old_shard['FLX']) // 1000`
  - Reasoning: Use CertifiedMath.idiv(), not // (can produce float)

- **v13/libs\economics\HarmonicEconomics.py:268**
  - Code: `base_envelope = self.math.mul(new_shard['CHR'], new_shard['ATR']) // self.SCALE_FACTOR`
  - Reasoning: Use CertifiedMath.idiv(), not // (can produce float)

- **v13/libs\economics\HoloRewardEngine.py:65**
  - Code: `return reward_multiplier * total_distributed // self.SCALE_FACTOR`
  - Reasoning: Use CertifiedMath.idiv(), not // (can produce float)

- **v13/libs\economics\HoloRewardEngine.py:91**
  - Code: `avg_intensity_per_shard = intensity // max(1, total_shards)`
  - Reasoning: Use CertifiedMath.idiv(), not // (can produce float)

  - ... and 168 more

## FORBIDDEN_TYPE (29)
- **v13/libs\deterministic_hash.py:37**
  - Code: `elif isinstance(obj, (set, frozenset)):`
  - Reasoning: set is nondeterministic

- **v13/libs\deterministic_hash.py:37**
  - Code: `elif isinstance(obj, (set, frozenset)):`
  - Reasoning: frozenset is nondeterministic

- **v13/libs\economics\EconomicAdversarySuite.py:280**
  - Code: `if set(result1.keys()) != set(result2.keys()):`
  - Reasoning: set is nondeterministic

- **v13/libs\economics\EconomicAdversarySuite.py:280**
  - Code: `if set(result1.keys()) != set(result2.keys()):`
  - Reasoning: set is nondeterministic

- **v13/libs\economics\GenesisHarmonicState.py:43**
  - Code: `shard_ids = set(GENESIS_STATE['token_allocations']['shards'].keys())`
  - Reasoning: set is nondeterministic

- **v13/libs\economics\GenesisHarmonicState.py:44**
  - Code: `graph = {shard: set() for shard in shard_ids}`
  - Reasoning: set is nondeterministic

- **v13/libs\economics\GenesisHarmonicState.py:53**
  - Code: `visited = set()`
  - Reasoning: set is nondeterministic

- **v13/libs\economics\HarmonicEconomics.py:128**
  - Code: `neighbors = self.psi_field.graph.get(shard_id, set())`
  - Reasoning: set is nondeterministic

- **v13/libs\economics\HarmonicEconomics.py:180**
  - Code: `neighbors = self.psi_field.graph.get(shard_id, set())`
  - Reasoning: set is nondeterministic

- **v13/libs\economics\HoloRewardEngine.py:31**
  - Code: `self.processed_epochs = set()`
  - Reasoning: set is nondeterministic

- **v13/libs\economics\PsiFieldEngine.py:44**
  - Code: `self.shard_ids = set()`
  - Reasoning: set is nondeterministic

- **v13/libs\economics\PsiFieldEngine.py:61**
  - Code: `shard_set = set()`
  - Reasoning: set is nondeterministic

- **v13/libs\economics\PsiFieldEngine.py:69**
  - Code: `self.graph = {shard: set() for shard in self.shard_ids}`
  - Reasoning: set is nondeterministic

- **v13/libs\economics\PsiFieldEngine.py:101**
  - Code: `visited = set()`
  - Reasoning: set is nondeterministic

- **v13/libs\economics\PsiFieldEngine.py:104**
  - Code: `cycle_cache = set()`
  - Reasoning: set is nondeterministic

- **v13/libs\economics\PsiFieldEngine.py:150**
  - Code: `set1 = set(path1)`
  - Reasoning: set is nondeterministic

- **v13/libs\economics\PsiFieldEngine.py:169**
  - Code: `if len(cycle) != len(set(cycle)):`
  - Reasoning: set is nondeterministic

- **v13/libs\economics\PsiFieldEngine.py:219**
  - Code: `if j not in self.graph.get(i, set()):`
  - Reasoning: set is nondeterministic

- **v13/libs\economics\PsiFieldEngine.py:243**
  - Code: `if len(cycle) != len(set(cycle)):`
  - Reasoning: set is nondeterministic

- **v13/libs\economics\PsiFieldEngine.py:251**
  - Code: `if v not in self.graph.get(u, set()):`
  - Reasoning: set is nondeterministic

  - ... and 9 more

## FLOAT_LITERAL (129)
- **v13/libs\deterministic_helpers.py:42**
  - Code: `return _prng_state / 2147483648.0`
  - Reasoning: Float literals forbidden

- **v13/libs\deterministic_helpers.py:78**
  - Code: `return 1000.0`
  - Reasoning: Float literals forbidden

- **v13/libs\deterministic\random.py:27**
  - Code: `return _prng_state / 2147483648.0`
  - Reasoning: Float literals forbidden

- **v13/libs\deterministic\time.py:13**
  - Code: `_det_perf_counter_state = 1000.0  # Fixed starting performance counter`
  - Reasoning: Float literals forbidden

- **v13/libs\deterministic\time.py:103**
  - Code: `return 42.0`
  - Reasoning: Float literals forbidden

- **v13/libs\deterministic\time.py:114**
  - Code: `return 24.0`
  - Reasoning: Float literals forbidden

- **v13/libs\economics\EconomicAdversarySuite.py:81**
  - Code: `ADVERSARIES = {'EA-1': {'name': 'Coherence Spoof', 'description': 'Attempt to spoof coherence metrics with invalid state', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_manipulation', 'severity_weight': 1.0}, 'EA-2': {'name': 'ΨSync Desync', 'description': 'Attempt to desynchronize global ΨSync consensus', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'consensus_manipulation', 'severity_weight': 1.0}, 'EA-3': {'name': 'Treasury Siphon', 'description': 'Attempt to siphon treasury rewards through coordinated shard manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.5}, 'EA-4': {'name': 'Resonance Overdrive', 'description': 'Attempt to generate excessive RES through ψ-field manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'resonance_manipulation', 'severity_weight': 1.2}, 'EA-5': {'name': 'CHR Inflation', 'description': 'Attempt to create new CHR tokens violating conservation law', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'token_creation', 'severity_weight': 2.0}, 'EA-6': {'name': 'FLX Negative Flow', 'description': "Attempt to create negative FLX flows violating Kirchhoff's law", 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'flow_manipulation', 'severity_weight': 1.5}, 'EA-7': {'name': 'ψCurl Collapse', 'description': 'Attempt to create ψ-curl anomalies that collapse field stability', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'field_manipulation', 'severity_weight': 1.8}, 'EA-8': {'name': 'ΨSync Race', 'description': 'Attempt to create race conditions in ΨSync consensus between shards', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.3}, 'EA-9': {'name': 'Harmonic Divergence', 'description': 'Attempt to cause economic state divergence across shards', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_divergence', 'severity_weight': 1.7}, 'EA-10': {'name': 'Cross-Shard Imbalance', 'description': 'Attempt to create severe token imbalances between shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'imbalance_attack', 'severity_weight': 1.4}, 'EA-11': {'name': 'Oracle Timing', 'description': 'Attempt to manipulate economic oracle timing for profit', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.1}, 'EA-12': {'name': 'QPU Mismatch', 'description': 'Attempt to exploit QPU differences for consensus advantage', 'expected_cir': 'None', 'expected_response': 'DETERMINISTIC_FALLBACK', 'attack_vector': 'platform_divergence', 'severity_weight': 0.8}, 'EA-13': {'name': 'Reward Amplification', 'description': 'Attempt to amplify rewards beyond A_MAX bound', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.6}, 'EA-14': {'name': 'CHR Imbalance', 'description': 'Attempt to create CHR allocation imbalances across shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'allocation_manipulation', 'severity_weight': 1.3}}`
  - Reasoning: Float literals forbidden

- **v13/libs\economics\EconomicAdversarySuite.py:81**
  - Code: `ADVERSARIES = {'EA-1': {'name': 'Coherence Spoof', 'description': 'Attempt to spoof coherence metrics with invalid state', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_manipulation', 'severity_weight': 1.0}, 'EA-2': {'name': 'ΨSync Desync', 'description': 'Attempt to desynchronize global ΨSync consensus', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'consensus_manipulation', 'severity_weight': 1.0}, 'EA-3': {'name': 'Treasury Siphon', 'description': 'Attempt to siphon treasury rewards through coordinated shard manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.5}, 'EA-4': {'name': 'Resonance Overdrive', 'description': 'Attempt to generate excessive RES through ψ-field manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'resonance_manipulation', 'severity_weight': 1.2}, 'EA-5': {'name': 'CHR Inflation', 'description': 'Attempt to create new CHR tokens violating conservation law', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'token_creation', 'severity_weight': 2.0}, 'EA-6': {'name': 'FLX Negative Flow', 'description': "Attempt to create negative FLX flows violating Kirchhoff's law", 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'flow_manipulation', 'severity_weight': 1.5}, 'EA-7': {'name': 'ψCurl Collapse', 'description': 'Attempt to create ψ-curl anomalies that collapse field stability', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'field_manipulation', 'severity_weight': 1.8}, 'EA-8': {'name': 'ΨSync Race', 'description': 'Attempt to create race conditions in ΨSync consensus between shards', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.3}, 'EA-9': {'name': 'Harmonic Divergence', 'description': 'Attempt to cause economic state divergence across shards', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_divergence', 'severity_weight': 1.7}, 'EA-10': {'name': 'Cross-Shard Imbalance', 'description': 'Attempt to create severe token imbalances between shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'imbalance_attack', 'severity_weight': 1.4}, 'EA-11': {'name': 'Oracle Timing', 'description': 'Attempt to manipulate economic oracle timing for profit', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.1}, 'EA-12': {'name': 'QPU Mismatch', 'description': 'Attempt to exploit QPU differences for consensus advantage', 'expected_cir': 'None', 'expected_response': 'DETERMINISTIC_FALLBACK', 'attack_vector': 'platform_divergence', 'severity_weight': 0.8}, 'EA-13': {'name': 'Reward Amplification', 'description': 'Attempt to amplify rewards beyond A_MAX bound', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.6}, 'EA-14': {'name': 'CHR Imbalance', 'description': 'Attempt to create CHR allocation imbalances across shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'allocation_manipulation', 'severity_weight': 1.3}}`
  - Reasoning: Float literals forbidden

- **v13/libs\economics\EconomicAdversarySuite.py:81**
  - Code: `ADVERSARIES = {'EA-1': {'name': 'Coherence Spoof', 'description': 'Attempt to spoof coherence metrics with invalid state', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_manipulation', 'severity_weight': 1.0}, 'EA-2': {'name': 'ΨSync Desync', 'description': 'Attempt to desynchronize global ΨSync consensus', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'consensus_manipulation', 'severity_weight': 1.0}, 'EA-3': {'name': 'Treasury Siphon', 'description': 'Attempt to siphon treasury rewards through coordinated shard manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.5}, 'EA-4': {'name': 'Resonance Overdrive', 'description': 'Attempt to generate excessive RES through ψ-field manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'resonance_manipulation', 'severity_weight': 1.2}, 'EA-5': {'name': 'CHR Inflation', 'description': 'Attempt to create new CHR tokens violating conservation law', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'token_creation', 'severity_weight': 2.0}, 'EA-6': {'name': 'FLX Negative Flow', 'description': "Attempt to create negative FLX flows violating Kirchhoff's law", 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'flow_manipulation', 'severity_weight': 1.5}, 'EA-7': {'name': 'ψCurl Collapse', 'description': 'Attempt to create ψ-curl anomalies that collapse field stability', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'field_manipulation', 'severity_weight': 1.8}, 'EA-8': {'name': 'ΨSync Race', 'description': 'Attempt to create race conditions in ΨSync consensus between shards', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.3}, 'EA-9': {'name': 'Harmonic Divergence', 'description': 'Attempt to cause economic state divergence across shards', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_divergence', 'severity_weight': 1.7}, 'EA-10': {'name': 'Cross-Shard Imbalance', 'description': 'Attempt to create severe token imbalances between shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'imbalance_attack', 'severity_weight': 1.4}, 'EA-11': {'name': 'Oracle Timing', 'description': 'Attempt to manipulate economic oracle timing for profit', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.1}, 'EA-12': {'name': 'QPU Mismatch', 'description': 'Attempt to exploit QPU differences for consensus advantage', 'expected_cir': 'None', 'expected_response': 'DETERMINISTIC_FALLBACK', 'attack_vector': 'platform_divergence', 'severity_weight': 0.8}, 'EA-13': {'name': 'Reward Amplification', 'description': 'Attempt to amplify rewards beyond A_MAX bound', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.6}, 'EA-14': {'name': 'CHR Imbalance', 'description': 'Attempt to create CHR allocation imbalances across shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'allocation_manipulation', 'severity_weight': 1.3}}`
  - Reasoning: Float literals forbidden

- **v13/libs\economics\EconomicAdversarySuite.py:81**
  - Code: `ADVERSARIES = {'EA-1': {'name': 'Coherence Spoof', 'description': 'Attempt to spoof coherence metrics with invalid state', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_manipulation', 'severity_weight': 1.0}, 'EA-2': {'name': 'ΨSync Desync', 'description': 'Attempt to desynchronize global ΨSync consensus', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'consensus_manipulation', 'severity_weight': 1.0}, 'EA-3': {'name': 'Treasury Siphon', 'description': 'Attempt to siphon treasury rewards through coordinated shard manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.5}, 'EA-4': {'name': 'Resonance Overdrive', 'description': 'Attempt to generate excessive RES through ψ-field manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'resonance_manipulation', 'severity_weight': 1.2}, 'EA-5': {'name': 'CHR Inflation', 'description': 'Attempt to create new CHR tokens violating conservation law', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'token_creation', 'severity_weight': 2.0}, 'EA-6': {'name': 'FLX Negative Flow', 'description': "Attempt to create negative FLX flows violating Kirchhoff's law", 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'flow_manipulation', 'severity_weight': 1.5}, 'EA-7': {'name': 'ψCurl Collapse', 'description': 'Attempt to create ψ-curl anomalies that collapse field stability', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'field_manipulation', 'severity_weight': 1.8}, 'EA-8': {'name': 'ΨSync Race', 'description': 'Attempt to create race conditions in ΨSync consensus between shards', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.3}, 'EA-9': {'name': 'Harmonic Divergence', 'description': 'Attempt to cause economic state divergence across shards', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_divergence', 'severity_weight': 1.7}, 'EA-10': {'name': 'Cross-Shard Imbalance', 'description': 'Attempt to create severe token imbalances between shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'imbalance_attack', 'severity_weight': 1.4}, 'EA-11': {'name': 'Oracle Timing', 'description': 'Attempt to manipulate economic oracle timing for profit', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.1}, 'EA-12': {'name': 'QPU Mismatch', 'description': 'Attempt to exploit QPU differences for consensus advantage', 'expected_cir': 'None', 'expected_response': 'DETERMINISTIC_FALLBACK', 'attack_vector': 'platform_divergence', 'severity_weight': 0.8}, 'EA-13': {'name': 'Reward Amplification', 'description': 'Attempt to amplify rewards beyond A_MAX bound', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.6}, 'EA-14': {'name': 'CHR Imbalance', 'description': 'Attempt to create CHR allocation imbalances across shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'allocation_manipulation', 'severity_weight': 1.3}}`
  - Reasoning: Float literals forbidden

- **v13/libs\economics\EconomicAdversarySuite.py:81**
  - Code: `ADVERSARIES = {'EA-1': {'name': 'Coherence Spoof', 'description': 'Attempt to spoof coherence metrics with invalid state', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_manipulation', 'severity_weight': 1.0}, 'EA-2': {'name': 'ΨSync Desync', 'description': 'Attempt to desynchronize global ΨSync consensus', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'consensus_manipulation', 'severity_weight': 1.0}, 'EA-3': {'name': 'Treasury Siphon', 'description': 'Attempt to siphon treasury rewards through coordinated shard manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.5}, 'EA-4': {'name': 'Resonance Overdrive', 'description': 'Attempt to generate excessive RES through ψ-field manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'resonance_manipulation', 'severity_weight': 1.2}, 'EA-5': {'name': 'CHR Inflation', 'description': 'Attempt to create new CHR tokens violating conservation law', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'token_creation', 'severity_weight': 2.0}, 'EA-6': {'name': 'FLX Negative Flow', 'description': "Attempt to create negative FLX flows violating Kirchhoff's law", 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'flow_manipulation', 'severity_weight': 1.5}, 'EA-7': {'name': 'ψCurl Collapse', 'description': 'Attempt to create ψ-curl anomalies that collapse field stability', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'field_manipulation', 'severity_weight': 1.8}, 'EA-8': {'name': 'ΨSync Race', 'description': 'Attempt to create race conditions in ΨSync consensus between shards', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.3}, 'EA-9': {'name': 'Harmonic Divergence', 'description': 'Attempt to cause economic state divergence across shards', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_divergence', 'severity_weight': 1.7}, 'EA-10': {'name': 'Cross-Shard Imbalance', 'description': 'Attempt to create severe token imbalances between shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'imbalance_attack', 'severity_weight': 1.4}, 'EA-11': {'name': 'Oracle Timing', 'description': 'Attempt to manipulate economic oracle timing for profit', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.1}, 'EA-12': {'name': 'QPU Mismatch', 'description': 'Attempt to exploit QPU differences for consensus advantage', 'expected_cir': 'None', 'expected_response': 'DETERMINISTIC_FALLBACK', 'attack_vector': 'platform_divergence', 'severity_weight': 0.8}, 'EA-13': {'name': 'Reward Amplification', 'description': 'Attempt to amplify rewards beyond A_MAX bound', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.6}, 'EA-14': {'name': 'CHR Imbalance', 'description': 'Attempt to create CHR allocation imbalances across shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'allocation_manipulation', 'severity_weight': 1.3}}`
  - Reasoning: Float literals forbidden

- **v13/libs\economics\EconomicAdversarySuite.py:81**
  - Code: `ADVERSARIES = {'EA-1': {'name': 'Coherence Spoof', 'description': 'Attempt to spoof coherence metrics with invalid state', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_manipulation', 'severity_weight': 1.0}, 'EA-2': {'name': 'ΨSync Desync', 'description': 'Attempt to desynchronize global ΨSync consensus', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'consensus_manipulation', 'severity_weight': 1.0}, 'EA-3': {'name': 'Treasury Siphon', 'description': 'Attempt to siphon treasury rewards through coordinated shard manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.5}, 'EA-4': {'name': 'Resonance Overdrive', 'description': 'Attempt to generate excessive RES through ψ-field manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'resonance_manipulation', 'severity_weight': 1.2}, 'EA-5': {'name': 'CHR Inflation', 'description': 'Attempt to create new CHR tokens violating conservation law', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'token_creation', 'severity_weight': 2.0}, 'EA-6': {'name': 'FLX Negative Flow', 'description': "Attempt to create negative FLX flows violating Kirchhoff's law", 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'flow_manipulation', 'severity_weight': 1.5}, 'EA-7': {'name': 'ψCurl Collapse', 'description': 'Attempt to create ψ-curl anomalies that collapse field stability', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'field_manipulation', 'severity_weight': 1.8}, 'EA-8': {'name': 'ΨSync Race', 'description': 'Attempt to create race conditions in ΨSync consensus between shards', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.3}, 'EA-9': {'name': 'Harmonic Divergence', 'description': 'Attempt to cause economic state divergence across shards', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_divergence', 'severity_weight': 1.7}, 'EA-10': {'name': 'Cross-Shard Imbalance', 'description': 'Attempt to create severe token imbalances between shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'imbalance_attack', 'severity_weight': 1.4}, 'EA-11': {'name': 'Oracle Timing', 'description': 'Attempt to manipulate economic oracle timing for profit', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.1}, 'EA-12': {'name': 'QPU Mismatch', 'description': 'Attempt to exploit QPU differences for consensus advantage', 'expected_cir': 'None', 'expected_response': 'DETERMINISTIC_FALLBACK', 'attack_vector': 'platform_divergence', 'severity_weight': 0.8}, 'EA-13': {'name': 'Reward Amplification', 'description': 'Attempt to amplify rewards beyond A_MAX bound', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.6}, 'EA-14': {'name': 'CHR Imbalance', 'description': 'Attempt to create CHR allocation imbalances across shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'allocation_manipulation', 'severity_weight': 1.3}}`
  - Reasoning: Float literals forbidden

- **v13/libs\economics\EconomicAdversarySuite.py:81**
  - Code: `ADVERSARIES = {'EA-1': {'name': 'Coherence Spoof', 'description': 'Attempt to spoof coherence metrics with invalid state', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_manipulation', 'severity_weight': 1.0}, 'EA-2': {'name': 'ΨSync Desync', 'description': 'Attempt to desynchronize global ΨSync consensus', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'consensus_manipulation', 'severity_weight': 1.0}, 'EA-3': {'name': 'Treasury Siphon', 'description': 'Attempt to siphon treasury rewards through coordinated shard manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.5}, 'EA-4': {'name': 'Resonance Overdrive', 'description': 'Attempt to generate excessive RES through ψ-field manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'resonance_manipulation', 'severity_weight': 1.2}, 'EA-5': {'name': 'CHR Inflation', 'description': 'Attempt to create new CHR tokens violating conservation law', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'token_creation', 'severity_weight': 2.0}, 'EA-6': {'name': 'FLX Negative Flow', 'description': "Attempt to create negative FLX flows violating Kirchhoff's law", 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'flow_manipulation', 'severity_weight': 1.5}, 'EA-7': {'name': 'ψCurl Collapse', 'description': 'Attempt to create ψ-curl anomalies that collapse field stability', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'field_manipulation', 'severity_weight': 1.8}, 'EA-8': {'name': 'ΨSync Race', 'description': 'Attempt to create race conditions in ΨSync consensus between shards', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.3}, 'EA-9': {'name': 'Harmonic Divergence', 'description': 'Attempt to cause economic state divergence across shards', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_divergence', 'severity_weight': 1.7}, 'EA-10': {'name': 'Cross-Shard Imbalance', 'description': 'Attempt to create severe token imbalances between shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'imbalance_attack', 'severity_weight': 1.4}, 'EA-11': {'name': 'Oracle Timing', 'description': 'Attempt to manipulate economic oracle timing for profit', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.1}, 'EA-12': {'name': 'QPU Mismatch', 'description': 'Attempt to exploit QPU differences for consensus advantage', 'expected_cir': 'None', 'expected_response': 'DETERMINISTIC_FALLBACK', 'attack_vector': 'platform_divergence', 'severity_weight': 0.8}, 'EA-13': {'name': 'Reward Amplification', 'description': 'Attempt to amplify rewards beyond A_MAX bound', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.6}, 'EA-14': {'name': 'CHR Imbalance', 'description': 'Attempt to create CHR allocation imbalances across shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'allocation_manipulation', 'severity_weight': 1.3}}`
  - Reasoning: Float literals forbidden

- **v13/libs\economics\EconomicAdversarySuite.py:81**
  - Code: `ADVERSARIES = {'EA-1': {'name': 'Coherence Spoof', 'description': 'Attempt to spoof coherence metrics with invalid state', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_manipulation', 'severity_weight': 1.0}, 'EA-2': {'name': 'ΨSync Desync', 'description': 'Attempt to desynchronize global ΨSync consensus', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'consensus_manipulation', 'severity_weight': 1.0}, 'EA-3': {'name': 'Treasury Siphon', 'description': 'Attempt to siphon treasury rewards through coordinated shard manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.5}, 'EA-4': {'name': 'Resonance Overdrive', 'description': 'Attempt to generate excessive RES through ψ-field manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'resonance_manipulation', 'severity_weight': 1.2}, 'EA-5': {'name': 'CHR Inflation', 'description': 'Attempt to create new CHR tokens violating conservation law', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'token_creation', 'severity_weight': 2.0}, 'EA-6': {'name': 'FLX Negative Flow', 'description': "Attempt to create negative FLX flows violating Kirchhoff's law", 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'flow_manipulation', 'severity_weight': 1.5}, 'EA-7': {'name': 'ψCurl Collapse', 'description': 'Attempt to create ψ-curl anomalies that collapse field stability', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'field_manipulation', 'severity_weight': 1.8}, 'EA-8': {'name': 'ΨSync Race', 'description': 'Attempt to create race conditions in ΨSync consensus between shards', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.3}, 'EA-9': {'name': 'Harmonic Divergence', 'description': 'Attempt to cause economic state divergence across shards', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_divergence', 'severity_weight': 1.7}, 'EA-10': {'name': 'Cross-Shard Imbalance', 'description': 'Attempt to create severe token imbalances between shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'imbalance_attack', 'severity_weight': 1.4}, 'EA-11': {'name': 'Oracle Timing', 'description': 'Attempt to manipulate economic oracle timing for profit', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.1}, 'EA-12': {'name': 'QPU Mismatch', 'description': 'Attempt to exploit QPU differences for consensus advantage', 'expected_cir': 'None', 'expected_response': 'DETERMINISTIC_FALLBACK', 'attack_vector': 'platform_divergence', 'severity_weight': 0.8}, 'EA-13': {'name': 'Reward Amplification', 'description': 'Attempt to amplify rewards beyond A_MAX bound', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.6}, 'EA-14': {'name': 'CHR Imbalance', 'description': 'Attempt to create CHR allocation imbalances across shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'allocation_manipulation', 'severity_weight': 1.3}}`
  - Reasoning: Float literals forbidden

- **v13/libs\economics\EconomicAdversarySuite.py:81**
  - Code: `ADVERSARIES = {'EA-1': {'name': 'Coherence Spoof', 'description': 'Attempt to spoof coherence metrics with invalid state', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_manipulation', 'severity_weight': 1.0}, 'EA-2': {'name': 'ΨSync Desync', 'description': 'Attempt to desynchronize global ΨSync consensus', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'consensus_manipulation', 'severity_weight': 1.0}, 'EA-3': {'name': 'Treasury Siphon', 'description': 'Attempt to siphon treasury rewards through coordinated shard manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.5}, 'EA-4': {'name': 'Resonance Overdrive', 'description': 'Attempt to generate excessive RES through ψ-field manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'resonance_manipulation', 'severity_weight': 1.2}, 'EA-5': {'name': 'CHR Inflation', 'description': 'Attempt to create new CHR tokens violating conservation law', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'token_creation', 'severity_weight': 2.0}, 'EA-6': {'name': 'FLX Negative Flow', 'description': "Attempt to create negative FLX flows violating Kirchhoff's law", 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'flow_manipulation', 'severity_weight': 1.5}, 'EA-7': {'name': 'ψCurl Collapse', 'description': 'Attempt to create ψ-curl anomalies that collapse field stability', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'field_manipulation', 'severity_weight': 1.8}, 'EA-8': {'name': 'ΨSync Race', 'description': 'Attempt to create race conditions in ΨSync consensus between shards', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.3}, 'EA-9': {'name': 'Harmonic Divergence', 'description': 'Attempt to cause economic state divergence across shards', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_divergence', 'severity_weight': 1.7}, 'EA-10': {'name': 'Cross-Shard Imbalance', 'description': 'Attempt to create severe token imbalances between shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'imbalance_attack', 'severity_weight': 1.4}, 'EA-11': {'name': 'Oracle Timing', 'description': 'Attempt to manipulate economic oracle timing for profit', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.1}, 'EA-12': {'name': 'QPU Mismatch', 'description': 'Attempt to exploit QPU differences for consensus advantage', 'expected_cir': 'None', 'expected_response': 'DETERMINISTIC_FALLBACK', 'attack_vector': 'platform_divergence', 'severity_weight': 0.8}, 'EA-13': {'name': 'Reward Amplification', 'description': 'Attempt to amplify rewards beyond A_MAX bound', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.6}, 'EA-14': {'name': 'CHR Imbalance', 'description': 'Attempt to create CHR allocation imbalances across shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'allocation_manipulation', 'severity_weight': 1.3}}`
  - Reasoning: Float literals forbidden

- **v13/libs\economics\EconomicAdversarySuite.py:81**
  - Code: `ADVERSARIES = {'EA-1': {'name': 'Coherence Spoof', 'description': 'Attempt to spoof coherence metrics with invalid state', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_manipulation', 'severity_weight': 1.0}, 'EA-2': {'name': 'ΨSync Desync', 'description': 'Attempt to desynchronize global ΨSync consensus', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'consensus_manipulation', 'severity_weight': 1.0}, 'EA-3': {'name': 'Treasury Siphon', 'description': 'Attempt to siphon treasury rewards through coordinated shard manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.5}, 'EA-4': {'name': 'Resonance Overdrive', 'description': 'Attempt to generate excessive RES through ψ-field manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'resonance_manipulation', 'severity_weight': 1.2}, 'EA-5': {'name': 'CHR Inflation', 'description': 'Attempt to create new CHR tokens violating conservation law', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'token_creation', 'severity_weight': 2.0}, 'EA-6': {'name': 'FLX Negative Flow', 'description': "Attempt to create negative FLX flows violating Kirchhoff's law", 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'flow_manipulation', 'severity_weight': 1.5}, 'EA-7': {'name': 'ψCurl Collapse', 'description': 'Attempt to create ψ-curl anomalies that collapse field stability', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'field_manipulation', 'severity_weight': 1.8}, 'EA-8': {'name': 'ΨSync Race', 'description': 'Attempt to create race conditions in ΨSync consensus between shards', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.3}, 'EA-9': {'name': 'Harmonic Divergence', 'description': 'Attempt to cause economic state divergence across shards', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_divergence', 'severity_weight': 1.7}, 'EA-10': {'name': 'Cross-Shard Imbalance', 'description': 'Attempt to create severe token imbalances between shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'imbalance_attack', 'severity_weight': 1.4}, 'EA-11': {'name': 'Oracle Timing', 'description': 'Attempt to manipulate economic oracle timing for profit', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.1}, 'EA-12': {'name': 'QPU Mismatch', 'description': 'Attempt to exploit QPU differences for consensus advantage', 'expected_cir': 'None', 'expected_response': 'DETERMINISTIC_FALLBACK', 'attack_vector': 'platform_divergence', 'severity_weight': 0.8}, 'EA-13': {'name': 'Reward Amplification', 'description': 'Attempt to amplify rewards beyond A_MAX bound', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.6}, 'EA-14': {'name': 'CHR Imbalance', 'description': 'Attempt to create CHR allocation imbalances across shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'allocation_manipulation', 'severity_weight': 1.3}}`
  - Reasoning: Float literals forbidden

- **v13/libs\economics\EconomicAdversarySuite.py:81**
  - Code: `ADVERSARIES = {'EA-1': {'name': 'Coherence Spoof', 'description': 'Attempt to spoof coherence metrics with invalid state', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_manipulation', 'severity_weight': 1.0}, 'EA-2': {'name': 'ΨSync Desync', 'description': 'Attempt to desynchronize global ΨSync consensus', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'consensus_manipulation', 'severity_weight': 1.0}, 'EA-3': {'name': 'Treasury Siphon', 'description': 'Attempt to siphon treasury rewards through coordinated shard manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.5}, 'EA-4': {'name': 'Resonance Overdrive', 'description': 'Attempt to generate excessive RES through ψ-field manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'resonance_manipulation', 'severity_weight': 1.2}, 'EA-5': {'name': 'CHR Inflation', 'description': 'Attempt to create new CHR tokens violating conservation law', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'token_creation', 'severity_weight': 2.0}, 'EA-6': {'name': 'FLX Negative Flow', 'description': "Attempt to create negative FLX flows violating Kirchhoff's law", 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'flow_manipulation', 'severity_weight': 1.5}, 'EA-7': {'name': 'ψCurl Collapse', 'description': 'Attempt to create ψ-curl anomalies that collapse field stability', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'field_manipulation', 'severity_weight': 1.8}, 'EA-8': {'name': 'ΨSync Race', 'description': 'Attempt to create race conditions in ΨSync consensus between shards', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.3}, 'EA-9': {'name': 'Harmonic Divergence', 'description': 'Attempt to cause economic state divergence across shards', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_divergence', 'severity_weight': 1.7}, 'EA-10': {'name': 'Cross-Shard Imbalance', 'description': 'Attempt to create severe token imbalances between shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'imbalance_attack', 'severity_weight': 1.4}, 'EA-11': {'name': 'Oracle Timing', 'description': 'Attempt to manipulate economic oracle timing for profit', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.1}, 'EA-12': {'name': 'QPU Mismatch', 'description': 'Attempt to exploit QPU differences for consensus advantage', 'expected_cir': 'None', 'expected_response': 'DETERMINISTIC_FALLBACK', 'attack_vector': 'platform_divergence', 'severity_weight': 0.8}, 'EA-13': {'name': 'Reward Amplification', 'description': 'Attempt to amplify rewards beyond A_MAX bound', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.6}, 'EA-14': {'name': 'CHR Imbalance', 'description': 'Attempt to create CHR allocation imbalances across shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'allocation_manipulation', 'severity_weight': 1.3}}`
  - Reasoning: Float literals forbidden

- **v13/libs\economics\EconomicAdversarySuite.py:81**
  - Code: `ADVERSARIES = {'EA-1': {'name': 'Coherence Spoof', 'description': 'Attempt to spoof coherence metrics with invalid state', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_manipulation', 'severity_weight': 1.0}, 'EA-2': {'name': 'ΨSync Desync', 'description': 'Attempt to desynchronize global ΨSync consensus', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'consensus_manipulation', 'severity_weight': 1.0}, 'EA-3': {'name': 'Treasury Siphon', 'description': 'Attempt to siphon treasury rewards through coordinated shard manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.5}, 'EA-4': {'name': 'Resonance Overdrive', 'description': 'Attempt to generate excessive RES through ψ-field manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'resonance_manipulation', 'severity_weight': 1.2}, 'EA-5': {'name': 'CHR Inflation', 'description': 'Attempt to create new CHR tokens violating conservation law', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'token_creation', 'severity_weight': 2.0}, 'EA-6': {'name': 'FLX Negative Flow', 'description': "Attempt to create negative FLX flows violating Kirchhoff's law", 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'flow_manipulation', 'severity_weight': 1.5}, 'EA-7': {'name': 'ψCurl Collapse', 'description': 'Attempt to create ψ-curl anomalies that collapse field stability', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'field_manipulation', 'severity_weight': 1.8}, 'EA-8': {'name': 'ΨSync Race', 'description': 'Attempt to create race conditions in ΨSync consensus between shards', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.3}, 'EA-9': {'name': 'Harmonic Divergence', 'description': 'Attempt to cause economic state divergence across shards', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_divergence', 'severity_weight': 1.7}, 'EA-10': {'name': 'Cross-Shard Imbalance', 'description': 'Attempt to create severe token imbalances between shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'imbalance_attack', 'severity_weight': 1.4}, 'EA-11': {'name': 'Oracle Timing', 'description': 'Attempt to manipulate economic oracle timing for profit', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.1}, 'EA-12': {'name': 'QPU Mismatch', 'description': 'Attempt to exploit QPU differences for consensus advantage', 'expected_cir': 'None', 'expected_response': 'DETERMINISTIC_FALLBACK', 'attack_vector': 'platform_divergence', 'severity_weight': 0.8}, 'EA-13': {'name': 'Reward Amplification', 'description': 'Attempt to amplify rewards beyond A_MAX bound', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.6}, 'EA-14': {'name': 'CHR Imbalance', 'description': 'Attempt to create CHR allocation imbalances across shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'allocation_manipulation', 'severity_weight': 1.3}}`
  - Reasoning: Float literals forbidden

- **v13/libs\economics\EconomicAdversarySuite.py:81**
  - Code: `ADVERSARIES = {'EA-1': {'name': 'Coherence Spoof', 'description': 'Attempt to spoof coherence metrics with invalid state', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_manipulation', 'severity_weight': 1.0}, 'EA-2': {'name': 'ΨSync Desync', 'description': 'Attempt to desynchronize global ΨSync consensus', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'consensus_manipulation', 'severity_weight': 1.0}, 'EA-3': {'name': 'Treasury Siphon', 'description': 'Attempt to siphon treasury rewards through coordinated shard manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.5}, 'EA-4': {'name': 'Resonance Overdrive', 'description': 'Attempt to generate excessive RES through ψ-field manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'resonance_manipulation', 'severity_weight': 1.2}, 'EA-5': {'name': 'CHR Inflation', 'description': 'Attempt to create new CHR tokens violating conservation law', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'token_creation', 'severity_weight': 2.0}, 'EA-6': {'name': 'FLX Negative Flow', 'description': "Attempt to create negative FLX flows violating Kirchhoff's law", 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'flow_manipulation', 'severity_weight': 1.5}, 'EA-7': {'name': 'ψCurl Collapse', 'description': 'Attempt to create ψ-curl anomalies that collapse field stability', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'field_manipulation', 'severity_weight': 1.8}, 'EA-8': {'name': 'ΨSync Race', 'description': 'Attempt to create race conditions in ΨSync consensus between shards', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.3}, 'EA-9': {'name': 'Harmonic Divergence', 'description': 'Attempt to cause economic state divergence across shards', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_divergence', 'severity_weight': 1.7}, 'EA-10': {'name': 'Cross-Shard Imbalance', 'description': 'Attempt to create severe token imbalances between shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'imbalance_attack', 'severity_weight': 1.4}, 'EA-11': {'name': 'Oracle Timing', 'description': 'Attempt to manipulate economic oracle timing for profit', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.1}, 'EA-12': {'name': 'QPU Mismatch', 'description': 'Attempt to exploit QPU differences for consensus advantage', 'expected_cir': 'None', 'expected_response': 'DETERMINISTIC_FALLBACK', 'attack_vector': 'platform_divergence', 'severity_weight': 0.8}, 'EA-13': {'name': 'Reward Amplification', 'description': 'Attempt to amplify rewards beyond A_MAX bound', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.6}, 'EA-14': {'name': 'CHR Imbalance', 'description': 'Attempt to create CHR allocation imbalances across shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'allocation_manipulation', 'severity_weight': 1.3}}`
  - Reasoning: Float literals forbidden

- **v13/libs\economics\EconomicAdversarySuite.py:81**
  - Code: `ADVERSARIES = {'EA-1': {'name': 'Coherence Spoof', 'description': 'Attempt to spoof coherence metrics with invalid state', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_manipulation', 'severity_weight': 1.0}, 'EA-2': {'name': 'ΨSync Desync', 'description': 'Attempt to desynchronize global ΨSync consensus', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'consensus_manipulation', 'severity_weight': 1.0}, 'EA-3': {'name': 'Treasury Siphon', 'description': 'Attempt to siphon treasury rewards through coordinated shard manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.5}, 'EA-4': {'name': 'Resonance Overdrive', 'description': 'Attempt to generate excessive RES through ψ-field manipulation', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'resonance_manipulation', 'severity_weight': 1.2}, 'EA-5': {'name': 'CHR Inflation', 'description': 'Attempt to create new CHR tokens violating conservation law', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'token_creation', 'severity_weight': 2.0}, 'EA-6': {'name': 'FLX Negative Flow', 'description': "Attempt to create negative FLX flows violating Kirchhoff's law", 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'flow_manipulation', 'severity_weight': 1.5}, 'EA-7': {'name': 'ψCurl Collapse', 'description': 'Attempt to create ψ-curl anomalies that collapse field stability', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'field_manipulation', 'severity_weight': 1.8}, 'EA-8': {'name': 'ΨSync Race', 'description': 'Attempt to create race conditions in ΨSync consensus between shards', 'expected_cir': 'CIR-412', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.3}, 'EA-9': {'name': 'Harmonic Divergence', 'description': 'Attempt to cause economic state divergence across shards', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'state_divergence', 'severity_weight': 1.7}, 'EA-10': {'name': 'Cross-Shard Imbalance', 'description': 'Attempt to create severe token imbalances between shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'imbalance_attack', 'severity_weight': 1.4}, 'EA-11': {'name': 'Oracle Timing', 'description': 'Attempt to manipulate economic oracle timing for profit', 'expected_cir': 'CIR-302', 'expected_response': 'BLOCKED', 'attack_vector': 'timing_attack', 'severity_weight': 1.1}, 'EA-12': {'name': 'QPU Mismatch', 'description': 'Attempt to exploit QPU differences for consensus advantage', 'expected_cir': 'None', 'expected_response': 'DETERMINISTIC_FALLBACK', 'attack_vector': 'platform_divergence', 'severity_weight': 0.8}, 'EA-13': {'name': 'Reward Amplification', 'description': 'Attempt to amplify rewards beyond A_MAX bound', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'reward_manipulation', 'severity_weight': 1.6}, 'EA-14': {'name': 'CHR Imbalance', 'description': 'Attempt to create CHR allocation imbalances across shards', 'expected_cir': 'CIR-511', 'expected_response': 'BLOCKED', 'attack_vector': 'allocation_manipulation', 'severity_weight': 1.3}}`
  - Reasoning: Float literals forbidden

  - ... and 109 more

## MISSING_TIMESTAMP_PARAM (29)
- **v13/libs\economics\EconomicsGuard.py:73**
  - Code: `def to_dict(self) -> Dict[str, Any]:`
  - Reasoning: Missing param: deterministic_timestamp (required in EconomicsGuard.py)

- **v13/libs\economics\EconomicsGuard.py:95**
  - Code: `def validate_chr_reward(self, reward_amount: BigNum128, current_daily_total: BigNum128, current_total_supply: BigNum128, log_list: Optional[List[Dict[str, Any]]]=None) -> ValidationResult:`
  - Reasoning: Missing param: deterministic_timestamp (required in EconomicsGuard.py)

- **v13/libs\economics\EconomicsGuard.py:127**
  - Code: `def validate_flx_reward(self, flx_amount: BigNum128, chr_reward: BigNum128, user_current_balance: BigNum128, log_list: Optional[List[Dict[str, Any]]]=None) -> ValidationResult:`
  - Reasoning: Missing param: deterministic_timestamp (required in EconomicsGuard.py)

- **v13/libs\economics\EconomicsGuard.py:157**
  - Code: `def validate_nod_allocation(self, nod_amount: BigNum128, total_fees: BigNum128, node_voting_power: BigNum128, total_voting_power: BigNum128, node_reward_share: BigNum128, total_epoch_issuance: BigNum128, active_node_count: int, log_list: Optional[List[Dict[str, Any]]]=None) -> ValidationResult:`
  - Reasoning: Missing param: deterministic_timestamp (required in EconomicsGuard.py)

- **v13/libs\economics\EconomicsGuard.py:202**
  - Code: `def validate_psi_accumulation(self, psi_delta: BigNum128, current_psi_value: BigNum128, log_list: Optional[List[Dict[str, Any]]]=None) -> ValidationResult:`
  - Reasoning: Missing param: deterministic_timestamp (required in EconomicsGuard.py)

- **v13/libs\economics\EconomicsGuard.py:228**
  - Code: `def validate_atr_usage(self, cost_multiplier: BigNum128, accumulated_atr: BigNum128, log_list: Optional[List[Dict[str, Any]]]=None) -> ValidationResult:`
  - Reasoning: Missing param: deterministic_timestamp (required in EconomicsGuard.py)

- **v13/libs\economics\EconomicsGuard.py:252**
  - Code: `def validate_emission_rate(self, emission_amount: BigNum128, emission_cap: BigNum128, log_list: Optional[List[Dict[str, Any]]]=None) -> ValidationResult:`
  - Reasoning: Missing param: deterministic_timestamp (required in EconomicsGuard.py)

- **v13/libs\economics\EconomicsGuard.py:273**
  - Code: `def validate_supply_change(self, supply_delta: BigNum128, current_supply: BigNum128, log_list: Optional[List[Dict[str, Any]]]=None) -> ValidationResult:`
  - Reasoning: Missing param: deterministic_timestamp (required in EconomicsGuard.py)

- **v13/libs\economics\EconomicsGuard.py:302**
  - Code: `def validate_governance_change(self, parameter_name: str, new_value: BigNum128, log_list: Optional[List[Dict[str, Any]]]=None) -> ValidationResult:`
  - Reasoning: Missing param: deterministic_timestamp (required in EconomicsGuard.py)

- **v13/libs\economics\EconomicsGuard.py:327**
  - Code: `def generate_violation_event_hash(self, validation_result: ValidationResult, timestamp: int) -> str:`
  - Reasoning: Missing param: deterministic_timestamp (required in EconomicsGuard.py)

- **v13/libs\economics\EconomicsGuard.py:342**
  - Code: `def test_economics_guard():`
  - Reasoning: Missing param: deterministic_timestamp (required in EconomicsGuard.py)

- **v13/libs\governance\AEGIS_Node_Verification.py:59**
  - Code: `def metrics_str(self) -> str:`
  - Reasoning: Missing param: deterministic_timestamp (required in AEGIS_Node_Verification.py)

- **v13/libs\governance\AEGIS_Node_Verification.py:63**
  - Code: `def to_dict(self) -> Dict[str, Any]:`
  - Reasoning: Missing param: deterministic_timestamp (required in AEGIS_Node_Verification.py)

- **v13/libs\governance\AEGIS_Node_Verification.py:91**
  - Code: `def verify_node(self, node_id: str, registry_snapshot: Dict[str, Any], telemetry_snapshot: Dict[str, Any], log_list: Optional[List[Dict[str, Any]]]=None) -> NodeVerificationResult:`
  - Reasoning: Missing param: deterministic_timestamp (required in AEGIS_Node_Verification.py)

- **v13/libs\governance\AEGIS_Node_Verification.py:248**
  - Code: `def verify_nodes_batch(self, node_ids: List[str], registry_snapshot: Dict[str, Any], telemetry_snapshot: Dict[str, Any], log_list: Optional[List[Dict[str, Any]]]=None) -> Dict[str, NodeVerificationResult]:`
  - Reasoning: Missing param: deterministic_timestamp (required in AEGIS_Node_Verification.py)

- **v13/libs\governance\AEGIS_Node_Verification.py:271**
  - Code: `def test_aegis_node_verification():`
  - Reasoning: Missing param: deterministic_timestamp (required in AEGIS_Node_Verification.py)

- **v13/libs\governance\NODAllocator.py:255**
  - Code: `def test_nod_allocator():`
  - Reasoning: Missing param: deterministic_timestamp (required in NODAllocator.py)

- **v13/libs\governance\NODInvariantChecker.py:63**
  - Code: `def to_dict(self) -> Dict[str, Any]:`
  - Reasoning: Missing param: deterministic_timestamp (required in NODInvariantChecker.py)

- **v13/libs\governance\NODInvariantChecker.py:91**
  - Code: `def check_non_transferability(self, caller_module: str, operation_type: str, node_balances: Dict[str, BigNum128], log_list: Optional[List[Dict[str, Any]]]=None) -> InvariantCheckResult:`
  - Reasoning: Missing param: deterministic_timestamp (required in NODInvariantChecker.py)

- **v13/libs\governance\NODInvariantChecker.py:116**
  - Code: `def check_supply_conservation(self, previous_total_supply: BigNum128, new_total_supply: BigNum128, allocations: List['NODAllocation'], log_list: Optional[List[Dict[str, Any]]]=None) -> InvariantCheckResult:`
  - Reasoning: Missing param: deterministic_timestamp (required in NODInvariantChecker.py)

  - ... and 9 more

## GLOBAL_ATTR_MUTATION (8)
- **v13/libs\economics\PsiFieldEngine.py:130**
  - Code: `self.cycle_basis = cycles`
  - Reasoning: Global attribute assignment forbidden: cycle_basis

- **v13/libs\economics\PsiFieldEngine.py:131**
  - Code: `self.cycle_basis_hash = self._compute_cycle_basis_hash()`
  - Reasoning: Global attribute assignment forbidden: cycle_basis_hash

- **v13/policy\storage_explainability.py:106**
  - Code: `explanation.epoch_assigned = payload.get('epoch', 0)`
  - Reasoning: Global attribute assignment forbidden: epoch_assigned

- **v13/policy\storage_explainability.py:107**
  - Code: `explanation.shard_ids = payload.get('shard_ids', [])`
  - Reasoning: Global attribute assignment forbidden: shard_ids

- **v13/policy\storage_explainability.py:108**
  - Code: `explanation.integrity_hash = payload.get('hash_commit', '')`
  - Reasoning: Global attribute assignment forbidden: integrity_hash

- **v13/policy\storage_explainability.py:113**
  - Code: `explanation.storage_nodes = sorted(list(nodes))`
  - Reasoning: Global attribute assignment forbidden: storage_nodes

- **v13/policy\storage_explainability.py:114**
  - Code: `explanation.replica_count = len(explanation.storage_nodes)`
  - Reasoning: Global attribute assignment forbidden: replica_count

- **v13/policy\storage_explainability.py:122**
  - Code: `explanation.explanation_hash = hashlib.sha256(explanation_str.encode()).hexdigest()`
  - Reasoning: Global attribute assignment forbidden: explanation_hash

## UNCERTIFIED_ARITHMETIC (2)
- **v13/libs\governance\AEGIS_Node_Verification.py:279**
  - Code: `telemetry_snapshot = {'schema_version': 'v1.0', 'telemetry_hash': 'a' * 64, 'block_height': 12345, 'nodes': {'node_valid': {'uptime_ratio': '0.95', 'health_score': '0.80', 'conflict_detected': False}, 'node_low_uptime': {'uptime_ratio': '0.85', 'health_score': '0.80', 'conflict_detected': False}, 'node_unhealthy': {'uptime_ratio': '0.95', 'health_score': '0.70', 'conflict_detected': False}, 'node_conflict': {'uptime_ratio': '0.95', 'health_score': '0.80', 'conflict_detected': True, 'conflict_reason': 'Duplicate entries in different shards'}}}`
  - Reasoning: Direct arithmetic forbidden in economics. Use CertifiedMath.mult()

- **v13/libs\governance\NODInvariantChecker.py:333**
  - Code: `bad_hash = '0' * 64`
  - Reasoning: Direct arithmetic forbidden in economics. Use CertifiedMath.mult()

## FORBIDDEN_GENERATOR (2)
- **v13/libs\governance\NODAllocator.py:249**
  - Code: `details = {'operation': 'nod_allocation', 'nod_reward_pool': nod_reward_pool.to_decimal_string(), 'total_contributions': sum((score.value for score in node_contributions.values())), 'total_allocated': total_allocated.to_decimal_string(), 'allocation_count': allocation_count, 'epoch': epoch_number, 'timestamp': deterministic_timestamp}`
  - Reasoning: Generator expressions forbidden in deterministic modules

- **v13/libs\governance\NODInvariantChecker.py:345**
  - Code: `assert all((r.passed for r in all_results)), 'All invariants should pass'`
  - Reasoning: Generator expressions forbidden in deterministic modules

## DYNAMIC_IMPORT (1)
- **v13/tests\pqc\TestPQCAdapters.py:153**
  - Code: `evidence = {'artifact_type': 'pqc_adapter_verification', 'version': 'V13.6', 'test_suite': 'TestPQCAdapters.py', 'backend': self.backend_name, 'backend_info': PQCAdapterFactory.get_backend_info(), 'timestamp': __import__('datetime').datetime.utcnow().isoformat() + 'Z', 'summary': {'total_tests': self.pass_count + self.fail_count, 'passed': self.pass_count, 'failed': self.fail_count, 'pass_rate_percent': self.pass_count / (self.pass_count + self.fail_count) * 100 if self.pass_count + self.fail_count > 0 else 0}, 'test_results': self.test_results}`
  - Reasoning: Dynamic imports forbidden

## WILDCARD_IMPORT (2)
- **v13/tests\v13_6\BoundaryConditionTests.py:23**
  - Code: `from v13.libs.economics.economic_constants import *`
  - Reasoning: Wildcard imports forbidden

- **v13/tests\v13_6\FailureModeTests.py:22**
  - Code: `from v13.libs.economics.economic_constants import *`
  - Reasoning: Wildcard imports forbidden

## BARE_EXCEPT (2)
- **v13/tests\v13_6\PerformanceBenchmark.py:170**
  - Code: `except:`
  - Reasoning: Bare 'except:' forbidden

- **v13/tools\generate_violation_taxonomy.py:245**
  - Code: `except:`
  - Reasoning: Bare 'except:' forbidden

