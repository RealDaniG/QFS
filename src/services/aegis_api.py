"""
aegis_api.py - Secure API Gateway for QFS V13

Implements the AEGIS API Gateway for receiving transaction bundles,
validating PQC signatures, instantiating log contexts, and committing
validated state updates with PQC-signed finality seals.
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


@dataclass
class APIResponse:
    """Response from the AEGIS API."""
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str]
    finality_seal: Optional[str]
    pqc_cid: Optional[str]


class AEGIS_API:
    """
    Secure API Gateway for QFS V13.
    
    Receives transaction bundles, validates PQC signatures, instantiates log contexts,
    and commits validated state updates with PQC-signed finality seals.
    """
    
    def __init__(self, cm_instance: CertifiedMath, pqc_key_pair: Optional[tuple] = None):
        """
        Initialize the AEGIS API Gateway.
        
        Args:
            cm_instance: CertifiedMath instance for deterministic operations
            pqc_key_pair: Optional PQC key pair for signing API responses
        """
        self.cm = cm_instance
        self.pqc_private_key = pqc_key_pair[0] if pqc_key_pair else None
        self.pqc_public_key = pqc_key_pair[1] if pqc_key_pair else None
        self.hsmf = HSMF(cm_instance)
        self.treasury_engine = TreasuryEngine(cm_instance, pqc_key_pair)
        self.cir302_handler = CIR302_Handler(cm_instance, pqc_key_pair)
        self.quantum_metadata = {
            "component": "AEGIS_API",
            "version": "QFS-V13-P1-2",
            "timestamp": None,
            "pqc_scheme": "Dilithium-5"
        }
        
    def process_transaction_bundle(self, drv_packet: DRV_Packet, 
                                 token_bundle: TokenStateBundle,
                                 f_atr: BigNum128) -> APIResponse:
        """
        Process a transaction bundle through the full QFS V13 pipeline.
        
        Args:
            drv_packet: DRV_Packet with PQC signature and deterministic timestamp
            token_bundle: Current token state bundle
            f_atr: Directional force from Utility Oracle
            
        Returns:
            APIResponse with result and finality seal
        """
        try:
            # Validate DRV_Packet PQC signature
            if not drv_packet.verify_signature(self.pqc_public_key if self.pqc_public_key else b""):
                return APIResponse(
                    success=False,
                    data=None,
                    error="Invalid DRV_Packet PQC signature",
                    finality_seal=None,
                    pqc_cid=""
                )
            
            # Validate DRV_Packet sequence and chain integrity
            # For this example, we'll assume previous_packet is None (genesis packet)
            # In a real implementation, you would pass the previous packet
            chain_validation = DRV_Packet.validate_chain(None, drv_packet)
            if not chain_validation.is_valid:
                return APIResponse(
                    success=False,
                    data=None,
                    error=f"Invalid DRV_Packet sequence or chain: {chain_validation.error_message}",
                    finality_seal=None,
                    pqc_cid=""
                )
            
            # Create log context for this transaction
            with CertifiedMath.LogContext() as log_list:
                # Validate action bundle through HSMF
                hsmf_result = self.hsmf.validate_action_bundle(
                    token_bundle=token_bundle,
                    f_atr=f_atr,
                    drv_packet_sequence=drv_packet.sequence,  # Use sequence number
                    log_list=log_list,
                    pqc_cid=drv_packet.pqc_signature.hex() if drv_packet.pqc_signature else "",
                    quantum_metadata=drv_packet.metadata,  # Use metadata as quantum metadata
                    raise_on_failure=False
                )
                
                # Check if HSMF validation passed
                if not hsmf_result.is_valid:
                    # Trigger CIR-302 quarantine
                    system_state = {
                        "token_bundle": token_bundle.to_dict(),
                        "drv_packet": drv_packet.to_dict(),
                        "hsmf_errors": hsmf_result.errors,
                        "log_list": log_list
                    }
                    
                    quarantine_result = self.cir302_handler.trigger_quarantine(
                        reason="HSMF validation failed",
                        system_state=system_state
                    )
                    
                    return APIResponse(
                        success=False,
                        data=None,
                        error="HSMF validation failed",
                        finality_seal=quarantine_result.finality_seal,
                        pqc_cid=quarantine_result.pqc_cid
                    )
                
                # Calculate rewards through Treasury Engine
                treasury_result = self.treasury_engine.compute_rewards(
                    hsmf_result=hsmf_result,
                    token_bundle=token_bundle
                )
                
                # Check if treasury computation passed
                if not treasury_result.is_valid:
                    # Trigger CIR-302 quarantine
                    system_state = {
                        "token_bundle": token_bundle.to_dict(),
                        "drv_packet": drv_packet.to_dict(),
                        "treasury_errors": treasury_result.validation_errors,
                        "log_list": log_list
                    }
                    
                    quarantine_result = self.cir302_handler.trigger_quarantine(
                        reason="Treasury computation failed",
                        system_state=system_state
                    )
                    
                    return APIResponse(
                        success=False,
                        data=None,
                        error="Treasury computation failed",
                        finality_seal=quarantine_result.finality_seal,
                        pqc_cid=quarantine_result.pqc_cid
                    )
                
                # Generate finality seal
                log_hash = CertifiedMath.get_log_hash(log_list)
                pqc_cid = self._generate_pqc_cid(drv_packet, token_bundle, hsmf_result, treasury_result)
                
                # Update quantum metadata
                self.quantum_metadata["timestamp"] = str(drv_packet.ttsTimestamp)
                
                # Create response data
                response_data = {
                    "token_bundle": token_bundle.to_dict(),
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
                    "log_hash": log_hash,
                    "pqc_cid": pqc_cid,
                    "quantum_metadata": self.quantum_metadata
                }
                
                # Sign the final bundle hash
                finality_seal = self._sign_finality_seal(response_data, log_list)
                
                return APIResponse(
                    success=True,
                    data=response_data,
                    error=None,
                    finality_seal=finality_seal,
                    pqc_cid=pqc_cid
                )
                
        except Exception as e:
            # Trigger CIR-302 quarantine on any unexpected error
            system_state = {
                "token_bundle": token_bundle.to_dict() if token_bundle else {},
                "drv_packet": drv_packet.to_dict() if drv_packet else {},
                "error": str(e)
            }
            
            quarantine_result = self.cir302_handler.trigger_quarantine(
                reason=f"Unexpected API error: {str(e)}",
                system_state=system_state
            )
            
            return APIResponse(
                success=False,
                data=None,
                error=f"Unexpected API error: {str(e)}",
                finality_seal=quarantine_result.finality_seal,
                pqc_cid=quarantine_result.pqc_cid
            )
    
    def _sign_finality_seal(self, response_data: Dict[str, Any], log_list: List[Dict[str, Any]]) -> str:
        """
        Sign the finality seal for a validated transaction bundle.
        
        Args:
            response_data: Response data to sign
            log_list: Log list for PQC operation
            
        Returns:
            str: Hex representation of PQC signature
        """
        if not self.pqc_private_key:
            return ""
            
        try:
            # Serialize response data for signing
            response_json = json.dumps(response_data, sort_keys=True, separators=(',', ':'))
            signature = PQC.sign_data(self.pqc_private_key, response_json.encode('utf-8'), log_list)
            return signature.hex()
        except Exception as e:
            print(f"Finality seal signing failed: {str(e)}")
            return ""
    
    def _generate_pqc_cid(self, drv_packet: DRV_Packet, token_bundle: TokenStateBundle,
                         hsmf_result: Any, treasury_result: Any) -> str:
        """
        Generate deterministic PQC correlation ID.
        
        Args:
            drv_packet: DRV_Packet
            token_bundle: Token state bundle
            hsmf_result: HSMF validation result
            treasury_result: Treasury computation result
            
        Returns:
            str: Deterministic PQC correlation ID
        """
        data_to_hash = {
            "drv_packet_hash": drv_packet.get_hash(),
            "token_bundle_hash": token_bundle.get_deterministic_hash(),
            "hsmf_valid": hsmf_result.is_valid if hasattr(hsmf_result, 'is_valid') else False,
            "treasury_valid": treasury_result.is_valid if hasattr(treasury_result, 'is_valid') else False,
            "timestamp": drv_packet.ttsTimestamp
        }
        
        data_json = json.dumps(data_to_hash, sort_keys=True)
        return hashlib.sha256(data_json.encode()).hexdigest()[:32]


# Test function
def test_aegis_api():
    """Test the AEGIS_API implementation."""
    print("Testing AEGIS_API...")
    
    # Create test log list and CertifiedMath instance
    with CertifiedMath.LogContext() as log_list:
        cm = CertifiedMath()
    
    # Create test PQC key pair
    with PQC.LogContext() as pqc_log:
        keypair = PQC.generate_keypair(pqc_log)
        pqc_keypair = (bytes(keypair.private_key), keypair.public_key)
    
    # Initialize AEGIS API
    api = AEGIS_API(cm, pqc_keypair)
    
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
    
    # Create test token bundle
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
    
    token_bundle = TokenStateBundle(
        chr_state=chr_state,
        flx_state={"flux_metric": "0.15"},
        psi_sync_state={"psi_sync_metric": "0.08"},
        atr_state={"atr_metric": "0.85"},
        res_state={"resonance_metric": "0.05"},
        signature="test_signature",
        timestamp=1234567890,
        bundle_id="test_bundle_id",
        pqc_cid="test_pqc_cid",
        quantum_metadata={"test": "data"},
        lambda1=CertifiedMath.from_string("0.3"),
        lambda2=CertifiedMath.from_string("0.2"),
        c_crit=CertifiedMath.from_string("0.9"),
        parameters=parameters
    )
    
    # Create test f_atr value
    f_atr = CertifiedMath.from_string("0.85")
    
    # Process transaction bundle
    result = api.process_transaction_bundle(drv_packet, token_bundle, f_atr)
    
    print(f"Transaction processing success: {result.success}")
    if result.error:
        print(f"Error: {result.error}")
    if result.finality_seal:
        print(f"Finality seal: {result.finality_seal[:32]}...")
    if result.pqc_cid:
        print(f"PQC CID: {result.pqc_cid}")


if __name__ == "__main__":
    test_aegis_api()