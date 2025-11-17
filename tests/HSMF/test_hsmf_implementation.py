"""
Test script for HSMF.py to verify the implementation works correctly.
"""

import json
import sys
import os

# Add the libs directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

from CertifiedMath import BigNum128, CertifiedMath
from TokenStateBundle import TokenStateBundle, create_token_state_bundle
from CIR302_Handler import CIR302_Handler
from HSMF import HSMF


def test_hsmf():
    """Test the HSMF implementation."""
    print("Testing HSMF...")
    
    # Create test log list and CertifiedMath instance
    log_list = []
    cm = CertifiedMath(log_list)
    
    # Create CIR302 handler
    cir302_handler = CIR302_Handler(cm)
    
    # Create HSMF instance
    hsmf = HSMF(cm, cir302_handler)
    
    # Create test token bundle
    chr_state = {"coherence_metric": "0.98"}
    flx_state = {"magnitudes": [
        BigNum128.from_string("1.0"),
        BigNum128.from_string("1.618"),
        BigNum128.from_string("2.618")
    ]}
    psi_sync_state = {"current_sequence": BigNum128.from_int(100)}
    atr_state = {"atr_magnitude": BigNum128.from_string("1.0")}
    res_state = {"inertial_metric": "0.05"}
    
    lambda1 = BigNum128.from_string("1.618033988749894848")  # Golden ratio
    lambda2 = BigNum128.from_string("0.95")
    c_crit = BigNum128.from_string("0.9")
    
    token_bundle = create_token_state_bundle(
        chr_state=chr_state,
        flx_state=flx_state,
        psi_sync_state=psi_sync_state,
        atr_state=atr_state,
        res_state=res_state,
        lambda1=lambda1,
        lambda2=lambda2,
        c_crit=c_crit,
        pqc_cid="TEST_PQC"
    )
    
    f_atr = BigNum128.from_string("0.005")  # Should be coherent (< 1% of atr_magnitude)
    
    # Test validation
    try:
        result = hsmf.validate_action_bundle(token_bundle, f_atr, pqc_cid="TEST_PQC")
        print(f"Validation successful: {result.is_valid}")
        print(f"DEZ OK: {result.dez_ok}")
        print(f"Survival OK: {result.survival_ok}")
        print(f"Errors: {result.errors}")
        print("Metrics:")
        for name, value in result.metrics_str.items():
            print(f"  {name}: {value}")
        print(f"Total log entries: {len(log_list)}")
        return True
    except Exception as e:
        print(f"Validation failed with exception: {e}")
        return False


if __name__ == "__main__":
    success = test_hsmf()
    if success:
        print("HSMF test passed!")
    else:
        print("HSMF test failed!")
        sys.exit(1)