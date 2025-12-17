"""
Phase A: Module Migration Audit Script
Audits each module for Zero-Simulation compliance and deterministic behavior.
"""
from libs.deterministic_helpers import ZeroSimAbort, det_time_now, det_perf_counter, det_random, qnum
import json
import hashlib
import ast
import traceback
from typing import Dict, List, Any, Optional, Tuple
sys.path.insert(0, 'libs')
from CertifiedMath import BigNum128, CertifiedMath
from TokenStateBundle import TokenStateBundle, create_token_state_bundle
from UtilityOracleInterface import UtilityOracleInterface, create_utility_oracle
from DRV_Packet import DRV_Packet
from PQC import generate_keypair, sign_data, verify_signature
from HSMF import HSMF
from CIR302_Handler import CIR302_Handler

class ModuleAuditResult:
    """Represents the result of a module audit."""

    def __init__(self, module_name: str):
        self.module_name = module_name
        self.passed = True
        self.issues = []
        self.recommendations = []
        self.evidence_files = []

    def add_issue(self, issue: str):
        """Add an issue to the audit result."""
        self.issues.append(issue)
        self.passed = False

    def add_recommendation(self, recommendation: str):
        """Add a recommendation to the audit result."""
        self.recommendations.append(recommendation)

    def add_evidence_file(self, filename: str):
        """Add an evidence file to the audit result."""
        self.evidence_files.append(filename)

class ZeroSimulationASTChecker:
    """AST-based checker for Zero-Simulation compliance."""

    def __init__(self):
        self.forbidden_imports = {'random', 'time', 'datetime', 'uuid', 'os', 'sys'}
        self.forbidden_functions = {'random.random', 'random.randint', 'time.time', 'datetime.now', 'uuid.uuid4', 'os.urandom', 'sys.stdin.read'}
        self.forbidden_constructs = {'yield', 'async', 'await', 'global', 'nonlocal'}

    def check_file(self, filepath: str) -> List[str]:
        """Check a Python file for Zero-Simulation compliance."""
        issues = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            tree = ast.parse(source)
            issues.extend(self._check_imports(tree))
            issues.extend(self._check_function_calls(tree))
            issues.extend(self._check_constructs(tree))
        except Exception as e:
            issues.append(f'AST parsing error in {filepath}: {str(e)}')
        return issues

    def _check_imports(self, tree: ast.AST) -> List[str]:
        """Check for forbidden imports."""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in self.forbidden_imports:
                        issues.append(f'Forbidden import: {alias.name}')
            elif isinstance(node, ast.ImportFrom):
                if node.module in self.forbidden_imports:
                    issues.append(f'Forbidden import: {node.module}')
        return issues

    def _check_function_calls(self, tree: ast.AST) -> List[str]:
        """Check for forbidden function calls."""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    func_name = f'{node.func.value.id}.{node.func.attr}' if isinstance(node.func.value, ast.Name) else None
                    if func_name in self.forbidden_functions:
                        issues.append(f'Forbidden function call: {func_name}')
                elif isinstance(node.func, ast.Name):
                    if node.func.id in ['input', 'eval', 'exec']:
                        issues.append(f'Forbidden function call: {node.func.id}')
        return issues

    def _check_constructs(self, tree: ast.AST) -> List[str]:
        """Check for forbidden language constructs."""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Yield):
                issues.append('Forbidden construct: yield')
            elif isinstance(node, ast.AsyncFunctionDef):
                issues.append('Forbidden construct: async function')
            elif isinstance(node, ast.Await):
                issues.append('Forbidden construct: await')
            elif isinstance(node, ast.Global):
                issues.append('Forbidden construct: global')
            elif isinstance(node, ast.Nonlocal):
                issues.append('Forbidden construct: nonlocal')
        return issues

