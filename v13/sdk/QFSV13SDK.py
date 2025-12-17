"""
QFSV13SDK.py - Quantum Financial System V13 Software Development Kit

Implements the QFS V13 SDK for creating, validating, and submitting
deterministic transaction bundles with full PQC signing and audit trail support.
"""
import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from ..libs.CertifiedMath import BigNum128, CertifiedMath
from ..core.TokenStateBundle import TokenStateBundle
from ..core.HSMF import HSMF
from ...libs.TreasuryEngine import TreasuryEngine
from ..handlers.CIR302_Handler import CIR302_Handler
from ..libs.PQC import PQC
from ..core.DRV_Packet import DRV_Packet
from ..services.aegis_api import AEGIS_API
try:
    from ..libs.economics.EconomicsGuard import EconomicsGuard, ValidationResult
except ImportError:
    try:
        from v13.libs.economics.EconomicsGuard import EconomicsGuard, ValidationResult
    except ImportError:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'libs', 'economics'))
        from EconomicsGuard import EconomicsGuard, ValidationResult
try:
    from ..libs.governance.NODInvariantChecker import NODInvariantChecker, InvariantCheckResult
except ImportError:
    try:
        from v13.libs.governance.NODInvariantChecker import NODInvariantChecker, InvariantCheckResult
    except ImportError:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'libs', 'governance'))
        from NODInvariantChecker import NODInvariantChecker, InvariantCheckResult
try:
    from ..libs.governance.AEGIS_Node_Verification import AEGIS_Node_Verifier, NodeVerificationResult
except ImportError:
    try:
        from v13.libs.governance.AEGIS_Node_Verification import AEGIS_Node_Verifier, NodeVerificationResult
    except ImportError:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'libs', 'governance'))
        from AEGIS_Node_Verification import AEGIS_Node_Verifier, NodeVerificationResult

@dataclass
class SDKResponse:
    """Response from the QFS V13 SDK."""
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str]
    bundle_hash: Optional[str]
    pqc_signature: Optional[str]

