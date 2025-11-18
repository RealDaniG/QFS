"""
QFSV13SDK.py - Quantum Financial System V13 Software Development Kit

Implements the QFS V13 SDK for creating, validating, and submitting
deterministic transaction bundles with full PQC signing and audit trail support.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Import required components
from ..libs.CertifiedMath import BigNum128, CertifiedMath
from ..core.TokenStateBundle import TokenStateBundle
from ..core.HSMF import HSMF
from ...libs.TreasuryEngine import TreasuryEngine
from ..handlers.CIR302_Handler import CIR302_Handler
from ..libs.PQC import PQC
from ..core.DRV_Packet import DRV_Packet
from ..services.aegis_api import AEGIS_API


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
    
    def __init__(self, cm_instance: CertifiedMath, pqc_key_pair: Optional[tuple] = None):
        """
        Initialize the QFS V13 SDK.
        
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
        self.quantum_metadata = {
            "component": "QFSV13SDK",
            "version": "QFS-V13-P1-2",
            "timestamp": None,
            "pqc_scheme": "Dilithium-5"
        }
        
    def create_transaction_bundle(self, 
                                chr_state: Dict[str, Any],
                                flx_state: Dict[str, Any],
                                psi_sync_state: Dict[str, Any],
                                atr_state: Dict[str, Any],
                                res_state: Dict[str, Any],
                                lambda1: BigNum128,
                                lambda2: BigNum128,
                                c_crit: BigNum128,
                                pqc_cid: str,
                                timestamp: int,
                                quantum_metadata: Optional[Dict[str, Any]] = None,
                                bundle_id: Optional[str] = None,
                                parameters: Optional[Dict[str, BigNum128]] = None) -> SDKResponse:
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
            # Create token state bundle
            token_bundle = TokenStateBundle(
                chr_state=chr_state,
                flx_state=flx_state,
                psi_sync_state=psi_sync_state,
                atr_state=atr_state,
                res_state=res_state,
                signature="",  # Signature will be added by the AGI Control Plane
                timestamp=timestamp,
                bundle_id=bundle_id or "",
                pqc_cid=pqc_cid,
                quantum_metadata=quantum_metadata or {},
                lambda1=lambda1,
                lambda2=lambda2,
                c_crit=c_crit,
                parameters=parameters or {
                    "beta_penalty": BigNum128.from_int(100000000),
                    "phi": BigNum128(1618033988749894848)  # φ (golden ratio) * 1e18
                }
            )
            
            # If bundle_id wasn't provided, generate it from the bundle hash
            if not bundle_id:
                bundle_id = token_bundle.get_deterministic_hash(include_signature=False)
                # Update the bundle with the generated ID
                token_bundle.bundle_id = bundle_id
            
            # Generate bundle hash
            bundle_hash = token_bundle.get_deterministic_hash()
            
            return SDKResponse(
                success=True,
                data={
                    "token_bundle": token_bundle.to_dict(),
                    "bundle_hash": bundle_hash,
                    "bundle_id": bundle_id
                },
                error=None,
                bundle_hash=bundle_hash,
                pqc_signature=None
            )
            
        except Exception as e:
            return SDKResponse(
                success=False,
                data=None,
                error=f"Failed to create transaction bundle: {str(e)}",
                bundle_hash=None,
                pqc_signature=None
            )
    
    def validate_transaction_bundle(self, token_bundle: TokenStateBundle, 
                                  f_atr: BigNum128, drv_packet: DRV_Packet) -> SDKResponse:
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
            # Create log context for this validation
            with CertifiedMath.LogContext() as log_list:
                # Validate action bundle through HSMF
                hsmf_result = self.hsmf.validate_action_bundle(
                    token_bundle=token_bundle,
                    f_atr=f_atr,
                    drv_packet_sequence=drv_packet.sequence,
                    log_list=log_list,
                    pqc_cid=drv_packet.pqc_signature.hex() if drv_packet.pqc_signature else "",
                    quantum_metadata=drv_packet.metadata,
                    raise_on_failure=False
                )
                
                # Check if HSMF validation passed
                if not hsmf_result.is_valid:
                    return SDKResponse(
                        success=False,
                        data=None,
                        error=f"HSMF validation failed: {'; '.join(hsmf_result.errors)}",
                        bundle_hash=None,
                        pqc_signature=None
                    )
                
                # Calculate rewards through Treasury Engine
                treasury_result = self.treasury_engine.compute_rewards(
                    hsmf_result=hsmf_result,
                    token_bundle=token_bundle
                )
                
                # Check if treasury computation passed
                if not treasury_result.is_valid:
                    return SDKResponse(
                        success=False,
                        data=None,
                        error=f"Treasury computation failed: {'; '.join(treasury_result.validation_errors)}",
                        bundle_hash=None,
                        pqc_signature=None
                    )
                
                # Generate validation hash
                log_hash = CertifiedMath.get_log_hash(log_list)
                
                return SDKResponse(
                    success=True,
                    data={
                        "hsmf_result": {
                            "is_valid": hsmf_result.is_valid,
                            "c_holo": hsmf_result.raw_metrics.get("c_holo", BigNum128(0)).to_decimal_string(),
                            "s_flx": hsmf_result.raw_metrics.get("s_flx", BigNum128(0)).to_decimal_string(),
                            "s_psi_sync": hsmf_result.raw_metrics.get("s_psi_sync", BigNum128(0)).to_decimal_string(),
                            "f_atr": hsmf_result.raw_metrics.get("f_atr", BigNum128(0)).to_decimal_string()
                        },
                        "treasury_result": {
                            "is_valid": treasury_result.is_valid,
                            "total_allocation": treasury_result.total_allocation.to_decimal_string(),
                            "rewards_count": len(treasury_result.rewards)
                        },
                        "log_hash": log_hash
                    },
                    error=None,
                    bundle_hash=log_hash,
                    pqc_signature=None
                )
                
        except Exception as e:
            return SDKResponse(
                success=False,
                data=None,
                error=f"Failed to validate transaction bundle: {str(e)}",
                bundle_hash=None,
                pqc_signature=None
            )
    
    def sign_and_submit_bundle(self, token_bundle: TokenStateBundle, 
                             f_atr: BigNum128, drv_packet: DRV_Packet) -> SDKResponse:
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
            # Process transaction through AEGIS API
            api_response = self.aegis_api.process_transaction_bundle(
                drv_packet=drv_packet,
                token_bundle=token_bundle,
                f_atr=f_atr
            )
            
            if not api_response.success:
                return SDKResponse(
                    success=False,
                    data=None,
                    error=api_response.error,
                    bundle_hash=None,
                    pqc_signature=None
                )
            
            return SDKResponse(
                success=True,
                data=api_response.data,
                error=None,
                bundle_hash=api_response.data.get("log_hash") if api_response.data else None,
                pqc_signature=api_response.finality_seal
            )
            
        except Exception as e:
            return SDKResponse(
                success=False,
                data=None,
                error=f"Failed to sign and submit bundle: {str(e)}",
                bundle_hash=None,
                pqc_signature=None
            )
    
    def load_token_state_bundle(self, bundle_data: Dict[str, Any]) -> TokenStateBundle:
        """
        Load a TokenStateBundle from serialized data.
        
        Args:
            bundle_data: Dictionary containing token state bundle data
            
        Returns:
            TokenStateBundle: Loaded token state bundle
        """
        return TokenStateBundle(
            chr_state=bundle_data.get('chr_state', {}),
            flx_state=bundle_data.get('flx_state', {}),
            psi_sync_state=bundle_data.get('psi_sync_state', {}),
            atr_state=bundle_data.get('atr_state', {}),
            res_state=bundle_data.get('res_state', {}),
            signature=bundle_data.get('signature', ''),
            timestamp=bundle_data.get('timestamp', 0),
            bundle_id=bundle_data.get('bundle_id', ''),
            pqc_cid=bundle_data.get('pqc_cid', ''),
            quantum_metadata=bundle_data.get('quantum_metadata', {}),
            lambda1=CertifiedMath.from_string(bundle_data.get('lambda1', '1.618033988749894848')),
            lambda2=CertifiedMath.from_string(bundle_data.get('lambda2', '0.618033988749894848')),
            c_crit=CertifiedMath.from_string(bundle_data.get('c_crit', '1.0')),
            parameters=bundle_data.get('parameters', {
                "beta_penalty": CertifiedMath.from_string('100000000.0'),
                "phi": CertifiedMath.from_string('1.618033988749894848')
            })
        )