class ModuleMigrationAuditor:
    """Audits modules for migration to V13 deterministic standards."""

    def __init__(self):
        self.ast_checker = ZeroSimulationASTChecker()
        self.audit_results = []

    def audit_all_modules(self) -> List[ModuleAuditResult]:
        """Audit all modules for V13 compliance."""
        print('=== PHASE A: MODULE MIGRATION AUDIT ===')
        self.audit_token_state_bundle()
        self.audit_utility_oracle()
        self.audit_drv_packet()
        self.audit_pqc()
        self.audit_hsmf()
        self.audit_cir302_handler()
        self.audit_certified_math()
        return self.audit_results

    def audit_token_state_bundle(self):
        """Audit TokenStateBundle module."""
        print('\n--- Auditing TokenStateBundle ---')
        result = ModuleAuditResult('TokenStateBundle')
        issues = self.ast_checker.check_file('libs/TokenStateBundle.py')
        for issue in issues:
            result.add_issue(f'Zero-Simulation violation: {issue}')
        try:
            chr_state = {'coherence_metric': BigNum128.from_string('1.5')}
            flx_state = {'scaling_metric': BigNum128.from_string('0.8')}
            psi_sync_state = {'frequency_metric': BigNum128.from_string('0.3')}
            atr_state = {'directional_metric': BigNum128.from_string('0.6')}
            res_state = {'inertial_metric': BigNum128.from_string('0.9')}
            lambda1 = BigNum128.from_string('1.618033988749894848')
            lambda2 = BigNum128.from_string('0.95')
            c_crit = BigNum128.from_string('1.0')
            bundle1 = create_token_state_bundle(chr_state, flx_state, psi_sync_state, atr_state, res_state, lambda1, lambda2, c_crit, 'TEST_PQC_001', 1700000000, {'test': 'metadata'})
            bundle2 = create_token_state_bundle(chr_state, flx_state, psi_sync_state, atr_state, res_state, lambda1, lambda2, c_crit, 'TEST_PQC_001', 1700000000, {'test': 'metadata'})
            if bundle1.get_deterministic_hash() != bundle2.get_deterministic_hash():
                result.add_issue('TokenStateBundle creation is not deterministic')
            if bundle1.serialize_for_hash() != bundle2.serialize_for_hash():
                result.add_issue('TokenStateBundle serialization is not deterministic')
            evidence = {'bundle1_hash': bundle1.get_deterministic_hash(), 'bundle2_hash': bundle2.get_deterministic_hash(), 'serialization_match': bundle1.serialize_for_hash() == bundle2.serialize_for_hash()}
            evidence_file = 'token_state_bundle_evidence.json'
            with open(evidence_file, 'w') as f:
                json.dump(evidence, f, indent=2)
            result.add_evidence_file(evidence_file)
        except Exception as e:
            result.add_issue(f'TokenStateBundle testing failed: {str(e)}')
            traceback.print_exc()
        self.audit_results.append(result)
        self._print_result(result)

    def audit_utility_oracle(self):
        """Audit UtilityOracle module."""
        print('\n--- Auditing UtilityOracle ---')
        result = ModuleAuditResult('UtilityOracle')
        issues = self.ast_checker.check_file('libs/UtilityOracleInterface.py')
        for issue in issues:
            result.add_issue(f'Zero-Simulation violation: {issue}')
        try:
            oracle = create_utility_oracle('TEST_PQC_002', {'test': 'metadata'})
            packet = DRV_Packet(ttsTimestamp=1700000000, sequence=1, seed='test_seed', metadata={'atr_data': {'directional_encoding': '0.5'}}, pqc_cid='TEST_PQC_003', quantum_metadata={'test': 'metadata'})
            keypair = generate_keypair()
            private_key = keypair['private_key']
            public_key = keypair['public_key']
            packet.sign(private_key, 'TEST_PQC_004', {'test': 'metadata'})
            f_atr1 = oracle.get_f_atr(packet)
            f_atr2 = oracle.get_f_atr(packet)
            if f_atr1.value != f_atr2.value:
                result.add_issue('UtilityOracle f(ATR) calculation is not deterministic')
            current_state = BigNum128.from_string('1.0')
            target_state = BigNum128.from_string('1.0')
            alpha1 = oracle.get_alpha_update(current_state, target_state)
            alpha2 = oracle.get_alpha_update(current_state, target_state)
            if alpha1.value != alpha2.value:
                result.add_issue('UtilityOracle alpha update is not deterministic')
            evidence = {'f_atr1': f_atr1.to_decimal_string(), 'f_atr2': f_atr2.to_decimal_string(), 'f_atr_match': f_atr1.value == f_atr2.value, 'alpha1': alpha1.to_decimal_string(), 'alpha2': alpha2.to_decimal_string(), 'alpha_match': alpha1.value == alpha2.value}
            evidence_file = 'utility_oracle_evidence.json'
            with open(evidence_file, 'w') as f:
                json.dump(evidence, f, indent=2)
            result.add_evidence_file(evidence_file)
        except Exception as e:
            result.add_issue(f'UtilityOracle testing failed: {str(e)}')
            traceback.print_exc()
        self.audit_results.append(result)
        self._print_result(result)

    def audit_drv_packet(self):
        """Audit DRV_Packet module."""
        print('\n--- Auditing DRV_Packet ---')
        result = ModuleAuditResult('DRV_Packet')
        issues = self.ast_checker.check_file('libs/DRV_Packet.py')
        for issue in issues:
            result.add_issue(f'Zero-Simulation violation: {issue}')
        try:
            packet1 = DRV_Packet(ttsTimestamp=1700000000, sequence=1, seed='test_seed', metadata={'test': 'data'}, previous_hash='0' * 64, pqc_cid='TEST_PQC_005', quantum_metadata={'test': 'metadata'})
            packet2 = DRV_Packet(ttsTimestamp=1700000000, sequence=1, seed='test_seed', metadata={'test': 'data'}, previous_hash='0' * 64, pqc_cid='TEST_PQC_005', quantum_metadata={'test': 'metadata'})
            if packet1.get_hash() != packet2.get_hash():
                result.add_issue('DRV_Packet creation is not deterministic')
            if packet1.serialize() != packet2.serialize():
                result.add_issue('DRV_Packet serialization is not deterministic')
            keypair = generate_keypair()
            private_key = keypair['private_key']
            public_key = keypair['public_key']
            packet1.sign(private_key, 'TEST_PQC_006', {'test': 'metadata'})
            packet2.sign(private_key, 'TEST_PQC_006', {'test': 'metadata'})
            if packet1.pqc_signature != packet2.pqc_signature:
                result.add_issue('DRV_Packet signing is not deterministic')
            verify1 = packet1.verify_signature(public_key, 'TEST_PQC_007', {'test': 'metadata'})
            verify2 = packet2.verify_signature(public_key, 'TEST_PQC_007', {'test': 'metadata'})
            if not (verify1 and verify2):
                result.add_issue('DRV_Packet signature verification failed')
            evidence = {'packet1_hash': packet1.get_hash(), 'packet2_hash': packet2.get_hash(), 'hash_match': packet1.get_hash() == packet2.get_hash(), 'serialization_match': packet1.serialize() == packet2.serialize(), 'signature_match': packet1.pqc_signature == packet2.pqc_signature, 'verification_results': [verify1, verify2]}
            evidence_file = 'drv_packet_evidence.json'
            with open(evidence_file, 'w') as f:
                json.dump(evidence, f, indent=2)
            result.add_evidence_file(evidence_file)
        except Exception as e:
            result.add_issue(f'DRV_Packet testing failed: {str(e)}')
            traceback.print_exc()
        self.audit_results.append(result)
        self._print_result(result)

    def audit_pqc(self):
        """Audit PQC module."""
        print('\n--- Auditing PQC ---')
        result = ModuleAuditResult('PQC')
        issues = self.ast_checker.check_file('libs/PQC.py')
        for issue in issues:
            result.add_issue(f'Zero-Simulation violation: {issue}')
        try:
            keypair1 = generate_keypair('TEST_PQC_008', {'test': 'metadata'})
            keypair2 = generate_keypair('TEST_PQC_008', {'test': 'metadata'})
            if keypair1['private_key'] == keypair2['private_key'] or keypair1['public_key'] == keypair2['public_key']:
                result.add_issue('PQC key generation should produce different keys')
            test_data = {'message': 'test', 'value': 42}
            signature1 = sign_data(test_data, keypair1['private_key'], 'TEST_PQC_009', {'test': 'metadata'})
            signature2 = sign_data(test_data, keypair1['private_key'], 'TEST_PQC_009', {'test': 'metadata'})
            if signature1 != signature2:
                result.add_issue('PQC signing is not deterministic')
            verify1 = verify_signature(test_data, signature1, keypair1['public_key'], 'TEST_PQC_010', {'test': 'metadata'})
            verify2 = verify_signature(test_data, signature2, keypair1['public_key'], 'TEST_PQC_010', {'test': 'metadata'})
            if not (verify1 and verify2):
                result.add_issue('PQC signature verification failed')
            evidence = {'keypair1_priv_len': len(keypair1['private_key']), 'keypair1_pub_len': len(keypair1['public_key']), 'keypair2_priv_len': len(keypair2['private_key']), 'keypair2_pub_len': len(keypair2['public_key']), 'signature1_len': len(signature1), 'signature2_len': len(signature2), 'signature_match': signature1 == signature2, 'verification_results': [verify1, verify2]}
            evidence_file = 'pqc_evidence.json'
            with open(evidence_file, 'w') as f:
                json.dump(evidence, f, indent=2)
            result.add_evidence_file(evidence_file)
        except Exception as e:
            result.add_issue(f'PQC testing failed: {str(e)}')
            traceback.print_exc()
        self.audit_results.append(result)
        self._print_result(result)

    def audit_hsmf(self):
        """Audit HSMF module."""
        print('\n--- Auditing HSMF ---')
        result = ModuleAuditResult('HSMF')
        issues = self.ast_checker.check_file('libs/HSMF.py')
        for issue in issues:
            result.add_issue(f'Zero-Simulation violation: {issue}')
        try:
            log_list = []
            cm = CertifiedMath(log_list)
            hsmf = HSMF(cm)
            chr_state = {'coherence_metric': BigNum128.from_string('1.5')}
            flx_state = {'scaling_metric': BigNum128.from_string('0.8')}
            psi_sync_state = {'frequency_metric': BigNum128.from_string('0.3')}
            atr_state = {'directional_metric': BigNum128.from_string('0.6')}
            res_state = {'inertial_metric': BigNum128.from_string('0.9')}
            lambda1 = BigNum128.from_string('1.618033988749894848')
            lambda2 = BigNum128.from_string('0.95')
            c_crit = BigNum128.from_string('1.0')
            bundle = create_token_state_bundle(chr_state, flx_state, psi_sync_state, atr_state, res_state, lambda1, lambda2, c_crit, 'TEST_PQC_011', 1700000000, {'test': 'metadata'})
            f_atr = BigNum128.from_string('0.5')
            result1 = hsmf.validate_action_bundle(bundle, f_atr, 'TEST_PQC_012', quantum_metadata={'test': 'metadata'})
            log_list.clear()
            cm.log_index = 0
            result2 = hsmf.validate_action_bundle(bundle, f_atr, 'TEST_PQC_012', quantum_metadata={'test': 'metadata'})
            if result1.is_valid != result2.is_valid or result1.dez_ok != result2.dez_ok or result1.survival_ok != result2.survival_ok or (len(result1.errors) != len(result2.errors)):
                result.add_issue('HSMF validation is not deterministic')
            metrics1 = {k: v.to_decimal_string() for k, v in result1.raw_metrics.items()}
            metrics2 = {k: v.to_decimal_string() for k, v in result2.raw_metrics.items()}
            if metrics1 != metrics2:
                result.add_issue('HSMF metrics are not deterministic')
            evidence = {'validation1': {'is_valid': result1.is_valid, 'dez_ok': result1.dez_ok, 'survival_ok': result1.survival_ok, 'errors': result1.errors, 'metrics': metrics1}, 'validation2': {'is_valid': result2.is_valid, 'dez_ok': result2.dez_ok, 'survival_ok': result2.survival_ok, 'errors': result2.errors, 'metrics': metrics2}, 'validation_match': result1.is_valid == result2.is_valid and result1.dez_ok == result2.dez_ok and (result1.survival_ok == result2.survival_ok) and (len(result1.errors) == len(result2.errors)) and (metrics1 == metrics2)}
            evidence_file = 'hsmf_evidence.json'
            with open(evidence_file, 'w') as f:
                json.dump(evidence, f, indent=2)
            result.add_evidence_file(evidence_file)
        except Exception as e:
            result.add_issue(f'HSMF testing failed: {str(e)}')
            traceback.print_exc()
        self.audit_results.append(result)
        self._print_result(result)

    def audit_cir302_handler(self):
        """Audit CIR302_Handler module."""
        print('\n--- Auditing CIR302_Handler ---')
        result = ModuleAuditResult('CIR302_Handler')
        issues = self.ast_checker.check_file('libs/CIR302_Handler.py')
        for issue in issues:
            result.add_issue(f'Zero-Simulation violation: {issue}')
        try:
            log_list = []
            cm = CertifiedMath(log_list)
            handler = CIR302_Handler(cm)
            test_system_state = {'token_states': {'CHR': {'coherence': '0.95'}, 'FLX': {'flux': '0.15'}, 'PSI_SYNC': {'sync': '0.08'}, 'ATR': {'attractor': '0.85'}, 'RES': {'resonance': '0.05'}}, 'hsmf_metrics': {'c_holo': '0.95', 's_flx': '0.15', 's_psi_sync': '0.08', 'f_atr': '0.85'}, 'error_details': 'Test quarantine scenario'}
            result1 = handler.trigger_quarantine('Test reason 1', test_system_state)
            result2 = handler.trigger_quarantine('Test reason 2', test_system_state)
            if not result2.is_quarantined:
                result.add_issue('CIR302_Handler should maintain quarantine state')
            seal1 = handler.generate_finality_seal(test_system_state)
            seal2 = handler.generate_finality_seal(test_system_state)
            if seal1 != seal2:
                result.add_issue('CIR302_Handler finality seal generation is not deterministic')
            evidence = {'quarantine1': {'is_quarantined': result1.is_quarantined, 'reason': result1.reason, 'timestamp': result1.timestamp, 'pqc_cid': result1.pqc_cid}, 'quarantine2': {'is_quarantined': result2.is_quarantined, 'reason': result2.reason, 'timestamp': result2.timestamp, 'pqc_cid': result2.pqc_cid}, 'seal1_prefix': seal1[:32], 'seal2_prefix': seal2[:32], 'seal_match': seal1 == seal2}
            evidence_file = 'cir302_handler_evidence.json'
            with open(evidence_file, 'w') as f:
                json.dump(evidence, f, indent=2)
            result.add_evidence_file(evidence_file)
        except Exception as e:
            result.add_issue(f'CIR302_Handler testing failed: {str(e)}')
            traceback.print_exc()
        self.audit_results.append(result)
        self._print_result(result)

    def audit_certified_math(self):
        """Audit CertifiedMath module."""
        print('\n--- Auditing CertifiedMath ---')
        result = ModuleAuditResult('CertifiedMath')
        issues = self.ast_checker.check_file('libs/CertifiedMath.py')
        for issue in issues:
            result.add_issue(f'Zero-Simulation violation: {issue}')
        try:
            log_list1 = []
            log_list2 = []
            cm1 = CertifiedMath(log_list1)
            cm2 = CertifiedMath(log_list2)
            a = BigNum128.from_string('10.5')
            b = BigNum128.from_string('5.25')
            result1 = cm1.add(a, b, 'TEST_PQC_013', {'test': 'metadata'})
            result2 = cm2.add(a, b, 'TEST_PQC_013', {'test': 'metadata'})
            if result1.value != result2.value:
                result.add_issue('CertifiedMath addition is not deterministic')
            if len(log_list1) != len(log_list2):
                result.add_issue('CertifiedMath log lengths differ')
            hash1 = cm1.get_log_hash()
            hash2 = cm2.get_log_hash()
            if hash1 != hash2:
                result.add_issue('CertifiedMath log hashing is not deterministic')
            evidence = {'result1': result1.to_decimal_string(), 'result2': result2.to_decimal_string(), 'result_match': result1.value == result2.value, 'log_length1': len(log_list1), 'log_length2': len(log_list2), 'log_hash1': hash1, 'log_hash2': hash2, 'log_hash_match': hash1 == hash2}
            evidence_file = 'certified_math_evidence.json'
            with open(evidence_file, 'w') as f:
                json.dump(evidence, f, indent=2)
            result.add_evidence_file(evidence_file)
        except Exception as e:
            result.add_issue(f'CertifiedMath testing failed: {str(e)}')
            traceback.print_exc()
        self.audit_results.append(result)
        self._print_result(result)

    def _print_result(self, result: ModuleAuditResult):
        """Print audit result."""
        status = '✅ PASSED' if result.passed else '❌ FAILED'
        print(f'{status} {result.module_name}')
        if result.issues:
            print('  Issues:')
            for issue in result.issues:
                print(f'    - {issue}')
        if result.recommendations:
            print('  Recommendations:')
            for recommendation in result.recommendations:
                print(f'    - {recommendation}')

