#!/usr/bin/env python3
"""
Deterministic Replay Test for QFS V13
Runs the same sequence of operations twice and verifies identical results
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.libs.CertifiedMath import CertifiedMath, BigNum128
from src.core.HSMF import HSMF
from src.core.TokenStateBundle import TokenStateBundle
from libs.UtilityOracleInterface import UtilityOracleInterface
from libs.TreasuryEngine import TreasuryEngine
from src.core.DRV_Packet import DRV_Packet

# Add the current directory to the path so we can import from libs
sys.path.insert(0, os.path.dirname(__file__))

def create_test_drv_packet():
    """Create a deterministic DRV_Packet for testing"""
    # Create deterministic test data
    test_data = {
        "action_type": "TRANSFER",
        "source_address": "test_source_1234567890",
        "destination_address": "test_destination_0987654321",
        "amount": "100.50",
        "nonce": "1",
        "timestamp": 1234567890,
        "quantum_seed": "deterministic_seed_for_testing_purposes_1234567890"
    }
    
    # Create packet with deterministic parameters
    packet = DRV_Packet(
        ttsTimestamp=1234567890,
        sequence=1,
        seed="deterministic_seed_for_testing"
    )
    
    return packet

def create_test_token_bundle():
    """Create a deterministic TokenStateBundle for testing"""
    chr_state = {
        "coherence_metric": "0.98",
        "c_holo_proxy": "0.99",
        "resonance_metric": "0.05",
        "flux_metric": "0.15",
        "psi_sync_metric": "0.08",
        "atr_metric": "0.85"
    }
    
    token_bundle = TokenStateBundle(
        chr_state=chr_state,
        flx_state={"flux_metric": "0.15"},
        psi_sync_state={"psi_sync_metric": "0.08"},
        atr_state={"atr_metric": "0.85"},
        res_state={"resonance_metric": "0.05"},
        signature="test_deterministic_signature",
        timestamp=1234567890,
        bundle_id="test_deterministic_bundle_id",
        pqc_cid="test_deterministic_pqc_cid",
        quantum_metadata={"test": "deterministic_data"},
        lambda1=BigNum128.from_int(300000000000000000),
        lambda2=BigNum128.from_int(200000000000000000),
        c_crit=BigNum128.from_int(900000000000000000),
        parameters={}
    )
    
    return token_bundle

def run_deterministic_test_run(run_number):
    """Run a deterministic test and return the log hash"""
    print(f"Running deterministic test run #{run_number}...")
    
    # Create CertifiedMath instance
    cm = CertifiedMath()
    
    # Create test components
    drv_packet = create_test_drv_packet()
    token_bundle = create_test_token_bundle()
    
    # Run through HSMF validation
    with CertifiedMath.LogContext() as hsmf_log:
        hsmf = HSMF(cm)
        # Create a mock f_atr value for testing
        f_atr = BigNum128.from_int(500000000000000000)  # 0.5
        validation_result = hsmf.validate_action_bundle(token_bundle, f_atr, drv_packet.sequence, hsmf_log)
    
    # Run through UtilityOracleInterface
    with CertifiedMath.LogContext() as oracle_log:
        oracle = UtilityOracleInterface(cm, "test_pqc_cid")
        f_atr = oracle.get_f_atr(drv_packet, oracle_log)
        # Create mock states for alpha update
        current_state = BigNum128.from_int(1000000000000000000)  # 1.0
        target_state = BigNum128.from_int(1100000000000000000)   # 1.1
        alpha_update = oracle.get_alpha_update(current_state, target_state, oracle_log)
    
    # Run through TreasuryEngine
    with CertifiedMath.LogContext() as treasury_log:
        treasury = TreasuryEngine(cm)
        # Create mock HSMF result
        class MockHSMFResult:
            def __init__(self):
                self.is_valid = True
                self.dez_ok = True
                self.errors = []
                self.raw_metrics = {
                    "c_holo": BigNum128.from_int(950000000000000000),
                    "s_flx": BigNum128.from_int(150000000000000000),
                    "s_psi_sync": BigNum128.from_int(80000000000000000),
                    "f_atr": f_atr,
                    "s_chr": BigNum128.from_int(980000000000000000)
                }
            
            @property
            def metrics_str(self):
                return {k: v.to_decimal_string() for k, v in self.raw_metrics.items()}
        
        hsmf_result = MockHSMFResult()
        treasury_result = treasury.compute_rewards(hsmf_result, token_bundle, 1234567890)
    
    # Combine all logs for final hash
    combined_log = hsmf_log + oracle_log + treasury_log
    final_hash = CertifiedMath.get_log_hash(combined_log)
    
    print(f"Run #{run_number} completed. Final log hash: {final_hash}")
    return final_hash

def main():
    """Main test function"""
    print("Starting deterministic replay test...")
    
    # Run the same sequence twice
    hash1 = run_deterministic_test_run(1)
    hash2 = run_deterministic_test_run(2)
    
    # Verify hashes match
    if hash1 == hash2:
        print("✅ DETERMINISTIC REPLAY TEST PASSED - Hashes match!")
        print(f"Hash: {hash1}")
        return True
    else:
        print("❌ DETERMINISTIC REPLAY TEST FAILED - Hashes do not match!")
        print(f"Hash 1: {hash1}")
        print(f"Hash 2: {hash2}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)