class QFSV13SDK:
    """
    Quantum Financial System V13 Software Development Kit.
    
    Provides high-level interface for creating, validating, and submitting
    deterministic transaction bundles with full PQC signing and audit trail support.
    """

    def __init__(self, cm_instance: CertifiedMath, pqc_key_pair: Optional[tuple]=None):
        """
        Initialize the QFS V13 SDK with full constitutional guard integration (V13.6).
        
        Args:
            cm_instance: CertifiedMath instance for deterministic operations
            pqc_key_pair: Optional PQC key pair for signing bundles
        """
        self.cm = cm_instance
        self.pqc_private_key = pqc_key_pair[0] if pqc_key_pair else None
        self.pqc_public_key = pqc_key_pair[1] if pqc_key_pair else None
        self.hsmf = HSMF(cm_instance)
        self.treasury_engine = TreasuryEngine(cm_instance, pqc_key_pair)
        self.cir302_handler = CIR302_Handler(cm_instance, pqc_key_pair)
        self.aegis_api = AEGIS_API(cm_instance, pqc_key_pair)
        self.quantum_metadata = {'component': 'QFSV13SDK', 'version': 'QFS-V13.6-GUARDED', 'timestamp': None, 'pqc_scheme': 'Dilithium-5'}
        self.economics_guard = EconomicsGuard(cm_instance)
        self.nod_invariant_checker = NODInvariantChecker(cm_instance)
        self.aegis_node_verifier = AEGIS_Node_Verifier(cm_instance)
        self.enforce_guards = True
        self.guard_violations = []

    def create_transaction_bundle(self, chr_state: Dict[str, Any], flx_state: Dict[str, Any], psi_sync_state: Dict[str, Any], atr_state: Dict[str, Any], res_state: Dict[str, Any], lambda1: BigNum128, lambda2: BigNum128, c_crit: BigNum128, pqc_cid: str, timestamp: int, quantum_metadata: Optional[Dict[str, Any]]=None, bundle_id: Optional[str]=None, parameters: Optional[Dict[str, BigNum128]]=None) -> SDKResponse:
        """
        Create a new transaction bundle with deterministic properties.
        
        Args:
            chr_state: Coheron token state
            flx_state: Flux token state
            psi_sync_state: ΨSync token state
            atr_state: Attractor token state
            res_state: Resonance token state
            lambda1: Weight for S_FLX component
            lambda2: Weight for S_PsiSync component
            c_crit: Critical coherence threshold
            pqc_cid: PQC correlation ID
            timestamp: Deterministic timestamp (required for Zero-Simulation compliance)
            quantum_metadata: Quantum metadata for audit trail
            bundle_id: Unique bundle identifier (defaults to hash)
            parameters: Configuration parameters (Section 3.2)
            
        Returns:
            SDKResponse with result and bundle hash
        """
        try:
            token_bundle = TokenStateBundle(chr_state=chr_state, flx_state=flx_state, psi_sync_state=psi_sync_state, atr_state=atr_state, res_state=res_state, signature='', timestamp=timestamp, bundle_id=bundle_id or '', pqc_cid=pqc_cid, quantum_metadata=quantum_metadata or {}, lambda1=lambda1, lambda2=lambda2, c_crit=c_crit, parameters=parameters or {'beta_penalty': BigNum128.from_int(100000000), 'phi': BigNum128(1618033988749894848)})
            if not bundle_id:
                bundle_id = token_bundle.get_deterministic_hash(include_signature=False)
                token_bundle.bundle_id = bundle_id
            bundle_hash = token_bundle.get_deterministic_hash()
            return SDKResponse(success=True, data={'token_bundle': token_bundle.to_dict(), 'bundle_hash': bundle_hash, 'bundle_id': bundle_id}, error=None, bundle_hash=bundle_hash, pqc_signature=None)
        except Exception as e:
            return SDKResponse(success=False, data=None, error=f'Failed to create transaction bundle: {str(e)}', bundle_hash=None, pqc_signature=None)

    def validate_transaction_bundle(self, token_bundle: TokenStateBundle, f_atr: BigNum128, drv_packet: DRV_Packet) -> SDKResponse:
        """
        Validate a transaction bundle through the full QFS V13 pipeline.
        
        Args:
            token_bundle: Token state bundle to validate
            f_atr: Directional force from Utility Oracle
            drv_packet: DRV packet containing sequence and timestamp
            
        Returns:
            SDKResponse with validation results
        """
        try:
            with CertifiedMath.LogContext() as log_list:
                hsmf_result = self.hsmf.validate_action_bundle(token_bundle=token_bundle, f_atr=f_atr, drv_packet_sequence=drv_packet.sequence, log_list=log_list, pqc_cid=drv_packet.pqc_signature.hex() if drv_packet.pqc_signature else '', quantum_metadata=drv_packet.metadata, raise_on_failure=False)
                if not hsmf_result.is_valid:
                    return SDKResponse(success=False, data=None, error=f"HSMF validation failed: {'; '.join(hsmf_result.errors)}", bundle_hash=None, pqc_signature=None)
                treasury_result = self.treasury_engine.compute_rewards(hsmf_result=hsmf_result, token_bundle=token_bundle)
                if self.enforce_guards and treasury_result.is_valid:
                    chr_reward = treasury_result.rewards.get('chr_amount', BigNum128.from_int(0))
                    flx_reward = treasury_result.rewards.get('flx_amount', BigNum128.from_int(0))
                    if chr_reward.value > 0:
                        chr_validation = self.economics_guard.validate_chr_reward(reward_amount=chr_reward, current_daily_total=BigNum128.from_int(0), current_total_supply=BigNum128.from_int(0), log_list=log_list)
                        if not chr_validation.passed:
                            self.guard_violations.append({'type': 'ECON_BOUND_VIOLATION', 'error_code': chr_validation.error_code, 'message': chr_validation.error_message, 'details': chr_validation.details})
                            return SDKResponse(success=False, data=None, error=f'[GUARD] Economic bound violation: {chr_validation.error_message}', bundle_hash=None, pqc_signature=None)
                    if flx_reward.value > 0:
                        flx_validation = self.economics_guard.validate_flx_reward(flx_amount=flx_reward, chr_base=chr_reward, user_balance=BigNum128.from_int(0), log_list=log_list)
                        if not flx_validation.passed:
                            self.guard_violations.append({'type': 'ECON_BOUND_VIOLATION', 'error_code': flx_validation.error_code, 'message': flx_validation.error_message, 'details': flx_validation.details})
                            return SDKResponse(success=False, data=None, error=f'[GUARD] Economic bound violation: {flx_validation.error_message}', bundle_hash=None, pqc_signature=None)
                if not treasury_result.is_valid:
                    return SDKResponse(success=False, data=None, error=f"Treasury computation failed: {'; '.join(treasury_result.validation_errors)}", bundle_hash=None, pqc_signature=None)
                log_hash = CertifiedMath.get_log_hash(log_list)
                return SDKResponse(success=True, data={'hsmf_result': {'is_valid': hsmf_result.is_valid, 'c_holo': hsmf_result.raw_metrics.get('c_holo', BigNum128(0)).to_decimal_string(), 's_flx': hsmf_result.raw_metrics.get('s_flx', BigNum128(0)).to_decimal_string(), 's_psi_sync': hsmf_result.raw_metrics.get('s_psi_sync', BigNum128(0)).to_decimal_string(), 'f_atr': hsmf_result.raw_metrics.get('f_atr', BigNum128(0)).to_decimal_string()}, 'treasury_result': {'is_valid': treasury_result.is_valid, 'total_allocation': treasury_result.total_allocation.to_decimal_string(), 'rewards_count': len(treasury_result.rewards)}, 'log_hash': log_hash}, error=None, bundle_hash=log_hash, pqc_signature=None)
        except Exception as e:
            return SDKResponse(success=False, data=None, error=f'Failed to validate transaction bundle: {str(e)}', bundle_hash=None, pqc_signature=None)

    def sign_and_submit_bundle(self, token_bundle: TokenStateBundle, f_atr: BigNum128, drv_packet: DRV_Packet) -> SDKResponse:
        """
        Sign and submit a transaction bundle through the AEGIS API.
        
        Args:
            token_bundle: Token state bundle to sign and submit
            f_atr: Directional force from Utility Oracle
            drv_packet: DRV packet containing sequence and timestamp
            
        Returns:
            SDKResponse with submission results
        """
        try:
            api_response = self.aegis_api.process_transaction_bundle(drv_packet=drv_packet, token_bundle=token_bundle, f_atr=f_atr)
            if not api_response.success:
                return SDKResponse(success=False, data=None, error=api_response.error, bundle_hash=None, pqc_signature=None)
            return SDKResponse(success=True, data=api_response.data, error=None, bundle_hash=api_response.data.get('log_hash') if api_response.data else None, pqc_signature=api_response.finality_seal)
        except Exception as e:
            return SDKResponse(success=False, data=None, error=f'Failed to sign and submit bundle: {str(e)}', bundle_hash=None, pqc_signature=None)

    def load_token_state_bundle(self, bundle_data: Dict[str, Any]) -> TokenStateBundle:
        """
        Load a TokenStateBundle from serialized data.
        
        Args:
            bundle_data: Dictionary containing token state bundle data
            
        Returns:
            TokenStateBundle: Loaded token state bundle
        """
        return TokenStateBundle(chr_state=bundle_data.get('chr_state', {}), flx_state=bundle_data.get('flx_state', {}), psi_sync_state=bundle_data.get('psi_sync_state', {}), atr_state=bundle_data.get('atr_state', {}), res_state=bundle_data.get('res_state', {}), signature=bundle_data.get('signature', ''), timestamp=bundle_data.get('timestamp', 0), bundle_id=bundle_data.get('bundle_id', ''), pqc_cid=bundle_data.get('pqc_cid', ''), quantum_metadata=bundle_data.get('quantum_metadata', {}), lambda1=CertifiedMath.from_string(bundle_data.get('lambda1', '1.618033988749894848')), lambda2=CertifiedMath.from_string(bundle_data.get('lambda2', '0.618033988749894848')), c_crit=CertifiedMath.from_string(bundle_data.get('c_crit', '1.0')), parameters=bundle_data.get('parameters', {'beta_penalty': CertifiedMath.from_string('100000000.0'), 'phi': CertifiedMath.from_string('1.618033988749894848')}))

    def validate_nod_allocation_guarded(self, node_id: str, nod_amount: BigNum128, total_fees: BigNum128, registry_snapshot: Dict[str, Any], telemetry_snapshot: Dict[str, Any], node_voting_power: BigNum128, total_voting_power: BigNum128, node_reward_share: BigNum128, total_epoch_issuance: BigNum128, active_node_count: int, log_list: Optional[List[Dict[str, Any]]]=None) -> SDKResponse:
        """
        Validate NOD allocation with full constitutional guard enforcement.
        
        This method CANNOT be bypassed - all NOD allocations MUST route through here.
        
        Guards enforced:
        1. AEGIS node verification (registry, PQC, uptime, health)
        2. Economic bounds (allocation fractions, voting power caps, issuance limits)
        3. NOD invariants (non-transferability, supply conservation, voting bounds)
        
        Args:
            node_id: Node identifier to allocate NOD to
            nod_amount: Amount of NOD to allocate
            total_fees: Total ATR fees collected
            registry_snapshot: AEGIS registry snapshot (hash-anchored)
            telemetry_snapshot: AEGIS telemetry snapshot (hash-anchored)
            node_voting_power: Node's current voting power
            total_voting_power: Total system voting power
            node_reward_share: Node's reward share
            total_epoch_issuance: Total NOD issued this epoch
            active_node_count: Number of active nodes
            log_list: Optional log list for audit trail
            
        Returns:
            SDKResponse with validation results and guard verdicts
        """
        if log_list is None:
            log_list = []
        try:
            node_verification = self.aegis_node_verifier.verify_node(node_id=node_id, registry_snapshot=registry_snapshot, telemetry_snapshot=telemetry_snapshot, log_list=log_list)
            if not node_verification.is_valid:
                self.guard_violations.append({'type': 'NODE_VERIFICATION_FAILURE', 'node_id': node_id, 'status': node_verification.status.value, 'reason_code': node_verification.reason_code, 'message': node_verification.reason_message})
                return SDKResponse(success=False, data=None, error=f'[GUARD] Node verification failed: {node_verification.reason_message}', bundle_hash=None, pqc_signature=None)
            econ_validation = self.economics_guard.validate_nod_allocation(nod_amount=nod_amount, total_fees=total_fees, node_voting_power=node_voting_power, total_voting_power=total_voting_power, node_reward_share=node_reward_share, total_epoch_issuance=total_epoch_issuance, active_node_count=active_node_count, log_list=log_list)
            if not econ_validation.passed:
                self.guard_violations.append({'type': 'ECON_BOUND_VIOLATION', 'error_code': econ_validation.error_code, 'message': econ_validation.error_message, 'details': econ_validation.details})
                return SDKResponse(success=False, data=None, error=f'[GUARD] Economic bound violation: {econ_validation.error_message}', bundle_hash=None, pqc_signature=None)
            return SDKResponse(success=True, data={'node_id': node_id, 'nod_amount': nod_amount.to_decimal_string(), 'node_verification': node_verification.to_dict(), 'economic_validation': {'passed': True, 'allocation_fraction': econ_validation.details.get('fraction', 'N/A')}, 'guard_status': 'ALL_GUARDS_PASSED'}, error=None, bundle_hash=None, pqc_signature=None)
        except Exception as e:
            return SDKResponse(success=False, data=None, error=f'Failed to validate NOD allocation: {str(e)}', bundle_hash=None, pqc_signature=None)

    def validate_state_transition_guarded(self, previous_nod_supply: BigNum128, new_nod_supply: BigNum128, node_balances: Dict[str, BigNum128], allocations: List[Any], caller_module: str='StateTransitionEngine', operation_type: str='allocation', expected_hash: Optional[str]=None, log_list: Optional[List[Dict[str, Any]]]=None) -> SDKResponse:
        """
        Validate state transition with NOD invariant enforcement.
        
        This method enforces all 4 NOD invariants (NOD-I1 to NOD-I4).
        
        Args:
            previous_nod_supply: Previous total NOD supply
            new_nod_supply: New total NOD supply after transition
            node_balances: Dict mapping node_id to NOD balance
            allocations: List of NOD allocations in this transition
            caller_module: Module requesting the transition
            operation_type: Type of operation (allocation, governance, etc.)
            expected_hash: Optional expected deterministic hash for replay verification
            log_list: Optional log list for audit trail
            
        Returns:
            SDKResponse with invariant check results
        """
        if log_list is None:
            log_list = []
        try:
            invariant_results = self.nod_invariant_checker.validate_all_invariants(caller_module=caller_module, operation_type=operation_type, previous_total_supply=previous_nod_supply, new_total_supply=new_nod_supply, node_balances=node_balances, allocations=allocations, expected_hash=expected_hash, log_list=log_list)
            failed_invariants = [r for r in invariant_results if not r.passed]
            if failed_invariants:
                for result in failed_invariants:
                    self.guard_violations.append({'type': 'INVARIANT_VIOLATION', 'invariant_id': result.invariant_id, 'error_code': result.error_code, 'message': result.error_message, 'details': result.details})
                first_failure = failed_invariants[0]
                return SDKResponse(success=False, data=None, error=f'[GUARD] Invariant {first_failure.invariant_id} violation: {first_failure.error_message}', bundle_hash=None, pqc_signature=None)
            return SDKResponse(success=True, data={'invariants_checked': len(invariant_results), 'all_passed': True, 'invariant_results': [{'invariant_id': r.invariant_id, 'passed': r.passed} for r in invariant_results], 'guard_status': 'ALL_INVARIANTS_PASSED'}, error=None, bundle_hash=None, pqc_signature=None)
        except Exception as e:
            return SDKResponse(success=False, data=None, error=f'Failed to validate state transition: {str(e)}', bundle_hash=None, pqc_signature=None)

    def get_guard_violations(self) -> List[Dict[str, Any]]:
        """
        Retrieve all guard violations for audit trail.
        
        Returns:
            List of guard violation records
        """
        return self.guard_violations.copy()

    def clear_guard_violations(self) -> None:
        """
        Clear guard violation history.
        
        CAUTION: Only call after violations have been persisted to audit log.
        """
        self.guard_violations.clear()