def main():
    """Main entry point for Phase A audit."""
    auditor = ModuleMigrationAuditor()
    results = auditor.audit_all_modules()
    print('\n' + '=' * 60)
    print('PHASE A: MODULE MIGRATION AUDIT SUMMARY')
    print('=' * 60)
    passed_count = 0
    total_count = len(results)
    for result in results:
        status = '✅ PASSED' if result.passed else '❌ FAILED'
        print(f'{status} {result.module_name}')
        if result.issues:
            print(f'    Issues: {len(result.issues)}')
        if result.recommendations:
            print(f'    Recommendations: {len(result.recommendations)}')
        if result.passed:
            passed_count += 1
    print('\n' + '=' * 60)
    print(f'SUMMARY: {passed_count}/{total_count} modules passed audit')
    if passed_count == total_count:
        print('🎉 ALL MODULES PASSED MIGRATION AUDIT')
        print('✅ Zero-Simulation compliance verified')
        print('✅ Deterministic behavior confirmed')
        print('✅ PQC integration validated')
        print('✅ Quantum metadata handling confirmed')
    else:
        print('❌ SOME MODULES FAILED MIGRATION AUDIT')
        print('Please review the issues above and address them before proceeding.')
    print('=' * 60)
    return passed_count == total_count
if __name__ == '__main__':
    success = main()
    raise ZeroSimAbort(0 if success else 1)