# Test function
def test_qfs_sdk():
    """Test the QFSV13SDK implementation."""
    print("Testing QFSV13SDK...")
    
    # Create test log list and CertifiedMath instance
    with CertifiedMath.LogContext() as log_list:
        cm = CertifiedMath()
    
    # Create test PQC key pair
    with PQC.LogContext() as pqc_log:
        keypair = PQC.generate_keypair(pqc_log)
        pqc_keypair = (bytes(keypair.private_key), keypair.public_key)
    
    # Initialize QFS V13 SDK
    sdk = QFSV13SDK(cm, pqc_keypair)
    
    # Create test token states
    chr_state = {
        "coherence_metric": "0.98",
        "c_holo_proxy": "0.99",
        "resonance_metric": "0.05",
        "flux_metric": "0.15",
        "psi_sync_metric": "0.08",
        "atr_metric": "0.85"
    }
    
    parameters = {
        "beta_penalty": CertifiedMath.from_string("100000000.0"),
        "phi": CertifiedMath.from_string("1.618033988749894848")
    }
    
    # Create transaction bundle
    bundle_response = sdk.create_transaction_bundle(
        chr_state=chr_state,
        flx_state={"flux_metric": "0.15"},
        psi_sync_state={"psi_sync_metric": "0.08"},
        atr_state={"atr_metric": "0.85"},
        res_state={"resonance_metric": "0.05"},
        lambda1=CertifiedMath.from_string("0.3"),
        lambda2=CertifiedMath.from_string("0.2"),
        c_crit=CertifiedMath.from_string("0.9"),
        pqc_cid="test_pqc_cid",
        timestamp=1234567890,
        quantum_metadata={"test": "data"},
        parameters=parameters
    )
    
    print(f"Bundle creation success: {bundle_response.success}")
    if bundle_response.error:
        print(f"Error: {bundle_response.error}")
    if bundle_response.bundle_hash:
        print(f"Bundle hash: {bundle_response.bundle_hash[:32]}...")
    
    # Create test DRV_Packet
    quantum_metadata = {
        "source": "test",
        "timestamp": "0",
        "pqc_scheme": "Dilithium-5"
    }
    
    drv_packet = DRV_Packet(
        ttsTimestamp=1234567890,
        sequence=1,
        seed="test_seed",
        metadata={"test": "data"},
        previous_hash="0" * 64,
        pqc_cid="test_pqc_cid",
        quantum_metadata=quantum_metadata
    )
    
    # Create test f_atr value
    f_atr = CertifiedMath.from_string("0.85")
    
    # Load the token bundle from the response
    if bundle_response.data and 'token_bundle' in bundle_response.data:
        token_bundle = sdk.load_token_state_bundle(bundle_response.data['token_bundle'])
        
        # Validate transaction bundle
        validation_response = sdk.validate_transaction_bundle(token_bundle, f_atr, drv_packet)
        print(f"Bundle validation success: {validation_response.success}")
        if validation_response.error:
            print(f"Validation error: {validation_response.error}")
        if validation_response.bundle_hash:
            print(f"Validation hash: {validation_response.bundle_hash[:32]}...")
        
        # Sign and submit bundle
        submission_response = sdk.sign_and_submit_bundle(token_bundle, f_atr, drv_packet)
        print(f"Bundle submission success: {submission_response.success}")
        if submission_response.error:
            print(f"Submission error: {submission_response.error}")
        if submission_response.pqc_signature:
            print(f"PQC signature: {submission_response.pqc_signature[:32]}...")


if __name__ == "__main__":
    test_qfs_sdk()