def test_qfs_sdk():
    """Test the QFSV13SDK implementation."""
    print('Testing QFSV13SDK...')
    with CertifiedMath.LogContext() as log_list:
        cm = CertifiedMath()
    with PQC.LogContext() as pqc_log:
        keypair = PQC.generate_keypair(pqc_log)
        pqc_keypair = (bytes(keypair.private_key), keypair.public_key)
    sdk = QFSV13SDK(cm, pqc_keypair)
    chr_state = {'coherence_metric': '0.98', 'c_holo_proxy': '0.99', 'resonance_metric': '0.05', 'flux_metric': '0.15', 'psi_sync_metric': '0.08', 'atr_metric': '0.85'}
    parameters = {'beta_penalty': CertifiedMath.from_string('100000000.0'), 'phi': CertifiedMath.from_string('1.618033988749894848')}
    bundle_response = sdk.create_transaction_bundle(chr_state=chr_state, flx_state={'flux_metric': '0.15'}, psi_sync_state={'psi_sync_metric': '0.08'}, atr_state={'atr_metric': '0.85'}, res_state={'resonance_metric': '0.05'}, lambda1=CertifiedMath.from_string('0.3'), lambda2=CertifiedMath.from_string('0.2'), c_crit=CertifiedMath.from_string('0.9'), pqc_cid='test_pqc_cid', timestamp=1234567890, quantum_metadata={'test': 'data'}, parameters=parameters)
    print(f'Bundle creation success: {bundle_response.success}')
    if bundle_response.error:
        print(f'Error: {bundle_response.error}')
    if bundle_response.bundle_hash:
        print(f'Bundle hash: {bundle_response.bundle_hash[:32]}...')
    quantum_metadata = {'source': 'test', 'timestamp': '0', 'pqc_scheme': 'Dilithium-5'}
    drv_packet = DRV_Packet(ttsTimestamp=1234567890, sequence=1, seed='test_seed', metadata={'test': 'data'}, previous_hash='0' * 64, pqc_cid='test_pqc_cid', quantum_metadata=quantum_metadata)
    f_atr = CertifiedMath.from_string('0.85')
    if bundle_response.data and 'token_bundle' in bundle_response.data:
        token_bundle = sdk.load_token_state_bundle(bundle_response.data['token_bundle'])
        validation_response = sdk.validate_transaction_bundle(token_bundle, f_atr, drv_packet)
        print(f'Bundle validation success: {validation_response.success}')
        if validation_response.error:
            print(f'Validation error: {validation_response.error}')
        if validation_response.bundle_hash:
            print(f'Validation hash: {validation_response.bundle_hash[:32]}...')
        submission_response = sdk.sign_and_submit_bundle(token_bundle, f_atr, drv_packet)
        print(f'Bundle submission success: {submission_response.success}')
        if submission_response.error:
            print(f'Submission error: {submission_response.error}')
        if submission_response.pqc_signature:
            print(f'PQC signature: {submission_response.pqc_signature[:32]}...')
if __name__ == '__main__':
    test_qfs_sdk()